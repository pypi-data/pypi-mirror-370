import kubernetes_asyncio
from enum import Enum
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.ownership import OwnershipInformation
from log.log import LoggerMixin
from typing import Optional


class AccessMode(Enum):
    """The access mode of a persistent volume claim. See:
      https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes
    """
    READ_WRITE_ONCE = 'ReadWriteOnce'
    READ_ONLY_MANY = 'ReadOnlyMany'
    READ_WRITE_MANY = 'ReadWriteMany'
    READ_WRITE_ONCE_POD = 'ReadWriteOncePod'


class AbstractPersistentVolumeClaims:

    async def create_or_update(
        self,
        *,
        namespace: str,
        name: str,
        storage_class_name: str,
        storage_request: str,  # e.g. "1Gi"
        access_modes: list[AccessMode],
        owner: Optional[OwnershipInformation] = None,
    ):
        """Create a Kubernetes PersistentVolumeClaim with the given name.

        If a persistent volume claim with the given name already exists,
        replaces it with the new one."""
        raise NotImplementedError

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ):
        """Delete the persistent volume claim with the given name from the given
        namespace."""
        raise NotImplementedError


class PersistentVolumeClaims(LoggerMixin, AbstractPersistentVolumeClaims):
    """An implementation of `AbstractPersistentVolumeClaims` that uses the real
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
        storage_class_name: str,
        storage_request: str,
        access_modes: list[AccessMode],
        owner: Optional[OwnershipInformation] = None,
    ):
        metadata = kubernetes_asyncio.client.V1ObjectMeta(
            namespace=namespace,
            name=name,
        )
        if owner is not None:
            # Add the owner information to the metadata in place.
            owner.add_to_metadata(metadata)

        persistent_volume_claim = kubernetes_asyncio.client.V1PersistentVolumeClaim(
            metadata=metadata,
            spec=kubernetes_asyncio.client.V1PersistentVolumeClaimSpec(
                storage_class_name=storage_class_name,
                resources=kubernetes_asyncio.client.V1ResourceRequirements(
                    requests={'storage': storage_request},
                ),
                access_modes=[
                    access_mode.value for access_mode in access_modes
                ],
            )
        )

        async def retryable_create_or_update_persistent_volume_claim():
            try:
                await self._apis.core.create_namespaced_persistent_volume_claim(
                    namespace=namespace,
                    body=persistent_volume_claim,
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Conflict':
                    # To update an existing persistent volume claim, we need to include the
                    # current metadata.resource_version value.
                    curr_persistent_volume_claim = (
                        await self._apis.core.
                        read_namespaced_persistent_volume_claim(
                            namespace=namespace,
                            name=name,
                        )
                    )
                    persistent_volume_claim.metadata.resource_version = (
                        curr_persistent_volume_claim.metadata.resource_version
                    )
                    # We must also maintain the volume name, since one may have
                    # been bound since the service was created. Note that the
                    # claim's volume name refers to the name of the volume
                    # according to Kubernetes (a randomly generated string for
                    # dynamically bound volumes), which is unrelated to the name
                    # of that volume according to the Pod that consumes it.
                    persistent_volume_claim.spec.volume_name = (
                        curr_persistent_volume_claim.spec.volume_name
                    )
                    await self._apis.core.replace_namespaced_persistent_volume_claim(
                        namespace=namespace,
                        name=name,
                        body=persistent_volume_claim,
                    )

                else:
                    raise

        await self._apis.retry_api_call(
            retryable_create_or_update_persistent_volume_claim
        )

    async def delete(
        self,
        *,
        namespace: str,
        name: str,
    ):

        async def retryable_delete_persistent_volume_claim():
            try:
                await self._apis.core.delete_namespaced_persistent_volume_claim(
                    namespace=namespace,
                    name=name,
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # The object doesn't exist, so we don't need to delete it.
                    pass
                else:
                    raise e

        await self._apis.retry_api_call(
            retryable_delete_persistent_volume_claim
        )
