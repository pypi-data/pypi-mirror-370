import base64
from collections import defaultdict
from kubernetes_asyncio.client import V1ObjectMeta, V1Secret
from kubernetes_asyncio.client.exceptions import ApiException
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractSecrets:

    async def _create(self, *, namespace: str, body: V1Secret) -> None:
        """Write a non-existing secret."""
        raise NotImplementedError

    async def _replace(
        self, *, namespace: str, name: str, body: V1Secret
    ) -> None:
        """Overwrite an existing secret."""
        raise NotImplementedError

    async def write(self, *, namespace: str, name: str, data: bytes) -> None:
        secret = V1Secret(
            data={name: base64.b64encode(data).decode()},
            metadata=V1ObjectMeta(name=name)
        )
        # NOTE: `replace` doesn't work if the secret doesn't exist yet, and `create` doesn't
        # work if the secret does exist.
        # TODO: Consider whether we should match `k8s`'s semantics and split into `create` vs `update`.
        try:
            await self._create(
                namespace=namespace,
                body=secret,
            )

            return
        except ApiException as e:
            if e.reason != 'Conflict':
                raise e
            # Else, the resource already exists: fall through to try a `replace` instead.

        await self._replace(
            namespace=namespace,
            name=name,
            body=secret,
        )

    async def read(self, *, namespace: str, name: str) -> bytes:
        """Read an existing secret."""
        raise NotImplementedError

    async def delete(self, *, namespace: str, name: str) -> None:
        """Delete an existing secret."""
        raise NotImplementedError


class InMemorySecrets(AbstractSecrets):
    """An in-memory implementation of `AbstractSecrets`."""

    secrets: dict[str, dict[str, bytes]] = defaultdict(dict)

    async def _create(self, *, namespace: str, body: V1Secret) -> None:
        if any(key in self.secrets[namespace] for key in body.data.keys()):
            # Already exists.
            raise ApiException(status=409, reason='Conflict')
        assert all(isinstance(data, str) for data in body.data.values())
        self.secrets[namespace].update(body.data)

    async def _replace(
        self, *, namespace: str, name: str, body: V1Secret
    ) -> None:
        assert name in body.data
        assert isinstance(body.data[name], str)
        self.secrets[namespace].update(body.data)

    async def read(self, *, namespace: str, name: str) -> bytes:
        data = self.secrets.get(namespace, {}).get(name)
        if data is None:
            raise NotFoundException(f"No secret was stored for {name=}")
        return base64.b64decode(data)

    async def delete(self, *, namespace: str, name: str) -> None:
        self.secrets[namespace].pop(name, None)


class Secrets(LoggerMixin, AbstractSecrets):
    """An implementation of `AbstractSecrets` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def _create(self, *, namespace: str, body: V1Secret) -> None:

        async def retryable() -> None:
            await self._apis.core.create_namespaced_secret(
                namespace=namespace, body=body
            )

        return await self._apis.retry_api_call(retryable)

    async def _replace(
        self, *, namespace: str, name: str, body: V1Secret
    ) -> None:

        async def retryable() -> None:
            await self._apis.core.replace_namespaced_secret(
                name=name, namespace=namespace, body=body
            )

        return await self._apis.retry_api_call(retryable)

    async def read(self, *, namespace: str, name: str) -> bytes:

        async def retryable() -> V1Secret:
            return await self._apis.core.read_namespaced_secret(
                name, namespace
            )

        try:
            v1_secret = await self._apis.retry_api_call(retryable)
        except ApiException as e:
            if e.reason != 'Not Found':
                raise e
            raise NotFoundException(f"No secret was stored for {name=}")
        return base64.b64decode(v1_secret.data[name])

    async def delete(self, *, namespace: str, name: str) -> None:

        async def retryable() -> None:
            await self._apis.core.delete_namespaced_secret(name, namespace)

        return await self._apis.retry_api_call(retryable)


class NotFoundException(Exception):
    pass
