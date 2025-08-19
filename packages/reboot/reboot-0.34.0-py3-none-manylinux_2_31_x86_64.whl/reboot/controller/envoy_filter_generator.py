import base64
import kubernetes_asyncio
import rbt.v1alpha1.placement_planner_pb2 as placement_planner_pb2
import reboot.templates.tools as template_tools
from enum import Enum
from google.protobuf import struct_pb2
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from rbt.cloud.v1alpha1.istio.envoy_filter_spec_pb2 import WorkloadSelector
from reboot.controller.envoy_filter import EnvoyFilter
from reboot.controller.settings import (
    IS_REBOOT_APPLICATION_LABEL_NAME,
    IS_REBOOT_APPLICATION_LABEL_VALUE,
    ISTIO_INGRESSGATEWAY_INTERNAL_PORT,
    ISTIO_INGRESSGATEWAY_LABEL_NAME,
    ISTIO_INGRESSGATEWAY_LABEL_VALUE,
    USER_CONTAINER_GRPC_PORT,
)
from reboot.routing.filters.lua import MANGLED_HTTP_PATH_FILENAME, load_lua
from rebootdev.aio.types import KubernetesNamespace, ServiceName
from typing import Optional


def generate_lua_routing_filter(
    consensuses: list[placement_planner_pb2.Consensus],
) -> str:
    """
    Generates Lua code that Envoy will accept as part of an `inline_code` block.
    NOTE: will generate this code with a base indentation of 0; you must indent it appropriately
          to make it part of valid YAML.
    """
    # Inject the Lua filter that handles "mangled" HTTP paths that
    # need to be translated into something that can be routed.
    mangled_http_path_filter = load_lua(MANGLED_HTTP_PATH_FILENAME)

    template_input = {
        "consensuses": consensuses,
        "mangled_http_path_filter": mangled_http_path_filter,
    }

    return template_tools.render_template(
        "routing_filter.lua.j2", template_input
    )


class FilterContext(Enum):
    GATEWAY = 'gateway'
    MESH = 'mesh'


def generate_istio_routing_filter(
    *,
    namespace: str,
    name: str,
    consensuses: list[placement_planner_pb2.Consensus],
    context: FilterContext,
) -> EnvoyFilter:
    """
    Generates a `EnvoyFilter` (which is a `CustomObject` representing an Istio
    `EnvoyFilter`) that contains the Lua routing filter.
    """
    lua_filter_code = generate_lua_routing_filter(consensuses)
    patch_value_struct = struct_pb2.Struct()
    patch_value_struct.update(
        {
            'name': 'envoy.filters.http.lua',
            'typed_config':
                {
                    '@type':
                        'type.googleapis.com/envoy.extensions.filters.http.lua.v3.Lua',
                    'inline_code':
                        lua_filter_code
                }
        }
    )

    match_spec: Optional[EnvoyFilter.Spec.EnvoyConfigObjectMatch] = None
    selector_labels: dict[str, str] = {}
    if context == FilterContext.GATEWAY:
        # The routing filter will match all traffic coming into the Reboot app
        # port. We don't want to match any other ports, since we don't want to
        # apply this filter to non-Reboot traffic that's also coming into the
        # gateway.
        match_spec = EnvoyFilter.Spec.EnvoyConfigObjectMatch(
            context=EnvoyFilter.Spec.PatchContext.GATEWAY,
            listener=EnvoyFilter.Spec.ListenerMatch(
                filter_chain=EnvoyFilter.Spec.ListenerMatch.FilterChainMatch(
                    filter=EnvoyFilter.Spec.ListenerMatch.FilterMatch(
                        name='envoy.filters.network.http_connection_manager',
                    )
                ),
                port_number=ISTIO_INGRESSGATEWAY_INTERNAL_PORT,
            ),
        )
        # The gateway routing filter should be applied to Istio ingress
        # gateways.
        selector_labels = {
            ISTIO_INGRESSGATEWAY_LABEL_NAME: ISTIO_INGRESSGATEWAY_LABEL_VALUE,
        }
    else:
        assert context == FilterContext.MESH
        # The internal routing filter only matches traffic outbound to the user
        # container port.
        match_spec = EnvoyFilter.Spec.EnvoyConfigObjectMatch(
            context=EnvoyFilter.Spec.PatchContext.SIDECAR_OUTBOUND,
            listener=EnvoyFilter.Spec.ListenerMatch(
                filter_chain=EnvoyFilter.Spec.ListenerMatch.FilterChainMatch(
                    filter=EnvoyFilter.Spec.ListenerMatch.FilterMatch(
                        name='envoy.filters.network.http_connection_manager',
                        sub_filter=EnvoyFilter.Spec.ListenerMatch.
                        SubFilterMatch(name='envoy.filters.http.router'),
                    )
                ),
                port_number=USER_CONTAINER_GRPC_PORT,
            )
        )
        # The internal routing filter should be applied to all pods that are
        # part of a Reboot application (including consensuses and config pods).
        selector_labels = {
            IS_REBOOT_APPLICATION_LABEL_NAME: IS_REBOOT_APPLICATION_LABEL_VALUE
        }

    return EnvoyFilter(
        metadata=kubernetes_asyncio.client.V1ObjectMeta(
            namespace=namespace,
            name=name,
        ),
        spec=EnvoyFilter.Spec(
            workload_selector=WorkloadSelector(
                # Deploy this EnvoyFilter to the right pods.
                labels=selector_labels
            ),
            config_patches=[
                EnvoyFilter.Spec.EnvoyConfigObjectPatch(
                    apply_to=EnvoyFilter.Spec.ApplyTo.HTTP_FILTER,
                    match=match_spec,
                    patch=EnvoyFilter.Spec.Patch(
                        operation=EnvoyFilter.Spec.Patch.Operation.
                        INSERT_FIRST,
                        value=patch_value_struct,
                    ),
                )
            ]
        )
    )


def generate_transcoding_filter(
    namespace: KubernetesNamespace,
    name: str,
    target_labels: dict[str, str],
    services: list[ServiceName],
    file_descriptor_set: FileDescriptorSet,
) -> EnvoyFilter:
    """Generates an EnvoyFilter that does HTTP(JSON) <-> gRPC transcoding for
    incoming traffic on pods with the given labels.
    """

    # The transcoding filter matches all inbound traffic on the user container's
    # gRPC port, but does NOT match inbound traffic on the websocket port.
    match_spec = EnvoyFilter.Spec.EnvoyConfigObjectMatch(
        context=EnvoyFilter.Spec.PatchContext.SIDECAR_INBOUND,
        listener=EnvoyFilter.Spec.ListenerMatch(
            filter_chain=EnvoyFilter.Spec.ListenerMatch.FilterChainMatch(
                filter=EnvoyFilter.Spec.ListenerMatch.FilterMatch(
                    name='envoy.filters.network.http_connection_manager',
                    sub_filter=EnvoyFilter.Spec.ListenerMatch.SubFilterMatch(
                        name='envoy.filters.http.router'
                    ),
                )
            ),
            port_number=USER_CONTAINER_GRPC_PORT,
        )
    )

    # The actual filter itself is defined as an untyped Struct.
    patch_value_struct = struct_pb2.Struct()
    patch_value_struct.update(
        {
            'name': 'envoy.filters.http.grpc_json_transcoder',
            'typed_config':
                {
                    '@type':
                        'type.googleapis.com/envoy.extensions.filters.http.grpc_json_transcoder.v3.GrpcJsonTranscoder',
                    # ATTENTION: if you update any of this, also update the
                    # matching values in `envoy_config.py`.
                    'convert_grpc_status': True,
                    'print_options':
                        {
                            'add_whitespace': True,
                            'always_print_enums_as_ints': False,
                            'always_print_primitive_fields': True,
                            'preserve_proto_field_names': False,
                        },
                    'proto_descriptor_bin':
                        # We need to manually base64-encode the bytes of
                        # `file_descriptor_set` here, and then decode them into
                        # a string - Kubernetes can't handle raw bytes. This is
                        # different than when we're writing a `bytes` field of a
                        # `CustomObject` (rather than of this `Struct`); the
                        # `CustomObject` does this encoding step for us.
                        base64.b64encode(file_descriptor_set.SerializeToString()).decode(),
                    'services':
                        services,
                    # The gRPC backend would be unhappy to receive non-gRPC
                    # `application/json` traffic and would reply with a `503`,
                    # which is not a good user experience and not helpful in
                    # debugging. In addition, we've observed that that
                    # interaction between Envoy and gRPC triggers a bug in one
                    # of those two  that will cause subsequent valid requests to
                    # fail.
                    # See https://github.com/reboot-dev/mono/issues/3074.
                    # Instead, simply (correctly) reject invalid
                    # `application/json` traffic with a 404.
                    'request_validation_options':
                        {
                            'reject_unknown_method': True,
                        },
                }
        }
    )

    return EnvoyFilter(
        metadata=kubernetes_asyncio.client.V1ObjectMeta(
            namespace=namespace,
            name=name,
        ),
        spec=EnvoyFilter.Spec(
            workload_selector=WorkloadSelector(
                # Deploy this EnvoyFilter to the right pods.
                labels=target_labels,
            ),
            config_patches=[
                EnvoyFilter.Spec.EnvoyConfigObjectPatch(
                    apply_to=EnvoyFilter.Spec.ApplyTo.HTTP_FILTER,
                    match=match_spec,
                    patch=EnvoyFilter.Spec.Patch(
                        operation=EnvoyFilter.Spec.Patch.Operation.
                        INSERT_FIRST,
                        value=patch_value_struct,
                    ),
                )
            ]
        ),
    )
