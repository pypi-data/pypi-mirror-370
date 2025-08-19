import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractRoleBindings:

    async def create(
        self,
        *,
        namespace: str,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        """Create new role binding."""
        raise NotImplementedError

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        """Create role binding if it doesn't already exist, replace it if it
        does."""
        raise NotImplementedError

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ):
        """Delete an existing role binding."""
        raise NotImplementedError


class RoleBindings(LoggerMixin, AbstractRoleBindings):
    """An implementation of `AbstractRoleBindings` that uses the real
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
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        role_binding = kubernetes_asyncio.client.V1RoleBinding(
            api_version='rbac.authorization.k8s.io/v1',
            kind='RoleBinding',
            metadata=kubernetes_asyncio.client.V1ObjectMeta(name=name),
            role_ref=kubernetes_asyncio.client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='Role',
                name=role_name,
            ),
            subjects=subjects,
        )

        async def retryable_create_role_binding():
            await self._apis.rbac_authz.create_namespaced_role_binding(
                namespace=namespace, body=role_binding
            )

        await self._apis.retry_api_call(retryable_create_role_binding)

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        role_name: str,
        subjects: list[kubernetes_asyncio.client.RbacV1Subject],
    ):
        try:
            return await self.create(
                namespace=namespace,
                name=name,
                role_name=role_name,
                subjects=subjects,
            )
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Conflict':
                await self.delete(namespace=namespace, name=name)
                return await self.create(
                    namespace=namespace,
                    name=name,
                    role_name=role_name,
                    subjects=subjects,
                )
            else:
                raise

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ):

        async def retryable_delete_role_binding():
            await self._apis.rbac_authz.delete_namespaced_role_binding(
                name=name, namespace=namespace
            )

        await self._apis.retry_api_call(retryable_delete_role_binding)
