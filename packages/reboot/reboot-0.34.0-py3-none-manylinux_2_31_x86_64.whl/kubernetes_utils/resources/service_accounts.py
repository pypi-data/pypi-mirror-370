import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractServiceAccounts:

    async def create(
        self,
        namespace: str,
        name: str,
    ) -> None:
        """Create a new service account."""
        raise NotImplementedError

    async def delete(
        self,
        namespace: str,
        name: str,
    ) -> None:
        """Delete an existing service account."""
        raise NotImplementedError

    async def ensure_created(
        self,
        namespace: str,
        name: str,
    ) -> None:
        """Create service account if it doesn't already exist."""
        raise NotImplementedError


class ServiceAccounts(LoggerMixin, AbstractServiceAccounts):
    """An implementation of `AbstractServiceAccounts` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(
        self,
        namespace: str,
        name: str,
    ) -> None:

        service_account = kubernetes_asyncio.client.V1ServiceAccount()
        service_account.metadata = kubernetes_asyncio.client.V1ObjectMeta(
            name=name, namespace=namespace
        )

        async def retryable_create_service_account():
            await self._apis.core.create_namespaced_service_account(
                namespace=namespace, body=service_account
            )

        await self._apis.retry_api_call(retryable_create_service_account)

    async def delete(
        self,
        namespace: str,
        name: str,
    ) -> None:

        async def retryable_delete_service_account():
            await self._apis.core.delete_namespaced_service_account(
                name=name,
                namespace=namespace,
            )

        await self._apis.retry_api_call(retryable_delete_service_account)

    async def ensure_created(
        self,
        namespace: str,
        name: str,
    ) -> None:
        try:
            await self.create(namespace, name)
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                # If a service account with this name already exists, great!
                pass
            else:
                raise
