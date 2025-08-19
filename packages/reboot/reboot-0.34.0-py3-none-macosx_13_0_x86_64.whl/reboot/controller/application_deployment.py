import kubernetes_asyncio.client
from rbt.cloud.v1alpha1 import application_deployment_pb2
from reboot.controller.reboot_custom_object import RebootCustomObject
from reboot.naming import ApplicationId
from typing import Optional, TypeAlias


class ApplicationDeployment(
    RebootCustomObject[application_deployment_pb2.ApplicationDeployment]
):
    """
    This Python class wraps a generated proto object representing a Reboot
    custom object (i.e., not a K8s or Istio specific custom object). The
    CustomObject children knows how to talk to the k8s API to instantiate these
    objects in k8s.
    """

    Spec: TypeAlias = application_deployment_pb2.ApplicationDeployment.Spec
    Status: TypeAlias = application_deployment_pb2.ApplicationDeployment.Status

    @classmethod
    def create(
        cls,
        application_id: ApplicationId,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta],
        spec: application_deployment_pb2.ApplicationDeployment.Spec,
        status: Optional[
            application_deployment_pb2.ApplicationDeployment.Status] = None,
    ) -> 'ApplicationDeployment':
        metadata = metadata or kubernetes_asyncio.client.V1ObjectMeta()

        # Invariant: the ApplicationDeployment's `metadata.name` will be the
        #            application ID. Even when we're not running on Kubernetes!
        assert metadata.name is None or metadata.name == application_id
        metadata.name = application_id

        return cls(
            metadata=metadata,
            spec=spec,
            status=status,
        )

    def application_id(self) -> ApplicationId:
        if self.metadata.name is None:
            raise ValueError(
                "Cannot determine application ID: ApplicationDeployment has no "
                "'metadata.name'"
            )
        return self.metadata.name
