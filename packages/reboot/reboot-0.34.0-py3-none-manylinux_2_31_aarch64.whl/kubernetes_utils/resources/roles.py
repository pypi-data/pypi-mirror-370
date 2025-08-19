import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractRoles:

    async def create(
        self,
        *,
        namespace: str,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        """Create new role."""
        raise NotImplementedError

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        """Create role if it doesn't already exist, replace it if it does."""
        raise NotImplementedError

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ) -> None:
        """Delete an existing role."""
        raise NotImplementedError


class Roles(LoggerMixin, AbstractRoles):
    """An implementation of `AbstractRoles` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(
        self,
        *,
        namespace: str,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        role = kubernetes_asyncio.client.V1Role(
            api_version='rbac.authorization.k8s.io/v1',
            kind='Role',
            metadata=kubernetes_asyncio.client.V1ObjectMeta(name=name),
            rules=rules,
        )

        async def retryable_create_role():
            await self._apis.rbac_authz.create_namespaced_role(
                namespace=namespace, body=role
            )

        await self._apis.retry_api_call(retryable_create_role)

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        rules: list[kubernetes_asyncio.client.V1PolicyRule],
    ) -> None:
        try:
            return await self.create(
                namespace=namespace, name=name, rules=rules
            )
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                # ISSUE(1301): these are not true `create_or_update` semantics.
                await self.delete(namespace=namespace, name=name)
                return await self.create(
                    namespace=namespace, name=name, rules=rules
                )
            else:
                raise

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ) -> None:

        async def retryable_delete_role():
            await self._apis.rbac_authz.delete_namespaced_role(
                namespace=namespace, name=name
            )

        await self._apis.retry_api_call(retryable_delete_role)
