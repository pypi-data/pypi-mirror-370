import kubernetes_asyncio
from aiohttp.client_exceptions import ClientConnectorError
from enum import Enum
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.helpers import wait_for_state
from log.log import LoggerMixin


class VolumeBindingMode(Enum):
    """The volume binding mode of a storage class. See:
      https://kubernetes.io/docs/concepts/storage/storage-classes/#volume-binding-mode
    """
    WAIT_FOR_FIRST_CONSUMER = 'WaitForFirstConsumer'
    IMMEDIATE = 'Immediate'


class AbstractStorageClasses:

    async def create_or_update(
        self,
        *,
        name: str,
        provisioner: str,
        volume_binding_mode: VolumeBindingMode,
        allow_volume_expansion: bool,
    ):
        """Create a Kubernetes StorageClass with the given name.

        If a StorageClass with the given name already exists, replaces it with
        the new one."""
        raise NotImplementedError

    async def delete(
        self,
        *,
        name: str,
    ):
        """Delete the storage class with the given name."""
        raise NotImplementedError

    async def wait_for_created(
        self,
        *,
        name: str,
    ) -> None:
        """Wait for the storage class with the given name to be created."""
        raise NotImplementedError


class StorageClasses(LoggerMixin, AbstractStorageClasses):
    """An implementation of `AbstractStorageClasses` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create_or_update(
        self,
        *,
        name: str,
        provisioner: str,
        volume_binding_mode: VolumeBindingMode,
        allow_volume_expansion: bool,
    ):
        metadata = kubernetes_asyncio.client.V1ObjectMeta(name=name)
        storage_class = kubernetes_asyncio.client.V1StorageClass(
            metadata=metadata,
            provisioner=provisioner,
            volume_binding_mode=volume_binding_mode.value,
            allow_volume_expansion=allow_volume_expansion,
        )

        async def retryable_create_or_update_storage_class():
            try:
                await self._apis.storage.create_storage_class(storage_class)
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Conflict':
                    # To update an existing storage class, we need to include
                    # the current metadata.resource_version value.
                    curr_storage_class = await self._apis.storage.read_storage_class(
                        name
                    )
                    storage_class.metadata.resource_version = (
                        curr_storage_class.metadata.resource_version
                    )
                    await self._apis.storage.replace_storage_class(
                        name, storage_class
                    )
                else:
                    raise

        await self._apis.retry_api_call(
            retryable_create_or_update_storage_class
        )

    async def delete(
        self,
        *,
        name: str,
    ):

        async def retryable_delete_storage_class():
            await self._apis.storage.delete_storage_class(name=name)

        await self._apis.retry_api_call(retryable_delete_storage_class)

    async def wait_for_created(
        self,
        *,
        name: str,
    ) -> None:

        async def check_for_storage_class_created():
            response = await self._apis.storage.list_storage_class(
                field_selector=f'metadata.name={name}'
            )
            return len(response.items) > 0

        await wait_for_state(
            check_for_storage_class_created,
            ClientConnectorError,
        )
