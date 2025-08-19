import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractClusterRoleBindings:

    async def create(
        self,
        *,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        """Create new ClusterRoleBinding."""
        raise NotImplementedError

    async def create_or_update(
        self,
        *,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        """Create ClusterRoleBinding if it doesn't already exist, replace it if
        it does."""
        raise NotImplementedError

    async def delete(
        self,
        *,
        name: str,
    ):
        """Delete an existing ClusterRoleBinding."""
        raise NotImplementedError


class ClusterRoleBindings(LoggerMixin, AbstractClusterRoleBindings):
    """An implementation of `AbstractClusterRoleBindings` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(
        self,
        *,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        role_binding = kubernetes_asyncio.client.V1ClusterRoleBinding(
            metadata=kubernetes_asyncio.client.V1ObjectMeta(name=name),
            role_ref=kubernetes_asyncio.client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='ClusterRole',
                name=role_name,
            ),
            subjects=subjects,
        )

        async def retryable_create_role_binding():
            await self._apis.rbac_authz.create_cluster_role_binding(
                body=role_binding
            )

        await self._apis.retry_api_call(retryable_create_role_binding)

    async def create_or_update(
        self,
        *,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        try:
            return await self.create(
                name=name, role_name=role_name, subjects=subjects
            )
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                # ISSUE(1301): these are not true `create_or_update` semantics.
                # However we want to remain consistent with the behavior of
                # `role_bindings.create_or_update()`.
                await self.delete(name=name)
                return await self.create(
                    name=name, role_name=role_name, subjects=subjects
                )
            else:
                raise

    async def delete(
        self,
        *,
        name: str,
    ):

        async def retryable_delete_role_binding():
            await self._apis.rbac_authz.delete_cluster_role_binding(name=name)

        await self._apis.retry_api_call(retryable_delete_role_binding)
