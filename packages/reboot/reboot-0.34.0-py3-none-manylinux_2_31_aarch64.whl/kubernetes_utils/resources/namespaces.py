import asyncio
import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractNamespaces:

    async def read(
        self, *, name: str
    ) -> kubernetes_asyncio.client.V1Namespace:
        """Read a single namespace. Useful for checking if a namespace
        exists."""
        raise NotImplementedError

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(self) -> list[kubernetes_asyncio.client.V1Namespace]:
        """List all namespaces."""
        raise NotImplementedError

    async def create(self, *, name: str, labels: dict[str, str]) -> None:
        """Create a new namespace."""
        raise NotImplementedError

    async def ensure_created(
        self, *, name: str, labels: dict[str, str]
    ) -> None:
        """Create namespace if it doesn't already exist."""
        raise NotImplementedError

    async def delete(self, *, name: str) -> None:
        """Delete a namespace.
        This method will return as soon as the deletion has been requested. The
        actual deletion might take longer.
        """
        raise NotImplementedError

    async def ensure_deleted(self, *, name: str) -> None:
        """Delete a namespace and wait for it to be deleted."""
        raise NotImplementedError


class Namespaces(LoggerMixin, AbstractNamespaces):
    """An implementation of `AbstractNamespaces` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def read(
        self, *, name: str
    ) -> kubernetes_asyncio.client.V1Namespace:
        return await self._apis.retry_api_call(
            lambda: self._apis.core.read_namespace(name)
        )

    async def list_all(self) -> list[kubernetes_asyncio.client.V1Namespace]:

        return (
            await self._apis.retry_api_call(self._apis.core.list_namespace)
        ).items

    async def create(self, *, name: str, labels: dict[str, str]) -> None:
        namespace = kubernetes_asyncio.client.V1Namespace()
        namespace.metadata = kubernetes_asyncio.client.V1ObjectMeta(
            name=name,
            labels=labels,
        )

        async def retryable_create_namespace():
            await self._apis.core.create_namespace(namespace)

        await self._apis.retry_api_call(retryable_create_namespace)

    async def ensure_created(
        self, *, name: str, labels: dict[str, str]
    ) -> None:
        try:
            return await self.create(name=name, labels=labels)
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                self.logger.debug('Namespace "%s" already exist', name)
            else:
                raise

    async def delete(self, *, name: str) -> None:

        async def retryable_delete_namespace():
            try:
                await self._apis.core.delete_namespace(name)
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # This is fine. The namespace was already deleted.
                    pass
                else:
                    raise

        await self._apis.retry_api_call(retryable_delete_namespace)

    async def ensure_deleted(self, *, name: str) -> None:
        # Request deletion of namespace.
        await self.delete(name=name)

        # Wait for Namespace to be deleted.
        async def retryable_wait_for_delete():
            while True:
                try:
                    await self._apis.core.read_namespace(name=name)
                    await asyncio.sleep(1)
                except kubernetes_asyncio.client.exceptions.ApiException as e:
                    if e.status == 404:
                        self.logger.debug('Namespace %s deleted', name)
                        break
                    else:
                        raise

        await self._apis.retry_api_call(retryable_wait_for_delete)
