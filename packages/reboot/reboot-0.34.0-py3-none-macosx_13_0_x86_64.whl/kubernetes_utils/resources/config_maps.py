import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractConfigMaps:

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        data: dict[str, str],
    ):
        """Construct a ConfigMap with the given data"""
        raise NotImplementedError

    async def delete(self, namespace: str, name: str):
        """Delete the ConfigMap with the given name from the given namespace."""
        raise NotImplementedError


class ConfigMaps(LoggerMixin, AbstractConfigMaps):
    """
    An implementation of `AbstractConfigMaps` that uses the real Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        data: dict[str, str],
    ):

        async def retryable_create_or_update():
            body = kubernetes_asyncio.client.V1ConfigMap(
                metadata=kubernetes_asyncio.client.V1ObjectMeta(
                    namespace=namespace,
                    name=name,
                ),
                data=data,
            )
            try:
                await self._apis.core.create_namespaced_config_map(
                    namespace, body
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Conflict':
                    # The ConfigMap already existed. Update (i.e.: replace) it.
                    await self._apis.core.replace_namespaced_config_map(
                        name, namespace, body
                    )
                else:
                    raise

        await self._apis.retry_api_call(retryable_create_or_update)

    async def delete(self, namespace: str, name: str):

        async def retryable_delete():
            try:
                await self._apis.core.delete_namespaced_config_map(
                    name, namespace
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # The object doesn't exist, so we don't need to delete it.
                    pass
                else:
                    raise e

        await self._apis.retry_api_call(retryable_delete)
