import kubernetes_asyncio
from kubernetes_asyncio.client.exceptions import ApiException
from kubernetes_utils.api import KubernetesAPIs
from log.log import LoggerMixin


class AbstractNodes:

    # Named `list_all` instead of `list` to not conflict with the built-in
    # Python keyword.
    async def list_all(self) -> list[kubernetes_asyncio.client.V1Node]:
        """Get a list of all nodes in the cluster."""
        raise NotImplementedError

    async def add_label(
        self, node_name: str, label_name: str, label_value: str
    ) -> None:
        """
        Label a node with the given name with the given label.
        """
        raise NotImplementedError


class Nodes(LoggerMixin, AbstractNodes):
    """An implementation of `AbstractNodes` that uses the real
    Kubernetes API.
    """

    def __init__(self, apis: KubernetesAPIs):
        super().__init__()
        self._apis = apis

    async def list_all(self) -> list[kubernetes_asyncio.client.V1Node]:

        async def retryable_get_nodes() -> list[str]:
            # Use the synchronous k8s API to handle fetching and labeling nodes
            # in cluster setup. Although the async API also has the same
            # functions listed, empirically, they throw InvalidUrl errors when
            # called.
            nodes = await self._apis.core.list_node()
            return nodes.items

        return await self._apis.retry_api_call(retryable_get_nodes)

    async def add_label(
        self, node_name: str, label_name: str, label_value: str
    ) -> None:

        async def retryable_label_node() -> None:
            # Fetch the node. This must be done inside this retryable function,
            # since it's possible that by the time we call `patch` below, the
            # node has changed, in which case both the `read_node` and the
            # `patch` need to be re-done.

            # Use the synchronous k8s API to handle fetching and labeling nodes
            # in cluster setup. Although the async API also has the same
            # functions listed, empirically, they throw InvalidUrl errors when
            # called.
            node = await self._apis.core.read_node(node_name)
            node.metadata.labels[label_name] = label_value
            # Update the node.
            await self._apis.core.patch_node(node_name, node)

        await self._apis.retry_api_call(
            retryable_label_node,
            additional_should_retry=lambda e: isinstance(e, ApiException),
        )
