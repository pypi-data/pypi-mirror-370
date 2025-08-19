# Support class methods that return that class's type: see
# https://stackoverflow.com/a/33533514
from __future__ import annotations

import kubernetes_asyncio
import os
import tempfile
from kubernetes_utils.api import KubernetesAPIs
from kubernetes_utils.resources.cluster_role_bindings import (
    AbstractClusterRoleBindings,
    ClusterRoleBindings,
)
from kubernetes_utils.resources.cluster_roles import (
    AbstractClusterRoles,
    ClusterRoles,
)
from kubernetes_utils.resources.config_maps import (
    AbstractConfigMaps,
    ConfigMaps,
)
from kubernetes_utils.resources.custom_objects import (
    AbstractCustomObjects,
    CustomObjects,
)
from kubernetes_utils.resources.custom_resource_definitions import (
    AbstractCustomResourceDefinitions,
    CustomResourceDefinitions,
)
from kubernetes_utils.resources.deployments import (
    AbstractDeployments,
    Deployments,
)
from kubernetes_utils.resources.namespaces import (
    AbstractNamespaces,
    Namespaces,
)
from kubernetes_utils.resources.nodes import AbstractNodes, Nodes
from kubernetes_utils.resources.persistent_volume_claims import (
    AbstractPersistentVolumeClaims,
    PersistentVolumeClaims,
)
from kubernetes_utils.resources.pods import AbstractPods, Pods
from kubernetes_utils.resources.role_bindings import (
    AbstractRoleBindings,
    RoleBindings,
)
from kubernetes_utils.resources.roles import AbstractRoles, Roles
from kubernetes_utils.resources.secrets import AbstractSecrets, Secrets
from kubernetes_utils.resources.service_accounts import (
    AbstractServiceAccounts,
    ServiceAccounts,
)
from kubernetes_utils.resources.services import AbstractServices, Services
from kubernetes_utils.resources.storage_classes import (
    AbstractStorageClasses,
    StorageClasses,
)


class AbstractEnhancedKubernetesClient:

    def __init__(
        self,
        # Subclasses of the AbstractEnhancedKubernetesClient are expected to
        # pass in implementations for all `Abstract*` classes they care about.
        # Not all implementations care about all classes; it's OK to leave
        # any/all of them as the default `Abstract*` implementations. Those
        # will throw runtime errors if called.
        pods: AbstractPods = AbstractPods(),
        deployments: AbstractDeployments = AbstractDeployments(),
        services: AbstractServices = AbstractServices(),
        custom_objects: AbstractCustomObjects = AbstractCustomObjects(),
        custom_resource_definitions:
        AbstractCustomResourceDefinitions = AbstractCustomResourceDefinitions(
        ),
        namespaces: AbstractNamespaces = AbstractNamespaces(),
        roles: AbstractRoles = AbstractRoles(),
        role_bindings: AbstractRoleBindings = AbstractRoleBindings(),
        cluster_roles: AbstractClusterRoles = AbstractClusterRoles(),
        cluster_role_bindings:
        AbstractClusterRoleBindings = AbstractClusterRoleBindings(),
        service_accounts: AbstractServiceAccounts = AbstractServiceAccounts(),
        secrets: AbstractSecrets = AbstractSecrets(),
        nodes: AbstractNodes = AbstractNodes(),
        storage_classes: AbstractStorageClasses = AbstractStorageClasses(),
        persistent_volume_claims:
        AbstractPersistentVolumeClaims = AbstractPersistentVolumeClaims(),
        config_maps: AbstractConfigMaps = AbstractConfigMaps(),
    ):
        self.pods = pods
        self.deployments = deployments
        self.services = services
        self.custom_objects = custom_objects
        self.custom_resource_definitions = custom_resource_definitions
        self.namespaces = namespaces
        self.roles = roles
        self.role_bindings = role_bindings
        self.cluster_roles = cluster_roles
        self.cluster_role_bindings = cluster_role_bindings
        self.service_accounts = service_accounts
        self.secrets = secrets
        self.nodes = nodes
        self.storage_classes = storage_classes
        self.persistent_volume_claims = persistent_volume_claims
        self.config_maps = config_maps

    def is_alive(self) -> bool:
        """Check whether the k8s client is up."""
        raise NotImplementedError


class EnhancedKubernetesClient(AbstractEnhancedKubernetesClient):

    @classmethod
    async def create_incluster_client(cls) -> EnhancedKubernetesClient:
        """
        Use this function to get a new EnhancedKubernetesClient instance when
        running inside of a Kubernetes cluster and wanting to communicate with
        that cluster.

        If you want to communicate with any other Kubernetes cluster, regardless
        of where you are running, please use `create_client()`.

        NOTE: we have made this an `async` function even though there are no
        `await`s to keep parity with `create_client()` so any refactors don't
        end up causing a runtime error, e.g., due to forgetting to await a
        coroutine.
        """
        # We validate that we are in fact "in cluster" (i.e., in a pod
        # on k8s) by checking for the presence of the
        # `KUBERNETES_SERVICE_HOST` environment variable, which is
        # always set when we're running inside a cluster.
        if os.environ.get('KUBERNETES_SERVICE_HOST') is None:
            raise ValueError(
                'Can not call `create_incluster_client()` when '
                'not running in a Kubernetes cluster'
            )

        # NOTE: `kubernetes_asyncio.config.load_kube_config()` is
        # async, `kubernetes_asyncio.config.load_incluster_config()`
        # is not.
        kubernetes_asyncio.config.load_incluster_config()

        return cls(k8s_config_initialized=True)

    @classmethod
    async def create_client(cls, context: str) -> EnhancedKubernetesClient:
        """
        Use this function to get a new EnhancedKubernetesClient instance.

        We must initialize the cluster configuration for the
        EnhancedKubernetesClient outside of the __init__ function because some
        of the potential initialization functions are async.

        Args:
          context: the name of a Kubernetes context.
        """
        await kubernetes_asyncio.config.load_kube_config(context=context)

        return cls(k8s_config_initialized=True)

    @classmethod
    async def create_client_from_kubeconfig(
        cls, kubeconfig: str
    ) -> EnhancedKubernetesClient:
        # The kubernetes_asyncio library can only load a kubeconfig from a file
        # (or a dict, but that's not useful here). So we write the kubeconfig to
        # a temporary file for it to read.
        with tempfile.NamedTemporaryFile() as f:
            f.write(kubeconfig.encode())
            f.flush()
            await kubernetes_asyncio.config.load_kube_config(
                config_file=f.name
            )
            return cls(k8s_config_initialized=True)

    def __init__(self, k8s_config_initialized: bool = False):
        self._apis = KubernetesAPIs(k8s_config_initialized)
        super().__init__(
            pods=Pods(self._apis),
            deployments=Deployments(self._apis),
            services=Services(self._apis),
            custom_objects=CustomObjects(self._apis),
            custom_resource_definitions=CustomResourceDefinitions(self._apis),
            namespaces=Namespaces(self._apis),
            roles=Roles(self._apis),
            role_bindings=RoleBindings(self._apis),
            cluster_roles=ClusterRoles(self._apis),
            cluster_role_bindings=ClusterRoleBindings(self._apis),
            service_accounts=ServiceAccounts(self._apis),
            secrets=Secrets(self._apis),
            nodes=Nodes(self._apis),
            storage_classes=StorageClasses(self._apis),
            persistent_volume_claims=PersistentVolumeClaims(self._apis),
            config_maps=ConfigMaps(self._apis),
        )

    async def close(self) -> None:
        """Close client connection(s)."""
        await self._apis.close()

    def is_alive(self) -> bool:
        # The real kubernetes never terminates.
        return True
