import asyncio
import kubernetes_asyncio
from aiohttp.client_exceptions import ClientConnectorError
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.custom_object import CustomObject
from kubernetes_utils.helpers import wait_for_state
from log.log import LoggerMixin


class AbstractCustomResourceDefinitions:

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self
    ) -> list[kubernetes_asyncio.client.V1CustomResourceDefinition]:
        """List all registered custom resource definitions."""
        raise NotImplementedError

    async def create(self, custom_object_class: type[CustomObject]) -> None:
        """Creates the Python custom object's class definition as a
        Custom Resource Definition in K8s."""
        raise NotImplementedError

    async def wait_for_applied(
        self,
        custom_object_class: type[CustomObject],
    ) -> None:
        """Wait for a custom resource definition with the given name to be
        applied."""
        raise NotImplementedError

    async def delete(self, custom_object_class: type[CustomObject]) -> None:
        """Request deletion of custom resource definition.
        Note, when the function returns, the definition might still be around.
        """
        raise NotImplementedError

    async def ensure_deleted(
        self, custom_object_class: type[CustomObject]
    ) -> None:
        """Delete custom resource definition and swallow potential errors if the
        definition doesn't exist.
        """
        raise NotImplementedError


class CustomResourceDefinitions(
    LoggerMixin, AbstractCustomResourceDefinitions
):
    """An implementation of `AbstractCustomResourceDefinitions` that uses the
    real Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def list_all(
        self
    ) -> list[kubernetes_asyncio.client.V1CustomResourceDefinition]:

        return (
            await self._apis.retry_api_call(
                self._apis.api_extensions.list_custom_resource_definition
            )
        ).items

    async def create(self, custom_object_class: type[CustomObject]) -> None:
        crd = custom_object_class.get_custom_resource_definition()

        async def retryable_create_custom_resource_definition():
            try:
                await self._apis.api_extensions.create_custom_resource_definition(
                    crd
                )
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Conflict':
                    self.logger.debug(
                        'Attempting to create custom resource definition '
                        f'twice: {crd.metadata.name}'
                    )
                else:
                    # This is not the API exception we were looking for. Re-raise.
                    raise

        await self._apis.retry_api_call(
            retryable_create_custom_resource_definition
        )

    async def wait_for_applied(
        self,
        custom_object_class: type[CustomObject],
    ) -> None:
        name = custom_object_class.get_kubernetes_definition_name()

        async def check_for_custom_resource_definition_applied():
            response = await self._apis.api_extensions.list_custom_resource_definition(
                field_selector=f'metadata.name={name}'
            )
            if len(response.items) > 0:
                return True
            return False

        await wait_for_state(
            check_for_custom_resource_definition_applied,
            ClientConnectorError,
        )

    async def delete(self, custom_object_class: type[CustomObject]) -> None:

        async def retryable_delete():
            await self._apis.api_extensions.delete_custom_resource_definition(
                name=
                f'{custom_object_class.get_plural()}.{custom_object_class.group}'
            )

        await self._apis.retry_api_call(retryable_delete)

    async def ensure_deleted(
        self, custom_object_class: type[CustomObject]
    ) -> None:
        # Request that the custom resource definition be deleted.
        try:
            await self.delete(custom_object_class=custom_object_class)
        except kubernetes_asyncio.client.exceptions.ApiException as e:
            if e.reason == 'Not Found':
                # If the definition is not there, there isn't much left to do.
                return
            raise e

        name = f'{custom_object_class.get_plural()}.{custom_object_class.group}'

        # Wait for the custom resource definition to be deleted.
        async def retryable_wait_for_delete():
            while True:
                try:
                    await self._apis.api_extensions.read_custom_resource_definition(
                        name=name
                    )
                    # Since the definition is still there (we didn't throw an
                    # exception), wait a bit and try again.
                    await asyncio.sleep(1)
                except kubernetes_asyncio.client.exceptions.ApiException as e:
                    if e.status == 404:
                        self.logger.debug(
                            'Custom resource definition deleted successfully: %s',
                            name
                        )
                        break

        await self._apis.retry_api_call(retryable_wait_for_delete)
