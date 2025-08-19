from __future__ import annotations

import aiofiles.os
import asyncio
import base64
import dataclasses
import kubernetes_asyncio
import multiprocessing
import os
import pickle
import rebootdev.aio.tracing
import rebootdev.nodejs.python
import secrets
import signal
import sys
import tempfile
import threading
import time
import traceback
from dataclasses import dataclass
from kubernetes_utils.kubernetes_client import EnhancedKubernetesClient
from kubernetes_utils.resources.deployments import (
    Container,
    DynamicVolumeMount,
    Resources,
)
from kubernetes_utils.resources.services import Port
from pathlib import Path
from rbt.v1alpha1 import placement_planner_pb2, sidecar_pb2
from reboot.aio.http import WebFramework
from reboot.aio.internals.application_metadata import ApplicationMetadata
from reboot.aio.monitoring import monitor_event_loop_lag
from reboot.aio.servers import _ServiceServer
from reboot.consensus.local_envoy import ConsensusAddress, LocalEnvoy
from reboot.consensus.local_envoy_factory import LocalEnvoyFactory
from reboot.controller.consensuses import Consensus
from reboot.controller.envoy_filter import EnvoyFilter
from reboot.controller.envoy_filter_generator import (
    generate_transcoding_filter,
)
from reboot.controller.fluent_bit import (
    delete_fluent_bit_configmap,
    fluent_bit_containers,
    write_fluent_bit_configmap,
)
from reboot.controller.settings import (
    ENVVAR_PORT,
    ENVVAR_REBOOT_ADMIN_AUTH_APPLICATION_ID,
    ENVVAR_REBOOT_APPLICATION_ID,
    ENVVAR_REBOOT_CONSENSUS_ID,
    ENVVAR_REBOOT_SPACE_ID,
    IS_REBOOT_APPLICATION_LABEL_NAME,
    IS_REBOOT_APPLICATION_LABEL_VALUE,
    REBOOT_APPLICATION_ID_LABEL_NAME,
    REBOOT_APPLICATION_MEMORY_LIMIT,
    REBOOT_APPLICATION_MEMORY_REQUEST,
    REBOOT_CONSENSUS_ID_LABEL_NAME,
    USER_CONTAINER_GRPC_PORT,
    USER_CONTAINER_HTTP_PORT,
    USER_CONTAINER_WEBSOCKET_PORT,
)
from reboot.controller.storage import (
    ensure_persistent_volume_claim,
    maybe_delete_persistent_volume_claim,
)
from reboot.naming import (
    ensure_valid_application_id,
    get_service_account_name_for_application,
    get_space_from_namespace,
    is_facilitator_application_id,
)
from rebootdev.aio.auth.token_verifiers import TokenVerifier
from rebootdev.aio.contexts import EffectValidation
from rebootdev.aio.exceptions import InputError
from rebootdev.aio.placement import PlanOnlyPlacementClient
from rebootdev.aio.resolvers import DirectResolver
from rebootdev.aio.servicers import Serviceable
from rebootdev.aio.state_managers import LocalSidecarStateManager
from rebootdev.aio.types import ApplicationId, ConsensusId, RoutableAddress
from rebootdev.run_environments import on_cloud
from rebootdev.settings import (
    ENVVAR_NODEJS_CONSENSUS_BASE64_ARGS,
    ENVVAR_RBT_EFFECT_VALIDATION,
    ENVVAR_RBT_NODEJS,
    ENVVAR_RBT_STATE_DIRECTORY,
    ENVVAR_REBOOT_CLOUD_VERSION,
    EVERY_LOCAL_NETWORK_ADDRESS,
    REBOOT_STATE_DIRECTORY,
    SIDECAR_SUFFIX,
)
from typing import Awaitable, Callable, Optional, Sequence


def get_deployment_name(consensus_id: ConsensusId) -> str:
    return f'{consensus_id}'


def get_service_name(consensus_id: ConsensusId) -> str:
    return f'{consensus_id}'


class ConsensusManager:

    def __init__(self):
        # Dict mapping consensus name to Consensus info.
        self.current_consensuses: dict[ConsensusId, Consensus] = {}

    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.Consensus.Address:
        """
        Make a consensus and returns its address. If a consensus with the same
        name already exists, overwrite it with the new config (if the config
        hasn't changed, this can and should be a no-op.)
        """
        raise NotImplementedError()

    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        """Delete the given consensus from the system."""
        raise NotImplementedError()

    @rebootdev.aio.tracing.function_span()
    async def set_consensuses(
        self,
        planned_consensuses: Sequence[Consensus],
    ) -> list[placement_planner_pb2.Consensus]:
        """
        Takes a list of planned consensuses, makes it so that these consensuses
        exist in the real world, and returns a list of `Consensus` objects that
        contain the addresses of those running consensuses.
        """
        new_consensus_protos: list[placement_planner_pb2.Consensus] = []
        new_consensuses_dict: dict[ConsensusId, Consensus] = {}

        async def _set_consensus_task(consensus: Consensus):
            consensus_address = await self._set_consensus(consensus)

            # Add a new consensus, or update the existing consensus (if any).
            consensus_proto = placement_planner_pb2.Consensus(
                id=consensus.id,
                application_id=consensus.application_id,
                revision_number=consensus.revision_number,
                address=consensus_address,
                namespace=consensus.namespace,
                file_descriptor_set=consensus.file_descriptor_set,
            )
            new_consensus_protos.append(consensus_proto)
            new_consensuses_dict[consensus.id] = consensus

        set_consensus_tasks: list[asyncio.Task] = []

        for consensus in planned_consensuses:
            set_consensus_tasks.append(
                asyncio.create_task(_set_consensus_task(consensus))
            )

        # The result of task might be 'None' or an exception.
        exception_list = await asyncio.gather(
            *set_consensus_tasks,
            return_exceptions=True,
        )

        # If there was an exception, raise it. Note that there might be more than one
        # exception with different types, but the most likely case is that they are
        # all somewhat similar.
        for exception in exception_list:
            if exception is not None:
                raise exception

        # Go through and delete consensuses that are no longer part of the plan.
        delete_consensus_tasks = []

        for consensus_id, consensus in self.current_consensuses.items():
            if consensus_id not in new_consensuses_dict:
                delete_consensus_tasks.append(
                    asyncio.create_task(self._delete_consensus(consensus))
                )

        await asyncio.gather(*delete_consensus_tasks)

        self.current_consensuses = new_consensuses_dict
        return new_consensus_protos


class KubernetesConsensusManager(ConsensusManager):

    def __init__(self, k8s_client: Optional[EnhancedKubernetesClient] = None):
        super().__init__()
        self._k8s_client = k8s_client

    @rebootdev.aio.tracing.function_span()
    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.Consensus.Address:
        if self._k8s_client is None:
            # We know we're inside a cluster.
            self._k8s_client = (
                await EnhancedKubernetesClient.create_incluster_client()
            )

        assert consensus.file_descriptor_set is not None
        assert consensus.namespace is not None
        assert consensus.container_image_name is not None

        deployment_name = get_deployment_name(consensus.id)

        # ISSUE(https://github.com/reboot-dev/mono/issues/1430): Fix
        # ownership. Owner should be the ApplicationConfig.
        mount_info = await ensure_persistent_volume_claim(
            k8s_client=self._k8s_client,
            namespace=consensus.namespace,
            application_id=ensure_valid_application_id(
                consensus.application_id
            ),
            consensus_id=consensus.id,
            # TODO(rjh): make this configurable via the ApplicationDeployment.
            size="10Gi",
        )

        # Non-facilitator applications get a facilitator.
        if not is_facilitator_application_id(consensus.application_id):
            # The FluentBit container we'll run needs a ConfigMap as its
            # configuration.
            await write_fluent_bit_configmap(
                k8s_client=self._k8s_client,
                namespace=consensus.namespace,
                application_id=consensus.application_id,
                revision_number=consensus.revision_number,
                deployment_name=deployment_name,
                consensus_id=consensus.id,
            )

        # TODO: set ownership to the original ApplicationDeployment object
        # associated with this consensus, NOT the controller Pod. (The owner
        # object must be in the same namespace as the objects being created, or
        # the new resources won't come up.)
        # ISSUE(https://github.com/reboot-dev/mono/issues/1430): Fix
        # ownership. Owner should be the ApplicationDeployment.
        pod_labels = {
            # Mark each pod as being part of a Reboot application.
            # That'll be used to target the pod for e.g. EnvoyFilter
            # distribution.
            IS_REBOOT_APPLICATION_LABEL_NAME:
                IS_REBOOT_APPLICATION_LABEL_VALUE,
            # Further mark it with its specific consensus name, for even
            # narrower EnvoyFilter targeting.
            REBOOT_CONSENSUS_ID_LABEL_NAME:
                consensus.id,
            REBOOT_APPLICATION_ID_LABEL_NAME:
                consensus.application_id,
        }
        await self._k8s_client.deployments.create_or_update(
            namespace=consensus.namespace,
            deployment_name=deployment_name,
            replicas=1,
            pod_labels=pod_labels,
            service_account_name=get_service_account_name_for_application(
                ensure_valid_application_id(consensus.application_id)
            ),
            update_strategy=mount_info.deployment_update_strategy,
            # Reboot containers don't terminate gracefully, so a termination
            # grace period is simply wasted time during which the container's
            # serving set is unavailable. Fortunately Reboot apps are robust to
            # a hard kill - so kill them immediately when the Pod needs to be
            # replaced, minimizing downtime during updates.
            termination_grace_period_seconds=0,
            init_containers=fluent_bit_containers(
                consensus.application_id, deployment_name
            ),
            containers=[
                Container(
                    name="main",
                    image_name=consensus.container_image_name,
                    resources=Resources(
                        limits=Resources.Values(
                            memory=REBOOT_APPLICATION_MEMORY_LIMIT
                        ),
                        requests=Resources.Values(
                            memory=REBOOT_APPLICATION_MEMORY_REQUEST
                        ),
                    ),
                    exposed_ports=[
                        USER_CONTAINER_GRPC_PORT,
                        USER_CONTAINER_WEBSOCKET_PORT,
                        USER_CONTAINER_HTTP_PORT,
                    ],
                    env=[
                        # Some environment variables are required when running on
                        # Kubernetes, see 'public/rebootdev/aio/servers.py'.
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_SPACE_ID,
                            value=get_space_from_namespace(
                                consensus.namespace
                            ),
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_APPLICATION_ID,
                            value=consensus.application_id,
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_CONSENSUS_ID,
                            value=consensus.id,
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_CLOUD_VERSION,
                            value='v1alpha1',
                        ),
                        # Tell the user container what port the platform expects their
                        # public port to be.
                        #
                        # On the Reboot Cloud we always use a static port,
                        # which is the same for all pods.
                        # We check that it is not overridden by the user in the
                        # "rbt serve" CLI.
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_PORT,
                            value=str(USER_CONTAINER_GRPC_PORT),
                        ),
                        # Ensure that any Python process always produces their output
                        # immediately. This is helpful for debugging purposes.
                        kubernetes_asyncio.client.V1EnvVar(
                            name="PYTHONUNBUFFERED",
                            value="1",
                        ),
                        # For containers using `rbt serve run`, tell them where the
                        # state directory will be.
                        #
                        # On the Reboot Cloud we always use the static state
                        # directory, which is the same for all pods.
                        # We check that it is not overridden by the user in the
                        # "rbt serve" CLI.
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_RBT_STATE_DIRECTORY,
                            value=REBOOT_STATE_DIRECTORY,
                        ),
                        # For endpoints using admin auth, use the cloud's admin
                        # auth.
                        kubernetes_asyncio.client.V1EnvVar(
                            # TODO(rjh) DO NOT SUBMIT: not a literal, plz.
                            name=ENVVAR_REBOOT_ADMIN_AUTH_APPLICATION_ID,
                            value="cloud",
                        ),
                    ],
                    volumes=[
                        DynamicVolumeMount(
                            persistent_volume_claim_name=mount_info.pvc_name,
                            mount_path=REBOOT_STATE_DIRECTORY,
                        ),
                    ],
                ),
            ],
        )

        # Instruct the consensus to transcode incoming HTTP traffic to gRPC.
        # We do this by setting up an EnvoyFilter for this specific consensus.
        assert consensus.file_descriptor_set is not None
        transcoding_filter_name = f'{deployment_name}-transcoding-filter'
        transcoding_filter: EnvoyFilter = generate_transcoding_filter(
            namespace=consensus.namespace,
            name=transcoding_filter_name,
            target_labels=pod_labels,
            services=[s for s in consensus.service_names],
            file_descriptor_set=consensus.file_descriptor_set,
        )
        await self._k8s_client.custom_objects.create_or_update(
            transcoding_filter
        )

        # TODO: set ownership to the original ApplicationDeployment object
        # associated with this consensus, NOT the controller Pod. (The owner
        # object must be in the same namespace as the objects being created, or
        # the new resources won't come up.)
        # ISSUE(https://github.com/reboot-dev/mono/issues/1430): Fix
        # ownership. Owner should be the ApplicationDeployment.
        service_name = get_service_name(consensus.id)
        await self._k8s_client.services.create_or_update(
            namespace=consensus.namespace,
            name=service_name,
            deployment_label=deployment_name,
            ports=[
                # To let this port serve gRPC traffic when there's an
                # intermediate Envoy proxy in gateway mode, this port
                # MUST be called "grpc".
                Port(port=USER_CONTAINER_GRPC_PORT, name="grpc"),
                # Port for WebSockets for browsers.
                Port(port=USER_CONTAINER_WEBSOCKET_PORT, name="websocket"),
                # Port for HTTP fallback.
                Port(port=USER_CONTAINER_HTTP_PORT, name="http"),
            ],
        )

        service_address = placement_planner_pb2.Consensus.Address(
            host=f'{service_name}.{consensus.namespace}.svc.cluster.local',
            port=USER_CONTAINER_GRPC_PORT
        )

        return service_address

    @rebootdev.aio.tracing.function_span()
    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        if self._k8s_client is None:
            # We know we're inside a cluster.
            self._k8s_client = (
                await EnhancedKubernetesClient.create_incluster_client()
            )

        assert consensus.namespace is not None

        await self._k8s_client.services.delete(
            namespace=consensus.namespace,
            name=get_service_name(consensus.id),
        )
        deployment_name = get_deployment_name(consensus.id)
        await self._k8s_client.deployments.delete(
            namespace=consensus.namespace, name=deployment_name
        )
        await maybe_delete_persistent_volume_claim(
            self._k8s_client,
            namespace=consensus.namespace,
            application_id=consensus.application_id,
            consensus_id=consensus.id,
        )
        await delete_fluent_bit_configmap(
            k8s_client=self._k8s_client,
            namespace=consensus.namespace,
            deployment_name=deployment_name,
        )


async def _run_consensus_process(
    *,
    application_id: ApplicationId,
    consensus_id: ConsensusId,
    shards: list[sidecar_pb2.ShardInfo],
    directory: str,
    address: str,
    serviceables: list[Serviceable],
    web_framework: WebFramework,
    placement_planner_address: RoutableAddress,
    token_verifier: Optional[TokenVerifier],
    fifo: Path,
    effect_validation: EffectValidation,
    app_internal_api_key_secret: str,
):
    """Helper that runs an instance of a server in its own process.
    """
    resolver: Optional[DirectResolver] = None
    state_manager: Optional[LocalSidecarStateManager] = None
    server: Optional[_ServiceServer] = None

    # Since we've just started a new process, we must start any tracers.
    rebootdev.aio.tracing.start(consensus_id=consensus_id)

    # This is the entrypoint for a consensus process; we monitor
    # its event loop.
    monitor_event_loop_lag_task = asyncio.create_task(
        monitor_event_loop_lag(consensus_id=consensus_id)
    )
    try:
        placement_client = PlanOnlyPlacementClient(placement_planner_address)

        resolver = DirectResolver(placement_client)

        await resolver.start()

        state_manager = LocalSidecarStateManager(
            directory, shards, serviceables
        )

        # Pass a port of 0 to allow the Server to pick its own
        # (unused) port.
        server = _ServiceServer(
            application_id=application_id,
            consensus_id=consensus_id,
            serviceables=serviceables,
            web_framework=web_framework,
            listen_address=address,
            token_verifier=token_verifier,
            state_manager=state_manager,
            placement_client=placement_client,
            actor_resolver=resolver,
            effect_validation=effect_validation,
            # For local consensuses, initialization is done at a higher
            # level.
            initialize=None,
            app_internal_api_key_secret=app_internal_api_key_secret,
        )

        await server.start()

        # Communicate the ports back to the caller.
        #
        # NOTE: we want to send a tuple of ports _or_ an exception
        # (see below) which we can do via `pickle`, but since we won't
        # know the size of the data we first encode the data into
        # Base64 and then append a '\n' to demarcate the "end".

        fifo.write_text(
            base64.b64encode(
                pickle.dumps(
                    (
                        server.port(),
                        server.websocket_port(),
                        server.http_port(),
                    )
                ),
            ).decode('utf-8') + '\n'
        )
    except Exception as e:
        # NOTE: passing exceptions across a process will lose the trace
        # information so we pass it as an argument to `InputError`.
        stack_trace = ''.join(traceback.format_exception(e))

        # If we already have an `InputError`, just attach the stack to
        # it here.
        if isinstance(e, InputError):
            e.stack_trace = stack_trace

        if on_cloud():
            # Emulate `traceback.print_exc()` by printing the
            # error to `sys.stderr`.
            print(stack_trace, file=sys.stderr)

        # We failed to communicate a port to the caller, so instead we'll
        # communicate the error back to the caller.
        fifo.write_text(
            # See comment above for why we are pickling + Base64 encoding.
            base64.b64encode(
                pickle.dumps(
                    e if isinstance(e, InputError) else InputError(
                        reason=f"Failed to start consensus {consensus_id}",
                        causing_exception=e,
                        stack_trace=stack_trace,
                    )
                )
            ).decode('utf-8') + '\n'
        )

        # NOTE: we don't re-raise the error here as it adds a lot
        # of cruft to the output and may get interleaved with
        # other output making it hard to parse.
    else:
        # TODO(benh): catch other errors and propagate them back
        # to the error as well.
        await server.wait()
    finally:
        if server is not None:
            await server.stop()
            await server.wait()

        if state_manager is not None:
            await state_manager.shutdown_and_wait()

        if resolver is not None:
            await resolver.stop()

        monitor_event_loop_lag_task.cancel()

        try:
            await monitor_event_loop_lag_task
        except asyncio.CancelledError:
            pass


async def run_nodejs_consensus_process(
    *,
    serviceables: list[Serviceable],
    web_framework: WebFramework,
    token_verifier: Optional[TokenVerifier],
):
    """Entry point for a nodejs based consensus subprocess.

    We extract pickled args to pass to `_run_consensus_process` from
    the environment, and then send the assigned ports back to the
    parent process via nodejs IPC that comes as part of using their
    `fork()` primitive (not to be confused with an POSIX `fork`, this
    does not "clone" but creates a full child process.

    NOTE: We do not attempt to pickle any user-defined TypeScript types:
    instead, we allow them to be re-created in the subprocess, and then
    be passed as arguments to this method. See #2911 about reducing
    complexity here.
    """
    base64_args = os.getenv(ENVVAR_NODEJS_CONSENSUS_BASE64_ARGS)

    assert base64_args is not None

    args = pickle.loads(base64.b64decode(base64_args.encode()))

    await _run_consensus_process(
        serviceables=serviceables,
        web_framework=web_framework,
        token_verifier=token_verifier,
        **args,
    )


def _run_python_consensus_process(
    application_id: ApplicationId,
    consensus_id: ConsensusId,
    shards: list[sidecar_pb2.ShardInfo],
    directory: str,
    address: str,
    serviceables: list[Serviceable],
    web_framework: WebFramework,
    placement_planner_address: RoutableAddress,
    token_verifier: Optional[TokenVerifier],
    fifo: Path,
    effect_validation: EffectValidation,
    app_internal_api_key_secret: str,
):
    asyncio.run(
        _run_consensus_process(
            application_id=application_id,
            consensus_id=consensus_id,
            shards=shards,
            directory=directory,
            address=address,
            serviceables=serviceables,
            web_framework=web_framework,
            placement_planner_address=placement_planner_address,
            token_verifier=token_verifier,
            fifo=fifo,
            effect_validation=effect_validation,
            app_internal_api_key_secret=app_internal_api_key_secret,
        )
    )


@rebootdev.aio.tracing.function_span()
async def get_subprocess_consensus_ports_via_fifo(fifo: Path):
    # Open the FIFO for reading in non-blocking mode to not block the
    # event loop, which would prevent the subprocess from starting.
    #
    # Not using 'aiofiles' there, because we've seen issues with it when reading
    # from FIFOs in parallel.
    fifo_fd = os.open(fifo, os.O_RDONLY | os.O_NONBLOCK)
    buffer = b''

    while True:
        try:
            chunk = os.read(fifo_fd, 1024)
            if chunk:
                buffer += chunk
                if b'\n' in chunk:
                    break
            else:
                # Wait for an other process to write to the FIFO.
                await asyncio.sleep(0.1)
        except BlockingIOError:
            # Wait for an other process to write to the FIFO.
            await asyncio.sleep(0.1)

    os.close(fifo_fd)

    ports_or_error: tuple[int, int, int] | InputError = pickle.loads(
        base64.b64decode(buffer.strip())
    )

    if isinstance(ports_or_error, InputError):
        raise ports_or_error

    # If we didn't get an error, we must have gotten the ports.
    return ports_or_error


@dataclass(
    frozen=True,
    kw_only=True,
)
class RegisteredRevision:
    """Helper class encapsulating properties for a "revision" of the app,
    meant to mimic the revisions we (intend to) expose to developers."""
    serviceables: list[Serviceable]
    web_framework: WebFramework
    in_process: bool
    local_envoy: bool
    local_envoy_port: int
    local_envoy_use_tls: bool
    token_verifier: Optional[TokenVerifier]
    effect_validation: Optional[EffectValidation]


@dataclass(
    frozen=True,
    kw_only=True,
)
class LaunchedConsensus:
    """Helper class for a launched consensus."""
    consensus: Consensus
    address: placement_planner_pb2.Consensus.Address
    websocket_address: placement_planner_pb2.Consensus.Address
    http_address: placement_planner_pb2.Consensus.Address

    @dataclass(
        frozen=True,
        kw_only=True,
    )
    class InProcess:
        """Encapsulates everything created for an "in process" consensus."""
        server: _ServiceServer
        resolver: DirectResolver
        state_manager: LocalSidecarStateManager

    @dataclass(
        frozen=True,
        kw_only=True,
    )
    class Subprocess:
        """Encapsulates everything created for a "subprocess" consensus."""
        # Callback for stopping this subprocess.
        stop: Callable[[], Awaitable[None]]

        # Indicator that we are attempting to stop the subprocess.
        stopping: asyncio.Event

    @dataclass(
        frozen=True,
        kw_only=True,
    )
    class Stopped:
        """A consensus that is currently stopped."""

    async def stop(self) -> LaunchedConsensus:
        if isinstance(self.state, LaunchedConsensus.Subprocess):
            self.state.stopping.set()
            await self.state.stop()
        elif isinstance(self.state, LaunchedConsensus.InProcess):
            await self.state.server.stop()
            await self.state.server.wait()

            await self.state.resolver.stop()

            # NOTE: need to explicitly shutdown+wait the state manager so that
            # another state manager can be brought up immediately for the same
            # consensus (e.g., as part of a consensus restart) without conflict.
            await self.state.state_manager.shutdown_and_wait()
        else:
            assert isinstance(self.state, LaunchedConsensus.Stopped)

        return dataclasses.replace(self, state=LaunchedConsensus.Stopped())

    def stopped(self) -> bool:
        return isinstance(self.state, LaunchedConsensus.Stopped)

    state: InProcess | Subprocess | Stopped


class LocalConsensusManager(ConsensusManager):

    def __init__(
        self,
        application_metadata: ApplicationMetadata,
    ):
        super().__init__()

        # Information on latest registered revision, if any.
        self._revision: Optional[RegisteredRevision] = None

        # Map of launched consensuses, indexed by consensus name.
        self._launched_consensuses: dict[ConsensusId, LaunchedConsensus] = {}

        # App internal secret, used to identify servicers within an
        # application to one another.
        self._app_internal_api_key_secret = secrets.token_urlsafe()

        # The LocalEnvoy that routes to the consensuses.
        self._local_envoy: Optional[LocalEnvoy] = None

        # Manages per-Application metadata, and the locations of the state directories.
        self._application_metadata = application_metadata

        # Placement planner address must be set later because there is
        # a cycle where PlacementPlanner depends on ConsensusManager,
        # so we won't know the address to give to the
        # LocalConsensusManager until after the PlacementPlanner has
        # been created.
        self._placement_planner_address: Optional[RoutableAddress] = None

    def __del__(self):
        """Custom destructor in order to avoid the temporary directory being
        deleted _before_ the consensuses have been shutdown.
        """

        async def stop_all_consensuses():
            stop_all_consensuses_tasks = []

            for launched_consensus in self._launched_consensuses.values():
                stop_all_consensuses_tasks.append(launched_consensus.stop())

            await asyncio.gather(*stop_all_consensuses_tasks)

        # This destructor cannot be async, but the `launched_consensus` code is
        # all async, so we need to go through this little hoop to run its
        # shutdown procedure.
        try:
            current_event_loop = asyncio.get_running_loop()
            # If the above doesn't raise, then this synchronous method is being
            # called from an async context.
            # Since we have a running event loop, we must call the async
            # function on that loop rather than via asyncio.run().
            _ = current_event_loop.create_task(
                stop_all_consensuses(),
                name=f'stop_all_consensuses() in {__name__}',
            )
        except RuntimeError:
            # We're in a fully synchronous context. Call the async function via
            # asyncio.run().
            asyncio.run(stop_all_consensuses())

    @property
    def local_envoy(self) -> Optional[LocalEnvoy]:
        return self._local_envoy

    def register_placement_planner_address(
        self, placement_planner_address: RoutableAddress
    ):
        """Register the placement planner address so that we can bring up new
        servers that can create resolvers that get actor routes from
        the placement planner.

        NOTE: this must be called _before_ a consensus can be created.
        Unfortunately we can't pass the address into the constructor because
        there is a cycle where PlacementPlanner depends on ConsensusManager,
        so we won't know the address to give to the LocalConsensusManager until
        after the PlacementPlanner has been created.
        """
        self._placement_planner_address = placement_planner_address

    def register_revision(
        self,
        *,
        serviceables: list[Serviceable],
        web_framework: WebFramework,
        token_verifier: Optional[TokenVerifier],
        in_process: bool,
        local_envoy: bool,
        local_envoy_port: int,
        local_envoy_use_tls: bool,
        effect_validation: Optional[EffectValidation],
    ):
        """Save the given serviceable definitions so that we can bring up
        corresponding objects if and when a Consensus requires them."""
        self._revision = RegisteredRevision(
            serviceables=serviceables,
            web_framework=web_framework,
            in_process=in_process,
            local_envoy=local_envoy,
            local_envoy_port=local_envoy_port,
            local_envoy_use_tls=local_envoy_use_tls,
            token_verifier=token_verifier,
            effect_validation=effect_validation,
        )

    def _application_state_directory(self) -> Path:
        return self._application_metadata.application_state_directory()

    async def _validate_stable_consensus_counts(
        self,
        consensuses: Sequence[Consensus],
    ) -> None:
        """Validates that the consensuses counts for each app are stable.

        The sidecar validates the shards that each consensus stores to
        prevent accidental shifts in shard boundaries, but does not have a
        global view of the expected consensus count: we validate that here
        to provide a more helpful error message.
        """
        for consensus in consensuses:
            application_id = ensure_valid_application_id(
                consensus.application_id
            )
            if application_id != self._application_metadata.application_id:
                raise AssertionError(
                    "Only one application is supported per instance."
                )

        consensus_count = len(consensuses)
        if consensus_count > 0:
            await self._application_metadata.validate_stable_consensus_count(
                consensus_count
            )

    @rebootdev.aio.tracing.function_span()
    async def set_consensuses(
        self,
        planned_consensuses: Sequence[Consensus],
    ) -> list[placement_planner_pb2.Consensus]:
        # Validate that the number of consensuses hasn't changed.
        await self._validate_stable_consensus_counts(planned_consensuses)

        # First update the consensuses.
        result = await super().set_consensuses(planned_consensuses)

        # Now update the Envoy that's routing to the consensuses.
        await self._configure_envoy()

        return result

    @rebootdev.aio.tracing.function_span()
    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        """Stop the process or server corresponding to the given Consensus and delete it
        from our internal records.
        If there is no such process or server, do nothing."""

        await self._stop_consensus(consensus)

        self._launched_consensuses.pop(consensus.id, None)

    async def _stop_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        """Stop the process or server corresponding to the given Consensus.
        If there is no such process or server, do nothing."""
        launched_consensus = self._launched_consensuses.get(consensus.id, None)

        if launched_consensus is None:
            return

        self._launched_consensuses[consensus.id
                                  ] = await launched_consensus.stop()

    @rebootdev.aio.tracing.function_span()
    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.Consensus.Address:
        """Start a gRPC server, in the same process or a separate process,
        serving all the services in the given Consensus, and return
        its address.
        """
        # If this is an "update" to an existing consensus, don't do
        # anything (assuming there is not anything to be done, which
        # locally should always be the case).
        launched_consensus = self._launched_consensuses.get(consensus.id, None)

        if launched_consensus is not None:
            assert launched_consensus.consensus == consensus
            return launched_consensus.address

        return await self._start_consensus(consensus)

    @rebootdev.aio.tracing.function_span()
    async def _start_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.Consensus.Address:
        """Start a gRPC server, in the same process or a separate process,
        serving all the services in the given Consensus, and return
        its address.
        """

        # Ok, this isn't an update, we want to create a consensus!
        assert self._placement_planner_address is not None

        assert self._revision is not None, (
            "Application should have been brought up already"
        )

        application_id = ensure_valid_application_id(consensus.application_id)

        assert application_id == self._application_metadata.application_id, (
            "Only one application is supported per instance."
        )

        effect_validation = self._revision.effect_validation or EffectValidation[
            os.getenv(ENVVAR_RBT_EFFECT_VALIDATION, "ENABLED").upper()]

        # Ensure we have a directory for the sidecar for this consensus.
        consensus_directory = os.path.join(
            self._application_state_directory(),
            f'{consensus.id}{SIDECAR_SUFFIX}',
        )

        try:
            await aiofiles.os.mkdir(consensus_directory)
        except FileExistsError:
            # The directory might already exist when we're bringing
            # back up a consensus after an induced failure as well as
            # when using 'rbt' locally for development.
            pass

        async def launch():
            assert self._revision is not None
            assert consensus_directory is not None

            host = EVERY_LOCAL_NETWORK_ADDRESS

            if not self._revision.in_process:
                return await self._launch_subprocess_consensus(
                    consensus_directory,
                    host,
                    consensus,
                    self._revision.serviceables,
                    self._revision.web_framework,
                    self._revision.token_verifier,
                    effect_validation,
                    self._app_internal_api_key_secret,
                )
            else:
                return await self._launch_in_process_consensus(
                    consensus_directory,
                    host,
                    consensus,
                    self._revision.serviceables,
                    self._revision.web_framework,
                    self._revision.token_verifier,
                    effect_validation,
                    self._app_internal_api_key_secret,
                )

        launched_consensus = await launch()

        self._launched_consensuses[consensus.id] = launched_consensus

        return launched_consensus.address

    @property
    def app_internal_api_key_secret(self) -> str:
        return self._app_internal_api_key_secret

    async def consensus_stop(self, consensus_id: ConsensusId) -> Consensus:
        """Temporarily shuts down the given consensus id, for tests."""
        assert self._local_envoy is not None, (
            "Can only stop consensuses when `local_envoy=True`."
        )

        launched_consensus = self._launched_consensuses.get(consensus_id, None)
        if launched_consensus is None:
            raise ValueError(
                f"No running consensus with the id `{consensus_id}`. "
                f"Running consensuses: {list(self._launched_consensuses.keys())}"
            )
        await self._stop_consensus(launched_consensus.consensus)
        return launched_consensus.consensus

    async def consensus_start(self, consensus: Consensus) -> None:
        """Start a consensus that was previously stopped by `consensus_stop`."""
        assert self._local_envoy is not None, (
            "Can only restart consensuses when `local_envoy=True`."
        )

        # Relaunch.
        await self._start_consensus(consensus)
        # And reconfigure envoy, since the consensus will be on a new port.
        await self._configure_envoy()

    @rebootdev.aio.tracing.function_span()
    async def _launch_in_process_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        serviceables: list[Serviceable],
        web_framework: WebFramework,
        token_verifier: Optional[TokenVerifier],
        effect_validation: EffectValidation,
        app_internal_api_key_secret: str,
    ) -> LaunchedConsensus:
        assert self._placement_planner_address is not None

        placement_client = PlanOnlyPlacementClient(
            self._placement_planner_address
        )
        resolver = DirectResolver(placement_client)

        await resolver.start()

        state_manager = LocalSidecarStateManager(
            directory,
            consensus.shards,
            serviceables,
        )

        server = _ServiceServer(
            application_id=ensure_valid_application_id(
                consensus.application_id
            ),
            consensus_id=consensus.id,
            serviceables=serviceables,
            web_framework=web_framework,
            listen_address=f'{host}:0',
            token_verifier=token_verifier,
            state_manager=state_manager,
            placement_client=placement_client,
            actor_resolver=resolver,
            effect_validation=effect_validation,
            # For local consensuses, initialization is done at a higher level.
            # This discrepancy is a little awkward, but any work we'd do to
            # address that awkwardness will be made moot when we remove all of
            # this code in favor of the new singletons approach.
            initialize=None,
            app_internal_api_key_secret=app_internal_api_key_secret,
        )

        await server.start()

        port = server.port()
        websocket_port = server.websocket_port()
        http_port = server.http_port()

        # The consensus should now be reachable at the address of the
        # server we started in the subprocess.
        address = placement_planner_pb2.Consensus.Address(host=host, port=port)
        websocket_address = placement_planner_pb2.Consensus.Address(
            host=host, port=websocket_port
        )
        http_address = placement_planner_pb2.Consensus.Address(
            host=host, port=http_port
        )

        return LaunchedConsensus(
            consensus=consensus,
            address=address,
            websocket_address=websocket_address,
            http_address=http_address,
            state=LaunchedConsensus.InProcess(
                server=server,
                resolver=resolver,
                state_manager=state_manager,
            ),
        )

    async def _stop_consensus_process(self, pid: int) -> None:
        # Perform a graceful termination by first doing 'terminate'
        # followed after a grace period by 'kill'
        loop = asyncio.get_running_loop()
        try:
            # Try and send a SIGTERM to the process, or if it has
            # already exited a `ProcessLookupError` will be raised
            # which we catch below.
            await loop.run_in_executor(
                None,
                os.kill,
                pid,
                signal.SIGTERM,
            )

            retries = 0

            while retries < 3:
                # Check if the process is still running, raises
                # `ProcessLookupError` that we catch below if it has
                # exited or been killed.
                await loop.run_in_executor(None, os.kill, pid, 0)
                retries += 1
                await asyncio.sleep(1)

            # Send a SIGKILL to the process, which can not be trapped,
            # or if it has already exited a `ProcessLookupError` will
            # be raised which we catch below.
            await loop.run_in_executor(None, os.kill, pid, signal.SIGKILL)

            # Waiting forever is safe because kill can not be trapped!
            while True:
                # Check if the process is still running, raises
                # `ProcessLookupError` that we catch below if it has
                # exited or been killed.
                await loop.run_in_executor(None, os.kill, pid, 0)
                await asyncio.sleep(1)
        except ProcessLookupError:
            # Process exited or was killed.
            return

    async def _launch_subprocess_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        serviceables: list[Serviceable],
        web_framework: WebFramework,
        token_verifier: Optional[TokenVerifier],
        effect_validation: EffectValidation,
        app_internal_api_key_secret: str,
    ) -> LaunchedConsensus:
        if os.getenv(ENVVAR_RBT_NODEJS, "false").lower() == "true":
            return await self._launch_nodejs_subprocess_consensus(
                directory,
                host,
                consensus,
                effect_validation,
                app_internal_api_key_secret,
            )
        else:
            return await self._launch_python_subprocess_consensus(
                directory,
                host,
                consensus,
                serviceables,
                web_framework,
                token_verifier,
                effect_validation,
                app_internal_api_key_secret,
            )

    async def _launch_nodejs_subprocess_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        effect_validation: EffectValidation,
        app_internal_api_key_secret: str,
    ) -> LaunchedConsensus:
        # We use a fifo to report back the ports as type `int` on
        # which the process is running. It may also report an error of
        # type `InputError`.
        fifo_directory = tempfile.TemporaryDirectory()
        fifo = Path(fifo_directory.name) / 'fifo'
        os.mkfifo(fifo)

        args = {
            'application_id': consensus.application_id,
            'consensus_id': consensus.id,
            'shards': consensus.shards,
            'directory': directory,
            'address': f'{host}:0',
            'placement_planner_address': self._placement_planner_address,
            'fifo': fifo,
            'effect_validation': effect_validation,
            'app_internal_api_key_secret': app_internal_api_key_secret,
        }

        pid = await rebootdev.nodejs.python.launch_subprocess_consensus(
            # NOTE: Base64 encoding returns bytes that we then need
            # "decode" into a string to pass into nodejs.
            base64.b64encode(pickle.dumps(args)).decode('utf-8')
        )

        pid_int = int(pid)

        port, websocket_port, http_port = await get_subprocess_consensus_ports_via_fifo(
            fifo
        )

        # Watch the process to see if it exits prematurely so that we
        # can try and provide some better debugging for end users. We
        # use a 'stopping' event to differentiate when we initiated
        # the stop vs when the process exits on its own.
        stopping = asyncio.Event()

        # The process may still fail after it started. We can't communicate that
        # directly to the user through a raised exception on the user's thread,
        # but we can at least do our best to notice and report it in a separate
        # thread.
        def watch():
            _, status = os.waitpid(pid_int, 0)
            if not stopping.is_set():
                # Since we can't easily determine whether or not `process`
                # has exited because it was stopped via a user doing
                # Ctrl-C or due to an error, we sleep for 1 second before
                # reporting this error and aborting ourselves so in the
                # event it was Ctrl-C hopefully we'll no longer exist.
                #
                # These semantics differs than with a Python subprocess
                # consensus because we can easily see if we have been
                # signaled because nodejs owns the signal handlers.
                time.sleep(1)
                print(
                    f"Process for consensus '{consensus.id}' has "
                    f"prematurely exited with status code '{status}'",
                    file=sys.stderr,
                )
                # TODO(benh): is there any place we can propagate this
                # failure instead of just terminating the process?
                os.kill(os.getpid(), signal.SIGTERM)

        threading.Thread(target=watch, daemon=True).start()

        # The consensus should now be reachable at the address of the
        # server we started in the subprocess.
        address = placement_planner_pb2.Consensus.Address(host=host, port=port)
        websocket_address = placement_planner_pb2.Consensus.Address(
            host=host, port=websocket_port
        )
        http_address = placement_planner_pb2.Consensus.Address(
            host=host, port=http_port
        )

        async def stop():
            await self._stop_consensus_process(pid_int)

        return LaunchedConsensus(
            consensus=consensus,
            address=address,
            websocket_address=websocket_address,
            http_address=http_address,
            state=LaunchedConsensus.Subprocess(
                stop=stop,
                stopping=stopping,
            ),
        )

    @rebootdev.aio.tracing.function_span()
    async def _launch_python_subprocess_consensus(
        self,
        directory: str,
        host: str,
        consensus: Consensus,
        serviceables: list[Serviceable],
        web_framework: WebFramework,
        token_verifier: Optional[TokenVerifier],
        effect_validation: EffectValidation,
        app_internal_api_key_secret: str,
    ) -> LaunchedConsensus:
        # Create and start a process to run a server for the servicers.
        #
        # We use a fifo to report back the ports as type `int` on
        # which the process is running. It may also report an error of
        # type `InputError`.
        fifo_directory = tempfile.TemporaryDirectory()
        fifo = Path(fifo_directory.name) / 'fifo'
        os.mkfifo(fifo)

        # Watch the process to see if it exits prematurely so that we
        # can try and provide some better debugging for end users. We
        # use a 'stopping' event to differentiate when we initiated
        # the stopping vs when the process exits on its own.
        stopping = asyncio.Event()

        process = multiprocessing.Process(
            target=_run_python_consensus_process,
            args=(
                consensus.application_id,
                consensus.id,
                consensus.shards,
                directory,
                f'{host}:0',
                serviceables,
                web_framework,
                self._placement_planner_address,
                token_verifier,
                fifo,
                effect_validation,
                app_internal_api_key_secret,
            ),
            # NOTE: we set 'daemon' to True so that this process will
            # attempt to terminate our subprocess when it exits.
            #
            # TODO(benh): ensure that this always happens by using
            # something like a pipe.
            daemon=True,
        )

        process.start()

        # The process may still fail after it started. We can't communicate that
        # directly to the user through a raised exception on the user's thread,
        # but we can at least do our best to notice and report it in a separate
        # thread.
        def watch():
            process.join()

            status = process.exitcode

            if not stopping.is_set() and status != 0:
                print(
                    f"Process for consensus '{consensus.id}' has "
                    f"prematurely exited with status code '{process.exitcode}'",
                    file=sys.stderr,
                )
                # TODO(benh): is there any place we can propagate this
                # failure instead of just terminating the process?
                os.kill(os.getpid(), signal.SIGTERM)

        async def stop():
            pid = process.pid
            # Process should be already started.
            assert pid is not None

            await self._stop_consensus_process(pid)

        threading.Thread(target=watch, daemon=True).start()

        port, websocket_port, http_port = await get_subprocess_consensus_ports_via_fifo(
            fifo
        )

        # The consensus should now be reachable at the address of the
        # server we started in the subprocess.
        address = placement_planner_pb2.Consensus.Address(host=host, port=port)
        websocket_address = placement_planner_pb2.Consensus.Address(
            host=host, port=websocket_port
        )
        http_address = placement_planner_pb2.Consensus.Address(
            host=host, port=http_port
        )

        return LaunchedConsensus(
            consensus=consensus,
            address=address,
            websocket_address=websocket_address,
            http_address=http_address,
            state=LaunchedConsensus.Subprocess(
                stop=stop,
                stopping=stopping,
            ),
        )

    @rebootdev.aio.tracing.function_span()
    async def _configure_envoy(self):
        if self._local_envoy is not None:
            # Stop the existing local Envoy, and replace it with a new one.
            await self._local_envoy.stop()
            self._local_envoy = None

        # Get list of `Serviceable`s if a local envoy has been
        # requested as well as possibly a specific port they'd like
        # Envoy to listen on.
        envoy_serviceables: list[Serviceable] = []
        envoy_port: int = 0
        envoy_use_tls: bool = False

        if self._revision is not None and self._revision.local_envoy:
            envoy_serviceables = self._revision.serviceables
            envoy_port = self._revision.local_envoy_port
            envoy_use_tls = self._revision.local_envoy_use_tls

        if len(envoy_serviceables) == 0:
            # No reason to launch an Envoy. We're done.
            return

        # Make a list of consensuses that have been launched, and which ports
        # they're running on. If the application has just started or is shutting
        # down there might be none.
        address_by_consensus: dict[ConsensusId, ConsensusAddress] = {}
        application_id: Optional[ApplicationId] = None
        stopped_consensuses = set()
        for launched_consensus in self._launched_consensuses.values():
            address_by_consensus[
                launched_consensus.consensus.id
            ] = ConsensusAddress(
                # TODO: when we do leader election with multiple replicas,
                #       consensuses currently hosted by other replicas will have
                #       non-localhost addresses using their public ports, but
                #       the local consensus must still be addressed as
                #       "localhost" with its internal port.
                host="localhost",
                grpc_port=launched_consensus.address.port,
                websocket_port=launched_consensus.websocket_address.port,
                http_port=launched_consensus.http_address.port,
            )
            if launched_consensus.stopped():
                stopped_consensuses.add(launched_consensus.consensus.id)
            new_application_id = ensure_valid_application_id(
                launched_consensus.consensus.application_id
            )
            if application_id is None:
                application_id = new_application_id
            else:
                assert application_id == new_application_id

        if len(address_by_consensus) == 0:
            # No reason to launch an Envoy. We're done.
            return
        assert application_id is not None

        self._local_envoy = LocalEnvoyFactory.create(
            listener_port=envoy_port,
            use_tls=envoy_use_tls,
            application_id=application_id,
            # NOTE: we also tell `LocalEnvoy` to proxy traffic for all
            # of the `Routable`s that the `_ServiceServer` declares
            # (i.e., system services).
            routables=envoy_serviceables + _ServiceServer.ROUTABLES,
            stopped_consensuses=stopped_consensuses,
        )

        await self._local_envoy.start()

        await self._local_envoy.set_consensuses(
            address_by_consensus=address_by_consensus,
        )


class FakeConsensusManager(ConsensusManager):
    """The FakeConsensusManager doesn't actually start any servers. It will just
    reply with a made-up address for any consensus that is requested.
    """

    @staticmethod
    def hostname_for_consensus(consensus_id: ConsensusId) -> str:
        return f'hostname-for-{consensus_id}'

    @staticmethod
    def first_port() -> int:
        return 1337

    def __init__(self):
        super().__init__()
        # Assign predictable ports to consensuses in order of arrival, and keep
        # them stable as long as the consensus exists. These predictable ports
        # are useful to tests.
        self.port_by_consensus_id: dict[ConsensusId, int] = {}
        self.next_port = self.first_port()

        # Track the consensuses that exist, also useful for tests.
        self.consensuses: dict[ConsensusId, Consensus] = {}

    def address_for_consensus(
        self,
        consensus_id: str,
    ) -> placement_planner_pb2.Consensus.Address:
        port = self.port_by_consensus_id.get(consensus_id) or self.next_port
        if port == self.next_port:
            self.port_by_consensus_id[consensus_id] = port
            self.next_port += 1

        return placement_planner_pb2.Consensus.Address(
            host=self.hostname_for_consensus(consensus_id),
            port=port,
        )

    @rebootdev.aio.tracing.function_span()
    async def _set_consensus(
        self,
        consensus: Consensus,
    ) -> placement_planner_pb2.Consensus.Address:
        self.consensuses[consensus.id] = consensus
        return self.address_for_consensus(consensus.id)

    @rebootdev.aio.tracing.function_span()
    async def _delete_consensus(
        self,
        consensus: Consensus,
    ) -> None:
        del self.consensuses[consensus.id]
        del self.port_by_consensus_id[consensus.id]
