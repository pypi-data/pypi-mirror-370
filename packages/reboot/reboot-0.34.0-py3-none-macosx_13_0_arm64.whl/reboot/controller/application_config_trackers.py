from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.custom_objects import MustRestartWatch
from log.log import get_logger
from reboot.controller.application_config import ApplicationConfig
from reboot.naming import ApplicationId
from rebootdev.aio.exceptions import InputError
from typing import Awaitable, Callable

logger = get_logger(__name__)


class ApplicationConfigTracker:

    def __init__(self):
        # All callbacks registered with this tracker, to be called on any
        # ApplicationConfig event.
        self.config_change_callbacks: list[Callable[[], Awaitable[None]]] = []

    async def get_application_configs(
        self
    ) -> dict[ApplicationId, ApplicationConfig]:
        """Return a map of application ID to ApplicationConfig."""
        raise NotImplementedError()

    def on_configs_change(self, callback: Callable[[], Awaitable[None]]):
        """Store a callback function to invoke whenever an application config is
        added, updated, or deleted.

        We expect our callbacks to be async functions with no params.
        """
        self.config_change_callbacks.append(callback)


class KubernetesApplicationConfigTracker(ApplicationConfigTracker):

    def __init__(
        self,
        k8s_client: AbstractEnhancedKubernetesClient,
    ):
        super().__init__()
        self._k8s_client = k8s_client

    async def run(self) -> None:
        """
        Start tracking ApplicationConfig events.

        Note that this function is expected to run indefinitely.
        """
        await self._watch_application_config()

    async def _handle_application_config_change(self) -> None:
        try:
            for callback in self.config_change_callbacks:
                await callback()
        except InputError as e:
            # TODO: Report these errors to the developer who wrote the
            # `ApplicationDeployment`, e.g. by updating the
            # `ApplicationDeployment.status` field.
            logger.error(
                'Got custom object error: %s',
                e.reason,
            )
        except Exception as e:
            # TODO: Report these errors to the developer who wrote the
            # `ApplicationDeployment` on a best effort basis, e.g. by
            # attempting to update the `ApplicationDeployment.status` field.
            logger.critical(
                'Got unknown error for object %s: %s',
                type(e).__name__,
                str(e),
            )
            raise

    async def _watch_application_config(self) -> None:
        """
        Start a watch on the ApplicationConfig definition with the k8s API, and
        call all our callbacks on any event.
        """
        logger.info('Starting ApplicationConfig watch in any namespace...')
        while True:
            try:
                # Find the Kubernetes resource version that we're currently at.
                _, resource_version = await self._k8s_client.custom_objects.list_all(
                    object_type=ApplicationConfig
                )

                # We may have missed some events that happened before this watch
                # started. Trigger our callbacks; better safe than sorry.
                await self._handle_application_config_change()

                # Now begin watching, starting at the previously-seen resource
                # version, ensuring that no events can get missed in between.
                async for watch_event in self._k8s_client.custom_objects.watch_all(
                    object_type=ApplicationConfig,
                    resource_version=resource_version,
                ):
                    logger.info(
                        'ApplicationConfig %s: %s',
                        watch_event.type,
                        watch_event.object.metadata.name or 'unknown',
                    )
                    await self._handle_application_config_change()

                logger.warning(
                    'Stopped watching for ApplicationConfig changes'
                )

            except MustRestartWatch:
                # This is expected from time to time. Simply start watching
                # again from scratch.
                continue

    async def get_application_configs(
        self
    ) -> dict[ApplicationId, ApplicationConfig]:
        application_config_dict: dict[ApplicationId, ApplicationConfig] = {}
        application_configs, _ = await self._k8s_client.custom_objects.list_all(
            object_type=ApplicationConfig,
        )
        for application_config in application_configs:
            if (
                len(application_config.spec.file_descriptor_set) == 0 or
                len(application_config.spec.container_image_name) == 0 or
                len(application_config.spec.service_names) == 0
            ):
                # ISSUE(https://github.com/reboot-dev/mono/issues/1416):
                # Controller should handle incorrect user input. We should
                # propagate this message back to the user instead of silently
                # failing.
                logger.warning(
                    'ApplicationConfig %s in %s is missing required fields, skipping',
                    application_config.metadata.name,
                    application_config.metadata.namespace,
                )
                continue

            application_config_dict[application_config.application_id()
                                   ] = application_config

        return application_config_dict


class LocalApplicationConfigTracker(ApplicationConfigTracker):

    def __init__(self):
        super().__init__()
        # Mapping of application ID to full ApplicationConfig.
        self.configs: dict[ApplicationId, ApplicationConfig] = {}

    async def refresh(self) -> None:
        for callback in self.config_change_callbacks:
            await callback()

    async def add_config(self, config: ApplicationConfig) -> None:
        self.configs[config.application_id()] = config
        for callback in self.config_change_callbacks:
            await callback()

    async def delete_config(self, config: ApplicationConfig) -> None:
        self.configs.pop(config.application_id(), None)
        for callback in self.config_change_callbacks:
            await callback()

    async def delete_all_configs(self) -> None:
        self.configs = {}
        for callback in self.config_change_callbacks:
            await callback()

    async def get_application_configs(
        self
    ) -> dict[ApplicationId, ApplicationConfig]:
        return self.configs
