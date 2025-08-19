import asyncio
import kubernetes_asyncio
import logging
from dataclasses import dataclass
from kubernetes_utils.kubernetes_client import (
    AbstractEnhancedKubernetesClient,
    EnhancedKubernetesClient,
)
from kubernetes_utils.resources.deployments import (
    Container,
    Resources,
    UpdateStrategy,
)
from reboot.controller.application_config import ApplicationConfig
from reboot.controller.application_deployment import ApplicationDeployment
from reboot.controller.settings import (
    ENVVAR_KUBERNETES_POD_NAME,
    ENVVAR_KUBERNETES_POD_NAMESPACE,
    ENVVAR_KUBERNETES_POD_UID,
    ENVVAR_REBOOT_FACILITATOR_IMAGE_NAME,
    ENVVAR_REBOOT_FLUENT_BIT_IMAGE_NAME,
    ENVVAR_REBOOT_STORAGE_TYPE,
    ENVVAR_REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME,
    ISTIO_NAMESPACE_LABELS,
    REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
    REBOOT_CONTROLLER_MEMORY_LIMIT,
    REBOOT_CONTROLLER_MEMORY_REQUEST,
    REBOOT_SYSTEM_NAMESPACE,
)
from reboot.controller.storage import StorageType
from typing import Optional

CONTROLLER_SERVICE_ACCOUNT = 'reboot-controller'


@dataclass(kw_only=True)
class Config:
    install_controller: bool

    # Parameters that are required if `install_controller=True`.
    controller_image: Optional[str] = None
    facilitator_image: Optional[str] = None
    fluent_bit_image: Optional[str] = None
    wait_for_healthy_image: Optional[str] = None

    # How will we provision storage?
    storage_type: StorageType


async def _apply_rbac(
    k8s_client: AbstractEnhancedKubernetesClient,
) -> None:
    """
    Set up namespaces and role based access control.

    There are two namespaces that need to get set up by the operator:
    1. The system namespace, which will contain the Reboot controller.
       TODO(rjh): we may consider renaming this to the "controller namespace"?
    2. The application deployment namespace, which will contain
       `ApplicationDeployment` objects.
    """

    # Ensure namespace and service account for reboot system.
    await k8s_client.namespaces.ensure_created(
        name=REBOOT_SYSTEM_NAMESPACE,
        labels=ISTIO_NAMESPACE_LABELS,
    )
    await k8s_client.service_accounts.ensure_created(
        namespace=REBOOT_SYSTEM_NAMESPACE,
        name=CONTROLLER_SERVICE_ACCOUNT,
    )

    # The Reboot Controller is allowed to do many things, in all namespaces in
    # the cluster. It needs these permissions in _all_ namespaces since we don't
    # know the names of namespaces that the controller will create in the
    # future.
    REBOOT_CONTROLLER_ROLE_NAME = 'reboot-controller-role'
    await k8s_client.cluster_roles.create_or_update(
        name=REBOOT_CONTROLLER_ROLE_NAME,
        rules=[
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['reboot.dev'],
                resources=['applicationdeployments'],
                verbs=[
                    'list',  # Used to reconcile application deployments with configs.
                    'update',  # Used to provide status updates on ApplicationDeployments.
                    'get',  # A prerequisite for "update" to not override unseen changes.
                    'watch',  # Creation/deletion will trigger application updates.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=[''],
                resources=['namespaces'],
                verbs=[
                    'create',  # Used to create "space" namespaces on-demand.
                    'update',  # Used when updating "space" labels, if needed.
                    'get',  # A prerequisite for "update" to not override unseen changes.
                    'delete',  # Used to delete namespaces when they're no longer needed.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=[''],
                resources=['configmaps'],
                verbs=[
                    'create',  # Used to create config maps for FluentBit containers.
                    'update',  # Used when updating the above config maps.
                    'get',  # A prerequisite for "update" to not override unseen changes.
                    'delete',  # Used to delete config maps when they're no longer needed.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=[''],
                resources=['serviceaccounts'],
                verbs=[
                    'create',  # Used to create application service accounts on demand.
                    'update',  # Used when updating application service accounts, if needed.
                    'get',  # A prerequisite for "update" to not override unseen changes.
                    'delete',  # Used to delete unused application service accounts.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['reboot.dev'],
                resources=['applicationconfigs'],
                verbs=[
                    'watch',  # Used to track config creation and know when to make new plans.
                    'list',  # Used to fetch current list of ApplicationConfigs for plan-making.
                    'get',  # Used as part of our create_or_update.
                    'create',  # Used by the config extractor to create an ApplicationConfig.
                    'update',  # Used by the config extractor to update an ApplicationConfig.
                    'delete',  # Used by the config extractor to delete an ApplicationConfig.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['', 'apps'],
                resources=['deployments', 'services', 'pods', 'pods/log'],
                verbs=[
                    'create',  # Used to bring up Consensuses for user containers on demand.
                    'update',  # Used to replace existing Consensuses whose details have changed.
                    'get',  # Used to fetch existing info needed when updating Consensuses, and logs.
                    'list',  # Used to list Pods, needed to address config pod.
                    'watch',  # Also used to list Pods, needed to address config pod, and follow logs.
                    'delete',  # Used to delete config pod.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['networking.istio.io'],
                resources=['virtualservices'],
                verbs=[
                    'create',  # Used to create the Reboot VirtualService.
                    'update',  # Used to update the Reboot VirtualService.
                    'get',  # Used to hermetically update the Reboot VirtualService.
                    'delete',  # Used to delete the Reboot VirtualService when it's no longer needed.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['networking.istio.io'],
                resources=['envoyfilters'],
                verbs=[
                    'create',  # Used to create the Reboot routing filter.
                    'update',  # Used to update the Reboot routing filter.
                    'get',  # Used to hermetically update the Reboot routing filter.
                    'list',  # Used to get unused filters.
                    'delete',  # Used to delete unused filters.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=['networking.istio.io'],
                resources=['gateways'],
                verbs=[
                    'create',  # Used to create the Reboot Gateway.
                    'update',  # Used to update the Reboot Gateway.
                    'get',  # Used to hermetically update the Reboot Gateway.
                ],
            ),
            kubernetes_asyncio.client.V1PolicyRule(
                api_groups=[''],
                resources=['persistentvolumeclaims'],
                verbs=[
                    'create',  # Used to create persistent volume claims for apps.
                    'update',  # Used to update persistent volume claims for apps.
                    'get',  # Used to hermetically update persistent volume claims.
                    'delete',  # Used to delete persistent volume claims when they're no longer needed.
                ],
            ),
        ],
    )

    await k8s_client.cluster_role_bindings.create_or_update(
        name='reboot-controller-binding',
        role_name=REBOOT_CONTROLLER_ROLE_NAME,
        subjects=[
            kubernetes_asyncio.client.RbacV1Subject(
                kind='ServiceAccount',
                namespace=REBOOT_SYSTEM_NAMESPACE,
                name=CONTROLLER_SERVICE_ACCOUNT,
            ),
        ],
    )

    # Ensure that there's a namespace that application deployments can be
    # written to.
    await k8s_client.namespaces.ensure_created(
        name=REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE,
        labels=ISTIO_NAMESPACE_LABELS,
    )


async def _teardown_namespaces(
    k8s_client: AbstractEnhancedKubernetesClient,
):
    """Clean up our Reboot installation.

    The simplest approach here is to delete the namespaces and be done with it,
    so that's what we do. We don't wait for cleanup to complete before
    returning, as that has been shown to cause a ~30 second slowdown in the
    termination of tests using this method.
    """
    return_values = await asyncio.gather(
        k8s_client.namespaces.delete(name=REBOOT_SYSTEM_NAMESPACE),
        k8s_client.namespaces.delete(
            name=REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE
        ),
        # Don't let exceptions propagate.
        return_exceptions=True
    )

    # Emit log messages if an exception was incurred.
    exceptions = [v for v in return_values if isinstance(v, Exception)]
    if len(exceptions) > 0:
        # TODO: Use reboot logging when we has it.
        logging.fatal(
            'Got the following exceptions while removing namespaces: %s',
            exceptions
        )


async def _install_controller(
    k8s_client: AbstractEnhancedKubernetesClient,
    controller_image: str,
    storage_type: StorageType,
    facilitator_image: str,
    fluent_bit_image: str,
    wait_for_healthy_image: str,
) -> None:

    env = [
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_KUBERNETES_POD_NAMESPACE,
            value_from=kubernetes_asyncio.client.V1EnvVarSource(
                field_ref=kubernetes_asyncio.client.V1ObjectFieldSelector(
                    api_version='v1',
                    field_path='metadata.namespace',
                ),
            ),
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_KUBERNETES_POD_NAME,
            value_from=kubernetes_asyncio.client.V1EnvVarSource(
                field_ref=kubernetes_asyncio.client.V1ObjectFieldSelector(
                    api_version='v1',
                    field_path='metadata.name',
                ),
            ),
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_KUBERNETES_POD_UID,
            value_from=kubernetes_asyncio.client.V1EnvVarSource(
                field_ref=kubernetes_asyncio.client.V1ObjectFieldSelector(
                    api_version='v1',
                    field_path='metadata.uid',
                ),
            ),
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_REBOOT_STORAGE_TYPE,
            value=storage_type.value,
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_REBOOT_FACILITATOR_IMAGE_NAME,
            value=facilitator_image,
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_REBOOT_FLUENT_BIT_IMAGE_NAME,
            value=fluent_bit_image,
        ),
        kubernetes_asyncio.client.V1EnvVar(
            name=ENVVAR_REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME,
            value=wait_for_healthy_image,
        ),
    ]

    await k8s_client.deployments.create_or_update(
        namespace=REBOOT_SYSTEM_NAMESPACE,
        deployment_name='reboot-controller',
        replicas=1,
        # During an update, remove any previous controller before starting a new
        # one. That avoids having multiple controllers thinking they're in
        # charge - at the expense of a brief period where there is no
        # controller.
        #
        # The temporary period without a running controller does not affect the
        # users applications other than potentially introducing a small delay
        # before new deployment updates are made. This scenario is equivalent to
        # if the reboot controller had crashed for other reasons.
        update_strategy=UpdateStrategy.RECREATE,
        service_account_name=CONTROLLER_SERVICE_ACCOUNT,
        containers=[
            Container(
                name='main',
                image_name=controller_image,
                resources=Resources(
                    limits=Resources.Values(
                        memory=REBOOT_CONTROLLER_MEMORY_LIMIT,
                    ),
                    requests=Resources.Values(
                        memory=REBOOT_CONTROLLER_MEMORY_REQUEST,
                    ),
                ),
                env=env,
            ),
        ]
    )

    await k8s_client.deployments.wait_for_started(
        namespace=REBOOT_SYSTEM_NAMESPACE,
        name='reboot-controller',
    )


async def _ensure_custom_resource_definitions(
    k8s_client: AbstractEnhancedKubernetesClient
) -> None:
    """Install reboot custom resource definitions."""
    await k8s_client.custom_resource_definitions.create(ApplicationDeployment)
    await k8s_client.custom_resource_definitions.create(ApplicationConfig)


async def _delete_custom_resource_definitions(
    k8s_client: AbstractEnhancedKubernetesClient
) -> None:
    """Remove reboot custom resource definitions."""
    await k8s_client.custom_resource_definitions.ensure_deleted(
        ApplicationDeployment
    )
    await k8s_client.custom_resource_definitions.ensure_deleted(
        ApplicationConfig
    )


@dataclass(kw_only=True)
class Installation:
    """Represents a running cluster, with enough information about its config
    that it can tear the cluster down when requested. Constructed by setting
    up an installation using `setup()`."""
    config: Config

    @staticmethod
    async def setup_with_kubeconfig(
        config: Config, *, kubeconfig: str
    ) -> 'Installation':
        """Install Reboot in the currently active Kubernetes cluster."""
        k8s_client = await EnhancedKubernetesClient.create_client_from_kubeconfig(
            kubeconfig
        )
        try:
            return await Installation.setup_with_client(
                config, k8s_client=k8s_client
            )
        finally:
            # The way we are using the underlying kubernetes client, we never
            # automatically close the network connection and thus we must do this
            # manually.
            await k8s_client.close()

    @staticmethod
    async def setup_with_context(
        config: Config, *, context: str
    ) -> 'Installation':
        """Install Reboot in the currently active Kubernetes cluster."""
        k8s_client = await EnhancedKubernetesClient.create_client(context)
        try:
            return await Installation.setup_with_client(
                config, k8s_client=k8s_client
            )
        finally:
            # The way we are using the underlying kubernetes client, we never
            # automatically close the network connection and thus we must do this
            # manually.
            await k8s_client.close()

    @staticmethod
    async def setup_with_client(
        config: Config, *, k8s_client: AbstractEnhancedKubernetesClient
    ) -> 'Installation':
        """
        Set up a Reboot installation in the cluster connected to the given
        `k8s_client`.

        Does not take ownership of `k8s_client`; the caller must close that
        client when they're done with it.
        """
        await _ensure_custom_resource_definitions(k8s_client)

        await _apply_rbac(
            k8s_client,
        )

        if config.install_controller:
            if config.controller_image is None:
                raise ValueError(
                    "Must specify `ClusterConfig.controller_image` "
                    "if `ClusterConfig.install_controller=True`"
                )
            if config.facilitator_image is None:
                raise ValueError(
                    "Must specify `ClusterConfig.facilitator_image` "
                    "if `ClusterConfig.install_controller=True`"
                )
            if config.fluent_bit_image is None:
                raise ValueError(
                    "Must specify `ClusterConfig.fluent_bit_image` "
                    "if `ClusterConfig.install_controller=True`"
                )
            if config.wait_for_healthy_image is None:
                raise ValueError(
                    "Must specify `ClusterConfig.wait_for_healthy_image` "
                    "if `ClusterConfig.install_controller=True`"
                )
            await _install_controller(
                k8s_client=k8s_client,
                controller_image=config.controller_image,
                storage_type=config.storage_type,
                facilitator_image=config.facilitator_image,
                fluent_bit_image=config.fluent_bit_image,
                wait_for_healthy_image=config.wait_for_healthy_image,
            )

        return Installation(config=config)

    async def teardown_with_kubeconfig(self, kubeconfig: str) -> None:
        """Remove reboot cluster modifications."""
        k8s_client = await EnhancedKubernetesClient.create_client_from_kubeconfig(
            kubeconfig
        )
        try:
            return await self.teardown_with_client(k8s_client)
        finally:
            # The way we are using the underlying kubernetes client, we never
            # automatically close the network connection and thus we must do this
            # manually.
            await k8s_client.close()

    async def teardown_with_context(self, context: str) -> None:
        """Remove reboot cluster modifications."""
        k8s_client = await EnhancedKubernetesClient.create_client(context)
        try:
            return await self.teardown_with_client(k8s_client)
        finally:
            # The way we are using the underlying kubernetes client, we never
            # automatically close the network connection and thus we must do this
            # manually.
            await k8s_client.close()

    async def teardown_with_client(
        self, k8s_client: AbstractEnhancedKubernetesClient
    ) -> None:
        await _delete_custom_resource_definitions(k8s_client)

        await _teardown_namespaces(
            k8s_client,
        )
