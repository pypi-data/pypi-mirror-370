"""
Tooling to work with Reboot Spaces.
"""
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from reboot.controller.settings import ISTIO_NAMESPACE_LABELS
from reboot.naming import (
    get_namespace_for_space,
    get_service_account_name_for_application,
)
from rebootdev.aio.types import ApplicationId


async def ensure_namespace_for_space(
    k8s_client: AbstractEnhancedKubernetesClient,
    space_id: str,
) -> str:
    """
    Ensure a Kubernetes namespace exists for the given space.

    Returns the name of the Kubernetes namespace.
    """
    namespace = get_namespace_for_space(space_id)
    await k8s_client.namespaces.ensure_created(
        name=namespace,
        labels=ISTIO_NAMESPACE_LABELS,
    )

    return namespace


async def ensure_application_service_account_in_space(
    k8s_client: AbstractEnhancedKubernetesClient,
    space_id: str,
    application_id: ApplicationId,
) -> str:
    """
    Ensure that the given space contains a service account for the given
    application.

    Returns the name of the service account.
    """
    namespace = get_namespace_for_space(space_id)
    service_account_name = get_service_account_name_for_application(
        application_id
    )

    await k8s_client.service_accounts.ensure_created(
        namespace=namespace,
        name=service_account_name,
    )

    return service_account_name
