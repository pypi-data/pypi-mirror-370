import kubernetes_asyncio
from kubernetes_utils.custom_object import CustomObject
from typing import Optional, TypeVar

T = TypeVar('T')


class IstioCustomObject(CustomObject[T]):
    """
    This Python class wraps a k8s custom object with the appropriate
    configuration for Istio objects which must use "camelCase" during
    serialization/deserialization.
    """

    def __init__(
        self,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta] = None,
        **kwargs,
    ):
        super().__init__(
            metadata=metadata,
            # Istio defines its fields in "camelCase", so we must convert our
            # "snake_case" proto field names to that shape.
            preserve_proto_field_names=False,
            **kwargs,
        )
