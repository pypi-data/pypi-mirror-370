import asyncio
import grpc
import hashlib
import kubernetes_asyncio
import os
import traceback
import uuid
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from kubernetes_utils.helpers import WatchEventType
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.custom_objects import MustRestartWatch
from kubernetes_utils.resources.deployments import Container, Resources
from kubernetes_utils.resources.pods import PodFailedError
from kubernetes_utils.retry import retry_insecure_grpc_unless_pods_have_failed
from log.log import get_logger
from rbt.v1alpha1 import (
    application_config_pb2,
    config_mode_pb2,
    config_mode_pb2_grpc,
    kubernetes_helpers_pb2,
)
from reboot.controller.application_config import (
    ApplicationConfig,
    application_config_spec_from_routables,
)
from reboot.controller.application_deployment import ApplicationDeployment
from reboot.controller.fluent_bit import (
    delete_fluent_bit_configmap,
    fluent_bit_containers,
    write_fluent_bit_configmap,
)
from reboot.controller.settings import (
    ENVVAR_PORT,
    ENVVAR_REBOOT_CONFIG_SERVER_PORT,
    ENVVAR_REBOOT_FACILITATOR_IMAGE_NAME,
    ENVVAR_REBOOT_MODE,
    ENVVAR_REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME,
    IS_REBOOT_APPLICATION_LABEL_NAME,
    IS_REBOOT_APPLICATION_LABEL_VALUE,
    REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
    REBOOT_CONFIG_POD_MAIN_MEMORY_LIMIT,
    REBOOT_CONFIG_POD_MAIN_MEMORY_REQUEST,
    REBOOT_MODE_CONFIG,
    REBOOT_ROUTABLE_HOSTNAME,
    REBOOT_WAIT_FOR_FACILITATOR_MEMORY_LIMIT,
    REBOOT_WAIT_FOR_FACILITATOR_MEMORY_REQUEST,
    USER_CONTAINER_GRPC_PORT,
)
from reboot.controller.spaces import (
    ensure_application_service_account_in_space,
    ensure_namespace_for_space,
)
from reboot.naming import (
    is_facilitator_application_id,
    make_facilitator_application_id,
)
from rebootdev.aio.exceptions import InputError
from rebootdev.aio.headers import APPLICATION_ID_HEADER
from rebootdev.aio.servicers import Serviceable
from rebootdev.aio.types import ApplicationId, ConfigRunId, RoutableAddress
from rebootdev.consensus.service_descriptor_validator import (
    ProtoValidationError,
    validate_descriptor_sets_are_backwards_compatible,
)
from rebootdev.helpers import maybe_cancel_task
from rebootdev.settings import (
    ENVVAR_RBT_STATE_DIRECTORY,
    ENVVAR_REBOOT_CLOUD_VERSION,
    REBOOT_STATE_DIRECTORY,
)
from typing import Optional

logger = get_logger(__name__)

# This hardcoded server port KUBERNETES_CONFIG_SERVER_PORT is safe because
# it will only ever run on Kubernetes where there is no chance of
# a port conflict due to simultaneous tests.
KUBERNETES_CONFIG_SERVER_PORT = 56653

# The prefix used for the names of all config pods.
CONFIG_POD_NAME_PREFIX = 'config-run-'
# By appending 10 random characters to the end of a config pod's name we have a
# very low chance of name collisions, while still being human-readable.
CONFIG_POD_NAME_SUFFIX_LENGTH = 10

# The maximum time to wait for the config pod to come up and the maximum
# time to wait after that to connect to the pod.
#
# TODO(rjh, stephanie): use this timeout ONLY for AFTER the pod has been
#                       reported as up. Before that, no timeout, but detect
#                       permanent errors.
CONFIG_POD_TIMEOUT_SECONDS = 30


class LocalConfigExtractor:

    def __init__(self, application_id: ApplicationId):
        self._application_id = application_id

    def config_from_serviceables(
        self,
        serviceables: list[Serviceable],
        consensuses: Optional[int],
    ) -> ApplicationConfig:
        spec = application_config_spec_from_routables(
            routables=serviceables,
            consensuses=consensuses,
        )

        return ApplicationConfig.create(
            application_id=self._application_id,
            metadata=None,  # We're local, so no (Kubernetes) metadata.
            spec=spec,
        )


def _from_environment_variable(envvar_name: str) -> str:
    result = os.environ.get(envvar_name)
    if result is None:
        raise ValueError(
            f"Missing required environment variable '{envvar_name}'."
        )
    return result


def _facilitator_image_name() -> str:
    return _from_environment_variable(ENVVAR_REBOOT_FACILITATOR_IMAGE_NAME)


def _wait_for_healthy_image_name() -> str:
    return _from_environment_variable(
        ENVVAR_REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME
    )


class ConfigPodRunner:
    """
    A class that will run a config pod and return the ApplicationConfig it
    produces.

    Factored out from `KubernetesConfigExtractor` for testing.
    """

    def __init__(self, k8s_client: AbstractEnhancedKubernetesClient):
        self._k8s_client = k8s_client

    async def create_config_pod(
        self,
        namespace: str,
        application_id: ApplicationId,
        revision_number: int,
        service_account_name: str,
        deployment_name: str,
        image: str,
    ) -> tuple[str, RoutableAddress]:
        """
        Creates the config pod

        Returns the name and IP address of the config pod.
        """
        # Create a ConfigMap for FluentBit.
        facilitator_application_id: Optional[ApplicationId] = None
        if not is_facilitator_application_id(application_id):
            await write_fluent_bit_configmap(
                k8s_client=self._k8s_client,
                namespace=namespace,
                application_id=application_id,
                revision_number=revision_number,
                deployment_name=deployment_name,
                config_run_id=ConfigRunId(deployment_name),
            )
            facilitator_application_id = make_facilitator_application_id(
                application_id
            )

        logger.info(
            f"Creating config pod: (namespace='{namespace}', "
            f"deployment_name='{deployment_name}', image='{image}'), "
            f"facilitator_application_id='{facilitator_application_id}'"
        )

        # We use a `Deployment` because it's the simplest way to get a `Pod`
        # going with our `k8s_client`.
        #
        # TODO: rework this to just be a `Pod` instead of a `Deployment`: a
        #       `Deployment` demands a `restartPolicy` of "Always", which means
        #       a crashing application container will be restarted and the logs
        #       of the crash will be repeated. This isn't a great user
        #       experience; it would be better if crashing config pod containers
        #       don't restart and thereby just log their error once.
        #
        # TODO: Consider making the controller the owner of this pod, for safety
        #       in case the controller is deleted while a config pod is running.
        #       ISSUE(https://github.com/reboot-dev/mono/issues/1430): Fix
        #       ownership.
        await self._k8s_client.deployments.create_or_update(
            namespace=namespace,
            deployment_name=deployment_name,
            replicas=1,
            service_account_name=service_account_name,
            # After termination still give the config pod lots of time
            # to flush its logs. We're in no rush to delete it.
            termination_grace_period_seconds=300,
            pod_labels={
                IS_REBOOT_APPLICATION_LABEL_NAME:
                    IS_REBOOT_APPLICATION_LABEL_VALUE,
            },
            init_containers=(
                [
                    # Blocks startup of the config pod until the facilitator
                    # is available (if there's a facilititator for this
                    # app). See:
                    #   https://github.com/reboot-dev/mono/issues/4671
                    Container(
                        name="wait-for-facilitator",
                        image_name=_wait_for_healthy_image_name(),
                        args=[
                            # These values match what gets built by
                            # `//reboot/docker:wait-for-ready`.
                            #
                            # We must repeat the container's command,
                            # because in Kubernetes `args` overrides
                            # `CMD`!? See:
                            #   https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/#define-a-command-and-arguments-when-you-create-a-pod
                            "/usr/bin/python",
                            "/app/reboot/wait-for-healthy/wait-for-healthy_binary",
                            # Rely on JSON-to-gRPC transcoding to also test
                            # that the transcoding is configured.
                            f"http://{REBOOT_ROUTABLE_HOSTNAME}.reboot-system:{USER_CONTAINER_GRPC_PORT}/grpc.health.v1.Health/Check",
                            "--method=POST",
                            f"--header={APPLICATION_ID_HEADER}:{facilitator_application_id}",
                            "--header=Content-Type:application/json",
                        ],
                        resources=Resources(
                            limits=Resources.Values(
                                memory=REBOOT_WAIT_FOR_FACILITATOR_MEMORY_LIMIT,
                            ),
                            requests=Resources.Values(
                                memory=
                                REBOOT_WAIT_FOR_FACILITATOR_MEMORY_REQUEST,
                            ),
                        ),
                    )
                ] if facilitator_application_id is not None else []
            ) + fluent_bit_containers(application_id, deployment_name),
            containers=[
                Container(
                    name="main",
                    image_name=image,
                    resources=Resources(
                        limits=Resources.Values(
                            memory=REBOOT_CONFIG_POD_MAIN_MEMORY_LIMIT,
                        ),
                        requests=Resources.Values(
                            memory=REBOOT_CONFIG_POD_MAIN_MEMORY_REQUEST,
                        ),
                    ),
                    env=[
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_MODE, value=REBOOT_MODE_CONFIG
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_CONFIG_SERVER_PORT,
                            value=f'{KUBERNETES_CONFIG_SERVER_PORT}'
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_REBOOT_CLOUD_VERSION,
                            value='v1alpha1',
                        ),
                        kubernetes_asyncio.client.V1EnvVar(
                            # On the Reboot Cloud we always use a static port,
                            # which is the same for all config pods. However,
                            # to pass the checks in `rbt serve` we still have to
                            # set the `PORT` environment variable, just like in
                            # a consensus pod.
                            #
                            # NOTE: The value of `PORT` is unused in config pods.
                            name=ENVVAR_PORT,
                            value=f'{USER_CONTAINER_GRPC_PORT}'
                        ),
                        # On the Reboot Cloud we always use a static state
                        # directory, which is the same for all config pods.
                        # However, to pass the checks in `rbt serve` we still
                        # have to pass the `RBT_STATE_DIRECTORY`
                        # environment variable, just like in a consensus pod.
                        kubernetes_asyncio.client.V1EnvVar(
                            name=ENVVAR_RBT_STATE_DIRECTORY,
                            value=REBOOT_STATE_DIRECTORY,
                        ),
                        # Ensure that any Python process
                        # always produces their output
                        # immediately. This is helpful for
                        # debugging purposes.
                        kubernetes_asyncio.client.V1EnvVar(
                            name='PYTHONUNBUFFERED', value='1'
                        ),
                    ],
                ),
            ],
        )

        logger.info('Waiting for config pod to come up...')
        try:
            await self._k8s_client.pods.wait_for_ready_with_prefix(
                namespace=namespace, name_prefix=deployment_name
            )
        except PodFailedError as e:
            raise InputError(
                reason='container failed before becoming ready',
                causing_exception=e,
            ) from e

        pods = await self._k8s_client.pods.list_for_name_prefix(
            namespace=namespace, name_prefix=deployment_name
        )
        assert len(pods) == 1, 'Incorrect number of pods for config-pod'
        pod = pods[0]

        return (pod.metadata.name, pod.status.pod_ip)

    async def get_application_config(
        self,
        *,
        namespace: str,
        pod_name: str,
        pod_ip: RoutableAddress,
    ) -> application_config_pb2.ApplicationConfig:
        try:
            async for retry in retry_insecure_grpc_unless_pods_have_failed(
                # This hardcoded server port KUBERNETES_CONFIG_SERVER_PORT
                # is safe because it will only ever run on Kubernetes
                # where there is no chance of a port conflict due to
                # simultaneous tests.
                f'{pod_ip}:{KUBERNETES_CONFIG_SERVER_PORT}',
                k8s_client=self._k8s_client,
                pods=[(namespace, [pod_name])],
                # TODO(benh): we only catch AioRpcError, but we should
                # also consider catching protobuf decoding errors.
                exceptions=[grpc.aio.AioRpcError],
            ):
                logger.info(
                    "Trying to get application config from namespace "
                    f"'{namespace}' pod '{pod_name}' ..."
                )
                with retry() as channel:
                    try:
                        config_server_stub = config_mode_pb2_grpc.ConfigStub(
                            channel
                        )

                        response = await config_server_stub.Get(
                            config_mode_pb2.GetConfigRequest()
                        )

                        return response.application_config
                    except grpc.aio.AioRpcError as e:
                        # `retry()` will retry these exceptions without
                        # logging, but we want to log them for debugging
                        # purposes.
                        logger.info(f"Encountered retryable error: {e}")
                        raise
        except Exception as e:
            # When `retry_insecure_grpc_unless_pods_have_failed` fails, it will
            # raise a _list_ of errors it encountered. In case of a pod failure,
            # the error will be a `PodFailedError`, and because we're watching
            # exactly one pod there can be at most one such error.
            if (
                len(e.args) == 0 or not isinstance(e.args[0], list) or
                len(e.args[0]) == 0 or
                not isinstance(e.args[0][0], PodFailedError)
            ):
                # This was not about a pod failure, and therefore is unexpected.
                # Have the exception bubble up to eventually make the controller
                # loudly crash.
                raise
            # Do not forward the error message from the PodFailedError; it is
            # not useful to a customer.
            raise InputError(
                reason='Container failed before producing configuration - check '
                'application logs for more information',
            )

    async def delete_config_pod(
        self, namespace: str, deployment_name: str
    ) -> None:
        await self._k8s_client.deployments.delete(namespace, deployment_name)
        # See https://github.com/reboot-dev/mono/issues/4671: we must
        # wait for the config pod to complete its termination before
        # continuing (especially before updating the
        # `ApplicationDeployment.status`), since that guarantees that
        # the logs from this config pod have been flushed to the
        # facilitator.
        #
        # TODO(rjh): this assumes that the config pod will obey a
        #            SIGTERM in a timely manner. If it doesn't, we might
        #            wait a long time (our whole
        #            `termination_grace_period_seconds`). Perhaps we
        #            could detect (using the equivalent of `kubectl
        #            describe pod`) that the pod's `main` container
        #            isn't exiting and tell the user that there's an
        #            issue.
        await self._k8s_client.pods.wait_for_deleted_with_prefix(
            namespace=namespace, name_prefix=deployment_name
        )
        await delete_fluent_bit_configmap(
            self._k8s_client, namespace, deployment_name
        )

    async def delete_all_config_pods(self) -> None:
        logger.info("Deleting existing config pods...")
        config_pod_deployments = await self._k8s_client.deployments.list_for_name_prefix(
            namespace=None, name_prefix=CONFIG_POD_NAME_PREFIX
        )
        for deployment in config_pod_deployments:
            await self._k8s_client.deployments.delete(
                deployment.metadata.namespace, deployment.metadata.name
            )
            logger.info(
                f"Deleted config pod '{deployment.metadata.name}' in namespace "
                f"'{deployment.metadata.namespace}'."
            )


def _get_revision(application_deployment: ApplicationDeployment) -> str:
    # We define the "revision" as being a hash of the ApplicationDeployment's
    # spec. That guarantees that the revision changes if, and only if, the spec
    # changes. Compared to e.g. the Kubernetes object's resource version, it
    # won't change when unrelated fields (e.g. status) change.
    #
    # NOTE: for historical reasons, this "revision" is NOT the same as (and not
    #       related to) the `ApplicationDeployment.Spec.revision_number` field -
    #       although changes in the `revision_number` do cause the "revision" to
    #       change, just like any other change to the `Spec` does.
    return hashlib.sha1(application_deployment.spec.SerializeToString()
                       ).hexdigest()


class KubernetesConfigExtractor:

    def __init__(
        self,
        k8s_client: AbstractEnhancedKubernetesClient,
        config_pod_runner: Optional[ConfigPodRunner] = None,
    ):
        self._k8s_client = k8s_client
        self._config_pod_runner = config_pod_runner or ConfigPodRunner(
            k8s_client
        )

        self._update_task_by_application_id: dict[str, asyncio.Task] = {}
        self._need_reconciliation = asyncio.Event()
        # Always do a reconciliation after startup.
        self._need_reconciliation.set()

    async def run(self) -> None:
        # Delete any existing config pods. They are left over from an
        # old controller run and will never be used by this run.
        await self._config_pod_runner.delete_all_config_pods()

        reconcile_task = asyncio.create_task(
            self._reconcile_deployments_and_configs(),
            name=f'self._reconcile_deployments_and_configs() in {__name__}',
        )
        watch_task = asyncio.create_task(
            self._watch_for_application_deployment_objects(),
            name=
            f'self._watch_for_application_deployment_objects() in {__name__}',
        )
        try:
            await asyncio.gather(reconcile_task, watch_task)
        finally:
            # The fact that we got here is unexpected; we would expect `gather`
            # to run forever. Therefore, we must have encountered an error. We
            # will let the exception propagate to crash the controller, but to
            # be sure that we'll exit as expected we'll first cancel any task
            # that didn't fail yet.
            await maybe_cancel_task(reconcile_task)
            await maybe_cancel_task(watch_task)

    async def _watch_for_application_deployment_objects(self) -> None:
        logger.info(
            "Watching for ApplicationDeployment changes in the "
            f"'{REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE}' namespace..."
        )

        while True:
            try:
                # Find the Kubernetes resource version that we're currently at.
                _, resource_version = await self._k8s_client.custom_objects.list_all(
                    object_type=ApplicationDeployment
                )

                # We may have missed some events that happened before this watch
                # started. Do reconciliation; better safe than sorry.
                self._need_reconciliation.set()

                # Now begin watching, starting at the previously-seen resource
                # version, ensuring that no events can get missed in between.
                async for watch_event in self._k8s_client.custom_objects.watch_all(
                    object_type=ApplicationDeployment,
                    namespace=REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
                    resource_version=resource_version,
                ):
                    event_type: WatchEventType = watch_event.type
                    logger.info(
                        "ApplicationDeployment '%s': '%s'",
                        watch_event.object.metadata.name or 'Unknown',
                        event_type,
                    )
                    self._need_reconciliation.set()

            except MustRestartWatch:
                # This is expected from time to time. Simply start watching
                # again from scratch.
                continue

        # This is unexpected; we would expect the loop above to run forever.
        # Crash the controller, so that it can be restarted by Kubernetes.
        raise RuntimeError(
            'Unexpectedly stopped watching for ApplicationDeployment changes'
        )

    async def _reconcile_deployments_and_configs(self) -> None:
        """
        The reconciliation loop is triggered when there are any changes that may
        prompt a need for reconciliation between ApplicationDeployments and
        ApplicationConfigs.

        Triggers of the reconciliation loop include:
        * Startup.
        * Any changes to ApplicationDeployments.
        * Completed updates (by the reconciliation loop) of ApplicationConfigs.

        Each iteration of the loop will do a full reconciliation, comparing all
        deployments to all configs.

        If any updates of ApplicationConfigs are needed, they are performed in
        parallel. However, each ApplicationConfig can only have one concurrent
        update - this is why each completed update must schedule another round
        of reconciliation: to ensure that any changes that occurred after the
        start of the update are also handled.
        """
        # Note: no try/catch here. Any errors that bubble up to this level are
        #       unexpected and should crash the controller, so that it can be
        #       restarted by Kubernetes.
        #
        # TODO(rjh): as in `_watch_for_application_deployment_objects()`, it is
        #            possible that our calls out to Kubernetes may raise errors
        #            that are temporary in nature and not worth crashing the
        #            controller over. We haven't observed such false alarms
        #            (yet), but when we do we likely want to add a try/except
        #            retry loop here instead of crashing the controller.
        while True:
            logger.debug(
                "Awaiting need for ApplicationDeployment/Config "
                "reconciliation"
            )
            await self._need_reconciliation.wait()
            self._need_reconciliation.clear()
            logger.info("Reconciling ApplicationDeployment/Config now")

            await self._reconcile_deployments_and_configs_once()

    async def _reconcile_deployments_and_configs_once(self) -> None:
        """
        The body of the `_reconcile_deployments_and_configs` loop. See there for
        detailed comments.

        Factored out for testing.
        """
        # TODO(rjh): this method of doing reconciliation, where we list all of
        # the ApplicationDeployments and ApplicationConfigs, is O(existent
        # applications). If we had a more diff-based approach to building these
        # lists we could reduce that to O(changed applications). But that would
        # be more complex to build and test, and we have a long way to go until
        # we hit current scalability limits.

        # Remove any completed update tasks, freeing up slots for subsequent
        # updates on the same objects.
        completed_update_application_ids = [
            application_id for application_id, update_task in
            self._update_task_by_application_id.items() if update_task.done()
        ]
        for application_id in completed_update_application_ids:
            # Await the completed task, so we can discover if it encountered an
            # error. Such an error will be re-thrown by the `await`; we don't
            # catch the error, since we want such an unexpected issue to crash
            # the controller.
            await self._update_task_by_application_id[application_id]
            del self._update_task_by_application_id[application_id]

        # Fetch all ApplicationDeployments and ApplicationConfigs.
        all_deployments, _ = await self._k8s_client.custom_objects.list_all(
            object_type=ApplicationDeployment,
            namespace=REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
        )
        deployments_by_application_id: dict[
            ApplicationId, ApplicationDeployment] = {
                deployment.application_id(): deployment
                for deployment in all_deployments
            }
        all_configs, _ = await self._k8s_client.custom_objects.list_all(
            object_type=ApplicationConfig,
            namespace=None,  # Anywhere in the cluster.
        )
        configs_by_application_id: dict[ApplicationId, ApplicationConfig] = {
            config.application_id(): config for config in all_configs
        }

        facilitator_deployments_by_application_id: dict[
            ApplicationId, ApplicationDeployment] = {}
        for application_id, deployment in deployments_by_application_id.items(
        ):
            # Every application should also get a facilitator application to
            # collect its logs.
            facilitator_application_id = make_facilitator_application_id(
                application_id
            )
            if facilitator_application_id in deployments_by_application_id:
                # Already added this facilitator (possible if multiple
                # applications share a single facilitator).
                continue

            # Add a "virtual" `ApplicationDeployment` for the facilitator
            # application.
            facilitator_deployment = ApplicationDeployment.create(
                application_id=facilitator_application_id,
                metadata=kubernetes_asyncio.client.V1ObjectMeta(
                    namespace=REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
                    name=facilitator_application_id,
                ),
                spec=ApplicationDeployment.Spec(
                    space_id=deployment.spec.space_id,
                    container_image_name=_facilitator_image_name(),
                ),
                status=ApplicationDeployment.Status(
                    # The facilitator application should always have some
                    # status, since otherwise the controller will forever
                    # attempt to give it one by configuring it. We'll say that
                    # it's `configured` - if the `spec` is out of date relative
                    # to the `ApplicationConfig` it will get reconfigured
                    # regardless of that status.
                    configured=ApplicationDeployment.Status.Configured(),
                ),
            )
            facilitator_deployments_by_application_id[
                facilitator_application_id] = facilitator_deployment
        # Update `deployments_by_application_id` now that we're done iterating
        # over it.
        all_deployments.extend(
            facilitator_deployments_by_application_id.values()
        )
        deployments_by_application_id.update(
            facilitator_deployments_by_application_id
        )

        all_application_ids = (
            set(configs_by_application_id.keys()) |
            set(deployments_by_application_id.keys())
        )

        for application_id in all_application_ids:

            # For every `ApplicationConfig` there must be a matching
            # `ApplicationDeployment`. If there isn't, the `ApplicationConfig`
            # must be deleted.
            if (
                application_id in configs_by_application_id and
                application_id not in deployments_by_application_id
            ):
                if application_id in self._update_task_by_application_id:
                    # We could attempt to cancel the ongoing update so we can
                    # immediately perform this new deletion, but making sure
                    # that our logic works in the face of cancellations at
                    # arbitrary moments would be complex. Instead, we'll simply
                    # come back to this deletion when the update is complete -
                    # every update will schedule another reconciliation when it
                    # completes.
                    logger.info(
                        f"Delaying delete of '{application_id}' because there is "
                        "still an update in progress"
                    )
                    continue

                logger.info(
                    f"Will delete orphaned ApplicationConfig '{application_id}'"
                )
                await self._k8s_client.custom_objects.delete(
                    configs_by_application_id[application_id]
                )
                continue

            assert application_id in deployments_by_application_id

            # For every `ApplicationDeployment` there must be a matching
            # `ApplicationConfig`, AND that config must have the same revision as
            # the ApplicationDeployment. If there isn't, we must handle an
            # update.
            needs_update = False
            deployment = deployments_by_application_id[application_id]
            deployment_revision = _get_revision(deployment)

            # If we've already tried to apply this revision but failed due to
            # user input errors, then we'll not try again.
            if deployment.status.failed.revision == deployment_revision:
                logger.info(
                    f"Previous deployment of '{application_id}' at revision "
                    f"'{deployment_revision}' failed. Not retrying."
                )
                continue

            # If the previous deployment failed, and now we've changed the
            # revision, we must always update the config - if only to clear the
            # `failed` status (e.g. after a rollback).
            if deployment.status.failed.revision != '':
                logger.info(
                    f"Previous deployment of '{application_id}' at revision "
                    f"'{deployment.status.failed.revision}' failed. "
                    f"Will retry with new revision '{deployment_revision}'..."
                )
                needs_update = True

            # If the deployment is status-less (e.g. overwritten by somebody),
            # then we must give it a status. The only way we have to do that is
            # to attempt a config update.
            if deployment.status.WhichOneof('state') is None:
                logger.info(
                    f"Deployment of '{application_id}' has no status. Needs update."
                )
                needs_update = True

            # If there were no prior failed deployments, then whether we need an
            # update depends on whether the ApplicationConfig is in sync with
            # the ApplicationDeployment.
            old_config: Optional[ApplicationConfig] = None
            if application_id not in configs_by_application_id:
                logger.info(
                    "Reconciliation detected missing ApplicationConfig "
                    f"'{application_id}'. Needs creating."
                )
                needs_update = True
            else:
                old_config = configs_by_application_id[application_id]
                if old_config.spec.revision != deployment_revision:
                    logger.info(
                        "Reconciliation detected stale ApplicationConfig "
                        f"'{application_id}' (have revision "
                        f"'{old_config.spec.revision}', want revision "
                        f"'{deployment_revision}'). Needs update."
                    )
                    needs_update = True

            if not needs_update:
                logger.info(
                    f"Deployment of '{application_id}' does not need update."
                )
                continue

            # To keep things simple we only want to have one update task per
            # application at any given time. If an update is already in progress,
            # don't schedule the next one yet.
            #
            # To ensure we don't miss newer updates while we're still handling older
            # updates, every update task will finish by requesting another round of
            # reconciliation. This will ensure that reconciliation continues until
            # there are no update tasks running AND there is a round of
            # reconciliation that doesn't find any additional updates to handle.
            if application_id in self._update_task_by_application_id:
                logger.info(
                    f"Delaying update of '{application_id}' because there is "
                    "still a prior update in progress"
                )
                continue

            # This application needs an update, so we'll start a task to handle
            # that.
            async def do_update(
                deployment: ApplicationDeployment,
                old_config: Optional[ApplicationConfig],
            ) -> None:
                # Do not use the `deployment_revision` from the outer scope; it
                # might have changed by the time this task runs.
                deployment_revision = _get_revision(deployment)
                try:
                    await self._update_status(
                        deployment,
                        ApplicationDeployment.Status(
                            configuring=ApplicationDeployment.Status.
                            Configuring(),
                            # Keep `application_config` unchanged for now.
                            application_config=deployment.status.
                            application_config,
                        ),
                    )

                    # Extract an ApplicationConfig for the ApplicationDeployment.
                    config = await self._get_application_config_for_deployment(
                        deployment
                    )

                    # Validate the config change, and then persist it.
                    self._validate_config_change(old_config, config)
                    await self._k8s_client.custom_objects.create_or_update(
                        config
                    )
                    logger.info(
                        f"Created/updated ApplicationConfig '{application_id}' at revision "
                        f"'{config.spec.revision}'"
                    )

                    await self._update_status(
                        deployment,
                        ApplicationDeployment.Status(
                            configured=ApplicationDeployment.Status.Configured(
                            ),
                            application_config=kubernetes_helpers_pb2.
                            V1ObjectMeta(
                                namespace=config.metadata.namespace,
                                name=config.metadata.name,
                                # TODO(rjh): do we need the UID? If so, we'll
                                #            have to modify our Kubernetes
                                #            client library to get it.
                            ),
                        ),
                    )

                    # Now that the ApplicationConfig has been updated,
                    # trigger another round of reconciliation to detect any
                    # ApplicationDeployment changes that may have come in
                    # during this update.
                    self._need_reconciliation.set()
                except InputError as e:
                    error_reason = str(e)
                    if isinstance(e, ProtoValidationError):
                        error_reason = e.reason
                        for validation_error in e.validation_errors:
                            error_reason += f'\n* {validation_error}'
                    logger.info(f"Failed application update: '{error_reason}'")

                    await self._update_status(
                        deployment,
                        ApplicationDeployment.Status(
                            failed=ApplicationDeployment.Status.Failed(
                                revision=deployment_revision,
                            ),
                            reason=error_reason,
                            # Keep `application_config` pointing at the last
                            # successful config (if any).
                            application_config=deployment.status.
                            application_config,
                        ),
                    )
                except Exception as e:
                    # An unexpected (internal) error occurred. Do not report
                    # this to the owner of the `ApplicationDeployment`; there's
                    # quite possibly nothing they did wrong, this is an internal
                    # bug in the controller.
                    logger.critical(
                        f"Got unknown error for object '{type(e).__name__}': "
                        f"'{str(e)}'",
                    )
                    traceback.print_exc()
                    raise

            self._update_task_by_application_id[
                application_id] = asyncio.create_task(
                    do_update(deployment, old_config),
                    name=f'do_update(deployment, old_config) in {__name__}',
                )

    async def _get_application_config_for_deployment(
        self,
        application_deployment: ApplicationDeployment,
    ) -> ApplicationConfig:
        application_id = application_deployment.application_id()

        if application_deployment.spec.space_id == '':
            raise InputError(reason="field 'space_id' must not be empty")
        space_id = application_deployment.spec.space_id

        if application_deployment.spec.container_image_name == '':
            raise InputError(
                reason="field 'container_image_name' must not be empty"
            )

        revision_hash = _get_revision(application_deployment)
        revision_number = application_deployment.spec.revision_number
        logger.info(
            f"Will create or update ApplicationConfig '{application_id}' at/to "
            f"revision number {revision_number}"
        )

        # The appropriate Kubernetes namespace to run the config pod in is based
        # on the application's space ID.
        #
        # Create the Kubernetes namespace if it doesn't exist yet.
        space_namespace = await ensure_namespace_for_space(
            k8s_client=self._k8s_client,
            space_id=space_id,
        )
        service_account_name = await ensure_application_service_account_in_space(
            k8s_client=self._k8s_client,
            space_id=space_id,
            application_id=application_id,
        )

        # Come up with a unique name for the config pod. Having a unique name is
        # important, since even if we handle just one ApplicationDeployment at a
        # time it is possible for an old config pod to still be in state
        # `Terminating`when we want to create the next one.
        random_suffix = uuid.uuid4().hex[:CONFIG_POD_NAME_SUFFIX_LENGTH]
        config_pod_deployment_name = f'{CONFIG_POD_NAME_PREFIX}{random_suffix}'
        logger.info(
            f"Creating config pod deployment '{config_pod_deployment_name}' "
            f"for application '{application_id}' revision number "
            f"{revision_number}",
        )

        try:
            config_pod_name, config_pod_ip = await self._config_pod_runner.create_config_pod(
                namespace=space_namespace,
                application_id=application_id,
                revision_number=revision_number,
                service_account_name=service_account_name,
                deployment_name=config_pod_deployment_name,
                image=application_deployment.spec.container_image_name,
            )

            application_config_proto = await asyncio.wait_for(
                self._config_pod_runner.get_application_config(
                    namespace=space_namespace,
                    pod_name=config_pod_name,
                    pod_ip=config_pod_ip,
                ),
                timeout=CONFIG_POD_TIMEOUT_SECONDS,
            )

            application_config = ApplicationConfig.from_proto(
                metadata=kubernetes_asyncio.client.V1ObjectMeta(
                    namespace=space_namespace,
                    name=application_id,
                ),
                proto=application_config_proto,
            )

            # The ApplicationConfig we get back from the config pod is
            # incomplete. Fill in the blanks.
            application_config.spec.container_image_name = application_deployment.spec.container_image_name
            application_config.spec.revision = revision_hash
            application_config.spec.revision_number = revision_number
            return application_config
        except asyncio.exceptions.TimeoutError as e:
            raise InputError(
                reason='Timed out trying to start the application. Reboot '
                f'only waits {CONFIG_POD_TIMEOUT_SECONDS} seconds for the '
                'application to start, have you tried starting the application? '
                f'Does it take more than {CONFIG_POD_TIMEOUT_SECONDS} seconds to '
                'start?',
                causing_exception=e,
            ) from e

        finally:
            await self._config_pod_runner.delete_config_pod(
                space_namespace, config_pod_deployment_name
            )

            logger.debug(
                f"Deleted config pod '{config_pod_deployment_name}' for "
                f"'{application_deployment.application_id()}'. Be aware, it may "
                "still be in state `Terminating`."
            )

    async def _update_status(
        self,
        application_deployment: ApplicationDeployment,
        new_status: ApplicationDeployment.Status,
    ) -> None:
        """
        Write the given ApplicationDeployment to Kubernetes with a new given
        status.
        NOTE: make sure to pass an unmodified ApplicationDeployment; this method
              doesn't check for changes and will overwrite the entire object.
        """
        # Facilitator deployment status updates are not written to Kubernetes
        # objects (since these objects aren't real, they're made up based on
        # real `ApplicationDeployment`s). They're printed to the logs instead.
        if is_facilitator_application_id(
            application_deployment.application_id()
        ):
            logger.info(
                f"Facilitator deployment '{application_deployment.application_id()}' "
                f"status: {new_status}"
            )
            return

        # The `application_deployment.status` field, being a `message` proto
        # field, is not directly writable - but we can copy a new status onto
        # the old status to replace it.
        application_deployment.status.CopyFrom(new_status)
        await self._k8s_client.custom_objects.create_or_update(
            application_deployment
        )

    def _validate_config_change(
        self, old: Optional[ApplicationConfig], new: ApplicationConfig
    ) -> None:
        """Validate that the given old and new ApplicationConfigs are compatible.

        Raises `InputError` for validation failures.
        """
        if old is None:
            return

        def file_descriptor_set(
            config: ApplicationConfig
        ) -> FileDescriptorSet:
            file_descriptor_set = FileDescriptorSet()
            file_descriptor_set.ParseFromString(
                config.spec.file_descriptor_set
            )
            return file_descriptor_set

        validate_descriptor_sets_are_backwards_compatible(
            file_descriptor_set(old),
            file_descriptor_set(new),
        )
