"""
Helpers for setting up Fluent Bit as a sidecar container.

Fluent Bit design notes:

* We use Fluent Bit as a sidecar container to forward logs from the main
  container to the facilitator.
* We chose Fluent Bit because we don't want to write our own log forwarding
  agent, and Fluent Bit is the industry standard.
* We chose to deploy Fluent Bit as a sidecar because it is forwards-compatible
  to Fargate, which does not support DaemonSets.
* The `fluent_bit_containers()` expect to be `initContainers` in a pod, and
  (since they set their `restartPolicy` to `Always`) they will be treated as
  "native sidecar" containers by Kubernetes; see:
    https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
* Being a "native sidecar" is important, because it ensures that...
    1. In combination with Istio's support for native sidecars, Fluent Bit can
       safely assume that the Istio proxy in the Pod is configured. Without this
       the Istio proxy could briefly return 404s for the facilitator, causing
       logs to be dropped.
    2. The Fluent Bit container gets its SIGTERM only after the main container
       is done, which ensures that the main container can't add logs after
       Fluent Bit has stopped forwarding.
    3. The Fluent Bit container gets its SIGTERM before the Istio proxy does,
       which ensures that Fluent Bit has the necessary network connectivity to
       flush any remaining logs.

TODO(rjh): the Fluent Bit container is still subject to the grace period set for
           the whole Pod, so it is possible that logs are dropped if for some
           reason Fluent Bit can't flush them in time. This is particularly
           something to watch out for in the case of consensus pods; config pods
           get a large grace period (30s), but consensus pods have a termination
           grace period of 0, so sidecars only get "a short grace period" [0].
           If this turns out to be a problem, we may need longer grace periods
           or a more sophisticated solution.

           [0]: https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#termination-with-sidecars
"""

import os
import textwrap
import yaml
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.deployments import (
    ConfigMapMount,
    Container,
    HostPathMount,
    Resources,
    RestartPolicy,
)
from reboot.controller.settings import (
    ENVVAR_REBOOT_FLUENT_BIT_IMAGE_NAME,
    REBOOT_FLUENT_BIT_MEMORY_LIMIT,
    REBOOT_FLUENT_BIT_MEMORY_REQUEST,
    REBOOT_ROUTABLE_HOSTNAME,
    USER_CONTAINER_GRPC_PORT,
)
from reboot.naming import (
    is_facilitator_application_id,
    make_facilitator_application_id,
)
from rebootdev.aio.headers import APPLICATION_ID_HEADER
from rebootdev.aio.types import ApplicationId, ConfigRunId, ConsensusId
from typing import Any, Optional

MAIN_CONTAINER_NAME = "main"
FACILITATOR_CONTAINER_NAME = "facilitator"

FLUENT_BIT_CONFIGFILE_NAME = "fluent-bit.yaml"
TRANSFORM_LUA_FILENAME = "transform.lua"


def fluent_bit_containers(
    application_id: ApplicationId,
    deployment_name: str,
) -> list[Container]:
    if is_facilitator_application_id(application_id):
        # Fluent Bit containers aren't added for facilitators, because that might
        # cause an infinite loop, e.g. when processing a log line would cause
        # something to get logged again.
        return []

    FLUENT_BIT_IMAGE = os.environ[ENVVAR_REBOOT_FLUENT_BIT_IMAGE_NAME]
    CONFIG_MAP_MOUNT_DIR = "/fluent-bit/etc"
    return [
        Container(
            name="fluent-bit",
            image_name=FLUENT_BIT_IMAGE,
            args=[
                "-c", f"{CONFIG_MAP_MOUNT_DIR}/{FLUENT_BIT_CONFIGFILE_NAME}"
            ],
            resources=Resources(
                limits=Resources.Values(
                    memory=REBOOT_FLUENT_BIT_MEMORY_LIMIT,
                ),
                requests=Resources.Values(
                    memory=REBOOT_FLUENT_BIT_MEMORY_REQUEST,
                ),
            ),
            # This container is intended to run as a Kubernetes-native "sidecar"
            # container; that ensures that it is started (and passing health
            # checks) before the main container is started, and that it is only
            # terminated after the main container has completed its termination.
            # To make this container a sidecar it must be...
            #   1. Set up as an `initContainer` - that's outside this code.
            #   2. Set up with a `restartPolicy` of "Always" - that's here.
            #
            # See:
            #   https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
            restart_policy=RestartPolicy.ALWAYS,
            volumes=[
                ConfigMapMount(
                    config_map_name=deployment_name + "-fluent-bit",
                    mount_path=CONFIG_MAP_MOUNT_DIR,
                ),
                # ATTENTION: to make this setup forwards-compatible with
                #            deployments on Fargate (which does not permit
                #            DaemonSets) this Fluent Bit has been deployed as a
                #            sidecar. However, the sidecar still needs access to
                #            the host's log files, and the host collects _all_
                #            its log files from _all_ pods in the same
                #            `/var/log/containers` directory. The following
                #            mount is therefore INSECURE, UNLESS deployed on
                #            Fargate - as it gives access to all logs by all
                #            applications running on this node, and only Fargate
                #            provides a one-application-per-node isolation.
                HostPathMount(
                    mount_name="varlog",
                    host_path="/var/log",
                    mount_path="/var/log",
                ),
            ],
        ),
    ]


async def write_fluent_bit_configmap(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    deployment_name: str,
    revision_number: int,
    consensus_id: Optional[ConsensusId] = None,
    config_run_id: Optional[ConfigRunId] = None,
) -> str:
    assert consensus_id or config_run_id
    assert not (consensus_id and config_run_id)
    facilitator_application_id = make_facilitator_application_id(
        application_id
    )
    name = get_fluent_bit_configmap_name(deployment_name)
    await k8s_client.config_maps.create_or_update(
        namespace=namespace,
        name=name,
        data={
            FLUENT_BIT_CONFIGFILE_NAME:
                yaml.safe_dump(
                    _make_fluent_bit_config(
                        facilitator_application_id=facilitator_application_id,
                        deployment_name=deployment_name,
                    )
                ),
            TRANSFORM_LUA_FILENAME:
                make_fluent_bit_transformation_lua(
                    consensus_id=consensus_id,
                    config_run_id=config_run_id,
                    revision_number=revision_number,
                ),
        },
    )
    return name


async def delete_fluent_bit_configmap(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    deployment_name: str,
) -> None:
    await k8s_client.config_maps.delete(
        namespace=namespace,
        name=get_fluent_bit_configmap_name(deployment_name),
    )


def get_fluent_bit_configmap_name(deployment_name: str) -> str:
    return f'{deployment_name}-fluent-bit'


def _make_fluent_bit_config(
    facilitator_application_id: ApplicationId,
    deployment_name: str,
) -> dict[str, Any]:
    return {
        "service": {
            "flush": 1,  # Flush every second for ~quick propagation.
            # On SIGTERM, give us 300 seconds to finish flushing. Fluent
            # Bit will terminate as soon as it has flushed all logs, or
            # after 300 seconds, whichever comes first.
            "grace": 300,
        },
        "pipeline": {
            "inputs":
                [
                    {
                        "name":
                            "tail",
                        "path":
                            # These patterns are picked so that only the logs of
                            # this specific deployment's main container (the one
                            # with the user code) are picked up.
                            f"/var/log/containers/{deployment_name}*_{MAIN_CONTAINER_NAME}-*.log",
                        "exclude_path":
                            f"/var/log/containers/{deployment_name}-{FACILITATOR_CONTAINER_NAME}-*.log",
                        # Fluent Bit will start before the main container does,
                        # so its first scan won't reveal that container's log
                        # file. It needs to re-scan to find the container's log
                        # and begin forwarding logs; this setting tells it to do
                        # so every second, so that developers don't have to wait
                        # too long to see their startup logs.
                        #
                        # TODO: it would be nice if we could somehow tell Fluent
                        #       Bit to increase this interval after it has found
                        #       the initial log file.
                        "refresh_interval": "1",
                        # If for any reason the Fluent Bit container were to
                        # restart (e.g. crash due to a bug) we will read all
                        # logs from head. That's safe, because the UUIDv7
                        # generated by the Lua filter for each record will
                        # prevent records from being ingested twice. If we
                        # didn't read from head, we would risk dropping records
                        # that were created while Fluent Bit was down.
                        "read_from_head": "True",
                        "multiline.parser":
                            "docker, cri",
                    }
                ],
            "filters": [
                # Restructure each log record to match the shape of an
                # `IngestRequest`, while also adding a UUIDv7 to each record.
                {
                    "name" : "lua",
                    "match": "*",
                    # See `make_fluent_bit_transformation_lua` for the contents
                    # of this file.
                    "script": TRANSFORM_LUA_FILENAME,
                    "call": "restructure_log",
                },
            ],
            "outputs":
                [
                    {
                        # For convenient debugging of this logs sidecar, log
                        # what we'll (try to) send to the facilitator to stdout
                        # also.
                        "name": "stdout",
                        "match": "*",
                    },
                    {
                        # Make an HTTP/JSON request to the facilitator; its
                        # sidecar will translate to gRPC.
                        "name": "http",
                        "match": "*",
                        # We target the legacy gRPC `LogsProxy`
                        # service because it can handle client-streaming gRPC
                        # requests.
                        "uri": "/rbt.cloud.v1alpha1.logs.LogsProxy/Ingest",
                        # Routing is done by the Istio sidecar, on the basis of
                        # the application ID header.
                        "host": REBOOT_ROUTABLE_HOSTNAME + ".reboot-system",
                        "header": f"{APPLICATION_ID_HEADER} {facilitator_application_id}",
                        "port": USER_CONTAINER_GRPC_PORT,
                        # Fluent Bit's JSON formatted requests are a newline
                        # delimited set of JSON objects. The JSON-gRPC
                        # transcoder will interpret this as a client-streaming
                        # request, which each object representing one request.
                        "format": "json",
                        # Match Protobuf's Timestamp JSON format.
                        "json_date_format": "iso8601",
                        # If the facilitator is somehow unavailable, keep
                        # retrying forever. We don't want to drop any logs if we
                        # can help it. The records contain UUIDs to ensure that
                        # retries are idempotent.
                        "retry_limit": "no_limits",
                    },
                ],
            }
        }


def make_fluent_bit_transformation_lua(
    consensus_id: Optional[ConsensusId],
    config_run_id: Optional[str],
    revision_number: int,
) -> str:
    assert consensus_id or config_run_id
    assert not (consensus_id and config_run_id)
    return textwrap.dedent(
        # See:
        #   https://docs.fluentbit.io/manual/pipeline/filters/lua#callback-prototype
        #
        # TODO(rjh): the UUID computed below helps the facilitator deduplicate
        #            logs that were sent multiple times by the same instance of
        #            Fluent Bit, and it provides a time-ordered key, but it
        #            doesn't help if Fluent Bit itself were to restart; it would
        #            give different UUIDs to the same records (though they'd
        #            still be appropriately time-ordered, because the timestamp
        #            is stable). Consider adding a UUID to the logs themselves
        #            in the user code, to provide true end-to-end idempotency.
        #
        # The UUID generator follows the standard UUIDv7 format:
        #     0                   1                   2                   3
        #     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #    |                           unix_ts_ms                          |
        #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #    |          unix_ts_ms           |  ver  |       rand_a          |
        #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #    |var|                        rand_b                             |
        #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #    |                            rand_b                             |
        #    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        #
        # In the first 24 bytes of `rand_a` and `rand_b` we use a monotonic
        # counter to correctly order records that were recorded in the same
        # millisecond.
        """
        -- Global variables for monotonic counter
        local last_timestamp_ms = nil
        local sequence_counter = 0

        local function generate_uuidv7(timestamp)
            -- Convert timestamp to milliseconds and keep only 48 bits
            local ts_ms = math.floor(timestamp * 1000) % (2^48)

            -- Manage the monotonic sequence counter (24 bits: 0-16777215)
            if ts_ms == last_timestamp_ms then
                sequence_counter = (sequence_counter + 1) % (2^24)
            else
                last_timestamp_ms = ts_ms
                sequence_counter = 0
            end

            -- Generate random bits for remaining rand_b (50 bits)
            local rand_b = math.random(0, 2^50 - 1)

            -- Split sequence counter into rand_a (12 bits) and start of rand_b (12 bits)
            local rand_a = sequence_counter % (2^12)  -- Lower 12 bits for rand_a
            local seq_in_rand_b = math.floor(sequence_counter / 2^12)  -- Upper 12 bits for start of rand_b

            -- Combine the upper sequence bits with rand_b, and position variant bits
            -- We want the variant bits (10) to be at bit positions 63-62, counting from the right
            -- So shift everything right by 2 and add the variant
            rand_b = (seq_in_rand_b * 2^48) + math.floor(rand_b / 4) + (0xa * 2^60)

            -- Format the components as hex
            local ts_ms_hex = string.format("%012x", ts_ms)  -- 48-bit timestamp
            local ver_rand_a_hex = string.format("%04x", 0x7000 + rand_a)  -- Version 7 + 12 bits of sequence
            local var_rand_b_hex = string.format("%016x", rand_b)  -- 12 bits sequence + variant + 50 random

            -- Assemble the UUID string
            return string.format(
                "%s-%s-%s-%s-%s",
                ts_ms_hex:sub(1, 8),          -- First 32 bits of timestamp
                ts_ms_hex:sub(9, 12),         -- Remaining 16 bits of timestamp
                ver_rand_a_hex,               -- Version + 12 bits of sequence
                var_rand_b_hex:sub(1, 4),     -- First 16 bits (12 sequence + variant + start of random)
                var_rand_b_hex:sub(5, 16)     -- Remaining 48 bits of random
            )
        end

        function restructure_log(tag, timestamp, record)
            local new_record = {
                records = {
                    {
                        -- The UUID has multiple purposes:
                        -- 1. Provide a time-ordered key to sort the records.
                        -- 2. Maintain relative order for records with the same timestamp.
                        -- 3. Provide uniqueness when generating records in many
                        --    Fluent Bit instances simultaneously.
                        uuid = generate_uuidv7(timestamp),
                        timestamp = record["time"] or timestamp,
                        text = record["log"],
                        {CONSENSUS_ID_OR_CONFIG_RUN_ID},
                        revision_number = {REVISION_NUMBER},
                    }
                }
            }
            return 1, timestamp, new_record
        end
        """.replace(
            "{CONSENSUS_ID_OR_CONFIG_RUN_ID}",
            f'consensus_id = "{consensus_id}"' if consensus_id is not None else
            f'config_run_id = "{config_run_id}"'
        ).replace("{REVISION_NUMBER}", f"{revision_number}")
    )
