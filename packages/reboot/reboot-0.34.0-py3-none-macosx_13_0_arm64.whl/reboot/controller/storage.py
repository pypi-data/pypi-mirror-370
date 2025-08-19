import os
from dataclasses import dataclass
from enum import Enum
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.deployments import UpdateStrategy
from kubernetes_utils.resources.persistent_volume_claims import AccessMode
from reboot.controller.settings import ENVVAR_REBOOT_STORAGE_TYPE
from reboot.naming import make_consensus_id
from rebootdev.aio.types import ApplicationId, ConsensusId

LOCAL_STORAGE_CLASS_NAME = "local"
EBS_STORAGE_CLASS_NAME = "ebs-gp3"
EFS_STORAGE_CLASS_NAME = "efs-shared"


class StorageType(Enum):
    LOCAL = 'LOCAL'
    AWS_EBS = 'AWS_EBS'
    AWS_EFS = 'AWS_EFS'


@dataclass
class MountInfo:
    pvc_name: str
    deployment_update_strategy: UpdateStrategy


async def _ensure_single_node_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    name: str,
    size: str,  # E.g. "10Gi".
    storage_class_name: str,
) -> MountInfo:
    await k8s_client.persistent_volume_claims.create_or_update(
        namespace=namespace,
        name=name,
        storage_class_name=storage_class_name,
        storage_request=size,
        # Only a single node will be able to access this PVC at a time.
        access_modes=[AccessMode.READ_WRITE_ONCE],
    )
    return MountInfo(
        pvc_name=name,
        # Currently, Reboot applications can't be replaced in a graceful rolling
        # restart. They must be brought down first, before a replacement can be
        # brought back up. This will cause some downtime, particularly since the
        # old application doesn't terminate instantly.
        #
        # ISSUE(https://github.com/reboot-dev/mono/issues/4110): There are two
        # reasons we don't support rolling restarts:
        # * Because of the access mode we must delete the old pod before
        #   creating the new one, or alternatively we'd have to somehow
        #   ensure that the new pod is started on the same node as the
        #   old one.
        # * Even if we could multi-attach, the application would crash if it
        #   doesn't have the rocksdb lock.
        deployment_update_strategy=UpdateStrategy.RECREATE,
    )


async def _delete_single_node_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    name: str,
) -> None:
    await k8s_client.persistent_volume_claims.delete(
        namespace=namespace,
        name=name,
    )


async def _ensure_local_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    return await _ensure_single_node_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        # NOTE: using the `application_id` as the name of the
        #       PersistentVolumeClaim means multiple consensuses of the
        #       same application will use the same
        #       PersistentVolumeClaim, mirroring the EFS storage type.
        #       This works because in the local case there is only a
        #       single node, so all pods will be able to access the same
        #       PersistentVolumeClaim.
        name=application_id,
        size=size,
        storage_class_name=LOCAL_STORAGE_CLASS_NAME,
    )


async def _delete_local_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
) -> None:
    await _delete_single_node_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        name=application_id,  # Matching `_ensure_...` above.
    )


async def _ensure_ebs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    consensus_id: ConsensusId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    return await _ensure_single_node_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        name=consensus_id,
        size=size,
        storage_class_name=EBS_STORAGE_CLASS_NAME,
    )


async def _delete_ebs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    consensus_id: ConsensusId,
) -> None:
    return await _delete_single_node_persistent_volume_claim(
        k8s_client=k8s_client,
        namespace=namespace,
        name=consensus_id,
    )


async def _ensure_efs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    await k8s_client.persistent_volume_claims.create_or_update(
        namespace=namespace,
        # Each application has one PersistentVolumeClaim that can be mounted by
        # many pods. Since Reboot consensuses create a subdirectory for
        # themselves they can all share the same folder.
        name=application_id,
        storage_class_name=EFS_STORAGE_CLASS_NAME,
        storage_request="1Ki",  # Storage request size is ignored by EFS.
        access_modes=[AccessMode.READ_WRITE_MANY],
    )
    return MountInfo(
        pvc_name=application_id,
        # Currently, Reboot applications can't be replaced in a graceful rolling
        # restart. They must be brought down first, before a replacement can be
        # brought back up. This will cause some downtime, particularly since the
        # old application doesn't terminate instantly.
        #
        # There reason we don't support rolling restarts is that the application
        # will crash if it doesn't have the rocksdb lock.
        #
        # TODO: when the above limitation has been addressed, switch to a
        #       rolling update for lower downtime:
        #         https://github.com/reboot-dev/mono/issues/4110
        deployment_update_strategy=UpdateStrategy.RECREATE,
    )


async def _delete_efs_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
) -> None:
    await k8s_client.persistent_volume_claims.delete(
        namespace=namespace,
        # Each application has one PersistentVolumeClaim that can be mounted by
        # many pods. Since Reboot consensuses create a subdirectory for
        # themselves they can all share the same folder.
        name=application_id,
    )


def _storage_type() -> StorageType:
    storage_type_str = os.environ.get(ENVVAR_REBOOT_STORAGE_TYPE)
    if storage_type_str is None:
        raise ValueError(
            f"Missing required environment variable '{ENVVAR_REBOOT_STORAGE_TYPE}'"
        )

    try:
        return StorageType[storage_type_str]
    except KeyError:
        raise ValueError(
            f"Invalid value '{storage_type_str}' for environment variable "
            f"'{ENVVAR_REBOOT_STORAGE_TYPE}'; supported values are: "
            f"{', '.join([storage_type.value for storage_type in StorageType])}"
        )


async def ensure_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    consensus_id: ConsensusId,
    size: str,  # E.g. "10Gi".
) -> MountInfo:
    storage_type = _storage_type()
    match storage_type:
        case StorageType.LOCAL:
            return await _ensure_local_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                application_id=application_id,
                size=size,
            )
        case StorageType.AWS_EBS:
            return await _ensure_ebs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                consensus_id=consensus_id,
                size=size,
            )
        case StorageType.AWS_EFS:
            # NOTE: keep this logic in sync with the "local" case above,
            #       to ensure test coverage for this usage pattern.
            return await _ensure_efs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                application_id=application_id,
                size=size,
            )
        case _:
            raise AssertionError(f"Unhandled storage type '{storage_type}'")


async def maybe_delete_persistent_volume_claim(
    k8s_client: AbstractEnhancedKubernetesClient,
    namespace: str,
    application_id: ApplicationId,
    consensus_id: ConsensusId,
):
    storage_type = _storage_type()
    match storage_type:
        case StorageType.LOCAL:
            if consensus_id != make_consensus_id(application_id, 0):
                # This is not the lowest consensus ID for the
                # application; do NOT delete the local volume claim.
                #
                # The local volume is shared across all consensuses of
                # the application; just as with EFS. We delete it only
                # if the lowest consensus is being deleted, since that
                # implies that the whole application is being deleted.
                return

            await _delete_local_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                application_id=application_id,
            )
            return

        case StorageType.AWS_EBS:
            await _delete_ebs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                consensus_id=consensus_id,
            )
            return

        case StorageType.AWS_EFS:
            # NOTE: keep this logic in sync with the "local" case above,
            #       to ensure test coverage for this usage pattern.
            if consensus_id != make_consensus_id(application_id, 0):
                # This is not the lowest consensus ID for the
                # application; do NOT delete the EFS volume claim.
                #
                # The EFS volume is shared across all consensuses of the
                # application; we delete it only if the lowest consensus
                # is being deleted, since that implies that the whole
                # application is being deleted.
                return

            await _delete_efs_persistent_volume_claim(
                k8s_client=k8s_client,
                namespace=namespace,
                application_id=application_id,
            )
            return
        case _:
            raise AssertionError(f"Unhandled storage type '{storage_type}'")
