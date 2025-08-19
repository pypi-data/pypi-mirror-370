import kubernetes_asyncio.client
from rbt.v1alpha1 import application_config_pb2
from reboot.controller.reboot_custom_object import RebootCustomObject
from reboot.naming import ApplicationId
from rebootdev.aio.servicers import Routable
from rebootdev.aio.types import ServiceName
from rebootdev.helpers import generate_proto_descriptor_set
from typing import Optional, Sequence


class ApplicationConfig(
    RebootCustomObject[application_config_pb2.ApplicationConfig]
):
    """
    This Python class wraps a generated proto object representing a Reboot
    custom object (i.e., not a K8s or Istio specific custom object). The
    CustomObject children knows how to talk to the k8s API to instantiate these
    objects in k8s.
    """

    Spec = application_config_pb2.ApplicationConfig.Spec

    @classmethod
    def create(
        cls,
        application_id: ApplicationId,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta],
        spec: application_config_pb2.ApplicationConfig.Spec,
    ) -> 'ApplicationConfig':
        metadata = metadata or kubernetes_asyncio.client.V1ObjectMeta()

        # Invariant: the ApplicationConfig's `metadata.name` will be the
        #            application ID. Even when we're not running on Kubernetes!
        assert metadata.name is None or metadata.name == application_id
        metadata.name = application_id

        return cls(
            metadata=metadata,
            spec=spec,
        )

    def application_id(self) -> ApplicationId:
        if self.metadata.name is None:
            raise ValueError(
                "Cannot determine application ID: ApplicationConfig has no "
                "'metadata.name'"
            )
        return self.metadata.name

    def __str__(self) -> str:
        return f"ApplicationConfig({self.spec})"

    def __repr__(self) -> str:
        return f"ApplicationConfig({self.spec})"


def application_config_spec_from_routables(
    routables: Sequence[Routable], consensuses: Optional[int]
):
    file_descriptor_set = generate_proto_descriptor_set(
        routables=list(routables)
    )

    all_service_names: list[ServiceName] = []
    legacy_grpc_service_full_names: list[ServiceName] = []
    states: list[application_config_pb2.ApplicationConfig.Spec.State] = []
    for r in routables:
        all_service_names.extend(r.service_names())

        if r.state_type_name() is None:
            # This routable isn't associated with a state type. That means
            # it's a legacy gRPC servicer.
            assert len(r.service_names()) == 1
            legacy_grpc_service_full_names.extend(r.service_names())
            continue

        states.append(
            application_config_pb2.ApplicationConfig.Spec.State(
                state_type_full_name=r.state_type_name(),
                service_full_names=r.service_names(),
            )
        )

    return ApplicationConfig.Spec(
        file_descriptor_set=file_descriptor_set.SerializeToString(),
        service_names=all_service_names,
        legacy_grpc_service_full_names=legacy_grpc_service_full_names,
        states=states,
        consensuses=consensuses,
    )
