import kubernetes_asyncio
from aiohttp.client_exceptions import ClientConnectorError
from dataclasses import dataclass
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.helpers import wait_for_state
from kubernetes_utils.ownership import OwnershipInformation
from kubernetes_utils.resources.deployments import Deployments
from log.log import LoggerMixin
from typing import Optional


@dataclass(kw_only=True, frozen=True)
class Port:
    port: int
    name: str


class AbstractServices:

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        ports: list[Port],
        deployment_label: Optional[str] = None,
        owner: Optional[OwnershipInformation] = None,
    ):
        """Create a Kubernetes Service with the given name. If a
        `deployment_label` is given, traffic to the `Service` will be routed to
        pods deployed (probably via a `Deployment`) with that label. If no such
        label is given, the service will be created without a selector.

        If a service with the given name already exists, replaces it with the
        new one."""
        raise NotImplementedError

    async def wait_for_created(self, namespace: str, name: str) -> None:
        """Waits until the service with the given name has been created."""
        raise NotImplementedError

    async def get(
        self,
        *,  # Make the rest of the arguments be keywords.
        namespace: str,
        name: str
    ) -> kubernetes_asyncio.client.V1Service:
        """Fetch the service with the given name from the given namespace."""
        raise NotImplementedError

    async def delete(self, namespace: str, name: str):
        """Delete the service with the given name from the given namespace."""
        raise NotImplementedError


class Services(LoggerMixin, AbstractServices):
    """An implementation of `AbstractServices` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        ports: list[Port],
        deployment_label: Optional[str] = None,
        owner: Optional[OwnershipInformation] = None,
    ):
        service_metadata = kubernetes_asyncio.client.V1ObjectMeta(
            namespace=namespace,
            name=name,
        )
        if owner is not None:
            # Add the owner information to the metadata in place.
            owner.add_to_metadata(service_metadata)

        service_spec = kubernetes_asyncio.client.V1ServiceSpec(
            ports=[
                kubernetes_asyncio.client.V1ServicePort(
                    port=port.port, name=port.name
                ) for port in ports
            ],
            selector=(
                {
                    Deployments.DEPLOYMENT_NAME_LABEL: deployment_label
                } if deployment_label is not None else None
            ),
        )

        async def retryable_create_or_update_service():
            body = kubernetes_asyncio.client.V1Service(
                metadata=service_metadata,
                spec=service_spec,
            )
            try:
                await self._apis.core.create_namespaced_service(
                    namespace=namespace,
                    body=body,
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Conflict':
                    # To update an existing service, we need to include the
                    # current metadata.resource_version value.
                    curr_service = await self._apis.core.read_namespaced_service(
                        namespace=namespace,
                        name=name,
                    )
                    body.metadata.resource_version = curr_service.metadata.resource_version
                    await self._apis.core.replace_namespaced_service(
                        namespace=namespace,
                        name=name,
                        body=body,
                    )
                else:
                    raise

        await self._apis.retry_api_call(retryable_create_or_update_service)

    async def wait_for_created(self, namespace: str, name: str) -> None:

        async def check_service_created():
            try:
                await self._apis.core.read_namespaced_service(
                    namespace=namespace,
                    name=name,
                )
                # We fetched the object successfully.
                return True
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if (e.reason == 'Not Found'):
                    # We failed to find the object, so we'll keep waiting.
                    return False
                raise e

        await wait_for_state(check_service_created, ClientConnectorError)

    async def get(
        self,
        *,  # Make the rest of the arguments be keywords.
        namespace: str,
        name: str
    ) -> kubernetes_asyncio.client.V1Service:

        async def retryable_get_service(
        ) -> kubernetes_asyncio.client.V1Service:
            return await self._apis.core.read_namespaced_service(
                namespace=namespace, name=name
            )

        return await self._apis.retry_api_call(retryable_get_service)

    async def delete(self, namespace: str, name: str):

        async def retryable_delete_service():
            await self._apis.core.delete_namespaced_service(name, namespace)

        await self._apis.retry_api_call(retryable_delete_service)
