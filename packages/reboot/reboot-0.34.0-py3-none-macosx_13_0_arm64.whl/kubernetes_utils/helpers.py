import asyncio
import datetime
import kubernetes_asyncio
import six
from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar

T = TypeVar('T')


class WatchEventType(Enum):
    ADDED = 'ADDED'
    MODIFIED = 'MODIFIED'
    DELETED = 'DELETED'


@dataclass(kw_only=True)
class WatchEvent(Generic[T]):
    """A generic event returned from a k8s watch on any resource type."""
    type: WatchEventType
    object: T


def get_kubernetes_plural(class_name: str) -> str:
    """Convert a class name (or kind) to a Kubernetes-friendly plural form."""
    return f'{class_name.lower()}s'


async def wait_for_state(
    check_state_fn: Callable[[], Awaitable[bool]],
    suppressed_exception: Optional[type[BaseException]],
    seconds_between_api_calls: float = 1
) -> None:
    """Waits for k8s to reach the desired state by periodically querying
    the API using check_state_fn.
    check_state_fn should return True when the desired state is found."""
    while True:
        if suppressed_exception is None:
            if await check_state_fn():
                return
        else:
            try:
                if await check_state_fn():
                    return
            except suppressed_exception:
                pass

        await asyncio.sleep(seconds_between_api_calls)


def native_object_to_dict(kubernetes_object: Any) -> Any:
    """Convert a native kubernetes api object to dict."""
    # NOTE: Typed to `Any` due to the recursive nature of how the resulting
    # dict is built.

    # The below code is taken from
    # [kubernetes.client.ApiClient.sanitize_for_serialization](https://github.com/tomplus/kubernetes_asyncio/blob/f4549213dc71e171f89f46aeb68eb30a100400e7/kubernetes_asyncio/client/api_client.py#L224)
    # The function should have been a class method, but isn't. This requires us
    # to construct an `ApiClient` instance, but by doing so, we'd open an
    # `async` connection that we'd need to `await`... To avoid having this
    # method be `async`, we'd rather copy and adapt the code.

    PRIMITIVE_TYPES = (float, bool, bytes, six.text_type) + six.integer_types

    if kubernetes_object is None:
        return None
    elif isinstance(kubernetes_object, PRIMITIVE_TYPES):
        return kubernetes_object
    elif isinstance(kubernetes_object, list):
        return [
            native_object_to_dict(sub_obj) for sub_obj in kubernetes_object
        ]
    elif isinstance(kubernetes_object, tuple):
        return tuple(
            native_object_to_dict(sub_obj) for sub_obj in kubernetes_object
        )
    elif isinstance(kubernetes_object, (datetime.datetime, datetime.date)):
        return kubernetes_object.isoformat()

    if isinstance(kubernetes_object, dict):
        kubernetes_object_dict = kubernetes_object
    else:
        # Convert model kubernetes_object to dict except
        # attributes `openapi_types`, `attribute_map`
        # and attributes which value is not None.
        # Convert attribute name to json key in
        # model definition for request.
        kubernetes_object_dict = {
            kubernetes_object.attribute_map[attr]:
                getattr(kubernetes_object, attr)
            for attr, _ in six.iteritems(kubernetes_object.openapi_types)
            if getattr(kubernetes_object, attr) is not None
        }

    return {
        key: native_object_to_dict(val)
        for key, val in six.iteritems(kubernetes_object_dict)
    }


async def metadata_from_dict(
    metadata_fields: dict[str, Any]
) -> kubernetes_asyncio.client.V1ObjectMeta:
    """Construct a V1ObjectMeta object from a dictionary of Kubernetes metadata
    fields (as might be returned from e.g. a Watch)."""
    # The kubernetes_asyncio.client.ApiClient has a utility for
    # deserializing dictionaries into its API objects. Unfortunately, that
    # functionality is not publicly accessible in isolation. Rather than
    # duplicating it in our code, we construct an API client and use the private
    # method here. This is an expensive construction as it opens a network
    # connection that we must close.
    # TODO: Include metadata construction with overall CustomObject construction
    # in `resources/custom_objects.py`, thus avoiding the ApiClient
    # reconstruction.
    async with kubernetes_asyncio.client.ApiClient() as api_client:
        return api_client._ApiClient__deserialize(
            metadata_fields, kubernetes_asyncio.client.V1ObjectMeta
        )
