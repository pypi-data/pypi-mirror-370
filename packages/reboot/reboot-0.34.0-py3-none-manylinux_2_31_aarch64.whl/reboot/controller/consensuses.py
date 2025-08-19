from dataclasses import dataclass, field
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from rbt.v1alpha1 import placement_planner_pb2, sidecar_pb2
from rebootdev.aio.types import ApplicationId, RevisionNumber, ServiceName
from typing import Optional


@dataclass(kw_only=True)
class Consensus:
    """
    Data structure used internally in the Controller to represent a Consensus.

    This is separate from `placement_planner_pb2.Consensus` because not all of
    these fields need to be shared outside the controller.
    """
    # The id of the Consensus.
    id: str

    # The id of the application that the Consensus is associated with.
    application_id: ApplicationId

    # List of service names that are served with the Consensus.
    service_names: list[ServiceName] = field(default_factory=list)

    # Shards owned by this Consensus.
    shards: list[sidecar_pb2.ShardInfo]

    # The name of the container image that the Consensus is associated with.
    # This is currently only relevant when running on Kubernetes.
    container_image_name: Optional[str] = None

    # The Kubernetes namespace that the Consensus is associated with.
    # When running on Kubernetes this must be set to a non-empty string.
    namespace: Optional[str] = None

    # The file descriptor set of the Services that the Consensus is associated
    # with.
    file_descriptor_set: Optional[FileDescriptorSet] = None

    # This might become `addresses: Optional[
    #   list[placement_planner_pb2.ConsensusAddresses]]` in the future when we
    # support replicated consensuses.
    address: Optional[placement_planner_pb2.Consensus.Address] = None

    # The current revision number of the application running in this consensus.
    revision_number: RevisionNumber = RevisionNumber(0)
