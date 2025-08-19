from kubernetes_utils.custom_object import CustomObject
from typing import ClassVar, TypeVar

T = TypeVar('T')


class RebootCustomObject(CustomObject[T]):
    """
    This Python class wraps a k8s custom object with the appropriate
    configuration for Reboot objects.
    """

    group: ClassVar[str] = 'reboot.dev'
    version: ClassVar[str] = 'v1'
