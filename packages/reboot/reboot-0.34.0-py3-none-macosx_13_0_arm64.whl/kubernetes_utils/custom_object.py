from __future__ import annotations

import google.protobuf
import kubernetes_asyncio
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message_factory import GetMessageClass
from kubernetes_utils.helpers import (
    get_kubernetes_plural,
    metadata_from_dict,
    native_object_to_dict,
)
from typing import Any, ClassVar, Generic, Optional, TypeVar, cast, get_args

CustomObjectT = TypeVar('CustomObjectT', bound='CustomObject')
ProtoMessageT = TypeVar('ProtoMessageT', bound=google.protobuf.message.Message)


def _delete_none_values(obj: dict) -> dict:
    """Delete None values recursively from obj."""
    for key, value in list(obj.items()):
        if isinstance(value, dict):
            _delete_none_values(value)
        elif value is None:
            del obj[key]

    return obj


def _get_message_schema(
    *,
    message_type: type[google.protobuf.message.Message],
    # Private variables passed on recursion.
    _known_types: Optional[dict[
        type, Optional[kubernetes_asyncio.client.V1JSONSchemaProps]]] = None,
) -> kubernetes_asyncio.client.V1JSONSchemaProps:
    """Recursively create the Kubernetes schema definition corresponding to a
    proto message type.

    For the recursion the function uses two private variables that should not be
    passed by the initial caller.
    """

    # Enforce input type.
    assert issubclass(
        message_type,
        google.protobuf.message.Message,
    ), type(message_type)

    # The `_known_types` dict, maps a (Python) proto message type to an
    # `Optional` schema definition. The `Optional` might seem surprising but is
    # useful in for recursion control. See (2) below.
    #
    # We use memoization for two things:
    #  1) As optimization, in case we have already computed the schema for a
    #     message type; but more importantly
    #  2) Recursion control. Proto messages supports recursive proto message
    #     definitions. Kubernetes does not. We thus need a mechanism to detect
    #     recursive/cyclical message definitions as deal with these. We'll use
    #     the memoization for this too.
    #
    # If a Python message type has a value (not None) in the dict, we have
    # already calculated the Kubernetes representation for this message type and
    # can reuse it.
    #
    # If a Python message type has a value in the dict and the value is None, it
    # means that we are currently in the process of calculating the kubernetes
    # representation.
    #
    # Considering the simple example:
    #   message M {
    #     string value = 1;
    #   }
    #
    # At first M is not in the dictionary. We update the dictionary with {M:
    # None} as we begin processing the message definition. When we have
    # calculated the Kubernetes representation we again update the known types
    # map; this time with the schema definition {M: V1JSONSchemaProps(...)}.
    #
    # We can use the None value to detect cycles. Consider this example:
    #
    #   message A {
    #     B b = 1;
    #   }
    #   message B {
    #     A a = 1;
    #   }
    #
    # Cycle detection happens as:
    # * Message A is unknown, update dict with {A: None}. Try to calculate
    #   representation of A.
    # * Message A contains Message B.
    # * Message B is unknown, update dict with {B: None} (i.e., known types are
    #   now {A: None, B: None}). Try to calculate representation of B.
    # * Message B contains Message A.
    # * Message B is in the dict with value None! Cycle detected!

    _known_types = _known_types or {}
    assert _known_types is not None

    try:
        # Try to get schema from memoization.
        message_schema_or_none = _known_types[message_type]

        if message_schema_or_none is not None:
            # Returned memoized schema.
            return message_schema_or_none

        # We do not have a memoized schema for this message type, but we have a
        # `None` entry in the dict.
        # This implies that there is a cycle as exemplified above; the message
        # definition depends on itself, either directly or through intermediate
        # message types.
        #
        # This recursive nature would lead to an infinitely big schema
        # definition and we have to truncate it. We know that message is an
        # `object`, so let's return a schema for a not fully defined `object`.
        #
        # The caller will update the `_known_types` dict.`
        return kubernetes_asyncio.client.V1JSONSchemaProps(
            type='object', x_kubernetes_preserve_unknown_fields=True
        )
    except KeyError:
        # This is the first time we encounter this message type! Let's get to
        # work!
        # Before we start, let's mark this message type in the memoization so we
        # will notice it in case of recursion.
        _known_types[message_type] = None

    def get_kubernetes_type_label(
        field: google.protobuf.descriptor.FieldDescriptor
    ) -> str:
        """Helper to translate from `FieldDescriptor.TYPE_` to Kubernetes object
        type.

        Proto and Kubernetes do not agree on what to call types. We need a way
        of translating from a proto field (descriptor) to a type label
        understood by Kubernetes schema definition.
        """
        # Relevant, though limited, documentation:
        # https://googleapis.dev/python/protobuf/latest/google/protobuf/descriptor.html#google.protobuf.descriptor.FieldDescriptor.TYPE_BOOL
        # https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.0.md#dataTypes

        # Enforce input type before we get started.
        assert isinstance(
            field,
            google.protobuf.descriptor.FieldDescriptor,
        ), type(field)

        # Attempt to map the proto field type to a Kubernetes supported type.
        field_type = field.type
        if field_type in [field.TYPE_STRING, field.TYPE_BYTES]:
            return 'string'
        elif field_type in [field.TYPE_DOUBLE, field.TYPE_FLOAT]:
            return 'number'
        elif field_type in [
            field.TYPE_FIXED32,
            field.TYPE_FIXED64,
            field.TYPE_SFIXED32,
            field.TYPE_SFIXED64,
        ]:
            return 'integer'
        elif field_type in [
            field.TYPE_INT32,
            field.TYPE_INT64,
            field.TYPE_UINT32,
            field.TYPE_UINT64,
            field.TYPE_SINT32,
            field.TYPE_SINT64,
        ]:
            return 'integer'
        elif field_type in [field.TYPE_ENUM]:
            # TODO: In the future if we have use of this, we could consider if
            # `object` or `string` are better representations for enums in
            # Kubernetes.
            return 'integer'
        elif field_type in [field.TYPE_BOOL]:
            return 'boolean'
        elif field_type in [field.TYPE_MESSAGE]:
            return 'object'
        else:
            raise TypeError(
                f'Missing Kubernetes type for {message_type.__name__}.{field.name} (TYPE == {field_type})'
            )

    def get_python_type(
        message_descriptor: google.protobuf.descriptor.Descriptor
    ) -> type[google.protobuf.descriptor.Message]:
        """Get a Python class that matches the message descriptor."""
        # Check the input.
        assert isinstance(
            message_descriptor,
            google.protobuf.descriptor.Descriptor,
        ), type(message_descriptor)

        # Get a (new) Python class for the message descriptor. Per
        # `GetMessageClass` docs, passing a descriptor with a fully qualified name matching a previous
        # invocation will cause the same class to be returned.
        return GetMessageClass(message_descriptor)

    def _get_property_schema(
        field: google.protobuf.descriptor.FieldDescriptor
    ) -> kubernetes_asyncio.client.V1JSONSchemaProps:
        """Build the schema object for a single field.

        A field can be "repeated" and a field can represent a `Message`-type or
        a primitive. The case where a field is a `Message`-type leads to
        recursion.
        """

        # Enforce input type.
        assert isinstance(
            field,
            google.protobuf.descriptor.FieldDescriptor,
        ), type(field)

        schema_prop: kubernetes_asyncio.client.V1JSONSchemaProps
        if field.type == field.TYPE_MESSAGE:
            # If the field is a message, we recurse to get the schema definition
            # for this message type.
            schema_prop = _get_message_schema(
                message_type=get_python_type(field.message_type),
                _known_types=_known_types,
            )
        else:
            # If the field is primitive, we can construct the schema for the
            # field type right away by translating the name of the proto field
            # type to the Kubernetes type label.
            schema_prop = kubernetes_asyncio.client.V1JSONSchemaProps(
                type=get_kubernetes_type_label(field),
                x_kubernetes_preserve_unknown_fields=True
            )

        if field.label == field.LABEL_REPEATED:
            # If the field is repeated, it is in fact an `array` containing the
            # schema type we derived above.
            return kubernetes_asyncio.client.V1JSONSchemaProps(
                type='array',
                x_kubernetes_preserve_unknown_fields=True,
                items=schema_prop,
            )
        else:
            # If the field is not repeated, then the schema is indeed the schema
            # from before.
            return schema_prop

    # Construct a dict for each attribute/field on the input message.
    properties: dict[str, kubernetes_asyncio.client.V1JSONSchemaProps] = {}
    for field in message_type.DESCRIPTOR.fields:
        # Fill the dict with the schema for the *field*, that might be a generic
        # type, message or repeated field.
        properties[field.name] = _get_property_schema(field)

    # Construct the message schema object.
    message_schema = kubernetes_asyncio.client.V1JSONSchemaProps(
        type='object',
        properties=properties,
        x_kubernetes_preserve_unknown_fields=True,
    )

    # Insert it into the memoization for performance but also to mark this as a
    # non-recursive type.
    _known_types[message_type] = message_schema

    # Return the result.
    return message_schema


def _get_custom_resource_definition(
    *,
    message_type: type[google.protobuf.message.Message],
    version_name: str,
    group: str,
) -> kubernetes_asyncio.client.V1CustomResourceDefinition:

    # This naming and pluralization may look a bit odd in some cases, but
    # it's very helpful to be formulaic about it.
    kind = message_type.__name__
    singular = kind.lower()
    plural = get_kubernetes_plural(kind)

    names = kubernetes_asyncio.client.V1CustomResourceDefinitionNames(
        kind=kind,
        singular=singular,
        plural=plural,
    )

    schema = _get_message_schema(message_type=message_type)

    version = kubernetes_asyncio.client.V1CustomResourceDefinitionVersion(
        name=version_name,
        served=True,
        storage=True,
        schema=kubernetes_asyncio.client.V1CustomResourceValidation(
            open_apiv3_schema=schema
        ),
    )

    spec = kubernetes_asyncio.client.V1CustomResourceDefinitionSpec(
        group=group, scope='Namespaced', names=names, versions=[version]
    )

    return kubernetes_asyncio.client.V1CustomResourceDefinition(
        api_version='apiextensions.k8s.io/v1',
        kind='CustomResourceDefinition',
        metadata=kubernetes_asyncio.client.V1ObjectMeta(
            name=f'{plural}.{group}',
        ),
        spec=spec,
    )


class CustomObjectMeta(type):
    """Meta class from CustomObjects.

    We use this meta-class to extract the template type of the CustomObject
    programmatically, so we can use it in our code at runtime.

    The metaclass is responsible for creating the class as opposed to creating
    an instance of the class. So we are hooking ourselves in where
    `CustomObject` but also any child class derived from it is created, and
    changing how these classes are created.
    """

    # The name of the attribute on the created class that holds the Python type
    # of the generic passed.
    __type_name__: str = '__message_type__'

    def __new__(
        cls, name: str, bases: tuple, classdict: dict
    ) -> CustomObjectMeta:

        # Let's start by assuming that there is only ever one class we are
        # deriving from.
        # TODO: We could add support for this in the future, it just requires
        # more logic that we currently don't need, like looping over the bases
        # to see which of the bases is the one we need to extract the template
        # variable from.
        if len(bases) != 1:
            raise TypeError('Multiple inheritance not supported')

        # Extract the template type.
        message_type: Optional[type] = None
        try:
            # Get message type from class definition.
            message_type = get_args(classdict['__orig_bases__'][0])[0]
        except (KeyError, IndexError):
            # Check if base class has a message type.
            base_class_has_message_type: bool = hasattr(
                bases[0], CustomObjectMeta.__type_name__
            )

            if not base_class_has_message_type:
                # We have no message type in either the class definition or from
                # the base class. This is a problem.
                raise TypeError(
                    f'Missing template class for CustomObject sub-class {name}.'
                )

        # Check if the template type is a `class` as opposed to a `TypeVar` (in
        # the Generic case) or `None`.
        if isinstance(message_type, type):

            # Check that what we got is a proto message type.
            if not issubclass(message_type, google.protobuf.message.Message):
                raise TypeError(
                    f'Template type {message_type.__name__} is not a proto Message type'
                )

            # Add the template type to the class definition of the new class.
            classdict[cls.__type_name__] = message_type

            # Extract dynamic type annotation dictionary and add the type
            # annotation for the type we just added.
            # Note: `mypy` appears to ignore this, however we'll be nice and add
            # it for any runtime type inspection. For `mypy` to accept it we
            # need the annotated methods added in `CustomObject`.
            annotations: dict[str, str] = classdict.get('__annotations__', {})

            full_type_name = f'{message_type.__module__}.{message_type.__qualname__}'
            annotations[cls.__type_name__] = f'type[{full_type_name}]'

            classdict['__annotations__'] = annotations

        return cast(
            CustomObjectMeta, type.__new__(cls, name, bases, classdict)
        )


class CustomObject(Generic[ProtoMessageT], metaclass=CustomObjectMeta):
    """
    CustomObject is intended to be a superclass of a protobuf message.
    It contains shared behavior for the Python proto wrappers where we define
    custom_resource_definitions.

    NOTE: we expect the k8s `group` and `version` associated with
    this custom object type to be set by subclasses.

    group: The k8s api group.
    version: The k8s api version name.

    """

    version: ClassVar[str]
    group: ClassVar[str]

    def __init__(
        self,
        *,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta] = None,
        preserve_proto_field_names: bool = True,
        **kwargs,
    ):
        """Parameters:
        `metadata`: is the optional contents of the Kubernetes object's
                    `metadata` field. If no metadata is provided, an empty one
                    will be created.

        `preserve_proto_field_names`: determines how "multi_word" fields are
                                      named in JSON: when `True`, it will be
                                      protobuf-style "multi_word", if `False` it
                                      will be camel-case "multiWord".

        `kwargs`: The keyword arguments passed for construction of the
                  underlying proto message. If none are given, an empty proto
                  message will be created.
        """

        self._proto: ProtoMessageT = self.get_proto_message_type()(**kwargs)

        self.metadata: kubernetes_asyncio.client.V1ObjectMeta = metadata or kubernetes_asyncio.client.V1ObjectMeta(
        )
        self._preserve_proto_field_names = preserve_proto_field_names

    def set_proto(self, proto: ProtoMessageT) -> None:
        """Set the underlying proto message."""
        self._proto = proto

    def get_proto(self) -> ProtoMessageT:
        """Get the underlying proto message."""
        return self._proto

    @classmethod
    def get_plural(cls) -> str:
        """Get the plural version of this custom object type's name, used to
        identify it to Kubernetes."""
        return get_kubernetes_plural(cls.__name__)

    @classmethod
    def get_kind(cls) -> str:
        """Return the object `kind`."""
        return cls.__name__

    @classmethod
    def get_proto_message_type(
        cls: type[CustomObject[ProtoMessageT]]
    ) -> type[ProtoMessageT]:
        """Get the Python type of the underlying proto message."""
        return getattr(cls, CustomObjectMeta.__type_name__)

    @classmethod
    def get_api_version(cls) -> str:
        """Return the apiVersion string in the appropriate format."""
        return f'{cls.group}/{cls.version}'

    @classmethod
    def get_kubernetes_definition_name(cls):
        """Return the name of the custom resource definition in kubernetes."""
        return f'{cls.get_plural()}.{cls.group}'

    @classmethod
    def get_custom_resource_definition(
        cls,
    ) -> kubernetes_asyncio.client.V1CustomResourceDefinition:
        """Given an object that inherits from CustomObject, this method returns
        a custom resource definition K8s object.
        Many custom resource definition messages can be defined in one proto
        file, so we need to specify which one we're interested in by its name.
        If name == None, we expect there to only be one message defined in the
        proto.
        """
        return _get_custom_resource_definition(
            message_type=cls.get_proto_message_type(),
            group=cls.group,
            version_name=cls.version,
        )

    @classmethod
    def from_proto(
        cls: type[CustomObjectT],
        *,
        proto: ProtoMessageT,
        metadata: Optional[kubernetes_asyncio.client.V1ObjectMeta] = None,
    ) -> CustomObjectT:
        """Create custom object from proto and (optionally) metadata."""
        custom_object = cls(metadata=metadata)
        custom_object.set_proto(proto)
        return custom_object

    @classmethod
    async def from_dict_with_metadata(
        cls: type[CustomObjectT],
        js_obj: dict[str, Any],
    ) -> CustomObjectT:
        """Takes a JSON serializable dict from, e.g. a `watch_event` and returns
        an instance of the child class on which this method is called, including
        filled object metadata."""
        metadata_fields = js_obj.pop('metadata', None)

        # Create an empty proto message we can serialize into.
        message = cls.get_proto_message_type()()
        # Use built in function to populate `message` *in place* from `js_obj`.
        ParseDict(
            message=message,
            js_dict=js_obj,
            ignore_unknown_fields=True,
        )

        obj = cls()
        obj.set_proto(message)
        obj.metadata = await metadata_from_dict(metadata_fields)
        return obj

    def to_dict(self) -> dict[str, Any]:
        """Get JSON serializable dict representation of object.

        Even though K8s create_namespaced_custom_object claims the body
        should be JSON, it actually wants a dict.
        """
        return _delete_none_values(
            {
                'apiVersion':
                    self.get_api_version(),
                'kind':
                    self.get_kind(),
                'metadata':
                    native_object_to_dict(self.metadata),
                **MessageToDict(
                    self.get_proto(),
                    preserving_proto_field_name=self._preserve_proto_field_names,
                )
            }
        )

    # __getattr__ is called when an attribute that doesn't exist on an object is
    # called. We use this facility to call through to the proto, if it contains
    # those fields.
    def __getattr__(self, name: str) -> Any:
        if name == 'metadata':
            return self.metadata
        elif name == '_preserve_proto_field_names':
            return self._preserve_proto_field_names
        try:
            return getattr(self._proto, name)
        except AttributeError:
            raise AttributeError(
                f'No attribute named "{name}" defined on self._proto.'
                ' You may only access fields defined on this objects corresponding'
                ' .proto definition'
            )

    # __setattr__ is called every time an attribute is set INSTEAD of the normal
    # Python setter. This proxies the setter through to the proto object so the
    # object can be treated like a normal proto, while also having other
    # behavior that can't be defined on the proto.
    def __setattr__(self, name: str, value: Any) -> None:
        # __setattr__ is called in __init__, so we have to explicitly set those
        # values on the object.
        if name in ['_proto', 'metadata', '_preserve_proto_field_names']:
            # Standard setting of instance attribute e.g. `self._proto = value`
            # will cause a recursive call to __setattr__, ad infinitum.
            # We avoid this by inserting the value into the dictionary of
            # instance attributes.
            # https://python-reference.readthedocs.io/en/latest/docs/dunderattr/setattr.html
            self.__dict__[name] = value
            return

        try:
            setattr(self._proto, name, value)
        except AttributeError:
            # Don't allow setters for anything other than proto fields or
            # self._proto.
            raise AttributeError(
                f'No attribute named "{name}" defined on self._proto, or '
                'attribute is not writable (e.g. complex fields). You may '
                'only access fields defined on this object\'s corresponding '
                '.proto definition, and those fields must be writable.'
            )

    def __eq__(self, other: Any) -> bool:
        if type(other) != type(self):
            return False
        return self.to_dict() == other.to_dict()
