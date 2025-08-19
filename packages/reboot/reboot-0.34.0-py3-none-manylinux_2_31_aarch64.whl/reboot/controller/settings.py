# The ports that user containers will be asked to use to expose their Reboot
# servers. We will expose these ports via k8s Deployment/Service as well.
USER_CONTAINER_GRPC_PORT = 50051
USER_CONTAINER_WEBSOCKET_PORT = 50052
USER_CONTAINER_HTTP_PORT = 50053

# On Kubernetes we use labels to identify which pods are Reboot applications,
# and what their consensuses are called. This defines what those labels are
# called.
IS_REBOOT_APPLICATION_LABEL_NAME = 'reboot.dev/is-reboot-application'
IS_REBOOT_APPLICATION_LABEL_VALUE = 'true'
REBOOT_CONSENSUS_ID_LABEL_NAME = 'reboot.dev/reboot-consensus-id'
REBOOT_APPLICATION_ID_LABEL_NAME = 'reboot.dev/reboot-application-id'

# On Kubernetes, how can we identify the Istio ingress gateways?
# ISSUE(1529): this should likely be something a cluster operator can configure.
#              The following are the settings that our LocalKubernetes gets when
#              it installs Istio using Istio's `demo` profile.
ISTIO_INGRESSGATEWAY_NAMESPACE = 'istio-system'
ISTIO_INGRESSGATEWAY_NAME = 'istio-ingressgateway'
# By "internal port" we mean the port that traffic already inside the Kubernetes
# cluster should use to access the Istio ingress gateway. This may differ from
# the port that external traffic from outside the Kubernetes cluster uses to
# reach the load balancer.
#
# TODO(rjh): change this to 9990 to be more unique and match the default
#            insecure port?
ISTIO_INGRESSGATEWAY_INTERNAL_PORT = 8080
ISTIO_INGRESSGATEWAY_LABEL_NAME = 'istio'
ISTIO_INGRESSGATEWAY_LABEL_VALUE = 'ingressgateway'

# In an Istio `VirtualService`, how do we address all Istio sidecars?
ISTIO_ALL_SIDECARS_GATEWAY_NAME = 'mesh'

# Labels that need to be set on a namespace in order for Istio to do sidecar
# injection.
ISTIO_NAMESPACE_LABELS = {
    # Required to be set in order for Istio to inject sidecars into a Reboot
    # namespace.
    'istio-injection': 'enabled',
}

# The reboot system requires two Kubernetes namespaces: one for the system
# itself, and one to place `ApplicationDeployment`s. What are these namespaces
# called?
REBOOT_SYSTEM_NAMESPACE = 'reboot-system'
REBOOT_APPLICATION_DEPLOYMENT_NAMESPACE = 'reboot-application-deployments'

# On Kubernetes, some objects need fixed names.
REBOOT_MESH_VIRTUAL_SERVICE_NAME = 'network-managers-mesh-virtual-service'
REBOOT_GATEWAY_VIRTUAL_SERVICE_NAME = 'network-managers-gateway-virtual-service'
REBOOT_MESH_ROUTING_FILTER_NAME = 'network-managers-mesh-routing-envoy-filter'
REBOOT_GATEWAY_ROUTING_FILTER_NAME = 'network-managers-gateway-routing-envoy-filter'
REBOOT_GATEWAY_NAME = 'reboot-gateway'

# On Kubernetes, the Reboot system will offer a fixed hostname that clients
# use when they want to talk to any Reboot service.
REBOOT_ROUTABLE_HOSTNAME = 'reboot-service'

# The memory limits for Reboot applications on Kubernetes.
# TODO: support "T-shirt sizes", so that users can choose between cost
#       and memory capacity.
#
# Reboot's customer applications get a solid chunk of memory, but little
# enough that they should be easy to schedule.
REBOOT_APPLICATION_MEMORY_LIMIT = '2Gi'
REBOOT_APPLICATION_MEMORY_REQUEST = '512Mi'
# Config pods load the whole application, but don't run any part of it.
# They should not take a lot of memory.
REBOOT_CONFIG_POD_MAIN_MEMORY_LIMIT = '512Mi'
REBOOT_CONFIG_POD_MAIN_MEMORY_REQUEST = '256Mi'
# The "wait-for-facilitator" pod is a very small application, but since
# it's built in Python on our big base image we don't want to give it
# too little memory.
REBOOT_WAIT_FOR_FACILITATOR_MEMORY_LIMIT = '512Mi'
REBOOT_WAIT_FOR_FACILITATOR_MEMORY_REQUEST = '128Mi'
# Fluent Bit is very compact, but in case of facilitator outages it may
# need to buffer a lot of logs, so we give it a bit more memory than we
# think it normally needs.
REBOOT_FLUENT_BIT_MEMORY_LIMIT = '512Mi'
REBOOT_FLUENT_BIT_MEMORY_REQUEST = '64Mi'
# The Reboot controller needs ~200MiB of memory in small clusters, but
# we give it plenty more to allow for growth.
REBOOT_CONTROLLER_MEMORY_LIMIT = '1Gi'
REBOOT_CONTROLLER_MEMORY_REQUEST = '256Mi'

### Environment variables.
# We use environment variables when we need to communicate information between
# processes. Our naming convention is as follows:
#   `ENVVAR_<SOMETHING>` is the name of an environment variable.
#   `<SOMETHING>_<VALUE-NAME>` is one VALUE the `SOMETHING` environment
#    variable might take.

# Space ID injected via an environment variable.
ENVVAR_REBOOT_SPACE_ID = 'REBOOT_SPACE_ID'
# Application ID injected via an environment variable.
ENVVAR_REBOOT_APPLICATION_ID = 'REBOOT_APPLICATION_ID'
# Consensus ID injected via an environment variable.
ENVVAR_REBOOT_CONSENSUS_ID = 'REBOOT_CONSENSUS_ID'

# Kubernetes pod metadata injected via environment variables.
ENVVAR_KUBERNETES_POD_UID = 'REBOOT_KUBERNETES_POD_UID'
ENVVAR_KUBERNETES_POD_NAME = 'REBOOT_KUBERNETES_POD_NAME'
ENVVAR_KUBERNETES_POD_NAMESPACE = 'REBOOT_KUBERNETES_POD_NAMESPACE'
ENVVAR_KUBERNETES_SERVICE_ACCOUNT = 'REBOOT_KUBERNETES_SERVICE_ACCOUNT'

# Gives the mode in which a Reboot application is expected to be started.
# Present on any Reboot config pod.
ENVVAR_REBOOT_MODE = 'REBOOT_MODE'
REBOOT_MODE_CONFIG = 'config'  # Start the server as a config server.

# Gives the port on which a config-mode server is expected to start serving.
# Present on any Reboot config pod.
ENVVAR_REBOOT_CONFIG_SERVER_PORT = 'REBOOT_CONFIG_SERVER_PORT'

# Gives the port on which an `rbt serve` application is expected to serve its
# application.
ENVVAR_PORT = 'PORT'

ENVVAR_RBT_PORT = 'RBT_PORT'

ENVVAR_REBOOT_STORAGE_TYPE = 'REBOOT_STORAGE_TYPE'

ENVVAR_REBOOT_FACILITATOR_IMAGE_NAME = 'REBOOT_FACILITATOR_IMAGE_NAME'

ENVVAR_REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME = 'REBOOT_WAIT_FOR_HEALTHY_IMAGE_NAME'

ENVVAR_REBOOT_FLUENT_BIT_IMAGE_NAME = 'REBOOT_FLUENT_BIT_IMAGE_NAME'

# The application ID of the Reboot application hosting the `AdminAuth` service.
ENVVAR_REBOOT_ADMIN_AUTH_APPLICATION_ID = 'REBOOT_ADMIN_AUTH_APPLICATION_ID'
