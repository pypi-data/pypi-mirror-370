from rbt.cloud.v1alpha1.istio import (
    virtual_service_pb2,
    virtual_service_spec_pb2,
)
from reboot.controller.istio_custom_object import IstioCustomObject


class VirtualService(IstioCustomObject[virtual_service_pb2.VirtualService]):
    """
    This Python class wraps a generated proto object representing a k8s custom
    object. The CustomObject children knows how to talk to the k8s API to
    instantiate these objects in k8s.

    Class variables:
    group        [optional]: The k8s api group. Default: 'reboot.dev'.
    version      [optional]: The k8s api version name. Default: 'v1'.
    """

    group = "networking.istio.io"
    version = "v1alpha3"  # Matching the Istio version we run.

    Spec = virtual_service_spec_pb2.VirtualService
