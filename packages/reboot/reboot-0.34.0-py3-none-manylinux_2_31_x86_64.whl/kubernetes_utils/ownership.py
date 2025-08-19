from __future__ import annotations

import kubernetes_asyncio
from dataclasses import dataclass
from kubernetes_utils.custom_object import CustomObject


# Each instance is immutable (frozen=True) to prevent accidental/in-place
# modifications.
# Construction must happen through keyword arguments (kw_only) to force us to
# not rely on implicit ordering that is prone to type checking errors.
@dataclass(
    frozen=True,
    kw_only=True,
)
class OwnershipInformation:
    """Dataclass to contain and work with information pertaining to object
    ownership in kubernetes.

    The data contained in this class maps directly to the data fields in
    `kubernetes_asyncio.client.V1OwnerReference`. This class additionally
    provides helper functions for converting between different formats
    and representations.
    """
    kind: str
    api_version: str
    name: str
    namespace: str
    uid: str

    def as_owner_reference(self) -> kubernetes_asyncio.client.V1OwnerReference:
        """Construct the corresponding V1OwnerReference."""
        return kubernetes_asyncio.client.V1OwnerReference(
            api_version=self.api_version,
            kind=self.kind,
            name=self.name,
            uid=self.uid,
            controller=True,
        )

    def add_to_metadata(
        self,
        metadata: kubernetes_asyncio.client.V1ObjectMeta,
    ) -> None:
        """Add self as owner in subjects metadata."""

        # Check that the namespace of owner and subject is the same. This is a
        # hard requirement set by kubernetes. Let's draw attention to it early.
        if self.namespace != metadata.namespace:
            raise ValueError(
                'Differing namespaces for subject and owner: '
                f'{self.namespace} != {metadata.namespace}'
            )

        # Update owner references of metadata. Use temporary as
        # `metadata.owner_references` is an `Optional[list]` that likely is
        # `None`.
        owner_references = metadata.owner_references or []
        owner_references.append(self.as_owner_reference())
        metadata.owner_references = owner_references

    @classmethod
    def from_metadata(
        cls,
        *,
        metadata: kubernetes_asyncio.client.V1ObjectMeta,
        kind: str,
        api_version: str,
    ) -> OwnershipInformation:
        """Create ownership information from metadata object and type
        information."""
        return cls(
            kind=kind,
            api_version=api_version,
            name=metadata.name,
            namespace=metadata.namespace,
            uid=metadata.uid,
        )

    @classmethod
    def from_custom_object(
        cls,
        custom_object: CustomObject,
    ) -> OwnershipInformation:
        """Create ownership information from a custom object."""
        custom_object_type = type(custom_object)
        return cls(
            kind=custom_object_type.get_kind(),
            api_version=custom_object_type.get_api_version(),
            name=custom_object.metadata.name,
            namespace=custom_object.metadata.namespace,
            uid=custom_object.metadata.uid,
        )
