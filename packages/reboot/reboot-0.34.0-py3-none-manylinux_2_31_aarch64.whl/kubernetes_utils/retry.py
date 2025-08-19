import asyncio
import grpc
import traceback
from contextlib import contextmanager
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.resources.pods import PodFailedError
from log.log import get_logger
from rebootdev.aio.backoff import Backoff
from typing import Any, Optional, Sequence

logger = get_logger(__name__)


class Retry:
    """Helper class returned from `retry_unless_pods_have_failed(...)`
    that should be used in a `with` to properly retry a block of code.

    Don't use this class directly, always call
    `retry_insecure_grpc_unless_pods_have_failed(...)` or one of the
    other wrappers around `retry_unless_pods_have_failed(...)`.
    """

    def __init__(self, value: Any):
        self._value = value
        self._exception: Optional[BaseException] = None

    @contextmanager
    def __call__(self):
        self._exception = None
        try:
            yield self._value
        except BaseException as exception:
            logger.debug(f"{''.join(traceback.format_exception(exception))}")
            self._exception = exception

    @property
    def exception(self):
        return self._exception


# Type aliases to simplify reading of types.
NamespaceName = str
PodNamePrefix = str


async def retry_unless_pods_have_failed(
    *,
    retry: Retry,
    k8s_client: AbstractEnhancedKubernetesClient,
    pods: list[tuple[NamespaceName, list[PodNamePrefix]]],
    exceptions: list[type[BaseException]],
    treat_not_found_as_failed: bool = False,
    max_backoff_seconds: int = 3,
):
    """Helper function for retrying a block of code as long as pods have
    not failed. This is helpful when trying to make RPCs to pods that
    don't have clear signals that they are "ready" (e.g., they don't
    have readiness probes, or those readiness probes have long
    delays), as well as to mitigate the fact that a pod may fail after
    signaling that it is ready.

    Don't use this function directly, always call
    `retry_insecure_grpc_unless_pods_have_failed(...)` or one of the
    other wrappers around this function.

    :param retry: instance of `Retry` that will be yielded in each
                  iteration of the loop.

    :param k8s_client: Kubernetes client to use for watching pods.

    :param pods: pods to watch, each pod name is treated as a pod prefix,
                 e.g., [('namespace', ['pod-prefix1', 'pod-prefix2']), ...].

    :param exceptions: exceptions to expect and still retry,
                       e.g., [grpc.aio.AioRpcError, ...].

    :param treat_not_found_as_failed: whether or not to treat a
                                      missing pod as failed.

    :param max_backoff_seconds: maximum amount of time we'll ever
                                backoff as part of the exponential
                                backoff that we'll perform when
                                retrying.
    """
    # TODO(benh): check that all `exceptions` are of `type[BaseException]`.

    # We start waiting for pods to fail right away so that a caller
    # can set `treat_not_found_as_failed=True` if they have already
    # checked that a pod is running and want to ensure that a missing
    # pod means that it has failed and been cleaned up by Kubernetes.
    wait_for_failed_tasks: dict[tuple[str, str], asyncio.Task[None]] = {
        (pod_namespace, pod_name_prefix):
            asyncio.create_task(
                k8s_client.pods.wait_for_failed_with_prefix(
                    namespace=pod_namespace,
                    name_prefix=pod_name_prefix,
                    treat_not_found_as_failed=treat_not_found_as_failed,
                ),
                name=f'k8s_client.pods.wait_for_failed... (#1) in {__name__}',
            ) for pod_namespace, pod_name_prefixes in pods
        for pod_name_prefix in pod_name_prefixes
    }

    async def check_for_failures() -> None:
        failures: list[PodFailedError] = []

        retry_wait_for_failed_tasks: dict[tuple[str, str],
                                          asyncio.Task[None]] = {}

        for (pod_namespace,
             pod_name_prefix), task in wait_for_failed_tasks.items():
            if task.done():
                try:
                    await task
                    failures.append(
                        PodFailedError(
                            f"pod '{pod_name_prefix}' in namespace "
                            f"'{pod_namespace}' has failed"
                        )
                    )
                except BaseException as exception:
                    # In the event that we failed to wait for failed
                    # pods, retry.
                    logger.debug(
                        f"{''.join(traceback.format_exception(exception))}"
                    )
                    retry_wait_for_failed_tasks[
                        (pod_namespace, pod_name_prefix)
                    ] = asyncio.create_task(
                        k8s_client.pods.wait_for_failed_with_prefix(
                            namespace=pod_namespace,
                            name_prefix=pod_name_prefix,
                            treat_not_found_as_failed=treat_not_found_as_failed,
                        ),
                        name=
                        f'k8s_client.pods.wait_for_failed... (#2) in {__name__}',
                    )

        wait_for_failed_tasks.update(retry_wait_for_failed_tasks)

        if len(failures) > 0:
            raise Exception(failures)

    try:
        # Now wait for all of the pods to be running, but bail out if
        # any pods have already failed.
        #
        # TODO: use `asyncio.gather()`.
        for (pod_namespace, pod_name_prefixes) in pods:
            for pod_name_prefix in pod_name_prefixes:
                logger.debug(
                    f"Waiting for '{pod_namespace}'/'{pod_name_prefix}' to start"
                )
                wait_for_ready_task = asyncio.create_task(
                    k8s_client.pods.wait_for_ready_with_prefix(
                        namespace=pod_namespace,
                        name_prefix=pod_name_prefix,
                    ),
                    name=f'k8s_client.pods.wait_for_ready... in {__name__}',
                )

                while True:
                    done, pending = await asyncio.wait(
                        [wait_for_ready_task] +
                        list(wait_for_failed_tasks.values()),
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    if len(done) == 1 and wait_for_ready_task in done:
                        break

                    try:
                        await check_for_failures()
                    except:
                        wait_for_ready_task.cancel()
                        try:
                            await wait_for_ready_task
                        except:
                            # Ignore because we're cancelling.
                            pass
                        raise

        # TODO(benh): let users configure the rest of the retry/backoff values.
        backoff = Backoff(max_backoff_seconds=max_backoff_seconds)

        while True:
            try:
                yield retry
            except GeneratorExit:
                raise
            except:
                raise RuntimeError(
                    "Not expecting an exception to be raised; ensure your code "
                    "looks something similar to: \n"
                    "\n"
                    "    async for retry in retry_...(...):\n"
                    "        with retry() as ...:\n"
                )
            else:
                if retry.exception is None:
                    break
                elif any(
                    isinstance(retry.exception, exception)
                    for exception in exceptions
                ):
                    logger.debug(
                        "Got an exception that we want to catch, backing off"
                    )

                    # NOTE: we exponentially backoff _before_ checking
                    # if the pod has failed to give it more time to
                    # actually record any failure in the Kubernetes
                    # API.
                    await backoff()

                    await check_for_failures()
                else:
                    raise retry.exception
    finally:
        for task in wait_for_failed_tasks.values():
            task.cancel()
            try:
                await task
            except:
                # We don't care about any exceptions at this point.
                continue


async def retry_insecure_grpc_unless_pods_have_failed(
    target: str,
    *,
    k8s_client: AbstractEnhancedKubernetesClient,
    pods: list[tuple[str, list[str]]],
    exceptions: list[type[BaseException]],
    treat_not_found_as_failed: bool = False,
    max_backoff_seconds: int = 3,
    options: Optional[Sequence[tuple[str, Any]]] = None,
    compression: Optional[grpc.Compression] = None,
    interceptors: Optional[Sequence[grpc.aio.ClientInterceptor]] = None,
):
    """Wrapper around `retry_unless_pods_have_failed(...)`.

    :param target: parameter from `grpc_aio.insecure_channel(...)`.

    :param options: parameter from `grpc_aio.insecure_channel(...)`.

    :param compression: parameter from `grpc_aio.insecure_channel(...)`.

    :param interceptors: parameter from `grpc_aio.insecure_channel(...)`.

    See other parameters described in `retry_unless_pods_have_failed(...)`.

    Example:

    async for retry in retry_insecure_grpc_unless_pods_have_failed(...):
        with retry() as channel:
            stub = SomeStub(channel)
            response = await stub.SomeMethod(...)
    """
    async with grpc.aio.insecure_channel(
        target, options, compression, interceptors
    ) as channel:
        async for retry in retry_unless_pods_have_failed(
            retry=Retry(channel),
            k8s_client=k8s_client,
            pods=pods,
            exceptions=exceptions,
            treat_not_found_as_failed=treat_not_found_as_failed,
            max_backoff_seconds=max_backoff_seconds,
        ):
            yield retry
