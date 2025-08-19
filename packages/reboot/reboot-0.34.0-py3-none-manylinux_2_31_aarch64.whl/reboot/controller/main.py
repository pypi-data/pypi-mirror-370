from __future__ import annotations

import asyncio
import kubernetes_asyncio
import log.log as logging
import os
from kubernetes_utils.kubernetes_client import EnhancedKubernetesClient
from reboot.controller.application_config_trackers import (
    KubernetesApplicationConfigTracker,
)
from reboot.controller.config_extractor import KubernetesConfigExtractor
from reboot.controller.consensus_managers import KubernetesConsensusManager
from reboot.controller.network_managers import KubernetesNetworkManager
from reboot.controller.placement_planner import PlacementPlanner
from reboot.controller.settings import (
    ENVVAR_KUBERNETES_POD_NAME,
    ENVVAR_KUBERNETES_POD_NAMESPACE,
    ENVVAR_KUBERNETES_POD_UID,
)
from rebootdev.helpers import maybe_cancel_task

logger = logging.get_logger(__name__)


async def main():
    logging.set_log_level(logging.INFO)
    own_pod_namespace = os.environ.get(ENVVAR_KUBERNETES_POD_NAMESPACE)
    own_pod_name = os.environ.get(ENVVAR_KUBERNETES_POD_NAME)
    own_pod_uid = os.environ.get(ENVVAR_KUBERNETES_POD_UID)
    if own_pod_namespace is None or own_pod_name is None or own_pod_uid is None:
        raise ValueError(
            f'Missing required Kubernetes downward API environment variables: '
            f'namespace={own_pod_namespace}, name={own_pod_name}, uid={own_pod_uid}'
        )
    own_pod_metadata = kubernetes_asyncio.client.V1ObjectMeta(
        namespace=own_pod_namespace, name=own_pod_name, uid=own_pod_uid
    )

    # We're on Kubernetes, so create an incluster client.
    k8s_client = await EnhancedKubernetesClient.create_incluster_client()
    consensus_manager = KubernetesConsensusManager(k8s_client=k8s_client)
    application_config_tracker = KubernetesApplicationConfigTracker(k8s_client)
    config_extractor = KubernetesConfigExtractor(k8s_client=k8s_client)
    placement_planner = PlacementPlanner(
        application_config_tracker, consensus_manager, '0.0.0.0:0'
    )
    # ATTENTION, after `start()`ing it we MUST `stop()` the `PlacementPlanner`
    # even if the program crashes, otherwise the `PlacementPlanner` will keep
    # running in the background and prevent the program from exiting.
    await placement_planner.start()

    try:
        application_config_tracker_task = None
        config_extractor_task = None
        network_manager_task = None

        network_manager = KubernetesNetworkManager(
            k8s_client, placement_planner, own_pod_metadata
        )

        # To be sure that we eventually await all the necessary tasks for the
        # different controller components, we collect them into a single future
        # using `asyncio.gather()`.
        # Note: if any these tasks raises, we expect the exception to crash
        #       the program.
        application_config_tracker_task = asyncio.Task(
            application_config_tracker.run()
        )
        config_extractor_task = asyncio.Task(config_extractor.run())
        network_manager_task = asyncio.Task(network_manager.run())
        await asyncio.gather(
            application_config_tracker_task,
            config_extractor_task,
            network_manager_task,
        )
    finally:
        # As mentioned above, we MUST stop the `PlacementPlanner`, even when
        # crashing.
        await placement_planner.stop()

        # The fact that we got here is unexpected; we would expect `gather`
        # to run forever. Therefore, we must have encountered an error. We
        # will let the exception propagate to crash the controller, but to
        # be sure that we'll exit as expected we'll first cancel any task
        # that didn't fail yet.
        await maybe_cancel_task(application_config_tracker_task)
        await maybe_cancel_task(config_extractor_task)
        await maybe_cancel_task(network_manager_task)


if __name__ == '__main__':
    asyncio.run(main())
    logger.info('Done with main function')
