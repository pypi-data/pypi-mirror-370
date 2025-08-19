from rbt.cloud.v1alpha1.istio import gateway_pb2, gateway_spec_pb2
from reboot.controller.istio_custom_object import IstioCustomObject


class Gateway(IstioCustomObject[gateway_pb2.Gateway]):
    """
    This Python class wraps a generated proto object representing an
    Istio custom object. The CustomObject children know how to talk to
    the k8s API to instantiate these objects in k8s.

    Class variables:
    group        [optional]: The k8s api group. Default: 'reboot.dev'.
    version      [optional]: The k8s api version name. Default: 'v1'.
    """

    group = "networking.istio.io"
    version = "v1alpha3"  # Matching the Istio version we run.

    Spec = gateway_spec_pb2.Gateway
