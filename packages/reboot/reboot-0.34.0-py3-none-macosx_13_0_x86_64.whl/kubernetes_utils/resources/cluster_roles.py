import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractClusterRoles:

    async def create(
        self,
        *,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        """Create new ClusterRole."""
        raise NotImplementedError

    async def create_or_update(
        self,
        *,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        """Create ClusterRole if it doesn't already exist, replace it if it
        does."""
        raise NotImplementedError

    async def delete(self, *, name: str) -> None:
        """Delete an existing ClusterRole."""
        raise NotImplementedError


class ClusterRoles(LoggerMixin, AbstractClusterRoles):
    """An implementation of `AbstractClusterRoles` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(
        self,
        *,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        role = kubernetes_asyncio.client.V1ClusterRole(
            metadata=kubernetes_asyncio.client.V1ObjectMeta(name=name),
            rules=rules
        )

        async def retryable_create_role():
            await self._apis.rbac_authz.create_cluster_role(body=role)

        await self._apis.retry_api_call(retryable_create_role)

    async def create_or_update(
        self,
        *,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        try:
            return await self.create(name=name, rules=rules)
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                # ISSUE(1301): these are not true `create_or_update` semantics.
                # However we want to remain consistent with the behavior of
                # `roles.create_or_update()`.
                await self.delete(name=name)
                return await self.create(name=name, rules=rules)
            else:
                raise

    async def delete(
        self,
        *,
        name: str,
    ) -> None:

        async def retryable_delete_role():
            await self._apis.rbac_authz.delete_cluster_role(name=name)

        await self._apis.retry_api_call(retryable_delete_role)
