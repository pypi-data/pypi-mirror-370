import asyncio
import kubernetes_asyncio
import rbt.cloud.v1alpha1.istio.gateway_spec_pb2 as gateway_spec_pb2
from google.protobuf.duration_pb2 import Duration
from kubernetes_utils.kubernetes_client import AbstractEnhancedKubernetesClient
from kubernetes_utils.ownership import OwnershipInformation
from kubernetes_utils.resources.services import Port
from log.log import get_logger
from rbt.cloud.v1alpha1.istio.virtual_service_spec_pb2 import (
    CorsPolicy,
    Destination,
    HTTPMatchRequest,
    HTTPRoute,
    HTTPRouteDestination,
    PortSelector,
    StringMatch,
)
from rbt.v1alpha1 import placement_planner_pb2
from reboot.controller.envoy_filter import EnvoyFilter
from reboot.controller.envoy_filter_generator import (
    FilterContext,
    generate_istio_routing_filter,
)
from reboot.controller.gateway import Gateway
from reboot.controller.placement_planner import PlacementPlanner
from reboot.controller.settings import (
    ISTIO_ALL_SIDECARS_GATEWAY_NAME,
    ISTIO_INGRESSGATEWAY_INTERNAL_PORT,
    ISTIO_INGRESSGATEWAY_LABEL_NAME,
    ISTIO_INGRESSGATEWAY_LABEL_VALUE,
    ISTIO_INGRESSGATEWAY_NAMESPACE,
    REBOOT_GATEWAY_NAME,
    REBOOT_GATEWAY_ROUTING_FILTER_NAME,
    REBOOT_GATEWAY_VIRTUAL_SERVICE_NAME,
    REBOOT_MESH_ROUTING_FILTER_NAME,
    REBOOT_MESH_VIRTUAL_SERVICE_NAME,
    REBOOT_ROUTABLE_HOSTNAME,
    USER_CONTAINER_GRPC_PORT,
    USER_CONTAINER_HTTP_PORT,
    USER_CONTAINER_WEBSOCKET_PORT,
)
from reboot.controller.virtual_service import VirtualService
from rebootdev.aio.headers import (
    APPLICATION_ID_HEADER,
    AUTHORIZATION_HEADER,
    CONSENSUS_ID_HEADER,
    IDEMPOTENCY_KEY_HEADER,
    STATE_REF_HEADER,
    WORKFLOW_ID_HEADER,
)
from rebootdev.aio.types import KubernetesNamespace
from rebootdev.helpers import get_path_prefixes_from_file_descriptor_set
from typing import Coroutine, Optional

logger = get_logger(__name__)

# Browsers will first send a CORS preflight request before sending an
# HTTP request and thus we need a relatively liberal policy.
#
# TODO(benh): let users specify origins for their applications and
# then reworking this to be more conservative.
#
# NOTE: if this CORS policy changes also consider if any changes need
# to be made in reboot/routing/envoy_config.py.
CORS_POLICY = CorsPolicy(
    allow_origins=[
        StringMatch(
            # While the name 'exact' suggests that the wildcard '*' won't work,
            # it in fact does.
            exact='*'
        )
    ],
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=[
        APPLICATION_ID_HEADER,
        STATE_REF_HEADER,
        CONSENSUS_ID_HEADER,
        IDEMPOTENCY_KEY_HEADER,
        WORKFLOW_ID_HEADER,
        'keep-alive',
        'user-agent',
        'cache-control',
        'content-type',
        'content-transfer-encoding',
        'x-accept-content-transfer-encoding',
        'x-accept-response-streaming',
        'x-user-agent',
        'grpc-timeout',
        AUTHORIZATION_HEADER,
    ],
    expose_headers=[
        'grpc-status',
        'grpc-message',
    ],
    max_age=Duration(seconds=1728000),
)


class KubernetesNetworkManager:
    """The KubernetesNetworkManager is the part of the controller that is
    responsible for managing the network configuration of the cluster. Most
    notably, it will create the `VirtualService` and `EnvoyFilter` objects
    needed to route traffic from reboot clients to the appropriate consensuses
    for serving.
    """

    def __init__(
        self,
        k8s_client: AbstractEnhancedKubernetesClient,
        placement_planner: PlacementPlanner,
        own_pod_metadata: kubernetes_asyncio.client.V1ObjectMeta,
    ):
        self._k8s_client = k8s_client
        self._own_pod_metadata = own_pod_metadata
        self._namespace = own_pod_metadata.namespace
        self._consensuses: list[placement_planner_pb2.Consensus] = []

        self._placement_planner = placement_planner
        self.plan_version = -1
        self._plan_processed = asyncio.Event()
        self._stop_event = asyncio.Event()

    async def wait_for_plan_version(self, version: int):
        """Returns once a placement plan with the given version number (or
        higher) has been processed, which may be immediately."""
        while self.plan_version < version:
            await self._plan_processed.wait()

    async def run(self) -> None:
        """Syntactic sugar for `start` and `wait`."""
        await self.start()
        await self.wait()

    async def wait(self) -> None:
        """Wait until we have stopped."""
        await self._stop_event.wait()

    async def _process_plan_with_consensuses(
        self,
        plan_with_consensuses: placement_planner_pb2.ListenForPlanResponse,
    ) -> None:
        """Process a new plan-with-locations as received via callback"""

        # We rely on `time.time_ns` to provide a monotonically increasing
        # version number for the plan. As the placement planner is running
        # in the same process it is highly unlikely that we would receive
        # a plan with a lower version number, unless someone is `mock`ing
        # `time.time_ns` in a test.
        assert self.plan_version <= plan_with_consensuses.plan.version

        self.plan_version = plan_with_consensuses.plan.version
        logger.info(
            'Received new plan with '
            f'{len(plan_with_consensuses.consensuses)} consensuses'
        )

        # Update our internal view of the world to match the new consensuses.
        await self._set_consensuses(plan_with_consensuses.consensuses)

        # Indicate to anyone currently listening that a plan has been processed.
        # Then immediately clear it again, so future listeners block until the
        # next plan is processed.
        self._plan_processed.set()
        self._plan_processed.clear()
        logger.info('Waiting for next plan...')

    def is_registered_for_callbacks(self) -> bool:
        return self._process_plan_with_consensuses in self._placement_planner.plan_change_callbacks

    async def start(self) -> None:
        """Subscribe to changes in the placement planner and start
        processing callbacks."""
        logger.info('Starting KubernetesNetworkManager')

        # Subscribe to new plans.
        self._placement_planner.plan_change_callbacks.add(
            self._process_plan_with_consensuses
        )

        # Eagerly process latest plan.
        await self._process_plan_with_consensuses(
            self._placement_planner.current_plan_with_consensuses
        )

    def stop(self) -> None:
        """Unsubscribe from placement planner updates and stop processing
        callbacks."""
        logger.info('Stopping KubernetesNetworkManager')

        # Unsubscribe from new plans.
        self._placement_planner.plan_change_callbacks.remove(
            self._process_plan_with_consensuses
        )

        # Notify all waiters that we are done.
        self._stop_event.set()

    def _make_virtual_service(
        self,
        *,
        name: str,
        gateway: str,
        hosts: list[str],
    ) -> Optional[VirtualService]:
        """Produces the `VirtualService` object appropriate for the Reboot
        gateway."""
        if len(self._consensuses) == 0:
            # If there are no consensuses, we don't need a VirtualService.
            # We also can't create an empty one; a VirtualService is required to
            # have at least one entry in its "http" list.
            return None

        # Every consensus gets routes to the websocket port, the gRPC
        # port, and the HTTP "catchall" port as described below.
        #
        # See corresponding routes for local Envoy in
        # reboot/routing/envoy_config.py.

        def websocket_routes():
            return [
                # There is only one route for websocket traffic which
                # requires both the 'x-reboot-consensus-id' header as
                # well as the 'upgrade' header indicating that it is
                # for a websocket.
                HTTPRoute(
                    name=f'websocket-route-to-{consensus.id}',
                    match=[
                        HTTPMatchRequest(
                            headers={
                                CONSENSUS_ID_HEADER:
                                    StringMatch(exact=consensus.id),
                                'upgrade':
                                    StringMatch(exact='websocket'),
                            },
                        )
                    ],
                    route=[
                        HTTPRouteDestination(
                            destination=Destination(
                                host=consensus.address.host,
                                # TODO(benh): propagate port
                                # through `ConsensusAddress`.
                                port=PortSelector(
                                    number=USER_CONTAINER_WEBSOCKET_PORT
                                )
                            ),
                        ),
                    ],
                    cors_policy=CORS_POLICY,
                ) for consensus in self._consensuses
            ]

        def grpc_routes():
            return [
                # This route sends all traffic with the
                # 'x-reboot-consensus-id' header and the
                # 'content-type: application/grpc' header to the gRPC
                # port.
                HTTPRoute(
                    name=f'grpc-route-to-{consensus.id}-with-content-type',
                    match=[
                        HTTPMatchRequest(
                            headers={
                                CONSENSUS_ID_HEADER:
                                    StringMatch(exact=consensus.id),
                                'content-type':
                                    StringMatch(exact='application/grpc'),
                            },
                        )
                    ],
                    route=[
                        HTTPRouteDestination(
                            destination=Destination(
                                host=consensus.address.host,
                                port=PortSelector(
                                    number=consensus.address.port
                                ),
                            ),
                        ),
                    ],
                    cors_policy=CORS_POLICY,
                ) for consensus in self._consensuses
            ] + [
                # This route sends all traffic with the
                # 'x-reboot-consensus-id' header and an exact path of
                # '/' to the gRPC port because currently that is what
                # serves '/'.
                HTTPRoute(
                    name=f'grpc-route-to-{consensus.id}-for-/',
                    match=[
                        HTTPMatchRequest(
                            headers={
                                CONSENSUS_ID_HEADER:
                                    StringMatch(exact=consensus.id),
                            },
                            uri=StringMatch(exact='/'),
                        )
                    ],
                    route=[
                        HTTPRouteDestination(
                            destination=Destination(
                                host=consensus.address.host,
                                port=PortSelector(
                                    number=consensus.address.port
                                ),
                            ),
                        ),
                    ],
                    cors_policy=CORS_POLICY,
                ) for consensus in self._consensuses
            ] + [
                # These routes send all traffic with the
                # 'x-reboot-consensus-id' header and a prefix path
                # from the file descriptor set of the application to
                # the gRPC port (where it will get gRPC-JSON
                # transcoded).
                HTTPRoute(
                    name=f'grpc-route-to-{consensus.id}-for-{prefix}',
                    match=[
                        HTTPMatchRequest(
                            headers={
                                CONSENSUS_ID_HEADER:
                                    StringMatch(exact=consensus.id),
                            },
                            uri=StringMatch(prefix=prefix),
                        )
                    ],
                    route=[
                        HTTPRouteDestination(
                            destination=Destination(
                                host=consensus.address.host,
                                port=PortSelector(
                                    number=consensus.address.port
                                ),
                            ),
                        ),
                    ],
                    cors_policy=CORS_POLICY,
                )
                for consensus in self._consensuses
                for prefix in get_path_prefixes_from_file_descriptor_set(
                    consensus.file_descriptor_set,
                )
                # We skip over the path '/' because we cover it above
                # as an exact path not a prefix here otherwise it
                # would catch everything which we don't want because
                # we want everything else to be caught below for the
                # HTTP port.
                if prefix != '/'
            ]

        def http_routes():
            return [
                # This is the "catchall" route for traffic that gets
                # sent to the HTTP port.
                HTTPRoute(
                    name=f'http-route-to-{consensus.id}',
                    match=[
                        HTTPMatchRequest(
                            headers={
                                CONSENSUS_ID_HEADER:
                                    StringMatch(exact=consensus.id),
                            },
                            uri=StringMatch(prefix='/'),
                        )
                    ],
                    route=[
                        HTTPRouteDestination(
                            destination=Destination(
                                host=consensus.address.host,
                                # TODO(benh): propagate port
                                # through `ConsensusAddress`.
                                port=PortSelector(
                                    number=USER_CONTAINER_HTTP_PORT
                                )
                            ),
                        ),
                    ],
                    cors_policy=CORS_POLICY,
                ) for consensus in self._consensuses
            ]

        return VirtualService(
            metadata=kubernetes_asyncio.client.V1ObjectMeta(
                namespace=self._namespace,
                name=name,
            ),
            spec=VirtualService.Spec(
                gateways=[gateway],
                hosts=hosts,
                # NOTE: ordering is important here! THe websockeet
                # routes need to come first as they are more specific
                # than the gRPC routes.
                http=websocket_routes() + grpc_routes() + http_routes(),
            )
        )

    def _make_virtual_service_for_mesh_traffic(
        self,
        name: str,
    ) -> Optional[VirtualService]:
        """Produces the `VirtualService` object appropriate for the current set
        of consensuses.
        """
        # The VirtualService we're constructing is intended to be applied to the
        # `mesh` gateway, which means: all sidecars in the Istio mesh. It is
        # then configured to (only) act on traffic routed to reboot's "routable
        # hostname". For a discussion on why that is, see the comments in
        # `_make_virtual_service_for_gateway_traffic()`.
        return self._make_virtual_service(
            name=name,
            gateway=ISTIO_ALL_SIDECARS_GATEWAY_NAME,
            hosts=[
                # The hostname without namespace is used by traffic that
                # has a `Service` with this name in their own namespace.
                REBOOT_ROUTABLE_HOSTNAME,
                # The hostname with namespace is used by traffic that does
                # not have a `Service` with this name in their own
                # namespace.
                f'{REBOOT_ROUTABLE_HOSTNAME}.{self._namespace}',
                # It's also allowed to specify the hostname with the full
                # Kubernetes domain name.
                f'{REBOOT_ROUTABLE_HOSTNAME}.{self._namespace}.svc.cluster.local',
            ]
        )

    def _make_virtual_service_for_gateway_traffic(
        self,
        name: str,
    ) -> Optional[VirtualService]:
        """Produces the `VirtualService` object appropriate for the gateways.
        """
        # The VirtualService we're constructing is intended to be applied to the
        # `reboot-gateway` gateway, which runs on the Istio ingress gateways.
        # There (and ONLY there) we want to accept traffic routed to any
        # hostname, most notably the hostnames the ingress gateways may use.
        #
        # This is a separate VirtualService from the one that handles mesh
        # traffic, because it's important that ONLY the gateways handle traffic
        # addressed to the gateways. It would be incorrect for sidecars in the
        # Istio mesh to handle gateway-bound traffic: gateway traffic likely
        # comes from pods that are part of the Istio mesh but are NOT part of a
        # Reboot application. Such pods do execute all `mesh` VirtualServices
        # (whose scope is all namespaces in the Istio mesh) but DON'T run the
        # Reboot routing filters (whose scope is all namespaces in a Reboot
        # application). It is a requirement for Reboot traffic that the
        # Reboot routing filter be applied before a VirtualService is
        # executed. On pods that don't run the routing filter, we must therefore
        # avoid having a `mesh` VirtualService that acts on the traffic. We do
        # this by scoping down the `mesh` VirtualService to only act on traffic
        # that is explicitly addressed to the Reboot routable hostname (which
        # is only ever used by Reboot applications), and not on traffic routed
        # to the Reboot gateways (which is used by non-Reboot applications).
        #
        # Instead, the VirtualService for mesh traffic will ignore traffic to
        # the gateways, allowing the gateways to do routing on behalf of these
        # non-Reboot pods. The following VirtualService is the one that will
        # do that routing on the gateways.
        #
        # Once traffic is at the gateway, we accept all traffic directed to all
        # hosts. That includes hostnames we've never heard of, since the
        # operator may have configured the ingress gateway with a hostname we
        # have no knowledge of.
        return self._make_virtual_service(
            name=name,
            gateway=REBOOT_GATEWAY_NAME,
            hosts=["*"],
        )

    async def _write_or_delete_virtual_service(
        self, name: str, virtual_service: Optional[VirtualService]
    ):
        if virtual_service is None:
            # Delete the VirtualService if it exists.
            logger.info(f'No VirtualService needed; deleting existing {name}')
            await self._k8s_client.custom_objects.delete_by_name(
                namespace=self._namespace,
                name=name,
                object_type=VirtualService,
            )
            return
        logger.debug(f'Writing VirtualService: {virtual_service.to_dict()}')
        await self._k8s_client.custom_objects.create_or_update(virtual_service)

    async def _write_virtual_services(self):
        """Writes the latest `VirtualService`s to Kubernetes."""
        # There are two VirtualServices: one for (Istio) mesh traffic (applied
        # to Istio's `mesh` gateway which deploys it on every sidecar in every
        # namespace that's part of Istio's mesh), and one for (Reboot) gateway
        # traffic (applied to the `rebootateway` gateway, which deploys it
        # ONLY on ingress gateway pods).
        #
        # The `mesh` VirtualService routes traffic from Reboot actors to other
        # Reboot actors point-to-point - thanks to the routing by the sidecars
        # we don't need to route through the gateways. This saves a hop, which
        # is important for performance: otherwise the gateways would have to
        # scale up with the intra-Reboot traffic, which will be a different
        # order of magnitude than the external traffic they're required to
        # handle.
        #
        # The `rebootateway` VirtualService routes traffic that's arrived at
        # a Gateway. It makes the same decisions as the `mesh` VirtualService,
        # but does so at a different place.
        #
        # These VirtualServices are separate, because it would be incorrect for
        # sidecars in the Istio mesh to act on gateway-bound traffic: gateway
        # traffic likely comes from pods that are part of the Istio mesh but are
        # NOT part of a Reboot application. Such pods do execute all `mesh`
        # VirtualServices (whose scope is all namespaces in the Istio mesh) but
        # DON'T run the Reboot routing filters (since the `EnvoyFilter`s that
        # configure those are scoped to only those namespaces that are also in a
        # Reboot application). It is a requirement for Reboot traffic that
        # the Reboot routing filter be applied before their VirtualService is
        # executed. On pods that don't run the routing filter, we must therefore
        # avoid having a VirtualService that acts on the traffic. We do this by
        # scoping down the `mesh` VirtualService to only act on traffic that is
        # explicitly addressed to the Reboot "routable hostname" (which is a
        # Reboot-internal name only ever used by Reboot applications), and
        # not on traffic routed to the Reboot gateways (which is used by
        # non-Reboot applications). The traffic bound for the Reboot
        # gateways will be run through the routing filter and
        # `reboot-gateway`'s virtual service once it reaches the gateway.
        name = REBOOT_MESH_VIRTUAL_SERVICE_NAME
        await self._write_or_delete_virtual_service(
            name, self._make_virtual_service_for_mesh_traffic(name)
        )
        name = REBOOT_GATEWAY_VIRTUAL_SERVICE_NAME
        await self._write_or_delete_virtual_service(
            name, self._make_virtual_service_for_gateway_traffic(name)
        )

    async def _write_routing_filters_for_mesh_traffic(
        self, namespaces: set[KubernetesNamespace]
    ):
        """Writes the latest routing filter `EnvoyFilter` for mesh (that is:
        Consensus-to-Consensus) traffic to Kubernetes.

        The argument `namespaces` specifies the kubernetes namespaces that
        should contain a routing filter. Our routing filter in these namespaces
        will be created or updated, while routing filters previously created by
        us in other namespaces will be deleted.
        """

        # A set of envoy filters that are no longer needed; we need to remove
        # these.
        obsolete_routing_filters: list[EnvoyFilter] = []

        # Find ALL the EnvoyFilters!
        existing_routing_filters, _ = await self._k8s_client.custom_objects.list_all(
            object_type=EnvoyFilter,
        )
        logger.debug(
            'Found %i routing filters...', len(existing_routing_filters)
        )

        # Loop over them, check if they are a) ours, b) desired.
        for existing_routing_filter in existing_routing_filters:
            name = existing_routing_filter.metadata.name
            namespace = existing_routing_filter.metadata.namespace

            if name != REBOOT_MESH_ROUTING_FILTER_NAME:
                # Not one of ours, skip.
                logger.debug(
                    "EnvoyFilter that is not a routing filter '%s' "
                    "encountered. Ignoring.", name
                )
                continue

            if namespace in namespaces:
                # We want to update this one, not remove it.
                logger.debug(
                    'Envoy filter in namespace %s should remain. Ignoring',
                    namespace
                )
                continue

            # Mark namespace for cleanup.
            obsolete_routing_filters.append(existing_routing_filter)

        # Remove our obsolete envoy filters.
        if len(obsolete_routing_filters) > 0:
            logger.info(
                'Removing envoy filter %s from the following namespaces: %s',
                REBOOT_MESH_ROUTING_FILTER_NAME,
                [
                    obsolete.metadata.namespace
                    for obsolete in obsolete_routing_filters
                ],
            )
            await asyncio.gather(
                *[
                    self._k8s_client.custom_objects.delete(obsolete)
                    for obsolete in obsolete_routing_filters
                ]
            )
        else:
            logger.info('No obsolete routing filters found')

        logger.info(
            'Writing routing filter to the following namespaces: %s',
            namespaces,
        )
        creations: list[Coroutine] = []
        for namespace in namespaces:
            # Get the `EnvoyFilter` representing our routing filter. That
            # object's `.metadata.name` is always the same, so we can safely use
            # `create_or_update` to update any previous version in-place.
            routing_filter: EnvoyFilter = generate_istio_routing_filter(
                namespace=namespace,
                name=REBOOT_MESH_ROUTING_FILTER_NAME,
                consensuses=self._consensuses,
                context=FilterContext.MESH,
            )
            logger.debug(f'Routing filter body: {routing_filter.to_dict()}')
            creations.append(
                self._k8s_client.custom_objects.
                create_or_update(routing_filter)
            )

        await asyncio.gather(*creations)

    async def _write_routing_filter_for_gateway_traffic(self):
        # Get the `EnvoyFilter` representing our routing filter. That object's
        # `.metadata.name` is always the same, so we can safely use
        # `create_or_update` to update any previous version in-place.
        routing_filter: EnvoyFilter = generate_istio_routing_filter(
            namespace=ISTIO_INGRESSGATEWAY_NAMESPACE,
            name=REBOOT_GATEWAY_ROUTING_FILTER_NAME,
            consensuses=self._consensuses,
            context=FilterContext.GATEWAY,
        )
        logger.debug(
            f'Writing gateway routing filter: {routing_filter.to_dict()}'
        )
        await self._k8s_client.custom_objects.create_or_update(routing_filter)

    async def _write_routable_service(self):
        """Writes the Kubernetes `Service` that gives us a single routable
        hostname for all services (and therefore actors) in the system.
        """
        await self._k8s_client.services.create_or_update(
            # There is one routable service for the entire Reboot system, so
            # we'll put it in the reboot system's own namespace.
            namespace=self._namespace,
            # The name of the routable service is a well-known string that all
            # clients use to contact any Reboot service.
            name=REBOOT_ROUTABLE_HOSTNAME,
            # The ports on which the routable service is reached is
            # universally known also.
            ports=[
                # To let this port serve gRPC traffic when there's an
                # intermediate Envoy proxy in gateway mode, this port
                # MUST be called "grpc".
                Port(port=USER_CONTAINER_GRPC_PORT, name="grpc"),
                # Port for WebSockets for browsers.
                Port(port=USER_CONTAINER_WEBSOCKET_PORT, name="websocket"),
                # Port for HTTP.
                Port(port=USER_CONTAINER_HTTP_PORT, name="http"),
            ],
            # We only need the routable service's hostname to exist and resolve,
            # it doesn't (shouldn't) point at any pods.
            deployment_label=None,
            # Unlike other objects created by the controller, this `Service`
            # isn't tied to a user action; it's an always-present part of the
            # system itself. Therefore, the controller itself is the owner of
            # the object.
            owner=OwnershipInformation.from_metadata(
                kind='Pod',
                api_version='v1',
                metadata=self._own_pod_metadata,
            )
        )

    async def _write_gateway(self):
        """Writes the Kubernetes `Gateway` that allows external traffic to
        reach the Reboot system.
        """
        # The Gateway object is an Istio configuration that instructs the Istio
        # gateway to accept traffic on a particular port. It also gives traffic
        # received on that port a name, which is used by VirtualServices to
        # name the traffic they'd like to be routing.
        await self._k8s_client.custom_objects.create_or_update(
            Gateway(
                metadata=kubernetes_asyncio.client.V1ObjectMeta(
                    namespace=self._namespace,
                    name=REBOOT_GATEWAY_NAME,
                ),
                spec=Gateway.Spec(
                    selector={
                        ISTIO_INGRESSGATEWAY_LABEL_NAME:
                            ISTIO_INGRESSGATEWAY_LABEL_VALUE
                    },
                    servers=[
                        gateway_spec_pb2.Server(
                            # Accept traffic for all hosts. We assume that if
                            # traffic can reach the gateway, we want to handle
                            # it.
                            hosts=['*'],
                            # Accept traffic on the following port.
                            #
                            # ISSUE(1529): this configures the gateway to accept
                            # (only) unencrypted traffic. Allow the user to
                            # configure their gateway to use TLS.
                            port=gateway_spec_pb2.Port(
                                number=ISTIO_INGRESSGATEWAY_INTERNAL_PORT,
                                name='grpc',
                                protocol='GRPC',
                            )
                        )
                    ]
                )
            )
        )

    async def _set_consensuses(
        self, consensuses: list[placement_planner_pb2.Consensus]
    ):
        """
        Sets the list of consensuses that the network manager knows about.
        """
        self._consensuses = consensuses

        # The routable service gives clients a hostname to connect to when
        # they want to talk to Reboot.
        await self._write_routable_service()

        # The Gateway allows external traffic to reach the Reboot system.
        await self._write_gateway()

        # The routing filter will select a consensus and set a consensus name
        # header based on the targeted service name and actor ID.
        # Invariant: All consensuses must have a namespace set!
        assert all([consensus.namespace for consensus in consensuses])
        namespaces: set[str] = {
            consensus.namespace
            for consensus in consensuses
            if consensus.namespace  # To satisfy mypy.
        }
        await self._write_routing_filters_for_mesh_traffic(namespaces)
        await self._write_routing_filter_for_gateway_traffic()

        # The VirtualServices direct connections to the appropriate consensus
        # based on their consensus name header.
        await self._write_virtual_services()
