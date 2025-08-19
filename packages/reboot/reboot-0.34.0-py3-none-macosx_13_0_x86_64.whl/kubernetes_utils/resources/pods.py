import kubernetes_asyncio
from aiohttp.client_exceptions import ClientConnectorError
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.helpers import wait_for_state
from kubernetes_utils.ownership import OwnershipInformation
from log.log import LoggerMixin
from typing import AsyncIterator, Optional


class PodFailedError(RuntimeError):
    pass


def _check_for_pod_error_message(
    pod: kubernetes_asyncio.client.V1Pod
) -> Optional[str]:
    """Check if the given pod has reached a known failure state, including
    startup failures that may not be indicated by an official Failure
    status. If so, return a string describing the reason for the error.

    If there is no error, returns None.
    """
    assert pod.status.phase in [
        'Pending', 'Running', 'Succeeded', 'Failed', 'Unknown'
    ]
    if pod.status.phase == 'Failed':
        return pod.status.message

    # One of a pod's containers could reach a terminal error state even if
    # the pod itself is Pending, so we need to check their statuses as well.
    container_statuses = pod.status.container_statuses or []
    container_statuses += pod.status.init_container_statuses or []
    for container_status in container_statuses:
        container_error_message = _check_for_container_error_message(
            container_status
        )
        if container_error_message is not None:
            return container_error_message

    return None


def _check_for_container_error_message(
    container_status: kubernetes_asyncio.client.V1ContainerStatus
) -> Optional[str]:
    if container_status.started is False or container_status.ready is False:
        assert (
            container_status.state.waiting is not None or
            container_status.state.running is not None or
            container_status.state.terminated is not None
        )
        # A container could be in an error state if it is `Waiting` or
        # `Terminated`, depending on the detailed message associated with
        # the state.
        #
        # There is unfortunately no single definitive list of all these
        # potential messages, but there are some partial lists in Kubernetes
        # source code.
        # The following error reasons are taken from:
        # https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/container/sync_result.go
        # https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/images/types.go
        # https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/kuberuntime/kuberuntime_container.go
        # https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/cri-api/pkg/errors/errors.go
        container_failure_reasons = [
            'CrashLoopBackOff',
            'RunContainerError',
            'KillContainerError',
            'CreatePodSandboxError',
            'ConfigPodSandboxError',
            'KillPodSandboxError',
            'ImagePullBackOff',
            'ImageInspectError',
            'ErrImagePull',
            'ErrImageNeverPull',
            'InvalidImageName',
            'CreateContainerConfigError',
            'PreCreateHookError',
            'CreateContainerError',
            'PreStartHookError',
            'PostStartHookError',
            'RegistryUnavailable',
            'SignatureValidationFailed',
        ]

        waiting_state = container_status.state.waiting
        if (
            waiting_state is not None and
            waiting_state.reason in container_failure_reasons
        ):
            return waiting_state.reason

        terminated_state = container_status.state.terminated
        if (
            terminated_state is not None and
            terminated_state.reason in container_failure_reasons
        ):
            return terminated_state.reason

    return None


class AbstractPods:

    async def create(
        self,
        *,
        pod: kubernetes_asyncio.client.V1Pod,
        owner: Optional[OwnershipInformation] = None,
    ):
        """Create a pod owned by the given owner object.

        The passed-in pod object is expected to have a filled metadata field to
        define its name and namespace - an owner reference will be injected
        into that metadata.

        NOTE: In most circumstances, you should create a Deployment rather than
        directly creating a Pod (to get resiliency benefits automatically from
        Kubernetes.)"""
        raise NotImplementedError

    async def delete(self, namespace: str, name: str):
        """Delete a namespaced pod."""
        raise NotImplementedError

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(
        self,
        *,
        namespace: Optional[str],
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        """
        Get all pods in the namespace specified.

        If no namespace is specified, get all pods in all namespaces.
        """
        raise NotImplementedError

    async def list_for_name_prefix(
        self, namespace: Optional[str], name_prefix: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        """
        Get a list of all pods with names starting with the given name
        prefix.
        """
        raise NotImplementedError

    async def list_for_label(
        self, namespace: Optional[str], label_name: str, label_value: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        """Get a list of all pods with the given label name/value combo."""
        raise NotImplementedError

    async def list_for_ip(
        self, namespace: Optional[str], pod_ip: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        """Get a list of all pods with the given IP address."""
        raise NotImplementedError

    async def wait_for_ready(self, *, namespace: str, name: str) -> str:
        """Wait for the given pod to reach 'Running' status."""
        raise NotImplementedError

    async def wait_for_ready_with_prefix(
        self, namespace: str, name_prefix: str
    ) -> None:
        """Wait for any pod with the given `name_prefix` to reach 'Running'
        status."""
        raise NotImplementedError

    async def wait_for_failed_with_prefix(
        self,
        *,
        namespace: str,
        name_prefix: str,
        treat_not_found_as_failed: bool = True,
        seconds_between_api_calls: float = 0.2,
    ) -> None:
        """Wait for any pod with the given `name_prefix` to reach 'Failed'
        status."""
        raise NotImplementedError

    async def wait_for_deleted(self, namespace: str, name: str) -> None:
        """Wait for the given pod to disappear from the k8s API."""
        raise NotImplementedError

    async def wait_for_deleted_with_prefix(
        self,
        *,
        namespace: str,
        name_prefix: str,
        seconds_between_api_calls: float = 0.2,
    ) -> None:
        """Wait for any pod with the given `name_prefix` to be deleted."""
        raise NotImplementedError

    async def get_logs(
        self,
        namespace: str,
        name: str,
        container_name: str,
    ) -> str:
        """Get the complete logs for a given container in a given pod.
        Loads the full logs from the pod, and returns them as a single
        string."""
        raise NotImplementedError

    async def follow_logs(
        self,
        *,
        namespace: str,
        name: str,
        container_name: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Follow the logs for a given container in a given pod."""
        raise NotImplementedError
        yield  # Necessary for type checking.


class Pods(LoggerMixin, AbstractPods):
    """An implementation of `AbstractPods` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def create(
        self,
        *,
        pod: kubernetes_asyncio.client.V1Pod,
        owner: Optional[OwnershipInformation] = None,
    ):
        if owner is not None:
            owner.add_to_metadata(pod.metadata)

        async def retryable_create_pod():
            await self._apis.core.create_namespaced_pod(
                pod.metadata.namespace, pod
            )

        await self._apis.retry_api_call(retryable_create_pod)

    async def delete(self, namespace: str, name: str):

        async def retryable_delete_pod():
            await self._apis.core.delete_namespaced_pod(name, namespace)

        await self._apis.retry_api_call(retryable_delete_pod)

    async def list_all(
        self,
        *,
        namespace: Optional[str],
    ) -> list[kubernetes_asyncio.client.V1Pod]:

        async def retryable_get_pods(
        ) -> list[kubernetes_asyncio.client.V1Pod]:
            if namespace is not None:
                pod_list = await self._apis.core.list_namespaced_pod(namespace)
            else:
                pod_list = await self._apis.core.list_pod_for_all_namespaces()
            return pod_list.items

        return await self._apis.retry_api_call(retryable_get_pods)

    async def list_for_name_prefix(
        self, namespace: Optional[str], name_prefix: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        pod_list = await self.list_all(namespace=namespace)
        return [
            pod for pod in pod_list
            if pod.metadata.name.startswith(name_prefix)
        ]

    async def list_for_label(
        self, namespace: Optional[str], label_name: str, label_value: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        pod_list = await self.list_all(namespace=namespace)
        return [
            pod for pod in pod_list
            if pod.metadata.labels.get(label_name) == label_value
        ]

    async def list_for_ip(
        self, namespace: Optional[str], pod_ip: str
    ) -> list[kubernetes_asyncio.client.V1Pod]:
        pod_list = await self.list_all(namespace=namespace)
        return [pod for pod in pod_list if pod.status.pod_ip == pod_ip]

    async def wait_for_ready(
        self,
        *,
        namespace: str,
        name: str,
    ) -> str:
        w = kubernetes_asyncio.watch.Watch()
        async with w.stream(
            func=self._apis.core.list_namespaced_pod,
            namespace=namespace,
            field_selector=f'metadata.name={name}',
        ) as stream:
            async for event in stream:
                # event.type: ADDED, MODIFIED, DELETED
                if event['type'] == 'DELETED':
                    w.stop()
                    raise PodFailedError(
                        'Pod was deleted while waiting for it to become ready.'
                    )

                pod = event['object']
                if pod.status.phase == 'Running':
                    # A running pod may not be ready yet. Check whether there is a "Ready" condition.
                    ready_condition = next(
                        (
                            condition
                            for condition in pod.status.conditions or []
                            if condition.type == "Ready"
                        ),
                        None,
                    )
                    if ready_condition is None or ready_condition.status != "True":
                        continue

                    # This is the status we're waiting to see!
                    w.stop()
                    ip = pod.status.pod_ip
                    return ip

                # Check if the pod has already reached a terminal error state,
                # so that we can end the watch.
                error_message = _check_for_pod_error_message(pod)
                if error_message is not None:
                    w.stop()
                    raise PodFailedError(
                        'Pod container reached error state while waiting '
                        f'for it to start: {error_message}'
                    )

                # The pod isn't up yet, but it hasn't failed either - keep
                # waiting.

        raise RuntimeError('Reached end of infinite stream watch?')

    async def wait_for_ready_with_prefix(
        self,
        namespace: str,
        name_prefix: str,
        seconds_between_api_calls: float = 0.2,
    ) -> None:

        async def check_pods() -> bool:
            pods_with_prefix = await self.list_for_name_prefix(
                namespace, name_prefix
            )

            if len(pods_with_prefix) == 0:
                return False

            # TODO(benh): should this be an error not an assert?
            assert len(pods_with_prefix) == 1, (
                f"Found {len(pods_with_prefix)} pods "
                f"[{', '.join([pod.metadata.name for pod in pods_with_prefix])}] "
                f"with prefix '{name_prefix}', please create a more specific prefix"
            )

            pod = pods_with_prefix[0]

            await self.wait_for_ready(
                namespace=namespace, name=pod.metadata.name
            )

            # As soon as any pod with the given prefix is running, we
            # are done.
            return True

        await wait_for_state(
            check_pods,
            ClientConnectorError,
            seconds_between_api_calls=seconds_between_api_calls,
        )

    async def wait_for_failed_with_prefix(
        self,
        *,
        namespace: str,
        name_prefix: str,
        treat_not_found_as_failed: bool = True,
        seconds_between_api_calls: float = 0.2,
    ) -> None:

        async def check_pod_failed() -> bool:
            try:
                pods_with_prefix = await self.list_for_name_prefix(
                    namespace, name_prefix
                )

                if len(pods_with_prefix) == 0:
                    return treat_not_found_as_failed

                # TODO(benh): should this be an error not an assert?
                assert len(pods_with_prefix) == 1, (
                    f"Found {len(pods_with_prefix)} pods "
                    f"[{', '.join([pod.metadata.name for pod in pods_with_prefix])}] "
                    f"with prefix '{name_prefix}', please create a more specific prefix"
                )

                pod = pods_with_prefix[0]

                return _check_for_pod_error_message(pod) is not None
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if e.reason == 'Not Found':
                    return treat_not_found_as_failed
                raise e

        await wait_for_state(
            check_pod_failed,
            ClientConnectorError,
            seconds_between_api_calls=seconds_between_api_calls,
        )

    async def wait_for_deleted(self, namespace: str, name: str) -> None:

        async def check_pod_deleted():
            try:
                await self._apis.core.read_namespaced_pod(
                    namespace=namespace,
                    name=name,
                )
                # We fetched the object successfully, so it hasn't been deleted.
                return False
            except kubernetes_asyncio.client.exceptions.ApiException as e:
                if (e.reason == 'Not Found'):
                    # We failed to find the object, so it's been deleted (which
                    # is what we've been waiting for.)
                    return True
                raise e

        await wait_for_state(check_pod_deleted, None)

    async def wait_for_deleted_with_prefix(
        self,
        *,
        namespace: str,
        name_prefix: str,
        seconds_between_api_calls: float = 0.2,
    ) -> None:
        pods_with_prefix = await self.list_for_name_prefix(
            namespace, name_prefix
        )
        for pod in pods_with_prefix:
            # Wait for each pod with the given prefix to be deleted.
            await self.wait_for_deleted(
                namespace=pod.metadata.namespace, name=pod.metadata.name
            )

    async def get_logs(
        self,
        namespace: str,
        name: str,
        container_name: str,
    ) -> str:

        async def retryable_get_logs():
            return await self._apis.core.read_namespaced_pod_log(
                name=name,
                namespace=namespace,
                container=container_name,
            )

        return await self._apis.retry_api_call(retryable_get_logs)

    async def follow_logs(
        self,
        *,
        namespace: str,
        name: str,
        container_name: Optional[str] = None,
    ) -> AsyncIterator[str]:
        w = kubernetes_asyncio.watch.Watch()
        async with w.stream(
            func=self._apis.core.read_namespaced_pod_log,
            name=name,
            namespace=namespace,
            container=container_name,
        ) as stream:
            async for line in stream:
                yield line
