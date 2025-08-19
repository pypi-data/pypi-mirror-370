import kubernetes_asyncio
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.custom_object import CustomObject, CustomObjectT
from kubernetes_utils.helpers import WatchEvent, WatchEventType, wait_for_state
from log.log import LoggerMixin
from typing import AsyncGenerator, NewType, Optional


def _testonly_hook_processing_watch_event():
    """
    Called when `watch()` is processing a new event.
    This method is normally empty; it is here to allow tests to mock it,
    e.g. to inject errors into `watch()`.
    """


class MustRestartWatch(Exception):
    """
    An exception that indicates that watching Kubernetes somehow failed, and the
    watch needs to be restarted from scratch. Events arriving between this event
    and the restart of the watch will not be observed as watch-events; it is the
    caller's responsibility to make sure that the latest state of the world is
    taken into account before the watch is restarted.
    """


KubernetesResourceVersion = NewType("KubernetesResourceVersion", str)


class AbstractCustomObjects:

    async def create(self, obj: CustomObject) -> None:
        """Create namespaced custom object."""
        raise NotImplementedError

    async def create_or_update(self, obj: CustomObject) -> None:
        """Create namespaced custom object if it doesn't exist, or update it
        in-place if it does exist."""
        raise NotImplementedError

    async def replace(self, obj: CustomObject):
        """Replace namespaced custom object. It must already exist, and the
        `body.metadata.resource_version` must match exactly what would
        be returned by a `get()` for this object. This ensures a hermetic
        replacement, without a chance of any intermediate updates being
        overwritten.
        """
        raise NotImplementedError

    async def get_by_name(
        self, *, namespace: str, name: str, object_type: type[CustomObjectT]
    ) -> CustomObjectT:
        """Get namespaced custom object."""
        raise NotImplementedError

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
    ) -> tuple[list[CustomObjectT], KubernetesResourceVersion]:
        """list namespaced custom objects."""
        raise NotImplementedError

    async def delete(self, obj: CustomObjectT) -> None:
        """Delete namespaced custom object."""
        raise NotImplementedError

    async def delete_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> None:
        """Delete namespaced custom object by name."""
        raise NotImplementedError

    async def wait_for_applied(
        self,
        *,
        obj: CustomObject,
    ) -> None:
        """
        Wait for an instance of the given custom resource type to be applied.
        """
        raise NotImplementedError

    async def watch_all(
        self,
        *,
        object_type: type[CustomObjectT],
        resource_version: Optional[KubernetesResourceVersion],
        namespace: Optional[str] = None,
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:
        """
        Start a long-lived watch for all instances of the given custom resource
        type.

        If `namespace` is not `None`, only watches for objects in the given
        namespace. Otherwise, watches for objects in all namespaces.

        If `resource_version` is not None, it sets the Kubernetes resource
        version from which the watch begins. Use together with `list_all` to
        first handle the current state of the world and then hermetically watch
        subsequent changes, by starting at the resource version returned by
        `list_all`.

        NOTE: may raise `MustRestartWatch` from time to time (as often as every
              5 minutes), which terminates the watch and requires it to be
              restarted. In the intervening time events might get missed, so a
              new `list_all` is likely also required.
        """
        if False:
            # This is here to show mypy that the _actual_ return type of this
            # method matches the declared return type: it's a generator.
            yield
        raise NotImplementedError


class CustomObjects(LoggerMixin, AbstractCustomObjects):
    """An implementation of `AbstractCustomObjects` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(self, obj: CustomObject) -> None:

        async def retryable_create_custom_object():
            await self._apis.custom_objects.create_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
                body=obj.to_dict(),
            )

        await self._apis.retry_api_call(retryable_create_custom_object)

    async def create_or_update(self, obj: CustomObject) -> None:

        async def _do_create_or_update():
            try:
                old_obj = await self.get_by_name(
                    namespace=obj.metadata.namespace,
                    name=obj.metadata.name,
                    object_type=type(obj),
                )
                # If the above didn't throw an exception the object exists, so
                # update it.
                obj.metadata.resource_version = old_obj.metadata.resource_version
                await self.replace(obj)

            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # The object doesn't exist, so create it.
                    await self.create(obj)

            # Success!
            return

        await self._apis.retry_api_call(
            _do_create_or_update,
            # It is possible for the object to be updated in between the
            # 'get' and the 'replace'/'create'. This can happen in
            # case of a race in the controller where two code paths
            # simultaneously want to update the object. We use
            # last-writer-wins semantics here, so we retry.
            additional_should_retry=lambda e: (
                isinstance(
                    e, kubernetes_asyncio.client.exceptions.ApiException
                ) and e.status == 409
            ),
        )

    async def replace(self, obj: CustomObject):

        async def retryable_replace_custom_object():
            response = await self._apis.custom_objects.replace_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                name=obj.metadata.name,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
                body=obj.to_dict(),
            )
            return response

        return await self._apis.retry_api_call(retryable_replace_custom_object)

    async def get_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> CustomObjectT:

        async def retryable_get_custom_object():
            response = await self._apis.custom_objects.get_namespaced_custom_object(
                namespace=namespace,
                name=name,
                group=object_type.group,
                version=object_type.version,
                plural=object_type.get_plural(),
            )
            return response

        return await object_type.from_dict_with_metadata(
            await self._apis.retry_api_call(retryable_get_custom_object)
        )

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
    ) -> tuple[list[CustomObjectT], KubernetesResourceVersion]:

        async def retryable_list_custom_object(
        ) -> tuple[list[dict], KubernetesResourceVersion]:
            if namespace is None:
                response = await self._apis.custom_objects.list_cluster_custom_object(
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )

            else:
                response = await self._apis.custom_objects.list_namespaced_custom_object(
                    namespace=namespace,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                )

            return (
                response['items'],
                KubernetesResourceVersion(
                    response['metadata']['resourceVersion']
                )
            )

        items, resource_version = await self._apis.retry_api_call(
            retryable_list_custom_object
        )
        return (
            [
                (await object_type.from_dict_with_metadata(item))
                for item in items
            ],
            resource_version,
        )

    async def watch_all(
        self,
        *,
        object_type: type[CustomObjectT],
        namespace: Optional[str] = None,
        resource_version: Optional[KubernetesResourceVersion] = None,
    ) -> AsyncGenerator[WatchEvent[CustomObjectT], None]:

        try:
            w = kubernetes_asyncio.watch.Watch()

            # Depending on whether we are watching a specific namespace or any
            # namespace, we must setup our watcher differently.
            if namespace is None:
                # Watch for object in the cluster.
                event_provider = w.stream(
                    self._apis.custom_objects.list_cluster_custom_object,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                    resource_version=resource_version,
                )
            else:
                # Watch for object in namespace.
                event_provider = w.stream(
                    self._apis.custom_objects.list_namespaced_custom_object,
                    namespace=namespace,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                    resource_version=resource_version,
                )

            async with event_provider as event_stream:
                async for event in event_stream:
                    _testonly_hook_processing_watch_event()
                    yield WatchEvent[CustomObjectT](
                        type=WatchEventType(event['type']),
                        object=(
                            await object_type.from_dict_with_metadata(
                                event['object']
                            )
                        ),
                    )

        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.status == 410:
                self.logger.debug('watch_all() expired; must restart')
                raise MustRestartWatch() from e

            self.logger.error(
                f'Kubernetes API exception raised ({e}); '
                'did you apply your custom resource definition ('
                f'{object_type.get_plural()}) before starting the watch?'
            )
            raise e

    async def delete(self, obj: CustomObjectT) -> None:
        await self.delete_by_name(
            namespace=obj.metadata.namespace,
            name=obj.metadata.name,
            object_type=type(obj),
        )

    async def delete_by_name(
        self,
        *,
        namespace: str,
        name: str,
        object_type: type[CustomObjectT],
    ) -> None:

        async def retryable_delete_object():
            try:
                await self._apis.custom_objects.delete_namespaced_custom_object(
                    namespace=namespace,
                    name=name,
                    group=object_type.group,
                    version=object_type.version,
                    plural=object_type.get_plural(),
                    grace_period_seconds=0,
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.status == 404:
                    # The object doesn't exist, so we don't need to delete it.
                    pass
                else:
                    raise e

        await self._apis.retry_api_call(retryable_delete_object)

    async def wait_for_applied(
        self,
        *,
        obj: CustomObject,
    ) -> None:

        async def check_for_custom_object_applied():
            await self._apis.custom_objects.get_namespaced_custom_object(
                namespace=obj.metadata.namespace,
                name=obj.metadata.name,
                group=obj.group,
                version=obj.version,
                plural=obj.get_plural(),
            )
            return True

        await wait_for_state(
            check_for_custom_object_applied,
            kubernetes_asyncio.client.exceptions.ApiException
        )
