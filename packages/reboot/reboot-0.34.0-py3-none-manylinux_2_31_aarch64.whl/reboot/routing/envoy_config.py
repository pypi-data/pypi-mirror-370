import enum
import math
from dataclasses import dataclass
from envoy.config.cluster.v3 import circuit_breaker_pb2, cluster_pb2
from envoy.config.core.v3 import address_pb2, base_pb2, protocol_pb2
from envoy.config.endpoint.v3 import endpoint_components_pb2, endpoint_pb2
from envoy.config.listener.v3 import listener_components_pb2, listener_pb2
from envoy.config.route.v3 import route_components_pb2, route_pb2
from envoy.extensions.filters.http.cors.v3 import cors_pb2
from envoy.extensions.filters.http.grpc_json_transcoder.v3 import (
    transcoder_pb2,
)
from envoy.extensions.filters.http.lua.v3 import lua_pb2
from envoy.extensions.filters.http.router.v3 import router_pb2
from envoy.extensions.filters.network.http_connection_manager.v3 import (
    http_connection_manager_pb2,
)
from envoy.extensions.transport_sockets.tls.v3 import common_pb2, tls_pb2
from envoy.extensions.upstreams.http.v3 import http_protocol_options_pb2
from envoy.type.matcher.v3 import regex_pb2, string_pb2
from google.protobuf import any_pb2
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from google.protobuf.duration_pb2 import Duration
from google.protobuf.message import Message
from google.protobuf.wrappers_pb2 import UInt32Value
from pathlib import Path
from reboot.routing.filters.lua import (
    ADD_HEADER_X_REBOOT_APPLICATION_ID_TEMPLATE_FILENAME,
    COMPUTE_HEADER_X_REBOOT_CONSENSUS_ID_TEMPLATE_FILENAME,
    MANGLED_HTTP_PATH_FILENAME,
    load_lua,
    render_lua_template,
)
from rebootdev.aio.headers import (
    APPLICATION_ID_HEADER,
    AUTHORIZATION_HEADER,
    CONSENSUS_ID_HEADER,
    IDEMPOTENCY_KEY_HEADER,
    STATE_REF_HEADER,
    WORKFLOW_ID_HEADER,
)
from rebootdev.aio.types import ApplicationId, ConsensusId
from rebootdev.helpers import get_path_prefixes_from_file_descriptor_set
from rebootdev.settings import MAX_GRPC_RESPONSE_SIZE_BYTES


@dataclass
class ConsensusInfo:
    consensus_id: ConsensusId
    host: str
    grpc_port: int
    websocket_port: int
    http_port: int


class ClusterKind(enum.Enum):
    GRPC = enum.auto()
    WEBSOCKET = enum.auto()
    HTTP = enum.auto()


ZERO_SECONDS = Duration()
ZERO_SECONDS.FromSeconds(0)


# Helper for packing an `Any`.
#
# TODO: replace with `from google.protobuf.any import pack` once we've
# upgraded to a version of protobuf that includes this.
def any_pack(message: Message) -> any_pb2.Any:
    any = any_pb2.Any()
    any.Pack(message)
    return any


def _shard_keyrange_starts(num_shards: int) -> list[int]:
    NUM_BYTE_VALUES = 256
    if num_shards > NUM_BYTE_VALUES:
        raise ValueError(
            f"'num_shards' must be less than or equal to "
            f"{NUM_BYTE_VALUES}; got {num_shards}."
        )
    if not math.log2(num_shards).is_integer():
        raise ValueError(
            f"'num_shards' must be a power of 2; got {num_shards}."
        )
    shard_size = NUM_BYTE_VALUES // num_shards
    # The first shard always begins at the very beginning of the key range.
    return [i * shard_size for i in range(0, num_shards)]


def _lua_any(source_code: str) -> any_pb2.Any:
    return any_pack(
        lua_pb2.Lua(
            default_source_code=base_pb2.DataSource(
                inline_string=source_code,
            ),
        )
    )


def _http_filter_add_header_x_reboot_application_id(
    application_id: ApplicationId
) -> http_connection_manager_pb2.HttpFilter:
    template_input = {
        'application_id': application_id,
    }
    filter_content = render_lua_template(
        ADD_HEADER_X_REBOOT_APPLICATION_ID_TEMPLATE_FILENAME, template_input
    )

    return http_connection_manager_pb2.HttpFilter(
        name="reboot.add_header_x_reboot_application_id",
        # TODO(rjh): can we replace this with a standard add-header filter?
        typed_config=_lua_any(filter_content)
    )


@dataclass
class RouteMapEntry:
    # The start of this shard's key range. Conceptually this represents a single
    # `byte`, but we store it as an `int` for easier embedding in Lua source
    # code.
    shard_keyrange_start: int
    # The consensus ID that traffic matching this entry should get sent to.
    consensus_id: ConsensusId


def _http_filter_compute_header_x_reboot_consensus_id(
    consensuses: list[ConsensusInfo],
) -> http_connection_manager_pb2.HttpFilter:
    consensus_ids = [consensus.consensus_id for consensus in consensuses]
    # Since the order of `consensus_ids` is not deterministic, we need to sort
    # them to ensure that the order of the shards is deterministic.
    consensus_ids.sort()

    shard_keyrange_starts = _shard_keyrange_starts(len(consensus_ids))
    route_map = [
        RouteMapEntry(
            # To safely embed an arbitrary byte in textual Lua source
            # code, we represent it as an int.
            shard_keyrange_start=int(shard_keyrange_start),
            consensus_id=consensus_id
        ) for shard_keyrange_start, consensus_id in
        zip(shard_keyrange_starts, consensus_ids)
    ]

    template_input = {
        'consensus_ids': consensus_ids,
        'route_map': route_map,
    }
    filter_content = render_lua_template(
        COMPUTE_HEADER_X_REBOOT_CONSENSUS_ID_TEMPLATE_FILENAME, template_input
    )
    return http_connection_manager_pb2.HttpFilter(
        name="reboot.compute_header_x_reboot_consensus_id",
        typed_config=_lua_any(filter_content),
    )


def _http_filter_mangled_http_path() -> http_connection_manager_pb2.HttpFilter:
    # The contents of the MANGLED_HTTP_PATH_FILENAME Lua file need to still be
    # wrapped in an `envoy_on_request` function, since `routing_filter.lua.j2`
    # also uses the same content.
    filter_content = (
        "function envoy_on_request(request_handle)\n"
        f"{load_lua(MANGLED_HTTP_PATH_FILENAME)}\n"
        "end\n"
    )
    return http_connection_manager_pb2.HttpFilter(
        name="reboot.mangled_http_path",
        typed_config=_lua_any(filter_content),
    )


def _http_filter_cors() -> http_connection_manager_pb2.HttpFilter:
    # TODO(rjh): set the `cors` policy here, instead of in `VirtualHost`; the
    #            latter is deprecated. Share code with `network_managers.py`.
    return http_connection_manager_pb2.HttpFilter(
        name="envoy.filters.http.cors",
        typed_config=any_pack(cors_pb2.Cors()),
    )


GRPC_JSON_TRANSCODER_HTTP_FILTER_NAME = "envoy.filters.http.grpc_json_transcoder"

# For those routes where we don't need the transcoding filter we have
# an empty configuration so it never activates (without this it has
# been shown to confuse the traffic).
EMPTY_GRPC_JSON_TRANSCODER_CONFIG = any_pack(
    transcoder_pb2.GrpcJsonTranscoder(
        # This field's presence is required (the listener will be rejected
        # without it), but we can leave it empty.
        proto_descriptor_bin=b"",
    )
)


def _http_filter_grpc_json_transcoder(
    file_descriptor_set: FileDescriptorSet,
) -> http_connection_manager_pb2.HttpFilter:
    return http_connection_manager_pb2.HttpFilter(
        name=GRPC_JSON_TRANSCODER_HTTP_FILTER_NAME,
        typed_config=any_pack(
            # ATTENTION: if you update any of this, also update the matching
            #            values in `envoy_filter_generator.py` method
            #            `generate_transcoding_filter`.
            # TODO(rjh): either obsolete `generate_transcoding_filter`,
            #            or use it, or share settings at least.
            transcoder_pb2.GrpcJsonTranscoder(
                convert_grpc_status=True,
                print_options=transcoder_pb2.GrpcJsonTranscoder.PrintOptions(
                    add_whitespace=True,
                    always_print_enums_as_ints=False,
                    always_print_primitive_fields=True,
                    preserve_proto_field_names=False,
                ),
                # The gRPC backend would be unhappy to receive
                # non-gRPC `application/json` traffic and would reply
                # with a `503`, which is not a good user experience
                # and not helpful in debugging. In addition, we've
                # observed that that interaction between Envoy and
                # gRPC triggers a bug in one of those two that will
                # cause subsequent valid requests to fail.
                #
                # See: https://github.com/reboot-dev/mono/issues/3074.
                #
                # Instead, simply (correctly) reject invalid
                # `application/json` traffic with a 404.
                request_validation_options=(
                    transcoder_pb2.GrpcJsonTranscoder.RequestValidationOptions(
                        reject_unknown_method=True,
                    )
                ),
                services=[
                    f"{file_descriptor_proto.package}.{service.name}"
                    for file_descriptor_proto in file_descriptor_set.file
                    for service in file_descriptor_proto.service
                ],
                proto_descriptor_bin=file_descriptor_set.SerializeToString(),
            )
        )
    )


def _http_filter_router() -> http_connection_manager_pb2.HttpFilter:
    return http_connection_manager_pb2.HttpFilter(
        name="envoy.filters.http.router",
        typed_config=any_pack(router_pb2.Router()),
    )


def _routes_for_consensus(
    application_id: ApplicationId,
    consensus: ConsensusInfo,
    kind: ClusterKind,
    file_descriptor_set: FileDescriptorSet,
) -> list[route_components_pb2.Route]:
    # Every consensus gets routes to the websocket port, the gRPC
    # port, and the HTTP "catchall" port as described below.
    #
    # See corresponding routes for Istio in
    # reboot/controller/network_managers.py.

    cluster_name = _cluster_name(
        application_id=application_id,
        consensus_id=consensus.consensus_id,
        kind=kind,
    )

    consensus_header_matcher = route_components_pb2.HeaderMatcher(
        name=CONSENSUS_ID_HEADER,
        string_match=string_pb2.StringMatcher(
            exact=consensus.consensus_id,
        ),
    )

    if kind == ClusterKind.GRPC:
        return [
            # This route sends all traffic with the
            # 'x-reboot-consensus-id' header and the 'content-type:
            # application/grpc' header to the gRPC port.
            route_components_pb2.Route(
                match=route_components_pb2.RouteMatch(
                    prefix="/",
                    headers=[
                        consensus_header_matcher,
                        route_components_pb2.HeaderMatcher(
                            name="content-type",
                            string_match=string_pb2.StringMatcher(
                                exact="application/grpc",
                            ),
                        ),
                    ],
                    grpc=route_components_pb2.RouteMatch.GrpcRouteMatchOptions(
                    ),
                ),
                route=route_components_pb2.RouteAction(
                    cluster=cluster_name,
                    max_stream_duration=route_components_pb2.RouteAction.
                    MaxStreamDuration(grpc_timeout_header_max=ZERO_SECONDS)
                ),
            ),
            # This route sends all traffic with the
            # 'x-reboot-consensus-id' header and an exact path of '/'
            # to the gRPC port because currently that is what serves
            # '/'.
            route_components_pb2.Route(
                match=route_components_pb2.RouteMatch(
                    path="/",
                    headers=[consensus_header_matcher],
                    grpc=route_components_pb2.RouteMatch.GrpcRouteMatchOptions(
                    ),
                ),
                route=route_components_pb2.RouteAction(
                    cluster=cluster_name,
                    max_stream_duration=route_components_pb2.RouteAction.
                    MaxStreamDuration(grpc_timeout_header_max=ZERO_SECONDS)
                ),
            ),
        ] + [
            # These routes send all traffic with the
            # 'x-reboot-consensus-id' header and a prefix path from
            # the file descriptor set of the application to the gRPC
            # port (where it will get gRPC-JSON transcoded).
            route_components_pb2.Route(
                match=route_components_pb2.RouteMatch(
                    prefix=prefix,
                    headers=[consensus_header_matcher],
                ),
                route=route_components_pb2.RouteAction(
                    cluster=cluster_name,
                    max_stream_duration=route_components_pb2.RouteAction.
                    MaxStreamDuration(grpc_timeout_header_max=ZERO_SECONDS)
                ),
            ) for prefix in get_path_prefixes_from_file_descriptor_set(
                file_descriptor_set,
            )
            # We skip over the path '/' because we cover it above as
            # an exact path not a prefix here otherwise it would catch
            # everything which we don't want because we want
            # everything else to be caught below for the HTTP port.
            if prefix != "/"
        ]

    elif kind == ClusterKind.HTTP:
        return [
            route_components_pb2.Route(
                match=route_components_pb2.RouteMatch(
                    prefix="/",
                    headers=[consensus_header_matcher],
                ),
                route=route_components_pb2.RouteAction(cluster=cluster_name),
                typed_per_filter_config={
                    GRPC_JSON_TRANSCODER_HTTP_FILTER_NAME:
                        EMPTY_GRPC_JSON_TRANSCODER_CONFIG,
                },
            )
        ]

    assert kind == ClusterKind.WEBSOCKET

    return [
        route_components_pb2.Route(
            match=route_components_pb2.RouteMatch(
                prefix="/",
                headers=[
                    route_components_pb2.HeaderMatcher(
                        name="upgrade",
                        string_match=string_pb2.StringMatcher(
                            exact="websocket",
                        ),
                    ),
                    consensus_header_matcher,
                ],
            ), route=route_components_pb2.RouteAction(cluster=cluster_name),
            typed_per_filter_config={
                GRPC_JSON_TRANSCODER_HTTP_FILTER_NAME:
                    EMPTY_GRPC_JSON_TRANSCODER_CONFIG,
            }
        )
    ]


def _filter_http_connection_manager(
    application_id: ApplicationId,
    consensuses: list[ConsensusInfo],
    file_descriptor_set: FileDescriptorSet,
) -> listener_components_pb2.Filter:
    http_connection_manager = http_connection_manager_pb2.HttpConnectionManager(
        stat_prefix="grpc_json",
        stream_idle_timeout=ZERO_SECONDS,
        upgrade_configs=[
            http_connection_manager_pb2.HttpConnectionManager.UpgradeConfig(
                upgrade_type="websocket",
            ),
        ],
        # TODO(rjh): this is a duration; but leaving out is the same as 0s, presumably?
        # stream_idle_timeout="0s",
        codec_type=http_connection_manager_pb2.HttpConnectionManager.AUTO,
        route_config=route_pb2.RouteConfiguration(
            name="local_route",
            virtual_hosts=[
                route_components_pb2.VirtualHost(
                    name="local_service",
                    domains=["*"],
                    # TODO(rjh): setting the `cors` policy here is deprecated,
                    #            instead we should set it directly on the
                    #            `envoy.filters.http.cors` filter in the filter
                    #            chain.
                    cors=route_components_pb2.CorsPolicy(
                        allow_origin_string_match=[
                            string_pb2.StringMatcher(
                                safe_regex=regex_pb2.RegexMatcher(
                                    # TODO(rjh): deprecated; can remove?
                                    google_re2=regex_pb2.RegexMatcher.
                                    GoogleRE2(),
                                    regex="\\*",
                                ),
                            )
                        ],
                        allow_methods="GET, PUT, DELETE, POST, OPTIONS",
                        allow_headers=
                        f"{APPLICATION_ID_HEADER},{STATE_REF_HEADER},{CONSENSUS_ID_HEADER},{IDEMPOTENCY_KEY_HEADER},{WORKFLOW_ID_HEADER},keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,x-accept-content-transfer-encoding,x-accept-response-streaming,x-user-agent,grpc-timeout,{AUTHORIZATION_HEADER}",
                        max_age="1728000",
                        expose_headers="grpc-status,grpc-message",
                    ),
                    routes=[
                        route for consensus in consensuses for kind in [
                            # Always list the route for the websocket first,
                            # since its matching is more specific.
                            ClusterKind.WEBSOCKET,
                            ClusterKind.GRPC,
                            ClusterKind.HTTP,
                        ] for route in _routes_for_consensus(
                            application_id=application_id,
                            consensus=consensus,
                            kind=kind,
                            file_descriptor_set=file_descriptor_set,
                        )
                    ],
                ),
            ],
        ),
        http_filters=[
            _http_filter_add_header_x_reboot_application_id(application_id),
            # Before picking a consensus, we need to possibly de-mangle the path
            # to extract any relevant headers.
            _http_filter_mangled_http_path(),
        ] + (
            [
                _http_filter_compute_header_x_reboot_consensus_id(consensuses),
            ] if len(consensuses) > 0 else []
        ) + [
            # Define CORS filter before the gRPC-JSON transcoding
            # filter, because otherwise perfectly-fine CORS requests
            # get rejected by the gRPC-JSON transcoding filter.
            _http_filter_cors(),
            # The gRPC-JSON transcoder filter comes before routing,
            # but note that we also need to override it for websocket
            # routes via a per-route config because otherwise it has
            # been shown to confuse traffic.
            _http_filter_grpc_json_transcoder(
                file_descriptor_set=file_descriptor_set,
            ),
            _http_filter_router(),
        ]
    )

    return listener_components_pb2.Filter(
        name="envoy.filters.network.http_connection_manager",
        typed_config=any_pack(http_connection_manager),
    )


def _tls_socket(
    certificate_path: Path, key_path: Path
) -> base_pb2.TransportSocket:
    return base_pb2.TransportSocket(
        name="envoy.transport_sockets.tls",
        typed_config=any_pack(
            tls_pb2.DownstreamTlsContext(
                common_tls_context=tls_pb2.CommonTlsContext(
                    alpn_protocols=["h2"],
                    tls_certificates=[
                        common_pb2.TlsCertificate(
                            certificate_chain=base_pb2.DataSource(
                                filename=str(certificate_path),
                            ),
                            private_key=base_pb2.DataSource(
                                filename=str(key_path),
                            ),
                        ),
                    ],
                    validation_context=common_pb2.CertificateValidationContext(
                        trusted_ca=base_pb2.DataSource(
                            filename=str(certificate_path),
                        ),
                    ),
                ),
            )
        ),
    )


def listener(
    application_id: ApplicationId,
    consensuses: list[ConsensusInfo],
    file_descriptor_set: FileDescriptorSet,
    port: int,
    use_tls: bool,
    certificate_path: Path,
    key_path: Path,
) -> listener_pb2.Listener:

    return listener_pb2.Listener(
        name="main",
        address=address_pb2.Address(
            socket_address=address_pb2.SocketAddress(
                address="0.0.0.0",
                port_value=port,
            ),
        ),
        filter_chains=[
            listener_components_pb2.FilterChain(
                filters=[
                    _filter_http_connection_manager(
                        application_id=application_id,
                        consensuses=consensuses,
                        file_descriptor_set=file_descriptor_set,
                    ),
                ],
                transport_socket=_tls_socket(certificate_path, key_path)
                if use_tls else None,
            )
        ],
        # See: https://github.com/reboot-dev/mono/issues/3944.
        per_connection_buffer_limit_bytes=UInt32Value(
            value=MAX_GRPC_RESPONSE_SIZE_BYTES
        ),
    )


def _cluster_name(
    application_id: ApplicationId, consensus_id: ConsensusId, kind: ClusterKind
) -> str:
    # There are two forms the `ConsensusId`s can take here, neither of which may
    # be what you might expect:
    #
    # A) If there are multiple consensuses, consensus IDs are of the shape
    #    `[application-id]-[consensus-id]`, e.g. `foo-c123456`.
    #
    # B) If there is only a single consensus, the consensus ID is the
    #    application ID.
    #
    # This is a leftover of how local consensus management and Kubernetes
    # consensus management used to overlap.
    #
    # TODO(rjh): sanify the 'application_id' and 'consensus_id' relationship.
    #            We'd expect a consensus ID to be e.g. `c123456`.
    assert (
        consensus_id.startswith(f"{application_id}-") or
        consensus_id == application_id
    ), f"invalid consensus ID '{consensus_id}'"

    if kind == ClusterKind.GRPC:
        return f"{consensus_id}_grpc"

    elif kind == ClusterKind.HTTP:
        return f"{consensus_id}_http"

    else:
        assert (kind == ClusterKind.WEBSOCKET)
        return f"{consensus_id}_websocket"


def _cluster(
    application_id: ApplicationId,
    consensus_id: ConsensusId,
    host: str,
    port: int,
    kind: ClusterKind,
) -> cluster_pb2.Cluster:
    cluster_name = _cluster_name(application_id, consensus_id, kind)
    return cluster_pb2.Cluster(
        name=cluster_name,
        type=cluster_pb2.Cluster.STRICT_DNS,
        lb_policy=cluster_pb2.Cluster.ROUND_ROBIN,
        common_http_protocol_options=protocol_pb2.HttpProtocolOptions(
            idle_timeout=ZERO_SECONDS,
        ),
        dns_lookup_family=cluster_pb2.Cluster.V4_ONLY,
        # Setting empty HTTP2 protocol options is required to encourage Envoy to
        # use HTTP2 when talking to the upstream, so we MUST set this for gRPC
        # traffic - and for gRPC traffic ONLY, because websockets are NOT HTTP2.
        # TODO(rjh): this field is deprecated; migrate to
        #            `typed_extension_protocol_options`:
        #            https://github.com/envoyproxy/envoy/blob/45e0325f8d7ddf64a396798803a3fb7e6717257a/api/envoy/config/cluster/v3/cluster.proto#L927
        http2_protocol_options=protocol_pb2.Http2ProtocolOptions()
        if kind == ClusterKind.GRPC else None,
        load_assignment=endpoint_pb2.ClusterLoadAssignment(
            cluster_name=cluster_name,
            endpoints=[
                endpoint_components_pb2.LocalityLbEndpoints(
                    lb_endpoints=[
                        endpoint_components_pb2.LbEndpoint(
                            endpoint=endpoint_components_pb2.Endpoint(
                                address=address_pb2.Address(
                                    socket_address=address_pb2.SocketAddress(
                                        address=host,
                                        port_value=port,
                                    )
                                )
                            )
                        )
                    ],
                )
            ],
        ),
        # "Disable" all circuit breakers; they don't make much sense when all
        # traffic will flow to the host we're already on. Follows the pattern
        # suggested here: Follows the pattern suggested here:
        #   https://www.envoyproxy.io/docs/envoy/latest/faq/load_balancing/disable_circuit_breaking
        circuit_breakers=circuit_breaker_pb2.CircuitBreakers(
            thresholds=[
                circuit_breaker_pb2.CircuitBreakers.Thresholds(
                    priority=base_pb2.RoutingPriority.DEFAULT,
                    max_connections=UInt32Value(value=1000000000),
                    max_pending_requests=UInt32Value(value=1000000000),
                    max_requests=UInt32Value(value=1000000000),
                    max_retries=UInt32Value(value=1000000000),
                ),
                circuit_breaker_pb2.CircuitBreakers.Thresholds(
                    priority=base_pb2.RoutingPriority.HIGH,
                    max_connections=UInt32Value(value=1000000000),
                    max_pending_requests=UInt32Value(value=1000000000),
                    max_requests=UInt32Value(value=1000000000),
                    max_retries=UInt32Value(value=1000000000),
                ),
            ]
        ),
        # See: https://github.com/reboot-dev/mono/issues/3944.
        per_connection_buffer_limit_bytes=UInt32Value(
            value=MAX_GRPC_RESPONSE_SIZE_BYTES
        ),
    )


def clusters(
    application_id: ApplicationId,
    consensuses: list[ConsensusInfo],
) -> list[cluster_pb2.Cluster]:
    result: list[cluster_pb2.Cluster] = []

    for consensus in consensuses:
        # Every consensus serves both a gRPC and a WebSocket endpoint, on
        # different ports. They are therefore different clusters to Envoy.
        for kind in [
            ClusterKind.GRPC, ClusterKind.HTTP, ClusterKind.WEBSOCKET
        ]:
            result.append(
                _cluster(
                    application_id=application_id,
                    consensus_id=consensus.consensus_id,
                    host=consensus.host,
                    port=(
                        consensus.grpc_port if kind == ClusterKind.GRPC else (
                            consensus.http_port if kind == ClusterKind.HTTP
                            else consensus.websocket_port
                        )
                    ),
                    kind=kind,
                )
            )

    return result


def xds_cluster(
    host: str,
    port: int,
) -> cluster_pb2.Cluster:
    return cluster_pb2.Cluster(
        name="xds_cluster",
        type=cluster_pb2.Cluster.STRICT_DNS,
        dns_lookup_family=cluster_pb2.Cluster.V4_ONLY,
        load_assignment=endpoint_pb2.ClusterLoadAssignment(
            cluster_name="xds_cluster", endpoints=[
                endpoint_components_pb2.LocalityLbEndpoints(
                    lb_endpoints=[
                        endpoint_components_pb2.LbEndpoint(
                            endpoint=endpoint_components_pb2.Endpoint(
                                address=address_pb2.Address(
                                    socket_address=address_pb2.SocketAddress(
                                        address=host,
                                        port_value=port,
                                    )
                                )
                            )
                        )
                    ],
                )
            ]
        ),
        typed_extension_protocol_options={
            "envoy.extensions.upstreams.http.v3.HttpProtocolOptions":
                any_pack(
                    http_protocol_options_pb2.HttpProtocolOptions(
                        explicit_http_config=http_protocol_options_pb2.
                        HttpProtocolOptions.ExplicitHttpConfig(
                            # We must set this field explicitly (even to
                            # its default), since it's part of a oneof.
                            http2_protocol_options=protocol_pb2.
                            Http2ProtocolOptions(),
                        )
                    )
                )
        },
    )
