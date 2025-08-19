import kubernetes_asyncio
from aiohttp.client_exceptions import ClientConnectorError
from log.log import LoggerMixin
from rebootdev.aio.backoff import Backoff
from typing import Awaitable, Callable, TypeVar

RetryReturnT = TypeVar('RetryReturnT')


class KubernetesAPIs(LoggerMixin):

    def __init__(self, k8s_config_initialized: bool = False):
        if not k8s_config_initialized:
            raise ValueError(
                'K8s API config must be loaded before calling this constructor.'
                ' Use EnhancedKubernetesClient.create_client() rather than'
                ' calling this constructor directly.'
            )
        super().__init__()

        self._client = kubernetes_asyncio.client.ApiClient()
        self.rbac_authz = kubernetes_asyncio.client.RbacAuthorizationV1Api(
            self._client
        )
        self.core = kubernetes_asyncio.client.CoreV1Api(self._client)
        self.custom_objects = kubernetes_asyncio.client.CustomObjectsApi(
            self._client
        )
        self.apps = kubernetes_asyncio.client.AppsV1Api(self._client)
        self.api_extensions = kubernetes_asyncio.client.ApiextensionsV1Api(
            self._client
        )
        self.storage = kubernetes_asyncio.client.StorageV1Api(self._client)

    async def close(self) -> None:
        """Close client connection(s)."""
        await self._client.close()

    async def retry_api_call(
        self,
        fn: Callable[[], Awaitable[RetryReturnT]],
        num_attempts: int = 15,
        initial_backoff_seconds: float = 1,
        backoff_multiplier: float = 2,
        max_backoff_seconds: float = 30,
        additional_should_retry: Callable[[Exception], bool] = lambda _: False,
    ) -> RetryReturnT:
        """Retries a k8s API call for around 120 seconds (by default) in case
        of transient errors. These errors are likely to happen when a pod is
        first starting up - its Istio proxy may not yet be ready to handle
        traffic.

        The `additional_should_retry` callable can be used to retry additional
        error types.
        """
        backoff = Backoff(
            initial_backoff_seconds=initial_backoff_seconds,
            backoff_multiplier=backoff_multiplier,
            max_backoff_seconds=max_backoff_seconds,
        )
        while True:
            try:
                return await fn()
            except Exception as e:
                if (
                    not isinstance(e, ClientConnectorError) and
                    not additional_should_retry(e)
                ):
                    raise

                # This likely indicates the Kubernetes API server isn't
                # reachable (yet); that's a common transient condition in our
                # tests just after they've started, even when the API server has
                # been up for a while - the exact cause is unclear.
                # TODO(rjh): figure out why the API frequently isn't available
                # at the start of a test; is there anything we can do to wait
                # until the API is available?
                self.logger.warning(
                    f'Got an exception calling Kubernetes: {e}'
                )

            num_attempts -= 1
            if num_attempts > 0:
                # Give the API a chance to come up.
                self.logger.warning('Will retry after backoff...')
                await backoff()
            else:
                break

        raise TimeoutError(
            'Failed to perform operation; maximum retries exceeded.'
        )
