# yapf: disable
# isort: skip_file
# ruff: noqa



# To not generate code where imported names might get shadowed when a user
# specifies some name in their proto file to be the same as one of our imported
# names, (for example: a request field named `uuid`) we bind all imports to
# names that are forbidden in 'proto' and therefore can never collide.

# Standard imports.
from __future__ import annotations as IMPORT_future_annotations

# The following MUST appear before the rest of the imports, since those imports
# may be invalid (broken) if the generated code is mismatched with the installed
# libraries.
import rebootdev.versioning as IMPORT_reboot_versioning
IMPORT_reboot_versioning.check_generated_code_compatible("0.34.0")

# ATTENTION: no types in this file should be imported with their unqualified
#            name (e.g. `from typing import Any`). That would cause clashes
#            with user-defined methods that have the same name. Use
#            fully-qualified names (e.g. `IMPORT_typing.Any`) instead.
import asyncio as IMPORT_asyncio
import builtins as IMPORT_builtins
import contextvars as IMPORT_contextvars
import dataclasses as IMPORT_dataclasses
import google.protobuf.descriptor as IMPORT_google_protobuf_descriptor
import google.protobuf.json_format as IMPORT_google_protobuf_json_format
import google.protobuf.message as IMPORT_google_protobuf_message
import grpc as IMPORT_grpc
import grpc_status._async as IMPORT_rpc_status_async
from grpc_status import rpc_status as IMPORT_rpc_status_sync
import json as IMPORT_json
import os as IMPORT_os
import traceback as IMPORT_traceback
import uuid as IMPORT_uuid
import pickle as IMPORT_pickle
import rebootdev as IMPORT_rebootdev
import log.log as IMPORT_log_log   # type: ignore[import]
import typing as IMPORT_typing
import rebootdev.aio.backoff as IMPORT_reboot_aio_backoff
import functools as IMPORT_functools
from abc import abstractmethod as IMPORT_abc_abstractmethod
from datetime import datetime as IMPORT_datetime_datetime
from datetime import timedelta as IMPORT_datetime_timedelta
from datetime import timezone as IMPORT_datetime_timezone
from google.protobuf import timestamp_pb2 as IMPORT_google_protobuf_timestamp_pb2
from google.protobuf import wrappers_pb2 as IMPORT_google_protobuf_wrappers_pb2
import rebootdev.aio.tracing as IMPORT_reboot_aio_tracing
from google.rpc import status_pb2 as IMPORT_google_rpc_status_pb2
from tzlocal import get_localzone as IMPORT_tzlocal_get_localzone
import rebootdev.aio.call as IMPORT_reboot_aio_call
import rebootdev.aio.contexts as IMPORT_reboot_aio_contexts
import rebootdev.aio.headers as IMPORT_reboot_aio_headers
import rebootdev.aio.idempotency as IMPORT_reboot_aio_idempotency
import rebootdev.aio.internals.channel_manager as IMPORT_reboot_aio_internals_channel_manager
import rebootdev.aio.internals.middleware as IMPORT_reboot_aio_internals_middleware
import rebootdev.aio.internals.tasks_cache as IMPORT_reboot_aio_internals_tasks_cache
import rebootdev.aio.internals.tasks_dispatcher as IMPORT_reboot_aio_internals_tasks_dispatcher
import rebootdev.aio.placement as IMPORT_reboot_aio_placement
import rebootdev.aio.servicers as IMPORT_reboot_aio_servicers
import rebootdev.aio.state_managers as IMPORT_reboot_aio_state_managers
import rebootdev.aio.stubs as IMPORT_reboot_aio_stubs
import rebootdev.aio.tasks as IMPORT_reboot_aio_tasks
import rebootdev.aio.types as IMPORT_reboot_aio_types
import rebootdev.aio.external as IMPORT_reboot_aio_external
import rebootdev.aio.workflows as IMPORT_reboot_aio_workflows
import rebootdev.settings as IMPORT_reboot_settings
import rebootdev.nodejs.python as IMPORT_reboot_nodejs_python
from rebootdev.time import DateTimeWithTimeZone as IMPORT_reboot_time_DateTimeWithTimeZone
import rbt.v1alpha1 as IMPORT_rbt_v1alpha1
import rbt.v1alpha1.nodejs_pb2 as IMPORT_rbt_v1alpha1_nodejs_pb2
import google.protobuf.any_pb2 as IMPORT_google_protobuf_any_pb2

# User defined or referenced imports.
import google.protobuf.descriptor_pb2
import google.protobuf.timestamp_pb2
import rbt.cloud.v1alpha1.logs.logs_pb2
import rbt.cloud.v1alpha1.logs.logs_pb2_grpc
import rbt.v1alpha1.options_pb2
# Additionally re-export all messages and enums from the pb2 module.
from rbt.cloud.v1alpha1.logs.logs_pb2 import (
    ArchiveRequest,
    ArchiveResponse,
    EnsureRequest,
    EnsureResponse,
    IngestRequest,
    IngestResponse,
    LogRecord,
    LogsRequest,
    LogsResponse,
    RegisterConsensusRequest,
    RegisterConsensusResponse,
    RegisterRevisionRequest,
    RegisterRevisionResponse,
    Source,
)

logger = IMPORT_log_log.get_logger(__name__)

############################ Legacy gRPC Servicers ############################
# This section is relevant (only) for servicers that implement a legacy gRPC
# service in a Reboot context. It is irrelevant to clients.

def MakeLegacyGrpcServiceable(
    # A legacy gRPC servicer type can't be more specific than `type`,
    # because legacy gRPC servicers (as generated by the gRPC `protoc`
    # plugin) do not share any common base class other than `object`.
    servicer_type: type
) -> IMPORT_reboot_aio_servicers.Serviceable:
    if issubclass(servicer_type, rbt.cloud.v1alpha1.logs.logs_pb2_grpc.LogsProxyServicer):
        return LogsProxyServiceable(servicer_type)
    raise ValueError(f"Unknown legacy gRPC servicer type '{servicer_type}'")


class LogsProxyServiceable(IMPORT_reboot_aio_servicers.Serviceable):
    """ A Servicable that makes it possible to host a legacy gRPC
    `LogsProxyServicer` on Reboot."""

    def __init__(self, legacy_grpc_servicer_type: type[rbt.cloud.v1alpha1.logs.logs_pb2_grpc.LogsProxyServicer]):
        self._legacy_grpc_servicer_type = legacy_grpc_servicer_type

    def service_names(self) -> list[IMPORT_reboot_aio_types.ServiceName]:
        return [IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.LogsProxy')]

    def state_type_name(self) -> None:
        # Legacy gRPC servicers don't have an associated state type.
        return None

    def file_descriptor(self) -> IMPORT_google_protobuf_descriptor.FileDescriptor:
        return rbt.cloud.v1alpha1.logs.logs_pb2.DESCRIPTOR

    def instantiate(self) -> tuple[
        rbt.cloud.v1alpha1.logs.logs_pb2_grpc.LogsProxyServicer,
        IMPORT_typing.Optional[IMPORT_typing.Callable[
            [object, IMPORT_grpc.aio.Server],
            None
        ]]
    ]:
        servicer = self._legacy_grpc_servicer_type()
        add_to_server_method = rbt.cloud.v1alpha1.logs.logs_pb2_grpc.add_LogsProxyServicer_to_server
        return servicer, add_to_server_method


############################ Reboot Servicer Middlewares ############################
# This section is relevant (only) for servicers implementing a Reboot servicer. It
# is irrelevant to clients, except for the fact that some clients are _also_ such
# servicers.

# For internal calls, we can use a magic token to bypass token verification and
# authorization checks. The token provides no auth information (e.g.,
# `context.auth is None`).
__internal_magic_token__: str = f'internal-{str(IMPORT_uuid.uuid4())}'

class ApplicationLogsServicerMiddleware(IMPORT_reboot_aio_internals_middleware.Middleware):

    def __init__(
        self,
        *,
        servicer: ApplicationLogsBaseServicer,
        application_id: IMPORT_reboot_aio_types.ApplicationId,
        consensus_id: IMPORT_reboot_aio_types.ConsensusId,
        state_manager: IMPORT_reboot_aio_state_managers.StateManager,
        placement_client: IMPORT_reboot_aio_placement.PlacementClient,
        channel_manager: IMPORT_reboot_aio_internals_channel_manager._ChannelManager,
        tasks_cache: IMPORT_reboot_aio_internals_tasks_cache.TasksCache,
        token_verifier: IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.token_verifiers.TokenVerifier],
        effect_validation: IMPORT_reboot_aio_contexts.EffectValidation,
        app_internal_api_key_secret: str,
        ready: IMPORT_asyncio.Event,
    ):
        super().__init__(
            application_id=application_id,
            consensus_id=consensus_id,
            state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            service_names = [
                IMPORT_reboot_aio_types.ServiceName("rbt.cloud.v1alpha1.logs.ApplicationLogsMethods"),
            ],
            placement_client=placement_client,
            channel_manager=channel_manager,
            effect_validation=effect_validation,
            app_internal_api_key_secret=app_internal_api_key_secret,
        )

        self._servicer = servicer
        self._state_manager = state_manager
        self.tasks_dispatcher = IMPORT_reboot_aio_internals_tasks_dispatcher.TasksDispatcher(
            application_id=application_id,
            dispatch=self.dispatch,
            tasks_cache=tasks_cache,
            ready=ready,
            complete_task=self._state_manager.complete_task,
        )

        # Store the type of each method's request so that stored requests can be
        # deserialized into the correct type.
        self.request_type_by_method_name: dict[str, type[IMPORT_google_protobuf_message.Message]] = {
            'Ensure': rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
            'RegisterConsensus': rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
            'RegisterRevision': rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
            'Logs': rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        }

        # Get authorizer, if any, converting from a rule if necessary.
        def convert_authorizer_rule_if_necessary(
            authorizer_or_rule: IMPORT_typing.Optional[
                IMPORT_rebootdev.aio.auth.authorizers.Authorizer | IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule
            ]
        ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer:

            # If no authorizer or rule is provided, return the default
            # authorizer which allows if app internal or allows if in
            # dev mode (and logs some warnings to help the user
            # realize where they are missing authorization).
            if authorizer_or_rule is None:
                return IMPORT_rebootdev.aio.auth.authorizers.DefaultAuthorizer(
                    'ApplicationLogs'
                )

            if isinstance(authorizer_or_rule, IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule):
                return ApplicationLogsAuthorizer(
                    _default=authorizer_or_rule
                )

            return authorizer_or_rule

        self._authorizer = convert_authorizer_rule_if_necessary(
            servicer.authorizer()
        )

        # Create token verifier.
        self._token_verifier: IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.token_verifiers.TokenVerifier] = (
            servicer.token_verifier() or token_verifier
        )

        # Since users specify errors as proto messages they can't raise them
        # directly - to do so they have to use the `Aborted` wrapper, which will
        # hold the original proto message. On errors we'll need to check whether
        # such wrappers hold a proto message for a specified error, so we can
        # avoid retrying tasks that complete with a specified error.
        self._specified_errors_by_service_method_name: dict[str, list[str]] = {
        }


    def add_to_server(self, server: IMPORT_grpc.aio.Server) -> None:
        rbt.cloud.v1alpha1.logs.logs_pb2_grpc.add_ApplicationLogsMethodsServicer_to_server(
            self, server
        )

    async def inspect(self, state_ref: IMPORT_reboot_aio_types.StateRef) -> IMPORT_typing.AsyncIterator[IMPORT_google_protobuf_message.Message]:
        """Implementation of `Middleware.inspect()`."""
        context = self.create_context(
            headers=IMPORT_reboot_aio_headers.Headers(
                application_id=self.application_id,
                state_ref=state_ref,
            ),
            state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            method="inspect",
            context_type=IMPORT_reboot_aio_contexts.ReaderContext,
        )

        async with self._state_manager.streaming_reader_idempotency_key(
            context,
            self._servicer.__state_type__,
            authorize=None,
        ) as states:
            async for (state, idempotency_key) in states:
                yield state

    async def react_query(
        self,
        headers: IMPORT_reboot_aio_headers.Headers,
        method: str,
        request_bytes: bytes,
    ) -> IMPORT_typing.AsyncIterator[tuple[IMPORT_typing.Optional[IMPORT_google_protobuf_message.Message], list[IMPORT_uuid.UUID]]]:
        """Returns the response of calling 'method' given a message
        deserialized from the provided 'request_bytes' for each state
        update that creates a different response.

        # The caller (react.py) should have already ensured that this consensus
        # is authoritative for this traffic.
        assert self.placement_client.consensus_for_actor(
            headers.application_id,
            headers.state_ref,
        ) == self._consensus_id

        NOTE: only unary reader methods are supported."""
        # Need to define these up here since we can only do that once.
        last_response: IMPORT_typing.Optional[IMPORT_google_protobuf_message.Message] = None
        aggregated_idempotency_keys: list[IMPORT_uuid.UUID] = []
        if method == 'Ensure':
            # Invariant here is that users should not have called this
            # directly but only through code generated React
            # components which should not have been generated except
            # for valid method candidates.
            logger.warning(
                "Got a React query request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have a browser tab open for an older version "
                "of this application, or for a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' is invalid"
            )
            yield  # Necessary for type checking.
        elif method == 'RegisterConsensus':
            # Invariant here is that users should not have called this
            # directly but only through code generated React
            # components which should not have been generated except
            # for valid method candidates.
            logger.warning(
                "Got a React query request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have a browser tab open for an older version "
                "of this application, or for a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' is invalid"
            )
            yield  # Necessary for type checking.
        elif method == 'RegisterRevision':
            # Invariant here is that users should not have called this
            # directly but only through code generated React
            # components which should not have been generated except
            # for valid method candidates.
            logger.warning(
                "Got a React query request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have a browser tab open for an older version "
                "of this application, or for a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' is invalid"
            )
            yield  # Necessary for type checking.
        elif method == 'Logs':
            # Invariant here is that users should not have called this
            # directly but only through code generated React
            # components which should not have been generated except
            # for valid method candidates.
            logger.warning(
                "Got a React query request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have a browser tab open for an older version "
                "of this application, or for a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' is invalid"
            )
            yield  # Necessary for type checking.
        else:
            logger.warning(
                "Got a React query request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have a browser tab open for an older version "
                "of this application, or for a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' not found"
            )
            yield  # Unreachable but necessary for mypy.

    async def react_mutate(
        self,
        headers: IMPORT_reboot_aio_headers.Headers,
        method: str,
        request_bytes: bytes,
    ) -> IMPORT_google_protobuf_message.Message:
        """Returns the response of calling 'method' given a message
        deserialized from the provided 'request_bytes'."""
        if method == 'Ensure':
            request = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest()
            request.ParseFromString(request_bytes)

            # NOTE: we automatically retry mutations that come through
            # React when we get a `IMPORT_grpc.StatusCode.UNAVAILABLE` to
            # match the retry logic we do in the React code generated
            # to handle lack/loss of connectivity.
            #
            # TODO(benh): revisit this decision if we ever see reason
            # to call `react_mutate()` from any place other than where
            # we're executing React (e.g., browser, next.js server
            # component, etc).
            call_backoff = IMPORT_reboot_aio_backoff.Backoff()
            while True:
                # We make a full-fledged gRPC call, so that if this traffic
                # was misrouted (i.e. this consensus is not authoritative
                # for the state), it will now go to the right place. The
                # receiving middleware will handle things like effect
                # validation and so forth.
                assert headers.application_id is not None  # Guaranteed by `Headers`.
                stub = rbt.cloud.v1alpha1.logs.logs_pb2_grpc.ApplicationLogsMethodsStub(
                    self.channel_manager.get_channel_to(
                        self.placement_client.address_for_actor(
                            headers.application_id,
                            headers.state_ref,
                        )
                    )
                )
                call = stub.Ensure(
                    request=request,
                    metadata=headers.to_grpc_metadata(),
                )
                try:
                    return await call
                except IMPORT_grpc.aio.AioRpcError as error:
                    if error.code() == IMPORT_grpc.StatusCode.UNAVAILABLE:
                        await call_backoff()
                        continue

                    # Reconstitute the error that the server threw, if it was a declared error.
                    status = await IMPORT_rpc_status_async.from_call(call)
                    if status is not None:
                        raise ApplicationLogs.EnsureAborted.from_status(
                            status
                        ) from None
                    raise ApplicationLogs.EnsureAborted.from_grpc_aio_rpc_error(
                        error
                     ) from None

        elif method == 'RegisterConsensus':
            request = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest()
            request.ParseFromString(request_bytes)

            # NOTE: we automatically retry mutations that come through
            # React when we get a `IMPORT_grpc.StatusCode.UNAVAILABLE` to
            # match the retry logic we do in the React code generated
            # to handle lack/loss of connectivity.
            #
            # TODO(benh): revisit this decision if we ever see reason
            # to call `react_mutate()` from any place other than where
            # we're executing React (e.g., browser, next.js server
            # component, etc).
            call_backoff = IMPORT_reboot_aio_backoff.Backoff()
            while True:
                # We make a full-fledged gRPC call, so that if this traffic
                # was misrouted (i.e. this consensus is not authoritative
                # for the state), it will now go to the right place. The
                # receiving middleware will handle things like effect
                # validation and so forth.
                assert headers.application_id is not None  # Guaranteed by `Headers`.
                stub = rbt.cloud.v1alpha1.logs.logs_pb2_grpc.ApplicationLogsMethodsStub(
                    self.channel_manager.get_channel_to(
                        self.placement_client.address_for_actor(
                            headers.application_id,
                            headers.state_ref,
                        )
                    )
                )
                call = stub.RegisterConsensus(
                    request=request,
                    metadata=headers.to_grpc_metadata(),
                )
                try:
                    return await call
                except IMPORT_grpc.aio.AioRpcError as error:
                    if error.code() == IMPORT_grpc.StatusCode.UNAVAILABLE:
                        await call_backoff()
                        continue

                    # Reconstitute the error that the server threw, if it was a declared error.
                    status = await IMPORT_rpc_status_async.from_call(call)
                    if status is not None:
                        raise ApplicationLogs.RegisterConsensusAborted.from_status(
                            status
                        ) from None
                    raise ApplicationLogs.RegisterConsensusAborted.from_grpc_aio_rpc_error(
                        error
                     ) from None

        elif method == 'RegisterRevision':
            request = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest()
            request.ParseFromString(request_bytes)

            # NOTE: we automatically retry mutations that come through
            # React when we get a `IMPORT_grpc.StatusCode.UNAVAILABLE` to
            # match the retry logic we do in the React code generated
            # to handle lack/loss of connectivity.
            #
            # TODO(benh): revisit this decision if we ever see reason
            # to call `react_mutate()` from any place other than where
            # we're executing React (e.g., browser, next.js server
            # component, etc).
            call_backoff = IMPORT_reboot_aio_backoff.Backoff()
            while True:
                # We make a full-fledged gRPC call, so that if this traffic
                # was misrouted (i.e. this consensus is not authoritative
                # for the state), it will now go to the right place. The
                # receiving middleware will handle things like effect
                # validation and so forth.
                assert headers.application_id is not None  # Guaranteed by `Headers`.
                stub = rbt.cloud.v1alpha1.logs.logs_pb2_grpc.ApplicationLogsMethodsStub(
                    self.channel_manager.get_channel_to(
                        self.placement_client.address_for_actor(
                            headers.application_id,
                            headers.state_ref,
                        )
                    )
                )
                call = stub.RegisterRevision(
                    request=request,
                    metadata=headers.to_grpc_metadata(),
                )
                try:
                    return await call
                except IMPORT_grpc.aio.AioRpcError as error:
                    if error.code() == IMPORT_grpc.StatusCode.UNAVAILABLE:
                        await call_backoff()
                        continue

                    # Reconstitute the error that the server threw, if it was a declared error.
                    status = await IMPORT_rpc_status_async.from_call(call)
                    if status is not None:
                        raise ApplicationLogs.RegisterRevisionAborted.from_status(
                            status
                        ) from None
                    raise ApplicationLogs.RegisterRevisionAborted.from_grpc_aio_rpc_error(
                        error
                     ) from None

        elif method == 'Logs':
            # Invariant here is that users should not have called this
            # directly but only through code generated React
            # components which should not have been generated except
            # for valid method candidates.
            logger.warning(
                "Got a react mutate request with an invalid method name: "
                "Method 'Logs' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have an old browser tab still open for an older version "
                "of this application, or a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=f"Method '{method}' is invalid"
            )
        else:
            logger.warning(
                "Got a react mutate request with an invalid method name: "
                f"Method '{method}' is invalid for servicer ApplicationLogs."
                "\n"
                "Do you have an old browser tab still open for an older version "
                "of this application, or a different application all together?"
            )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.InvalidMethod(),
                message=
                    f"Method '{method}' not found"
            )

    async def dispatch(
        self,
        task: IMPORT_reboot_aio_tasks.TaskEffect,
        *,
        only_validate: bool = False,
        on_loop_iteration: IMPORT_reboot_aio_internals_tasks_dispatcher.OnLoopIterationCallable = (lambda iteration, next_iteration_schedule: None),
    ) -> IMPORT_reboot_aio_internals_tasks_dispatcher.TaskResponseOrError:
        """Dispatches the tasks to execute unless 'only_validate' is set to
        true, in which case just ensures that the task actually exists.
        Note that this function will be called *by* tasks_dispatcher; it will
        not itself call into tasks_dispatcher."""

        if 'Ensure' == task.method_name:
            if only_validate:
                # TODO(benh): validate 'task.request' is correct type.
                return rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse()

            # Use an inline method to create a new scope, so that we can use
            # variable names like `context` and `effects` in multiple branches
            # in this code (notably when there are multiple task types) without
            # hitting a mypy error that the variable's type is not consistent.
            async def run_Ensure(
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                *,
                validating_effects: bool = False,
            ):
                async with self._state_manager.task_workflow(
                    context,
                    task,
                    on_loop_iteration=on_loop_iteration,
                    validating_effects=validating_effects,
                ) as complete:
                    try:
                        response = await (ApplicationLogsWorkflowStub(
                            context=context,
                            state_ref=context._state_ref,
                        ).Ensure(
                            IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest, task.request),
                            bearer_token=__internal_magic_token__,
                            idempotency=IMPORT_reboot_aio_idempotency.Idempotency(
                                alias=f'Task {task.task_id.task_uuid}',
                            ),
                        ))
                        await complete(task, (response, None))
                        return (response, None)
                    except IMPORT_asyncio.CancelledError:
                        # Check if the task was cancelled by a TasksServicer.
                        if self.tasks_dispatcher.is_task_cancelled(task.task_id.task_uuid):
                            # The running task was cancelled by a TasksServicer.
                            await complete(task, (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError()))
                            return (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError())
                        else:
                            raise
                    except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                        error_type = f'{aborted.error.__class__.__module__}.{aborted.error.__class__.__qualname__}'
                        # Do not retry a task if the error was specified in the
                        # proto file.
                        if error_type in self._specified_errors_by_service_method_name.get('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure', []):
                            await complete(task, (None, aborted.error))
                            return (None, aborted.error)
                        raise


            return await run_Ensure(
                self.create_context(
                    headers=IMPORT_reboot_aio_headers.Headers(
                        application_id=self.application_id,
                        state_ref=IMPORT_reboot_aio_types.StateRef(task.task_id.state_ref),
                    ),
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='Ensure',
                    context_type=IMPORT_reboot_aio_contexts.WorkflowContext,
                    task=task,
                )
            )
        elif 'RegisterConsensus' == task.method_name:
            if only_validate:
                # TODO(benh): validate 'task.request' is correct type.
                return rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse()

            # Use an inline method to create a new scope, so that we can use
            # variable names like `context` and `effects` in multiple branches
            # in this code (notably when there are multiple task types) without
            # hitting a mypy error that the variable's type is not consistent.
            async def run_RegisterConsensus(
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                *,
                validating_effects: bool = False,
            ):
                async with self._state_manager.task_workflow(
                    context,
                    task,
                    on_loop_iteration=on_loop_iteration,
                    validating_effects=validating_effects,
                ) as complete:
                    try:
                        response = await (ApplicationLogsWorkflowStub(
                            context=context,
                            state_ref=context._state_ref,
                        ).RegisterConsensus(
                            IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest, task.request),
                            bearer_token=__internal_magic_token__,
                            idempotency=IMPORT_reboot_aio_idempotency.Idempotency(
                                alias=f'Task {task.task_id.task_uuid}',
                            ),
                        ))
                        await complete(task, (response, None))
                        return (response, None)
                    except IMPORT_asyncio.CancelledError:
                        # Check if the task was cancelled by a TasksServicer.
                        if self.tasks_dispatcher.is_task_cancelled(task.task_id.task_uuid):
                            # The running task was cancelled by a TasksServicer.
                            await complete(task, (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError()))
                            return (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError())
                        else:
                            raise
                    except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                        error_type = f'{aborted.error.__class__.__module__}.{aborted.error.__class__.__qualname__}'
                        # Do not retry a task if the error was specified in the
                        # proto file.
                        if error_type in self._specified_errors_by_service_method_name.get('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus', []):
                            await complete(task, (None, aborted.error))
                            return (None, aborted.error)
                        raise


            return await run_RegisterConsensus(
                self.create_context(
                    headers=IMPORT_reboot_aio_headers.Headers(
                        application_id=self.application_id,
                        state_ref=IMPORT_reboot_aio_types.StateRef(task.task_id.state_ref),
                    ),
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='RegisterConsensus',
                    context_type=IMPORT_reboot_aio_contexts.WorkflowContext,
                    task=task,
                )
            )
        elif 'RegisterRevision' == task.method_name:
            if only_validate:
                # TODO(benh): validate 'task.request' is correct type.
                return rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse()

            # Use an inline method to create a new scope, so that we can use
            # variable names like `context` and `effects` in multiple branches
            # in this code (notably when there are multiple task types) without
            # hitting a mypy error that the variable's type is not consistent.
            async def run_RegisterRevision(
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                *,
                validating_effects: bool = False,
            ):
                async with self._state_manager.task_workflow(
                    context,
                    task,
                    on_loop_iteration=on_loop_iteration,
                    validating_effects=validating_effects,
                ) as complete:
                    try:
                        response = await (ApplicationLogsWorkflowStub(
                            context=context,
                            state_ref=context._state_ref,
                        ).RegisterRevision(
                            IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest, task.request),
                            bearer_token=__internal_magic_token__,
                            idempotency=IMPORT_reboot_aio_idempotency.Idempotency(
                                alias=f'Task {task.task_id.task_uuid}',
                            ),
                        ))
                        await complete(task, (response, None))
                        return (response, None)
                    except IMPORT_asyncio.CancelledError:
                        # Check if the task was cancelled by a TasksServicer.
                        if self.tasks_dispatcher.is_task_cancelled(task.task_id.task_uuid):
                            # The running task was cancelled by a TasksServicer.
                            await complete(task, (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError()))
                            return (None, IMPORT_rbt_v1alpha1.tasks_pb2.TaskCancelledError())
                        else:
                            raise
                    except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                        error_type = f'{aborted.error.__class__.__module__}.{aborted.error.__class__.__qualname__}'
                        # Do not retry a task if the error was specified in the
                        # proto file.
                        if error_type in self._specified_errors_by_service_method_name.get('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision', []):
                            await complete(task, (None, aborted.error))
                            return (None, aborted.error)
                        raise


            return await run_RegisterRevision(
                self.create_context(
                    headers=IMPORT_reboot_aio_headers.Headers(
                        application_id=self.application_id,
                        state_ref=IMPORT_reboot_aio_types.StateRef(task.task_id.state_ref),
                    ),
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='RegisterRevision',
                    context_type=IMPORT_reboot_aio_contexts.WorkflowContext,
                    task=task,
                )
            )

        # There are no tasks for this service.
        start_or_validate = "start" if not only_validate else "validate"
        raise RuntimeError(
            f"Attempted to {start_or_validate} task '{task.method_name}' "
            f"on 'ApplicationLogs' which does not exist"
        )

    # ApplicationLogs specific methods:
    async def __Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        *,
        validating_effects: bool,
    ) -> ApplicationLogs.EnsureEffects:
        try:
            response = (
                await self._servicer._Ensure(
                    context=context,
                    state=state,
                    request=request
                )
            )
            IMPORT_reboot_aio_types.assert_type(
                response,
                [rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse],
            )
            self.maybe_raise_effect_validation_retry(
                logger=logger,
                idempotency_manager=context,
                method_name='ApplicationLogs.Ensure',
                validating_effects=validating_effects,
                context=context,
            )
            return ApplicationLogs.EnsureEffects(
                state=state,
                response=response,
                tasks=context._tasks,
                _colocated_upserts=context._colocated_upserts,
            )
        except IMPORT_reboot_aio_contexts.RetryReactively:
            # Retrying reactively, just let this propagate.
            raise
        except IMPORT_reboot_aio_contexts.EffectValidationRetry:
            # Doing effect validation, just let this propagate.
            raise
        except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
            # If the caller aborted due to a retryable error, just
            # propagate the aborted instead of propagating `Unknown`
            # so that a client can transparently retry.
            if IMPORT_rebootdev.aio.aborted.is_retryable(aborted):
                raise aborted
            # Log any _unhandled_ abort stack traces to make it
            # easier for debugging.
            #
            # NOTE: we don't log if we're a task as it will be logged
            # in `public/rebootdev/aio/internals/tasks_dispatcher.py` instead.
            aborted_type: IMPORT_typing.Optional[type] = None
            aborted_type = ApplicationLogs.EnsureAborted
            if isinstance(aborted, IMPORT_rebootdev.aio.aborted.SystemAborted):
                # Not logging when within `node` as we already log there.
                if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                    logger.warning(
                        f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {aborted}; propagating as 'Unknown'\n" +
                        ''.join(IMPORT_traceback.format_exception(aborted))
                    )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                    # TODO(benh): consider whether or not we want to
                    # include the 'package.service.method' which may
                    # get concatenated together forming a kind of
                    # "stack trace"; while it's super helpful for
                    # debugging, it does expose implementation
                    # information.
                    message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {aborted}"
                )
            else:
                if (
                    aborted_type is not None and
                    not isinstance(aborted, aborted_type) and
                    aborted_type.is_declared_error(aborted.error)
                ):
                    # We propagate declared errors that might have
                    # come from another call, i.e., we might have an
                    # `Aborted` but not for this method but the
                    # `Aborted` that we have has an error that this
                    # method declared. This allows a developer to
                    # simply add the declared error to their `.proto`
                    # file rather than having to catch and re-raise
                    # the error with their own aborted type.
                    if context.task is None:
                        logger.warning(
                            f"Propagating unhandled but declared error (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {aborted}"
                        )
                elif (
                    aborted_type is None or
                    not isinstance(aborted, aborted_type)
                ):
                    # Not logging when within `node` as we already log there.
                    if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                        logger.warning(
                            f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {aborted}; propagating as 'Unknown'\n" +
                            ''.join(IMPORT_traceback.format_exception(aborted))
                        )
                    # If this wasn't a declared error than we
                    # propagate it as `Unknown`.
                    raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                        IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                        # TODO(benh): consider whether or not we want to
                        # include the 'package.service.method' which may
                        # get concatenated together forming a kind of
                        # "stack trace"; while it's super helpful for
                        # debugging, it does expose implementation
                        # information.
                        message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {aborted}"
                    )

            raise
        except IMPORT_asyncio.CancelledError:
            # It's pretty normal for an RPC to be cancelled; it's not useful to
            # print a stack trace.
            raise
        except IMPORT_google_protobuf_message.DecodeError as decode_error:
            # We usually see this error when we are trying to construct a proto
            # message which is too deeply nested: protobuf has a limit of 100
            # nested messages. See the limits here:
            #   https://protobuf.dev/programming-guides/proto-limits/

            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') "
                    f"{type(decode_error).__name__}{': ' + str(decode_error) if len(str(decode_error)) > 0 else ''}; "
                    "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                    "See the limits here: https://protobuf.dev/programming-guides/proto-limits/" +
                    ''.join(IMPORT_traceback.format_exception(decode_error))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {decode_error}; "
                        "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                        "See the limits here: https://protobuf.dev/programming-guides/proto-limits/"
            )
        except BaseException as exception:
            # Not logging when within `node` as we already log there.
            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') "
                    f"{type(exception).__name__}{': ' + str(exception) if len(str(exception)) > 0 else ''}; "
                    "propagating as 'Unknown'\n" +
                    ''.join(IMPORT_traceback.format_exception(exception))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                # TODO(benh): consider whether or not we want to
                # include the 'package.service.method' which may
                # get concatenated together forming a kind of
                # "stack trace"; while it's super helpful for
                # debugging, it does expose implementation
                # information.
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Ensure') {type(exception).__name__}: {exception}"
            )

    @IMPORT_reboot_aio_tracing.function_span(
        # We expect an `EffectValidationRetry` exception; that's not an error.
        set_status_on_exception=False
    )
    async def _Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        *,
        validating_effects: bool,
        grpc_context: IMPORT_typing.Optional[IMPORT_grpc.aio.ServicerContext] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        # Try to verify the token if a token verifier exists.
        context.auth = await self._maybe_verify_token(
            headers=context._headers, method='Ensure'
        )

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse()
            response.ParseFromString(idempotent_mutation.response)
            return response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.EnsureAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )
            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                transaction=transaction,
                from_constructor=False,
                requires_constructor=False,
            ) as (state, writer):

                effects = await self.__Ensure(
                    context,
                    state,
                    request,
                    validating_effects=validating_effects,
                )

                await writer.complete(effects)

                # TODO: We need a single `Effects` superclass for all methods, so we
                # would need to make it "partially" generic (with per-method subclasses
                # filling out the rest of the generic parameters) in order to fix this.
                return effects.response  # type: ignore[return-value]

    async def _schedule_Ensure(
        self,
        *,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        headers: IMPORT_reboot_aio_headers.Headers,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> tuple[IMPORT_reboot_aio_contexts.WriterContext, rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse]:
        context: IMPORT_reboot_aio_contexts.WriterContext = self.create_context(
            headers=headers,
            state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            method='Ensure',
            context_type=IMPORT_reboot_aio_contexts.WriterContext,
        )
        response = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse()

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response.ParseFromString(idempotent_mutation.response)

            # We should have only scheduled a single task!
            assert len(idempotent_mutation.task_ids) == 1
            assert grpc_context is not None
            grpc_context.set_trailing_metadata(
                grpc_context.trailing_metadata() +
                (
                    (
                        IMPORT_reboot_aio_headers.TASK_ID_UUID,
                        str(IMPORT_uuid.UUID(bytes=idempotent_mutation.task_ids[0].task_uuid))
                    ),
                )
            )

            return context, response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.EnsureAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )

            # Try to verify the token if a token verifier exists.
            context.auth = await self._maybe_verify_token(
                headers=headers, method='Ensure'
            )

            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                transaction=transaction,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                from_constructor=False,
                requires_constructor=False
            ) as (state, writer):

                task = await ApplicationLogsServicerTasks(
                    context=context,
                    state_ref=context._state_ref,
                ).Ensure(
                    request,
                    schedule=context._headers.task_schedule,
                )

                effects = IMPORT_reboot_aio_state_managers.Effects(
                    response=response,
                    state=state,
                    tasks=[task],
                )

                assert effects.tasks is not None

                await writer.complete(effects)

                assert grpc_context is not None

                grpc_context.set_trailing_metadata(
                    grpc_context.trailing_metadata() +
                    (
                        (
                            IMPORT_reboot_aio_headers.TASK_ID_UUID,
                            str(IMPORT_uuid.UUID(bytes=task.task_id.task_uuid))
                        ),
                    )
                )

                return context, response

        return context, response


    # Entrypoint for non-reactive network calls (i.e. typical gRPC calls).
    async def Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        headers = IMPORT_reboot_aio_headers.Headers.from_grpc_context(grpc_context)
        assert headers.application_id is not None  # Guaranteed by `Headers`.

        # Confirm whether this is the right consensus to be serving this
        # request.
        authoritative_consensus = self.placement_client.consensus_for_actor(
            headers.application_id,
            headers.state_ref,
        )
        if authoritative_consensus != self.consensus_id:
            # This is NOT the correct consensus. Fail.
            await grpc_context.abort(
                IMPORT_grpc.StatusCode.UNAVAILABLE,
                f"Consensus '{self.consensus_id}' is not authoritative for this "
                f"request; consensus '{authoritative_consensus}' is.",
            )
            raise  # Unreachable but necessary for mypy.

        @IMPORT_reboot_aio_internals_middleware.maybe_run_function_twice_to_validate_effects
        async def _run(
            validating_effects: bool,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
            context: IMPORT_typing.Optional[IMPORT_reboot_aio_contexts.Context] = None
            try:
                if headers.task_schedule is not None:
                    context, response = await self._schedule_Ensure(
                        headers=headers,
                        request=request,
                        grpc_context=grpc_context,
                    )
                    return response

                context = self.create_context(
                    headers=headers,
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='Ensure',
                    context_type=IMPORT_reboot_aio_contexts.WriterContext,
                )
                assert context is not None

                return await self._Ensure(
                    request,
                    context,
                    validating_effects=validating_effects,
                    grpc_context=grpc_context,
                )
            except IMPORT_reboot_aio_contexts.EffectValidationRetry:
                # Doing effect validation, just let this propagate.
                raise
            except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                status = IMPORT_rpc_status_sync.to_status(aborted.to_status())
                # Need to add transaction participants here because
                # calling `grpc_context.abort_with_status()` will
                # ignore any other trailing metadata.
                if context is not None and context.transaction_id is not None:
                    status = status._replace(
                        trailing_metadata=status.trailing_metadata + context.participants.to_grpc_metadata()
                    )
                await grpc_context.abort_with_status(status)
                raise  # Unreachable but necessary for mypy.
            except IMPORT_asyncio.CancelledError:
                # It's pretty normal for an RPC to be cancelled; it's not useful to
                # print a stack trace.
                raise
            except BaseException as exception:
                # Print the exception stack trace for easier debugging. Note
                # that we don't include the stack trace in an error message
                # for the same reason that gRPC doesn't do so by default,
                # see https://github.com/grpc/grpc/issues/14897, but since this
                # should only get logged on the server side it is safe.
                logger.warning(
                    'Unhandled exception\n' +
                    ''.join(IMPORT_traceback.format_exc() if IMPORT_reboot_nodejs_python.should_print_stacktrace() else [f"{type(exception).__name__}: {exception}"])
                )

                # Re-raise the exception for gRPC to handle!
                #
                # TODO: gRPC will print a stack trace from this
                # exception which we don't want if we're executing via
                # Node.js.
                raise
            finally:
                if context is not None and context.transaction_id is not None:
                    # Propagate transaction participants.
                    grpc_context.set_trailing_metadata(
                        grpc_context.trailing_metadata() +
                        context.participants.to_grpc_metadata()
                    )

        with IMPORT_reboot_aio_tracing.context_from_headers(headers):
            return await _run()

    async def __RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        *,
        validating_effects: bool,
    ) -> ApplicationLogs.RegisterConsensusEffects:
        try:
            response = (
                await self._servicer._RegisterConsensus(
                    context=context,
                    state=state,
                    request=request
                )
            )
            IMPORT_reboot_aio_types.assert_type(
                response,
                [rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse],
            )
            self.maybe_raise_effect_validation_retry(
                logger=logger,
                idempotency_manager=context,
                method_name='ApplicationLogs.RegisterConsensus',
                validating_effects=validating_effects,
                context=context,
            )
            return ApplicationLogs.RegisterConsensusEffects(
                state=state,
                response=response,
                tasks=context._tasks,
                _colocated_upserts=context._colocated_upserts,
            )
        except IMPORT_reboot_aio_contexts.RetryReactively:
            # Retrying reactively, just let this propagate.
            raise
        except IMPORT_reboot_aio_contexts.EffectValidationRetry:
            # Doing effect validation, just let this propagate.
            raise
        except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
            # If the caller aborted due to a retryable error, just
            # propagate the aborted instead of propagating `Unknown`
            # so that a client can transparently retry.
            if IMPORT_rebootdev.aio.aborted.is_retryable(aborted):
                raise aborted
            # Log any _unhandled_ abort stack traces to make it
            # easier for debugging.
            #
            # NOTE: we don't log if we're a task as it will be logged
            # in `public/rebootdev/aio/internals/tasks_dispatcher.py` instead.
            aborted_type: IMPORT_typing.Optional[type] = None
            aborted_type = ApplicationLogs.RegisterConsensusAborted
            if isinstance(aborted, IMPORT_rebootdev.aio.aborted.SystemAborted):
                # Not logging when within `node` as we already log there.
                if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                    logger.warning(
                        f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {aborted}; propagating as 'Unknown'\n" +
                        ''.join(IMPORT_traceback.format_exception(aborted))
                    )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                    # TODO(benh): consider whether or not we want to
                    # include the 'package.service.method' which may
                    # get concatenated together forming a kind of
                    # "stack trace"; while it's super helpful for
                    # debugging, it does expose implementation
                    # information.
                    message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {aborted}"
                )
            else:
                if (
                    aborted_type is not None and
                    not isinstance(aborted, aborted_type) and
                    aborted_type.is_declared_error(aborted.error)
                ):
                    # We propagate declared errors that might have
                    # come from another call, i.e., we might have an
                    # `Aborted` but not for this method but the
                    # `Aborted` that we have has an error that this
                    # method declared. This allows a developer to
                    # simply add the declared error to their `.proto`
                    # file rather than having to catch and re-raise
                    # the error with their own aborted type.
                    if context.task is None:
                        logger.warning(
                            f"Propagating unhandled but declared error (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {aborted}"
                        )
                elif (
                    aborted_type is None or
                    not isinstance(aborted, aborted_type)
                ):
                    # Not logging when within `node` as we already log there.
                    if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                        logger.warning(
                            f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {aborted}; propagating as 'Unknown'\n" +
                            ''.join(IMPORT_traceback.format_exception(aborted))
                        )
                    # If this wasn't a declared error than we
                    # propagate it as `Unknown`.
                    raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                        IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                        # TODO(benh): consider whether or not we want to
                        # include the 'package.service.method' which may
                        # get concatenated together forming a kind of
                        # "stack trace"; while it's super helpful for
                        # debugging, it does expose implementation
                        # information.
                        message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {aborted}"
                    )

            raise
        except IMPORT_asyncio.CancelledError:
            # It's pretty normal for an RPC to be cancelled; it's not useful to
            # print a stack trace.
            raise
        except IMPORT_google_protobuf_message.DecodeError as decode_error:
            # We usually see this error when we are trying to construct a proto
            # message which is too deeply nested: protobuf has a limit of 100
            # nested messages. See the limits here:
            #   https://protobuf.dev/programming-guides/proto-limits/

            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') "
                    f"{type(decode_error).__name__}{': ' + str(decode_error) if len(str(decode_error)) > 0 else ''}; "
                    "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                    "See the limits here: https://protobuf.dev/programming-guides/proto-limits/" +
                    ''.join(IMPORT_traceback.format_exception(decode_error))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {decode_error}; "
                        "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                        "See the limits here: https://protobuf.dev/programming-guides/proto-limits/"
            )
        except BaseException as exception:
            # Not logging when within `node` as we already log there.
            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') "
                    f"{type(exception).__name__}{': ' + str(exception) if len(str(exception)) > 0 else ''}; "
                    "propagating as 'Unknown'\n" +
                    ''.join(IMPORT_traceback.format_exception(exception))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                # TODO(benh): consider whether or not we want to
                # include the 'package.service.method' which may
                # get concatenated together forming a kind of
                # "stack trace"; while it's super helpful for
                # debugging, it does expose implementation
                # information.
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterConsensus') {type(exception).__name__}: {exception}"
            )

    @IMPORT_reboot_aio_tracing.function_span(
        # We expect an `EffectValidationRetry` exception; that's not an error.
        set_status_on_exception=False
    )
    async def _RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        *,
        validating_effects: bool,
        grpc_context: IMPORT_typing.Optional[IMPORT_grpc.aio.ServicerContext] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        # Try to verify the token if a token verifier exists.
        context.auth = await self._maybe_verify_token(
            headers=context._headers, method='RegisterConsensus'
        )

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse()
            response.ParseFromString(idempotent_mutation.response)
            return response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.RegisterConsensusAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )
            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                transaction=transaction,
                from_constructor=False,
                requires_constructor=False,
            ) as (state, writer):

                effects = await self.__RegisterConsensus(
                    context,
                    state,
                    request,
                    validating_effects=validating_effects,
                )

                await writer.complete(effects)

                # TODO: We need a single `Effects` superclass for all methods, so we
                # would need to make it "partially" generic (with per-method subclasses
                # filling out the rest of the generic parameters) in order to fix this.
                return effects.response  # type: ignore[return-value]

    async def _schedule_RegisterConsensus(
        self,
        *,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        headers: IMPORT_reboot_aio_headers.Headers,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> tuple[IMPORT_reboot_aio_contexts.WriterContext, rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse]:
        context: IMPORT_reboot_aio_contexts.WriterContext = self.create_context(
            headers=headers,
            state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            method='RegisterConsensus',
            context_type=IMPORT_reboot_aio_contexts.WriterContext,
        )
        response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse()

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response.ParseFromString(idempotent_mutation.response)

            # We should have only scheduled a single task!
            assert len(idempotent_mutation.task_ids) == 1
            assert grpc_context is not None
            grpc_context.set_trailing_metadata(
                grpc_context.trailing_metadata() +
                (
                    (
                        IMPORT_reboot_aio_headers.TASK_ID_UUID,
                        str(IMPORT_uuid.UUID(bytes=idempotent_mutation.task_ids[0].task_uuid))
                    ),
                )
            )

            return context, response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.RegisterConsensusAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )

            # Try to verify the token if a token verifier exists.
            context.auth = await self._maybe_verify_token(
                headers=headers, method='RegisterConsensus'
            )

            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                transaction=transaction,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                from_constructor=False,
                requires_constructor=False
            ) as (state, writer):

                task = await ApplicationLogsServicerTasks(
                    context=context,
                    state_ref=context._state_ref,
                ).RegisterConsensus(
                    request,
                    schedule=context._headers.task_schedule,
                )

                effects = IMPORT_reboot_aio_state_managers.Effects(
                    response=response,
                    state=state,
                    tasks=[task],
                )

                assert effects.tasks is not None

                await writer.complete(effects)

                assert grpc_context is not None

                grpc_context.set_trailing_metadata(
                    grpc_context.trailing_metadata() +
                    (
                        (
                            IMPORT_reboot_aio_headers.TASK_ID_UUID,
                            str(IMPORT_uuid.UUID(bytes=task.task_id.task_uuid))
                        ),
                    )
                )

                return context, response

        return context, response


    # Entrypoint for non-reactive network calls (i.e. typical gRPC calls).
    async def RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        headers = IMPORT_reboot_aio_headers.Headers.from_grpc_context(grpc_context)
        assert headers.application_id is not None  # Guaranteed by `Headers`.

        # Confirm whether this is the right consensus to be serving this
        # request.
        authoritative_consensus = self.placement_client.consensus_for_actor(
            headers.application_id,
            headers.state_ref,
        )
        if authoritative_consensus != self.consensus_id:
            # This is NOT the correct consensus. Fail.
            await grpc_context.abort(
                IMPORT_grpc.StatusCode.UNAVAILABLE,
                f"Consensus '{self.consensus_id}' is not authoritative for this "
                f"request; consensus '{authoritative_consensus}' is.",
            )
            raise  # Unreachable but necessary for mypy.

        @IMPORT_reboot_aio_internals_middleware.maybe_run_function_twice_to_validate_effects
        async def _run(
            validating_effects: bool,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
            context: IMPORT_typing.Optional[IMPORT_reboot_aio_contexts.Context] = None
            try:
                if headers.task_schedule is not None:
                    context, response = await self._schedule_RegisterConsensus(
                        headers=headers,
                        request=request,
                        grpc_context=grpc_context,
                    )
                    return response

                context = self.create_context(
                    headers=headers,
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='RegisterConsensus',
                    context_type=IMPORT_reboot_aio_contexts.WriterContext,
                )
                assert context is not None

                return await self._RegisterConsensus(
                    request,
                    context,
                    validating_effects=validating_effects,
                    grpc_context=grpc_context,
                )
            except IMPORT_reboot_aio_contexts.EffectValidationRetry:
                # Doing effect validation, just let this propagate.
                raise
            except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                status = IMPORT_rpc_status_sync.to_status(aborted.to_status())
                # Need to add transaction participants here because
                # calling `grpc_context.abort_with_status()` will
                # ignore any other trailing metadata.
                if context is not None and context.transaction_id is not None:
                    status = status._replace(
                        trailing_metadata=status.trailing_metadata + context.participants.to_grpc_metadata()
                    )
                await grpc_context.abort_with_status(status)
                raise  # Unreachable but necessary for mypy.
            except IMPORT_asyncio.CancelledError:
                # It's pretty normal for an RPC to be cancelled; it's not useful to
                # print a stack trace.
                raise
            except BaseException as exception:
                # Print the exception stack trace for easier debugging. Note
                # that we don't include the stack trace in an error message
                # for the same reason that gRPC doesn't do so by default,
                # see https://github.com/grpc/grpc/issues/14897, but since this
                # should only get logged on the server side it is safe.
                logger.warning(
                    'Unhandled exception\n' +
                    ''.join(IMPORT_traceback.format_exc() if IMPORT_reboot_nodejs_python.should_print_stacktrace() else [f"{type(exception).__name__}: {exception}"])
                )

                # Re-raise the exception for gRPC to handle!
                #
                # TODO: gRPC will print a stack trace from this
                # exception which we don't want if we're executing via
                # Node.js.
                raise
            finally:
                if context is not None and context.transaction_id is not None:
                    # Propagate transaction participants.
                    grpc_context.set_trailing_metadata(
                        grpc_context.trailing_metadata() +
                        context.participants.to_grpc_metadata()
                    )

        with IMPORT_reboot_aio_tracing.context_from_headers(headers):
            return await _run()

    async def __RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        *,
        validating_effects: bool,
    ) -> ApplicationLogs.RegisterRevisionEffects:
        try:
            response = (
                await self._servicer._RegisterRevision(
                    context=context,
                    state=state,
                    request=request
                )
            )
            IMPORT_reboot_aio_types.assert_type(
                response,
                [rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse],
            )
            self.maybe_raise_effect_validation_retry(
                logger=logger,
                idempotency_manager=context,
                method_name='ApplicationLogs.RegisterRevision',
                validating_effects=validating_effects,
                context=context,
            )
            return ApplicationLogs.RegisterRevisionEffects(
                state=state,
                response=response,
                tasks=context._tasks,
                _colocated_upserts=context._colocated_upserts,
            )
        except IMPORT_reboot_aio_contexts.RetryReactively:
            # Retrying reactively, just let this propagate.
            raise
        except IMPORT_reboot_aio_contexts.EffectValidationRetry:
            # Doing effect validation, just let this propagate.
            raise
        except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
            # If the caller aborted due to a retryable error, just
            # propagate the aborted instead of propagating `Unknown`
            # so that a client can transparently retry.
            if IMPORT_rebootdev.aio.aborted.is_retryable(aborted):
                raise aborted
            # Log any _unhandled_ abort stack traces to make it
            # easier for debugging.
            #
            # NOTE: we don't log if we're a task as it will be logged
            # in `public/rebootdev/aio/internals/tasks_dispatcher.py` instead.
            aborted_type: IMPORT_typing.Optional[type] = None
            aborted_type = ApplicationLogs.RegisterRevisionAborted
            if isinstance(aborted, IMPORT_rebootdev.aio.aborted.SystemAborted):
                # Not logging when within `node` as we already log there.
                if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                    logger.warning(
                        f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {aborted}; propagating as 'Unknown'\n" +
                        ''.join(IMPORT_traceback.format_exception(aborted))
                    )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                    # TODO(benh): consider whether or not we want to
                    # include the 'package.service.method' which may
                    # get concatenated together forming a kind of
                    # "stack trace"; while it's super helpful for
                    # debugging, it does expose implementation
                    # information.
                    message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {aborted}"
                )
            else:
                if (
                    aborted_type is not None and
                    not isinstance(aborted, aborted_type) and
                    aborted_type.is_declared_error(aborted.error)
                ):
                    # We propagate declared errors that might have
                    # come from another call, i.e., we might have an
                    # `Aborted` but not for this method but the
                    # `Aborted` that we have has an error that this
                    # method declared. This allows a developer to
                    # simply add the declared error to their `.proto`
                    # file rather than having to catch and re-raise
                    # the error with their own aborted type.
                    if context.task is None:
                        logger.warning(
                            f"Propagating unhandled but declared error (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {aborted}"
                        )
                elif (
                    aborted_type is None or
                    not isinstance(aborted, aborted_type)
                ):
                    # Not logging when within `node` as we already log there.
                    if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                        logger.warning(
                            f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {aborted}; propagating as 'Unknown'\n" +
                            ''.join(IMPORT_traceback.format_exception(aborted))
                        )
                    # If this wasn't a declared error than we
                    # propagate it as `Unknown`.
                    raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                        IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                        # TODO(benh): consider whether or not we want to
                        # include the 'package.service.method' which may
                        # get concatenated together forming a kind of
                        # "stack trace"; while it's super helpful for
                        # debugging, it does expose implementation
                        # information.
                        message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {aborted}"
                    )

            raise
        except IMPORT_asyncio.CancelledError:
            # It's pretty normal for an RPC to be cancelled; it's not useful to
            # print a stack trace.
            raise
        except IMPORT_google_protobuf_message.DecodeError as decode_error:
            # We usually see this error when we are trying to construct a proto
            # message which is too deeply nested: protobuf has a limit of 100
            # nested messages. See the limits here:
            #   https://protobuf.dev/programming-guides/proto-limits/

            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') "
                    f"{type(decode_error).__name__}{': ' + str(decode_error) if len(str(decode_error)) > 0 else ''}; "
                    "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                    "See the limits here: https://protobuf.dev/programming-guides/proto-limits/" +
                    ''.join(IMPORT_traceback.format_exception(decode_error))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {decode_error}; "
                        "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                        "See the limits here: https://protobuf.dev/programming-guides/proto-limits/"
            )
        except BaseException as exception:
            # Not logging when within `node` as we already log there.
            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') "
                    f"{type(exception).__name__}{': ' + str(exception) if len(str(exception)) > 0 else ''}; "
                    "propagating as 'Unknown'\n" +
                    ''.join(IMPORT_traceback.format_exception(exception))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                # TODO(benh): consider whether or not we want to
                # include the 'package.service.method' which may
                # get concatenated together forming a kind of
                # "stack trace"; while it's super helpful for
                # debugging, it does expose implementation
                # information.
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.RegisterRevision') {type(exception).__name__}: {exception}"
            )

    @IMPORT_reboot_aio_tracing.function_span(
        # We expect an `EffectValidationRetry` exception; that's not an error.
        set_status_on_exception=False
    )
    async def _RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        *,
        validating_effects: bool,
        grpc_context: IMPORT_typing.Optional[IMPORT_grpc.aio.ServicerContext] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        # Try to verify the token if a token verifier exists.
        context.auth = await self._maybe_verify_token(
            headers=context._headers, method='RegisterRevision'
        )

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse()
            response.ParseFromString(idempotent_mutation.response)
            return response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.RegisterRevisionAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )
            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                transaction=transaction,
                from_constructor=False,
                requires_constructor=False,
            ) as (state, writer):

                effects = await self.__RegisterRevision(
                    context,
                    state,
                    request,
                    validating_effects=validating_effects,
                )

                await writer.complete(effects)

                # TODO: We need a single `Effects` superclass for all methods, so we
                # would need to make it "partially" generic (with per-method subclasses
                # filling out the rest of the generic parameters) in order to fix this.
                return effects.response  # type: ignore[return-value]

    async def _schedule_RegisterRevision(
        self,
        *,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        headers: IMPORT_reboot_aio_headers.Headers,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> tuple[IMPORT_reboot_aio_contexts.WriterContext, rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse]:
        context: IMPORT_reboot_aio_contexts.WriterContext = self.create_context(
            headers=headers,
            state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            method='RegisterRevision',
            context_type=IMPORT_reboot_aio_contexts.WriterContext,
        )
        response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse()

        # Check if we already have performed this mutation!
        #
        # We do this _before_ calling 'transactionally()' because
        # if this call is for a transaction method _and_ we've
        # already performed the transaction then we don't want to
        # become a transaction participant (again) we just want to
        # return the transaction's response.
        idempotent_mutation = self._state_manager.check_for_idempotent_mutation(
            context
        )

        if idempotent_mutation is not None:
            response.ParseFromString(idempotent_mutation.response)

            # We should have only scheduled a single task!
            assert len(idempotent_mutation.task_ids) == 1
            assert grpc_context is not None
            grpc_context.set_trailing_metadata(
                grpc_context.trailing_metadata() +
                (
                    (
                        IMPORT_reboot_aio_headers.TASK_ID_UUID,
                        str(IMPORT_uuid.UUID(bytes=idempotent_mutation.task_ids[0].task_uuid))
                    ),
                )
            )

            return context, response

        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.RegisterRevisionAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )

            # Try to verify the token if a token verifier exists.
            context.auth = await self._maybe_verify_token(
                headers=headers, method='RegisterRevision'
            )

            async with self._state_manager.writer(
                context,
                self._servicer.__state_type__,
                self.tasks_dispatcher,
                transaction=transaction,
                authorize=self._maybe_authorize(
                    method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision',
                    headers=context._headers,
                    auth=context.auth,
                    request=request,
                ),
                from_constructor=False,
                requires_constructor=False
            ) as (state, writer):

                task = await ApplicationLogsServicerTasks(
                    context=context,
                    state_ref=context._state_ref,
                ).RegisterRevision(
                    request,
                    schedule=context._headers.task_schedule,
                )

                effects = IMPORT_reboot_aio_state_managers.Effects(
                    response=response,
                    state=state,
                    tasks=[task],
                )

                assert effects.tasks is not None

                await writer.complete(effects)

                assert grpc_context is not None

                grpc_context.set_trailing_metadata(
                    grpc_context.trailing_metadata() +
                    (
                        (
                            IMPORT_reboot_aio_headers.TASK_ID_UUID,
                            str(IMPORT_uuid.UUID(bytes=task.task_id.task_uuid))
                        ),
                    )
                )

                return context, response

        return context, response


    # Entrypoint for non-reactive network calls (i.e. typical gRPC calls).
    async def RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        headers = IMPORT_reboot_aio_headers.Headers.from_grpc_context(grpc_context)
        assert headers.application_id is not None  # Guaranteed by `Headers`.

        # Confirm whether this is the right consensus to be serving this
        # request.
        authoritative_consensus = self.placement_client.consensus_for_actor(
            headers.application_id,
            headers.state_ref,
        )
        if authoritative_consensus != self.consensus_id:
            # This is NOT the correct consensus. Fail.
            await grpc_context.abort(
                IMPORT_grpc.StatusCode.UNAVAILABLE,
                f"Consensus '{self.consensus_id}' is not authoritative for this "
                f"request; consensus '{authoritative_consensus}' is.",
            )
            raise  # Unreachable but necessary for mypy.

        @IMPORT_reboot_aio_internals_middleware.maybe_run_function_twice_to_validate_effects
        async def _run(
            validating_effects: bool,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
            context: IMPORT_typing.Optional[IMPORT_reboot_aio_contexts.Context] = None
            try:
                if headers.task_schedule is not None:
                    context, response = await self._schedule_RegisterRevision(
                        headers=headers,
                        request=request,
                        grpc_context=grpc_context,
                    )
                    return response

                context = self.create_context(
                    headers=headers,
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='RegisterRevision',
                    context_type=IMPORT_reboot_aio_contexts.WriterContext,
                )
                assert context is not None

                return await self._RegisterRevision(
                    request,
                    context,
                    validating_effects=validating_effects,
                    grpc_context=grpc_context,
                )
            except IMPORT_reboot_aio_contexts.EffectValidationRetry:
                # Doing effect validation, just let this propagate.
                raise
            except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                status = IMPORT_rpc_status_sync.to_status(aborted.to_status())
                # Need to add transaction participants here because
                # calling `grpc_context.abort_with_status()` will
                # ignore any other trailing metadata.
                if context is not None and context.transaction_id is not None:
                    status = status._replace(
                        trailing_metadata=status.trailing_metadata + context.participants.to_grpc_metadata()
                    )
                await grpc_context.abort_with_status(status)
                raise  # Unreachable but necessary for mypy.
            except IMPORT_asyncio.CancelledError:
                # It's pretty normal for an RPC to be cancelled; it's not useful to
                # print a stack trace.
                raise
            except BaseException as exception:
                # Print the exception stack trace for easier debugging. Note
                # that we don't include the stack trace in an error message
                # for the same reason that gRPC doesn't do so by default,
                # see https://github.com/grpc/grpc/issues/14897, but since this
                # should only get logged on the server side it is safe.
                logger.warning(
                    'Unhandled exception\n' +
                    ''.join(IMPORT_traceback.format_exc() if IMPORT_reboot_nodejs_python.should_print_stacktrace() else [f"{type(exception).__name__}: {exception}"])
                )

                # Re-raise the exception for gRPC to handle!
                #
                # TODO: gRPC will print a stack trace from this
                # exception which we don't want if we're executing via
                # Node.js.
                raise
            finally:
                if context is not None and context.transaction_id is not None:
                    # Propagate transaction participants.
                    grpc_context.set_trailing_metadata(
                        grpc_context.trailing_metadata() +
                        context.participants.to_grpc_metadata()
                    )

        with IMPORT_reboot_aio_tracing.context_from_headers(headers):
            return await _run()

    async def __Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        *,
        validating_effects: bool,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        try:
            async for response in self._servicer._Logs(
                context=context,
                states=states,
                request=request
            ):
                IMPORT_reboot_aio_types.assert_type(response, [rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse])
                yield response
        except IMPORT_reboot_aio_contexts.RetryReactively:
            # Retrying reactively, just let this propagate.
            raise
        except IMPORT_reboot_aio_contexts.EffectValidationRetry:
            # Doing effect validation, just let this propagate.
            raise
        except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
            # If the caller aborted due to a retryable error, just
            # propagate the aborted instead of propagating `Unknown`
            # so that a client can transparently retry.
            if IMPORT_rebootdev.aio.aborted.is_retryable(aborted):
                raise aborted
            # Log any _unhandled_ abort stack traces to make it
            # easier for debugging.
            #
            # NOTE: we don't log if we're a task as it will be logged
            # in `public/rebootdev/aio/internals/tasks_dispatcher.py` instead.
            aborted_type: IMPORT_typing.Optional[type] = None
            aborted_type = ApplicationLogs.LogsAborted
            if isinstance(aborted, IMPORT_rebootdev.aio.aborted.SystemAborted):
                # Not logging when within `node` as we already log there.
                if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                    logger.warning(
                        f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {aborted}; propagating as 'Unknown'\n" +
                        ''.join(IMPORT_traceback.format_exception(aborted))
                    )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                    # TODO(benh): consider whether or not we want to
                    # include the 'package.service.method' which may
                    # get concatenated together forming a kind of
                    # "stack trace"; while it's super helpful for
                    # debugging, it does expose implementation
                    # information.
                    message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {aborted}"
                )
            else:
                if (
                    aborted_type is not None and
                    not isinstance(aborted, aborted_type) and
                    aborted_type.is_declared_error(aborted.error)
                ):
                    # We propagate declared errors that might have
                    # come from another call, i.e., we might have an
                    # `Aborted` but not for this method but the
                    # `Aborted` that we have has an error that this
                    # method declared. This allows a developer to
                    # simply add the declared error to their `.proto`
                    # file rather than having to catch and re-raise
                    # the error with their own aborted type.
                    if context.task is None:
                        logger.warning(
                            f"Propagating unhandled but declared error (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {aborted}"
                        )
                elif (
                    aborted_type is None or
                    not isinstance(aborted, aborted_type)
                ):
                    # Not logging when within `node` as we already log there.
                    if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                        logger.warning(
                            f"Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {aborted}; propagating as 'Unknown'\n" +
                            ''.join(IMPORT_traceback.format_exception(aborted))
                        )
                    # If this wasn't a declared error than we
                    # propagate it as `Unknown`.
                    raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                        IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                        # TODO(benh): consider whether or not we want to
                        # include the 'package.service.method' which may
                        # get concatenated together forming a kind of
                        # "stack trace"; while it's super helpful for
                        # debugging, it does expose implementation
                        # information.
                        message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {aborted}"
                    )

            raise
        except IMPORT_asyncio.CancelledError:
            # It's pretty normal for an RPC to be cancelled; it's not useful to
            # print a stack trace.
            raise
        except IMPORT_google_protobuf_message.DecodeError as decode_error:
            # We usually see this error when we are trying to construct a proto
            # message which is too deeply nested: protobuf has a limit of 100
            # nested messages. See the limits here:
            #   https://protobuf.dev/programming-guides/proto-limits/

            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') "
                    f"{type(decode_error).__name__}{': ' + str(decode_error) if len(str(decode_error)) > 0 else ''}; "
                    "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                    "See the limits here: https://protobuf.dev/programming-guides/proto-limits/" +
                    ''.join(IMPORT_traceback.format_exception(decode_error))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {decode_error}; "
                        "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                        "See the limits here: https://protobuf.dev/programming-guides/proto-limits/"
            )
        except BaseException as exception:
            # Not logging when within `node` as we already log there.
            if IMPORT_reboot_nodejs_python.should_print_stacktrace():
                logger.warning(
                    "Unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') "
                    f"{type(exception).__name__}{': ' + str(exception) if len(str(exception)) > 0 else ''}; "
                    "propagating as 'Unknown'\n" +
                    ''.join(IMPORT_traceback.format_exception(exception))
                )
            raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                # TODO(benh): consider whether or not we want to
                # include the 'package.service.method' which may
                # get concatenated together forming a kind of
                # "stack trace"; while it's super helpful for
                # debugging, it does expose implementation
                # information.
                message=f"unhandled (in 'rbt.cloud.v1alpha1.logs.ApplicationLogs.Logs') {type(exception).__name__}: {exception}"
            )

    @IMPORT_reboot_aio_tracing.generator_span(
        # We expect an `EffectValidationRetry` exception; that's not an error.
        set_status_on_exception=False
    )
    async def _Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        *,
        validating_effects: bool,
        grpc_context: IMPORT_typing.Optional[IMPORT_grpc.aio.ServicerContext] = None,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        # Try to verify the token if a token verifier exists.
        context.auth = await self._maybe_verify_token(
            headers=context._headers, method='Logs'
        )


        async with self._state_manager.transactionally(
            context,
            self.tasks_dispatcher,
            aborted_type=ApplicationLogs.LogsAborted,
        ) as transaction:
            if transaction is not None:
                context.participants.add(
                    self._servicer.__state_type_name__, context._state_ref
                )
            authorizer = self._maybe_authorize(
                method_name='rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs',
                headers=context._headers,
                auth=context.auth,
                request=request,
            )
            async with self._state_manager.streaming_reader(
                context,
                self._servicer.__state_type__,
                authorize=authorizer,
            ) as states:
                async for response in self.__Logs(
                    context,
                    states,
                    request,
                    validating_effects=True,
                ):
                    yield response

    async def Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        grpc_context: IMPORT_grpc.aio.ServicerContext,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        headers = IMPORT_reboot_aio_headers.Headers.from_grpc_context(grpc_context)
        assert headers.application_id is not None  # Guaranteed by `Headers`.

        # Confirm whether this is the right consensus to be serving this
        # request.
        authoritative_consensus = self.placement_client.consensus_for_actor(
            headers.application_id,
            headers.state_ref,
        )
        if authoritative_consensus != self.consensus_id:
            # This is NOT the correct consensus. Fail.
            await grpc_context.abort(
                IMPORT_grpc.StatusCode.UNAVAILABLE,
                f"Consensus '{self.consensus_id}' is not authoritative for this "
                f"request; consensus '{authoritative_consensus}' is.",
            )
            raise  # Unreachable but necessary for mypy.

        async def _run(
        ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
            context: IMPORT_typing.Optional[IMPORT_reboot_aio_contexts.Context] = None
            try:

                context = self.create_context(
                    headers=headers,
                    state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    method='Logs',
                    context_type=IMPORT_reboot_aio_contexts.ReaderContext,
                )
                assert context is not None

                async for response in self._Logs(
                    request,
                    context,
                    validating_effects=True,
                    grpc_context=grpc_context,
                ):
                    yield response
            except IMPORT_reboot_aio_contexts.EffectValidationRetry:
                # Doing effect validation, just let this propagate.
                raise
            except IMPORT_rebootdev.aio.aborted.Aborted as aborted:
                status = IMPORT_rpc_status_sync.to_status(aborted.to_status())
                # Need to add transaction participants here because
                # calling `grpc_context.abort_with_status()` will
                # ignore any other trailing metadata.
                if context is not None and context.transaction_id is not None:
                    status = status._replace(
                        trailing_metadata=status.trailing_metadata + context.participants.to_grpc_metadata()
                    )
                await grpc_context.abort_with_status(status)
                raise  # Unreachable but necessary for mypy.
            except IMPORT_asyncio.CancelledError:
                # It's pretty normal for an RPC to be cancelled; it's not useful to
                # print a stack trace.
                raise
            except BaseException as exception:
                # Print the exception stack trace for easier debugging. Note
                # that we don't include the stack trace in an error message
                # for the same reason that gRPC doesn't do so by default,
                # see https://github.com/grpc/grpc/issues/14897, but since this
                # should only get logged on the server side it is safe.
                logger.warning(
                    'Unhandled exception\n' +
                    ''.join(IMPORT_traceback.format_exc() if IMPORT_reboot_nodejs_python.should_print_stacktrace() else [f"{type(exception).__name__}: {exception}"])
                )

                # Re-raise the exception for gRPC to handle!
                #
                # TODO: gRPC will print a stack trace from this
                # exception which we don't want if we're executing via
                # Node.js.
                raise
            finally:
                if context is not None and context.transaction_id is not None:
                    # Propagate transaction participants.
                    grpc_context.set_trailing_metadata(
                        grpc_context.trailing_metadata() +
                        context.participants.to_grpc_metadata()
                    )

        with IMPORT_reboot_aio_tracing.context_from_headers(headers):
            async for response in _run():
                yield response

    def _maybe_authorize(
        self,
        *,
        method_name: str,
        headers: IMPORT_reboot_aio_headers.Headers,
        auth: IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.Auth],
        request: IMPORT_typing.Optional[ApplicationLogsRequestTypes] = None,
    ) -> IMPORT_typing.Optional[IMPORT_typing.Callable[[IMPORT_typing.Optional[ApplicationLogsStateType]], IMPORT_typing.Awaitable[None]]]:
        """Returns a function to check authorization for the given method.

        Raises `PermissionDenied` in case Authorizer is present but the request
        is not authorized.
        """
        # To authorize internal calls, we use an internal magic token.
        if headers.bearer_token == __internal_magic_token__:
            return None

        assert self._authorizer is not None

        async def authorize(state: IMPORT_typing.Optional[ApplicationLogsStateType]) -> None:
            # Create context for the authorizer. This is a `ReaderContext`
            # independently of the calling context.
            with self.use_context(
                headers=(
                    # Get headers suitable for doing authorization.
                    headers.copy_for_token_verification_and_authorization()
                ),
                state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                method=method_name,
                context_type=IMPORT_reboot_aio_contexts.ReaderContext,
            ) as context:
                context.auth = auth

                # Get the authorizer decision.
                authorization_decision = await self._authorizer.authorize(
                    method_name=method_name,
                    context=context,
                    state=state,
                    request=request,
                )

            # Enforce correct authorizer decision type.
            try:
                IMPORT_reboot_aio_types.assert_type(
                    authorization_decision,
                    [
                        IMPORT_rbt_v1alpha1.errors_pb2.Ok,
                        IMPORT_rbt_v1alpha1.errors_pb2.Unauthenticated,
                        IMPORT_rbt_v1alpha1.errors_pb2.PermissionDenied,
                    ]
                )
            except TypeError as e:
                # Retyping.cast the exception to provide more context.
                authorizer_type = f"{type(self._authorizer).__module__}.{type(self._authorizer).__name__}"
                raise TypeError(
                    f"Authorizer '{authorizer_type}' "
                    f"returned unexpected type '{type(authorization_decision).__name__}' "
                    f"for method '{method_name}' on "
                    f"`rbt.cloud.v1alpha1.logs.ApplicationLogs('{headers.state_ref.id}')`"
                ) from e

            # If the decision is not `True`, raise a `SystemAborted` with either a
            # `PermissionDenied` error (in case of `False`) or an `Unauthenticated`
            # error.
            if not isinstance(authorization_decision, IMPORT_rbt_v1alpha1.errors_pb2.Ok):
                if isinstance(authorization_decision, IMPORT_rbt_v1alpha1.errors_pb2.Unauthenticated):
                    logger.warning(
                        f"Unauthenticated call to '{method_name}' on "
                        f"`rbt.cloud.v1alpha1.logs.ApplicationLogs('{headers.state_ref.id}')`"
                    )

                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    authorization_decision,
                    message=
                    f"You are not authorized to call '{method_name}' on "
                    f"`rbt.cloud.v1alpha1.logs.ApplicationLogs('{headers.state_ref.id}')`"
                )

        return authorize

    async def _maybe_verify_token(
        self,
        *,
        headers: IMPORT_reboot_aio_headers.Headers,
        method: str,
    ) -> IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.Auth]:
        """Verify the bearer token and if a token verifier is present.

        Returns the (optional) `rebootdev.aio.auth.Auth` object
        produced by the token verifier if the token can be verified.
        """
        if self._token_verifier is not None:
            if headers.bearer_token == __internal_magic_token__:
                return None

            with self.use_context(
                headers=(
                    # Get headers suitable for doing token verification.
                    headers.copy_for_token_verification_and_authorization()
                ),
                state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                method=method,
                context_type=IMPORT_reboot_aio_contexts.ReaderContext,
            ) as context:
                return await self._token_verifier.verify_token(
                    context=context,
                    token=headers.bearer_token,
                )

        return None


############################ Client Stubs ############################
# This section is relevant for clients accessing a Reboot service. Since
# servicers are themselves often clients also, this code is generated for
# them also.


class _ApplicationLogsStub(IMPORT_reboot_aio_stubs.Stub):

    __state_type_name__ = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs')

    def __init__(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        # Within a Reboot context we do not pass on the caller's bearer token, as that might
        # have security implications - we cannot simply trust any service we are calling with
        # the user's credentials. Instead, the developer can rely on the default app-internal
        # auth, or override that and set an explicit bearer token.
        #
        # In the case of `ExternalContext`, however, its `bearer_token` was set specifically
        # by the developer for the purpose of making these calls.
        app_internal_authorization: IMPORT_typing.Optional[str] = None
        if isinstance(context, IMPORT_reboot_aio_external.ExternalContext):
            # Note that only `ExternalContext` even has a `bearer_token` field.
            bearer_token = context.bearer_token
            app_internal_authorization = context.app_internal_authorization

        super().__init__(
            channel_manager=context.channel_manager,
            idempotency_manager=context,
            state_ref=state_ref,
            context=context if isinstance(context, IMPORT_reboot_aio_contexts.Context) else None,
            bearer_token=bearer_token,
            app_internal_authorization=app_internal_authorization,
        )

        # All the channels for all services of this state will go to the same
        # place, so we can just get a single channel and share it across all
        # stubs.
        channel = self._channel_manager.get_channel_to_state(
            self.__state_type_name__, state_ref
        )
        self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub = rbt.cloud.v1alpha1.logs.logs_pb2_grpc.ApplicationLogsMethodsStub(channel)


class ApplicationLogsReaderStub(_ApplicationLogsStub):

    def __init__(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext | IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        *,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.ReaderContext, IMPORT_reboot_aio_contexts.WriterContext, IMPORT_reboot_aio_contexts.TransactionContext, IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])
        super().__init__(
            context=context,
            state_ref=state_ref,
            bearer_token=bearer_token,
        )

    # ApplicationLogs specific methods:



    async def Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs')
        service_name = IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods')
        method = 'Logs'

        async def call():
            async with self._call(
                state_type_name,
                service_name,
                method,
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Logs,
                request,
                unary=False,
                reader=True,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse,
                aborted_type=ApplicationLogs.LogsAborted,
                metadata=metadata,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.AsyncIterable)
                async for response in call:
                    yield response

        async for response in call():
            yield response



class ApplicationLogsWriterStub(_ApplicationLogsStub):

    def __init__(
        self,
        context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        *,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.TransactionContext, IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])
        super().__init__(
            context=context,
            state_ref=state_ref,
            bearer_token=bearer_token,
        )

    # ApplicationLogs specific methods:
    async def Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='Ensure',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.EnsureAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'Ensure',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Ensure,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse,
                aborted_type=ApplicationLogs.EnsureAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterConsensus',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterConsensusAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterConsensus',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterConsensus,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse,
                aborted_type=ApplicationLogs.RegisterConsensusAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterRevision',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterRevisionAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterRevision',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterRevision,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse,
                aborted_type=ApplicationLogs.RegisterRevisionAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        async with self._call(
            IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            'Logs',
            self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Logs,
            request,
            unary=False,
            reader=True,
            response_type=rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse,
            aborted_type=ApplicationLogs.LogsAborted,
            metadata=metadata,
            bearer_token=bearer_token,
        ) as call:
            assert isinstance(call, IMPORT_typing.AsyncIterable), type(call)
            async for response in call:
                yield response


class ApplicationLogsWorkflowStub(_ApplicationLogsStub):

    def __init__(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.TransactionContext, IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])
        super().__init__(
            context=context,
            state_ref=state_ref,
            bearer_token=bearer_token,
        )

    # ApplicationLogs specific methods:
    async def Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='Ensure',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.EnsureAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'Ensure',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Ensure,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse,
                aborted_type=ApplicationLogs.EnsureAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterConsensus',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterConsensusAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterConsensus',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterConsensus,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse,
                aborted_type=ApplicationLogs.RegisterConsensusAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterRevision',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterRevisionAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterRevision',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterRevision,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse,
                aborted_type=ApplicationLogs.RegisterRevisionAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                return await call

    async def Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        async with self._call(
            IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            'Logs',
            self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Logs,
            request,
            unary=False,
            reader=True,
            response_type=rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse,
            aborted_type=ApplicationLogs.LogsAborted,
            metadata=metadata,
            bearer_token=bearer_token,
        ) as call:
            assert isinstance(call, IMPORT_typing.AsyncIterable), type(call)
            async for response in call:
                yield response



class ApplicationLogsTasksStub(_ApplicationLogsStub):

    def __init__(
        self,
        context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        *,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.TransactionContext, IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])
        super().__init__(
            context=context,
            state_ref=state_ref,
            bearer_token=bearer_token,
        )

    # ApplicationLogs specific methods:
    async def Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='Ensure',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.EnsureAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'Ensure',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.Ensure,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse,
                aborted_type=ApplicationLogs.EnsureAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                await call
                for (key, value) in await call.trailing_metadata():  # type: ignore[misc, attr-defined]
                    if key == IMPORT_reboot_aio_headers.TASK_ID_UUID:
                        return IMPORT_rbt_v1alpha1.tasks_pb2.TaskId(
                            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                            state_ref=self._headers.state_ref.to_str(),
                            task_uuid=IMPORT_uuid.UUID(value).bytes,
                        )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Internal(),
                    message='Trailing metadata missing for task schedule',
                )
    async def RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterConsensus',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterConsensusAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterConsensus',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterConsensus,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse,
                aborted_type=ApplicationLogs.RegisterConsensusAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                await call
                for (key, value) in await call.trailing_metadata():  # type: ignore[misc, attr-defined]
                    if key == IMPORT_reboot_aio_headers.TASK_ID_UUID:
                        return IMPORT_rbt_v1alpha1.tasks_pb2.TaskId(
                            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                            state_ref=self._headers.state_ref.to_str(),
                            task_uuid=IMPORT_uuid.UUID(value).bytes,
                        )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Internal(),
                    message='Trailing metadata missing for task schedule',
                )
    async def RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
        *,
        metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
        idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
        with self._idempotency_manager.idempotently(
            state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._headers.state_ref,
            service_name=IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
            method='RegisterRevision',
            mutation=True,
            request=request,
            metadata=metadata,
            idempotency=idempotency,
            aborted_type=ApplicationLogs.RegisterRevisionAborted,
        ) as idempotency_key:
            async with self._call(
                IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
                'RegisterRevision',
                self._rbt_cloud_v1alpha1_logs_applicationlogsmethods_stub.RegisterRevision,
                request,
                unary=True,
                reader=False,
                response_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse,
                aborted_type=ApplicationLogs.RegisterRevisionAborted,
                metadata=metadata,
                idempotency_key=idempotency_key,
                bearer_token=bearer_token,
            ) as call:
                assert isinstance(call, IMPORT_typing.Awaitable), type(call)
                await call
                for (key, value) in await call.trailing_metadata():  # type: ignore[misc, attr-defined]
                    if key == IMPORT_reboot_aio_headers.TASK_ID_UUID:
                        return IMPORT_rbt_v1alpha1.tasks_pb2.TaskId(
                            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                            state_ref=self._headers.state_ref.to_str(),
                            task_uuid=IMPORT_uuid.UUID(value).bytes,
                        )
                raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                    IMPORT_rbt_v1alpha1.errors_pb2.Internal(),
                    message='Trailing metadata missing for task schedule',
                )


class ApplicationLogsServicerTasks:

    _context: IMPORT_reboot_aio_contexts.WriterContext

    def __init__(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        *,
        state_ref: IMPORT_reboot_aio_types.StateRef,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ):
        IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.WriterContext])
        self._context = context
        self._state_ref = state_ref

    # ApplicationLogs specific methods:
    async def Ensure(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
        *,
        schedule: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
    ) -> IMPORT_reboot_aio_tasks.TaskEffect:
        schedule = ensure_has_timezone(when=schedule)
        task = IMPORT_reboot_aio_tasks.TaskEffect(
            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._state_ref,
            method_name='Ensure',
            request=request,
            schedule=(IMPORT_reboot_time_DateTimeWithTimeZone.now() + schedule) if isinstance(
                schedule, IMPORT_datetime_timedelta
            ) else schedule,
        )

        self._context._tasks.append(task)

        return task

    async def RegisterConsensus(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
        *,
        schedule: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
    ) -> IMPORT_reboot_aio_tasks.TaskEffect:
        schedule = ensure_has_timezone(when=schedule)
        task = IMPORT_reboot_aio_tasks.TaskEffect(
            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._state_ref,
            method_name='RegisterConsensus',
            request=request,
            schedule=(IMPORT_reboot_time_DateTimeWithTimeZone.now() + schedule) if isinstance(
                schedule, IMPORT_datetime_timedelta
            ) else schedule,
        )

        self._context._tasks.append(task)

        return task

    async def RegisterRevision(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
        *,
        schedule: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
    ) -> IMPORT_reboot_aio_tasks.TaskEffect:
        schedule = ensure_has_timezone(when=schedule)
        task = IMPORT_reboot_aio_tasks.TaskEffect(
            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._state_ref,
            method_name='RegisterRevision',
            request=request,
            schedule=(IMPORT_reboot_time_DateTimeWithTimeZone.now() + schedule) if isinstance(
                schedule, IMPORT_datetime_timedelta
            ) else schedule,
        )

        self._context._tasks.append(task)

        return task

    async def Logs(
        self,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
        *,
        schedule: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
    ) -> IMPORT_reboot_aio_tasks.TaskEffect:
        schedule = ensure_has_timezone(when=schedule)
        task = IMPORT_reboot_aio_tasks.TaskEffect(
            state_type=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
            state_ref=self._state_ref,
            method_name='Logs',
            request=request,
            schedule=(IMPORT_reboot_time_DateTimeWithTimeZone.now() + schedule) if isinstance(
                schedule, IMPORT_datetime_timedelta
            ) else schedule,
        )

        self._context._tasks.append(task)

        return task



############################ Authorizers ############################
# Relevant to servicers; irrelevant to clients.

ApplicationLogsStateType: IMPORT_typing.TypeAlias = rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs
ApplicationLogsRequestTypes: IMPORT_typing.TypeAlias = \
        rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest \
        | rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest \
        | rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest \
        | rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest

class ApplicationLogsAuthorizer(
    IMPORT_rebootdev.aio.auth.authorizers.Authorizer[ApplicationLogsStateType, ApplicationLogsRequestTypes],
):
    StateType: IMPORT_typing.TypeAlias = ApplicationLogsStateType
    RequestTypes: IMPORT_typing.TypeAlias = ApplicationLogsRequestTypes
    Decision: IMPORT_typing.TypeAlias = IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision

    def __init__(
        self,
        *,
        Ensure: IMPORT_typing.Optional[
            IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule[
              rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
              rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
            ]
        ] = None,
        RegisterConsensus: IMPORT_typing.Optional[
            IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule[
              rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
              rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
            ]
        ] = None,
        RegisterRevision: IMPORT_typing.Optional[
            IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule[
              rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
              rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
            ]
        ] = None,
        Logs: IMPORT_typing.Optional[
            IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule[
              rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
              rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
            ]
        ] = None,
        # NOTE: using `_` prefix for `_default` so as not to collide
        # with any method names since a prefixed `_` is forbidden by
        # our protoc plugins.
        _default: IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule[
            rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
            IMPORT_google_protobuf_message.Message,
        ] = IMPORT_rebootdev.aio.auth.authorizers.allow_if(
            all=[IMPORT_rebootdev.aio.auth.authorizers.is_app_internal],
        ),
    ):
        self._Ensure = Ensure
        self._RegisterConsensus = RegisterConsensus
        self._RegisterRevision = RegisterRevision
        self._Logs = Logs
        self.__default = _default

    async def authorize(
        self,
        *,
        method_name: str,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        state: IMPORT_typing.Optional[ApplicationLogsStateType],
        request: IMPORT_typing.Optional[ApplicationLogsRequestTypes],
        **kwargs,
    ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision:
        if method_name == 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure':
            return await self.Ensure(
                context=context,
                state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
                request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest, request),
            )
        elif method_name == 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus':
            return await self.RegisterConsensus(
                context=context,
                state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
                request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest, request),
            )
        elif method_name == 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision':
            return await self.RegisterRevision(
                context=context,
                state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
                request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest, request),
            )
        elif method_name == 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs':
            return await self.Logs(
                context=context,
                state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
                request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest, request),
            )
        else:
            return IMPORT_rbt_v1alpha1.errors_pb2.PermissionDenied()

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    async def Ensure(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision:
        return await (self._Ensure or self.__default).execute(
            context=context,
            state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
            request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest, request),
        )

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    async def RegisterConsensus(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision:
        return await (self._RegisterConsensus or self.__default).execute(
            context=context,
            state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
            request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest, request),
        )

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    async def RegisterRevision(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision:
        return await (self._RegisterRevision or self.__default).execute(
            context=context,
            state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
            request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest, request),
        )

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    async def Logs(
        self,
        *,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_rebootdev.aio.auth.authorizers.Authorizer.Decision:
        return await (self._Logs or self.__default).execute(
            context=context,
            state=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs, state),
            request=IMPORT_typing.cast(rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest, request),
        )



############################ Reboot Servicers ############################
# Base classes for server-side implementations of Reboot servicers.
# Irrelevant to clients.

class ApplicationLogsBaseServicer(IMPORT_reboot_aio_servicers.Servicer):
    Authorizer: IMPORT_typing.TypeAlias = ApplicationLogsAuthorizer

    __service_names__ = [
        IMPORT_reboot_aio_types.ServiceName('rbt.cloud.v1alpha1.logs.ApplicationLogsMethods'),
    ]
    __state_type_name__ = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs')
    __state_type__ = rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs
    __file_descriptor__ = rbt.cloud.v1alpha1.logs.logs_pb2.DESCRIPTOR

    def __init__(self):
        super().__init__()
        # NOTE: need to hold on to the middleware so we can do inline
        # writes (see 'self.write(...)').
        #
        # Because '_middleware' is not really private this does mean
        # users may do possibly dangerous things, but this is no more
        # likely given they could have already overridden
        # 'create_middleware()'.
        self._middleware: IMPORT_typing.Optional[ApplicationLogsServicerMiddleware] = None

    def create_middleware(
        self,
        *,
        application_id: IMPORT_reboot_aio_types.ApplicationId,
        consensus_id: IMPORT_reboot_aio_types.ConsensusId,
        state_manager: IMPORT_reboot_aio_state_managers.StateManager,
        placement_client: IMPORT_reboot_aio_placement.PlacementClient,
        channel_manager: IMPORT_reboot_aio_internals_channel_manager._ChannelManager,
        tasks_cache: IMPORT_reboot_aio_internals_tasks_cache.TasksCache,
        token_verifier: IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.token_verifiers.TokenVerifier],
        effect_validation: IMPORT_reboot_aio_contexts.EffectValidation,
        app_internal_api_key_secret: str,
        ready: IMPORT_asyncio.Event,
    ) -> ApplicationLogsServicerMiddleware:
        self._middleware = ApplicationLogsServicerMiddleware(
            servicer=self,
            application_id=application_id,
            consensus_id=consensus_id,
            state_manager=state_manager,
            placement_client=placement_client,
            channel_manager=channel_manager,
            tasks_cache=tasks_cache,
            token_verifier=token_verifier,
            effect_validation=effect_validation,
            app_internal_api_key_secret=app_internal_api_key_secret,
            ready=ready,
        )
        return self._middleware

    def authorizer(self) -> IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.authorizers.Authorizer | IMPORT_rebootdev.aio.auth.authorizers.AuthorizerRule]:
        return None

    def token_verifier(self) -> IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.token_verifiers.TokenVerifier]:
        return None

    def ref(
        self,
        *,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> ApplicationLogs.WeakReference[ApplicationLogs.WeakReference._WriterSchedule]:
        context = IMPORT_reboot_aio_contexts.Context.get()

        if context is None:
            raise RuntimeError(
                'Missing asyncio context variable `context`; '
                'are you using this class without Reboot?'
            )

        return ApplicationLogs.WeakReference(
            # TODO(https://github.com/reboot-dev/mono/issues/3226): add support for calling other applications.
            # For now this always stays within the application that creates the context.
            application_id=None,
            state_id=context._state_ref.id,
            schedule_type=ApplicationLogs.WeakReference._WriterSchedule,
            # If the user didn't specify a bearer token we may still end up using the app-internal bearer token,
            # but that's decided at the time of the call.
            bearer_token=bearer_token,
            servicer=self,
        )

    class Effects(IMPORT_reboot_aio_state_managers.Effects):
        def __init__(
            self,
            *,
            state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
            response: IMPORT_typing.Optional[IMPORT_google_protobuf_message.Message] = None,
            tasks: IMPORT_typing.Optional[list[IMPORT_reboot_aio_tasks.TaskEffect]] = None,
            _colocated_upserts: IMPORT_typing.Optional[list[tuple[str, IMPORT_typing.Optional[bytes]]]] = None,
        ):
            IMPORT_reboot_aio_types.assert_type(state, [rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs])

            super().__init__(state=state, response=response, tasks=tasks, _colocated_upserts=_colocated_upserts)

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    class EnsureEffects(Effects):
        def __init__(
            self,
            *,
            state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
            response: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse,
            tasks: IMPORT_typing.Optional[list[IMPORT_reboot_aio_tasks.TaskEffect]] = None,
            _colocated_upserts: IMPORT_typing.Optional[list[tuple[str, IMPORT_typing.Optional[bytes]]]] = None,
        ):
            IMPORT_reboot_aio_types.assert_type(state, [rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs])
            IMPORT_reboot_aio_types.assert_type(response, [rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse])

            super().__init__(state=state, response=response, tasks=tasks, _colocated_upserts=_colocated_upserts)


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    class RegisterConsensusEffects(Effects):
        def __init__(
            self,
            *,
            state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
            response: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse,
            tasks: IMPORT_typing.Optional[list[IMPORT_reboot_aio_tasks.TaskEffect]] = None,
            _colocated_upserts: IMPORT_typing.Optional[list[tuple[str, IMPORT_typing.Optional[bytes]]]] = None,
        ):
            IMPORT_reboot_aio_types.assert_type(state, [rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs])
            IMPORT_reboot_aio_types.assert_type(response, [rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse])

            super().__init__(state=state, response=response, tasks=tasks, _colocated_upserts=_colocated_upserts)


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    class RegisterRevisionEffects(Effects):
        def __init__(
            self,
            *,
            state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
            response: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse,
            tasks: IMPORT_typing.Optional[list[IMPORT_reboot_aio_tasks.TaskEffect]] = None,
            _colocated_upserts: IMPORT_typing.Optional[list[tuple[str, IMPORT_typing.Optional[bytes]]]] = None,
        ):
            IMPORT_reboot_aio_types.assert_type(state, [rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs])
            IMPORT_reboot_aio_types.assert_type(response, [rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse])

            super().__init__(state=state, response=response, tasks=tasks, _colocated_upserts=_colocated_upserts)




    InlineWriterCallableResult = IMPORT_typing.TypeVar('InlineWriterCallableResult', covariant=True)

    class InlineWriterCallable(IMPORT_typing.Protocol[InlineWriterCallableResult]):
        async def __call__(
            self,
            state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs
        ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
            ...

    class WorkflowState:

        def __init__(
            self,
            servicer,
        ):
            self._servicer = servicer

        async def read(
            self, context: IMPORT_reboot_aio_contexts.WorkflowContext
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
            """Read the current state within a workflow."""
            return await (
                self.always() if context.within_until()
                else (
                    self.per_iteration() if context.within_loop()
                    else self.per_workflow()
                )
            ).read(context)

        @IMPORT_typing.overload
        async def write(
            self,
            idempotency_alias: str,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[None],
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            *,
            type: type = type(None),
        ) -> None:
            ...

        @IMPORT_typing.overload
        async def write(
            self,
            idempotency_alias: str,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            *,
            type: type[ApplicationLogsBaseServicer.InlineWriterCallableResult],
        ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
            ...

        async def write(
            self,
            idempotency_alias: str,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            *,
            type: type = type(None),
        ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
            """Perform an "inline write" within a workflow."""
            return await (
                self.per_iteration(idempotency_alias) if context.within_loop()
                else self.per_workflow(idempotency_alias)
            ).write(
                context, writer, __options__, type=type
            )

        class _Idempotently:

            def __init__(
                self,
                *,
                servicer: ApplicationLogsBaseServicer,
                alias: IMPORT_typing.Optional[str],
                how: IMPORT_reboot_aio_workflows.How,
            ):
                self._servicer = servicer
                self._alias = alias
                self._how = how

            async def read(
                self, context: IMPORT_reboot_aio_contexts.WorkflowContext
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
                """Read the current state within a workflow."""
                return await self._read(
                    self._servicer,
                    context.idempotency(
                        key=IMPORT_uuid.uuid4(),
                        generated=True,
                    ) if self._how == IMPORT_reboot_aio_workflows.ALWAYS else context.idempotency(
                        alias=self._alias,
                        each_iteration=self._how == IMPORT_reboot_aio_workflows.PER_ITERATION
                    ),
                    context,
                )

            @staticmethod
            async def _read(
                servicer: ApplicationLogsBaseServicer,
                idempotency: IMPORT_reboot_aio_idempotency.Idempotency,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
                """Read the current state within a workflow."""
                IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.WorkflowContext])

                if servicer._middleware is None:
                    raise RuntimeError(
                        'Reboot middleware was not created; '
                        'are you using this class without Reboot?'
                    )

                async def read():
                    assert servicer._middleware is not None
                    return await servicer._middleware._state_manager.read(
                        context, servicer.__state_type__
                    )

                if idempotency.always:
                    return await read()

                state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs')

                # Use the idempotency manager to make sure that this
                # reader is being called following the rules.
                with context.idempotently(
                    state_type_name=state_type_name,
                    state_ref=context._state_ref,
                    # Not calling a method so `service_name`,
                    # `method`, `request`, etc are irrelevant.
                    service_name=None,
                    method=None,
                    mutation=False,
                    request=None,
                    metadata=None,
                    idempotency=idempotency,
                    # Only need to pass `aborted_type` for mutations.
                    aborted_type=None,
                ) as idempotency_key:
                    assert idempotency_key is not None
                    return await IMPORT_reboot_aio_workflows.at_least_once(
                        (
                            # TODO: for easier debugging include the
                            # original alias (or generated alias in
                            # the case of `.per_iteration()` w/o an
                            # alias) instead of just
                            # `idempotency_key`.
                            f"inline reader of '{ state_type_name }' ({str(idempotency_key)})",
                            # NOTE: we want this to be `PER_WORKFLOW`
                            # because any per iteration concerns
                            # should have already been taken care of
                            # by caller using `.per_iteration()`.
                            IMPORT_reboot_aio_workflows.PER_WORKFLOW
                        ),
                        context,
                        read,
                        type=rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
                    )

            @IMPORT_typing.overload
            async def write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[None],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                type: type = type(None),
                check_type: bool = True,
            ) -> None:
                ...

            @IMPORT_typing.overload
            async def write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                type: type[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                check_type: bool = True,
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                ...

            async def write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                type: type = type(None),
                check_type: bool = True,
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                return await self._write(
                    context,
                    writer,
                    __options__,
                    type_result=type,
                    check_type=check_type,
                )

            async def _write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                type_result: type,
                check_type: bool,
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                unidempotently = self._how == IMPORT_reboot_aio_workflows.ALWAYS
                idempotency = (
                    context.idempotency(
                        key=IMPORT_uuid.uuid4(),
                        generated=True,
                    ) if unidempotently else context.idempotency(
                        alias=self._alias,
                        each_iteration=self._how == IMPORT_reboot_aio_workflows.PER_ITERATION
                    )
                )

                return await self._write_validating_effects(
                    self._servicer,
                    idempotency,
                    context,
                    writer,
                    __options__,
                    type_result=type_result,
                    check_type=check_type,
                    unidempotently=unidempotently,
                    checkpoint=context.checkpoint(),
                )

            @staticmethod
            @IMPORT_reboot_aio_internals_middleware.maybe_run_function_twice_to_validate_effects
            async def _write_validating_effects(
                validating_effects: bool,
                servicer: ApplicationLogsBaseServicer,
                idempotency: IMPORT_reboot_aio_idempotency.Idempotency,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                type_result: type,
                check_type: bool,
                unidempotently: bool,
                checkpoint: IMPORT_reboot_aio_idempotency.Checkpoint,
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    raise RuntimeError(
                        'Found redundant idempotency in `Options`'
                    )

                IMPORT_reboot_aio_types.assert_type(context, [IMPORT_reboot_aio_contexts.WorkflowContext])

                if servicer._middleware is None:
                    raise RuntimeError(
                        'Reboot middleware was not created; '
                        'are you using this class without Reboot?'
                    )

                metadata: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None

                if __options__ is not None:
                    if __options__.metadata is not None:
                        metadata = __options__.metadata

                if metadata is None:
                    metadata = ()

                headers = IMPORT_reboot_aio_headers.Headers(
                    application_id=context.application_id,
                    state_ref=context._state_ref,
                )

                metadata += headers.to_grpc_metadata()

                idempotency_key: IMPORT_typing.Optional[IMPORT_uuid.UUID]
                with context.idempotently(
                    state_type_name=IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                    state_ref=context._state_ref,
                    service_name=None,  # Indicates an inline writer.
                    method=None,  # Indicates an inline writer.
                    mutation=True,
                    request=None,  # Indicates an inline writer.
                    metadata=metadata,
                    idempotency=idempotency,
                    aborted_type=None,  # Indicates an inline writer.
                ) as idempotency_key:

                    if any(t[0] == IMPORT_reboot_aio_headers.IDEMPOTENCY_KEY_HEADER for t in metadata):
                        raise ValueError(
                            f"Do not set '{IMPORT_reboot_aio_headers.IDEMPOTENCY_KEY_HEADER}' metadata yourself"
                        )

                    if idempotency_key is not None:
                        metadata += (
                            (IMPORT_reboot_aio_headers.IDEMPOTENCY_KEY_HEADER, str(idempotency_key)),
                        )

                    with servicer._middleware.use_context(
                        headers=IMPORT_reboot_aio_headers.Headers.from_grpc_metadata(metadata),
                        state_type_name = IMPORT_reboot_aio_types.StateTypeName('rbt.cloud.v1alpha1.logs.ApplicationLogs'),
                        method='inline writer',
                        context_type=IMPORT_reboot_aio_contexts.WriterContext,
                    ) as writer_context:
                        # Check if we already have performed this mutation!
                        #
                        # We do this _before_ calling 'transactionally()' because
                        # if this call is for a transaction method _and_ we've
                        # already performed the transaction then we don't want to
                        # become a transaction participant (again) we just want to
                        # return the transaction's response.
                        idempotent_mutation = (
                            servicer._middleware._state_manager.check_for_idempotent_mutation(
                                writer_context
                            )
                        )

                        if idempotent_mutation is not None:
                            assert len(idempotent_mutation.response) != 0
                            response = IMPORT_google_protobuf_wrappers_pb2.BytesValue()
                            response.ParseFromString(idempotent_mutation.response)
                            result: ApplicationLogsBaseServicer.InlineWriterCallableResult = IMPORT_pickle.loads(response.value)

                            if check_type and type(result) is not type_result:
                                raise TypeError(
                                    f"Stored result of type '{type(result).__name__}' from 'writer' "
                                    f"is not of expected type '{type_result.__name__}'; have you changed "
                                    "the 'type' that you expect after having stored a result?"
                                )

                            return result

                        async with servicer._middleware._state_manager.transactionally(
                            writer_context,
                            servicer._middleware.tasks_dispatcher,
                            aborted_type=None,
                        ) as transaction:
                            async with servicer._middleware._state_manager.writer(
                                writer_context,
                                servicer.__state_type__,
                                servicer._middleware.tasks_dispatcher,
                                # TODO: Decide if we want to do any kind of authorization for inline
                                # writers otherwise passing `None` here is fine.
                                authorize=None,
                                transaction=transaction,
                            ) as (state, state_manager_writer):
                                # Serialize the state so we can see if it changed.
                                serialized_state = state.SerializeToString(
                                    deterministic=True,
                                )

                                result = await writer(state=state)

                                if check_type and type(result) is not type_result:
                                    raise TypeError(
                                        f"Result of type '{type(result).__name__}' from 'writer' is "
                                        f"not of expected type '{type_result.__name__}'; "
                                        "did you specify an incorrect 'type'?"
                                    )

                                task: IMPORT_typing.Optional[IMPORT_reboot_aio_tasks.TaskEffect] = context.task

                                assert task is not None, (
                                    "Should always have a task when running a `workflow`"
                                )

                                method_name = f"ApplicationLogs.{task.method_name} inline writer"

                                if idempotency.alias is not None:
                                    method_name += " with idempotency alias '" + idempotency.alias + "'"
                                elif idempotency.key is not None:
                                    method_name += " with idempotency key=" + str(idempotency.key)

                                servicer._middleware.maybe_raise_effect_validation_retry(
                                    logger=logger,
                                    idempotency_manager=context,
                                    method_name=method_name,
                                    validating_effects=validating_effects,
                                    context=context,
                                    checkpoint=checkpoint,
                                )

                                # We don't pass the context to the
                                # writer, so we don't expect there to
                                # be any scheduled tasks!
                                assert len(context._tasks) == 0

                                effects = IMPORT_reboot_aio_state_managers.Effects(
                                    state=(
                                        # Pass `None` if the state hasn't changed!
                                        state if serialized_state != state.SerializeToString(
                                            deterministic=True,
                                        )
                                        else None
                                    ),
                                    response=IMPORT_google_protobuf_wrappers_pb2.BytesValue(
                                        value=IMPORT_pickle.dumps(result)
                                    ),
                                )

                                await state_manager_writer.complete(effects)

                                return result

        def per_workflow(self, alias: IMPORT_typing.Optional[str] = None):
            return ApplicationLogsBaseServicer.WorkflowState._Idempotently(
                servicer=self._servicer,
                alias=alias,
                how=IMPORT_reboot_aio_workflows.PER_WORKFLOW,
            )

        def per_iteration(self, alias: IMPORT_typing.Optional[str] = None):
            return ApplicationLogsBaseServicer.WorkflowState._Idempotently(
                servicer=self._servicer,
                alias=alias,
                how=IMPORT_reboot_aio_workflows.PER_ITERATION,
            )

        class _Always:
            """Helper class for providing better types for `write` that don't
            require passing `type` or `check_type`."""

            def __init__(
                self,
                *,
                servicer: ApplicationLogsBaseServicer,
            ):
                self._servicer = servicer

            async def read(
                self, context: IMPORT_reboot_aio_contexts.WorkflowContext
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
                return await ApplicationLogsBaseServicer.WorkflowState._Idempotently(
                    servicer=self._servicer,
                    alias=None,
                    how=IMPORT_reboot_aio_workflows.ALWAYS,
                ).read(context)

            async def write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                return await ApplicationLogsBaseServicer.WorkflowState._Idempotently(
                    servicer=self._servicer,
                    alias=None,
                    how=IMPORT_reboot_aio_workflows.ALWAYS,
                )._write(
                    context,
                    writer,
                    __options__,
                    type_result=type(None),
                    check_type=False,
                )

        def always(self):
            return ApplicationLogsBaseServicer.WorkflowState._Always(
                servicer=self._servicer,
            )

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    @IMPORT_abc_abstractmethod
    async def _Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    @IMPORT_abc_abstractmethod
    async def _RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    @IMPORT_abc_abstractmethod
    async def _RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    @IMPORT_abc_abstractmethod
    async def _Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        raise NotImplementedError
        yield  # Necessary for type checking.



class ApplicationLogsSingletonServicer(ApplicationLogsBaseServicer):

    @property
    def state(self):
        return ApplicationLogsBaseServicer.WorkflowState(
            servicer=self
        )

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    @IMPORT_abc_abstractmethod
    async def Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    @IMPORT_abc_abstractmethod
    async def RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    @IMPORT_abc_abstractmethod
    async def RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    @IMPORT_abc_abstractmethod
    async def Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        raise NotImplementedError
        yield  # Necessary for type checking.


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    async def _Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        # Wrap the call to the developer's method in a `span` so that it
        # is traced using its fully-qualified Python name.
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(self)}.Ensure()",
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                python_specific=True,
        ):
            return await self.Ensure(context, state, request)


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    async def _RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        # Wrap the call to the developer's method in a `span` so that it
        # is traced using its fully-qualified Python name.
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(self)}.RegisterConsensus()",
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                python_specific=True,
        ):
            return await self.RegisterConsensus(context, state, request)


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    async def _RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        # Wrap the call to the developer's method in a `span` so that it
        # is traced using its fully-qualified Python name.
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(self)}.RegisterRevision()",
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                python_specific=True,
        ):
            return await self.RegisterRevision(context, state, request)


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    async def _Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        # Wrap the call to the developer's method in a `span` so that it
        # is traced using its fully-qualified Python name.
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(self)}.Logs()",
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                python_specific=True,
        ):
            responses = (
                self.Logs(
                    context,
                    states,
                    request,
                )
            )
            async for response in responses:
                yield response



class ApplicationLogsServicer(ApplicationLogsBaseServicer):

    _state: IMPORT_contextvars.ContextVar[
        IMPORT_typing.Optional[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs]
    ] = IMPORT_contextvars.ContextVar(
        'Provides access to state for each call, i.e., there may be '
        'multiple readers executing concurrently but each might have '
        'a different `state`',
        default=None,
    )

    _workflow: IMPORT_contextvars.ContextVar[bool] = IMPORT_contextvars.ContextVar(
        'Whether or not current context is executing a workflow',
        default=False,
    )

    # An instance of the derived class for each state.
    _instances: dict[str, ApplicationLogsServicer] = {}

    def _instance(self, state_id: str):
        instances = ApplicationLogsServicer._instances
        instance = instances.get(state_id)
        if instance is None:
            instance = self.__class__()
            instance._middleware = self._middleware
        instances[state_id] = instance
        return instance

    @property
    def state(self) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
        state = ApplicationLogsServicer._state.get()
        if state is None:
            raise RuntimeError(
                "`state` property is only relevant within a `Servicer` method"
            )
        workflow = ApplicationLogsServicer._workflow.get()
        if workflow:
            raise RuntimeError(
                "`self.state` is not valid within a `workflow` because a "
                "`workflow ` is not _atomic_; use "
                "`await self.ref().read(context)` instead"
            )
        return state

    @state.setter
    def state(self, new_state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs):
        state = ApplicationLogsServicer._state.get()
        if state is None:
            raise RuntimeError(
                "`state` property is only relevant within a `Servicer` method"
            )
        workflow = ApplicationLogsServicer._workflow.get()
        if workflow:
            raise RuntimeError(
                "`self.state` is not valid within a `workflow` because a "
                "`workflow ` is not _atomic_; use "
                "`await self.ref().write(...)` instead"
            )
        state.CopyFrom(new_state)

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    @IMPORT_abc_abstractmethod
    async def Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    @IMPORT_abc_abstractmethod
    async def RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    @IMPORT_abc_abstractmethod
    async def RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        raise NotImplementedError

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    @IMPORT_abc_abstractmethod
    async def Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse:
        raise NotImplementedError


    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Ensure'.
    async def _Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        # We should have an asyncio task and thus context per request,
        # let's confirm this assumption by making sure that
        # `_state is None`.
        assert ApplicationLogsServicer._state.get() is None
        ApplicationLogsServicer._state.set(state)
        try:
            # Wrap the call to the developer's method in a `span` so that it
            # is traced using its fully-qualified Python name.
            instance = self._instance(context.state_id)
            with IMPORT_reboot_aio_tracing.span(
                    state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                    span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(instance)}.Ensure()",
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    python_specific=True,
            ):
                return await instance.Ensure(context, request)
        finally:
            ApplicationLogsServicer._state.set(None)

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterConsensus'.
    async def _RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        # We should have an asyncio task and thus context per request,
        # let's confirm this assumption by making sure that
        # `_state is None`.
        assert ApplicationLogsServicer._state.get() is None
        ApplicationLogsServicer._state.set(state)
        try:
            # Wrap the call to the developer's method in a `span` so that it
            # is traced using its fully-qualified Python name.
            instance = self._instance(context.state_id)
            with IMPORT_reboot_aio_tracing.span(
                    state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                    span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(instance)}.RegisterConsensus()",
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    python_specific=True,
            ):
                return await instance.RegisterConsensus(context, request)
        finally:
            ApplicationLogsServicer._state.set(None)

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.RegisterRevision'.
    async def _RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        # We should have an asyncio task and thus context per request,
        # let's confirm this assumption by making sure that
        # `_state is None`.
        assert ApplicationLogsServicer._state.get() is None
        ApplicationLogsServicer._state.set(state)
        try:
            # Wrap the call to the developer's method in a `span` so that it
            # is traced using its fully-qualified Python name.
            instance = self._instance(context.state_id)
            with IMPORT_reboot_aio_tracing.span(
                    state_name=f"rbt.cloud.v1alpha1.logs.ApplicationLogs('{context.state_id}')",
                    span_name=f"{IMPORT_reboot_aio_tracing.qualified_type_name(instance)}.RegisterRevision()",
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    python_specific=True,
            ):
                return await instance.RegisterRevision(context, request)
        finally:
            ApplicationLogsServicer._state.set(None)

    # For 'rbt.cloud.v1alpha1.logs.ApplicationLogsMethods.Logs'.
    async def _Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        raise NotImplementedError(
            "Server streaming is not (yet) supported, please reach out "
            "if this is important so we can better understand your use case"
        )
        yield  # Necessary for type checking.



############################ Clients ############################
# The main developer-facing entrypoints for any Reboot type. Relevant to both
# clients and servicers (who use it to find the right servicer base types, as well
# as often being clients themselves).

# Attach an explicit time time zone to "naive" `datetime` objects. A "naive" `datetime` doesn't have a
# time zone. Such objects are typically interpreted as representing local time, but could be confused
# for objects representing UTC. This helper function disambiguates by explicitly attaching the local
# time zone to `datetime` objects that don't already have an explicit time zone. If the `datetime` object
# is already timezone-aware, we still convert it to our custom `DateTimeWithTimeZone` type.
def ensure_has_timezone(
    *,
    when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
) -> IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone | IMPORT_datetime_timedelta]:
    if isinstance(when, IMPORT_datetime_datetime):
        return IMPORT_reboot_time_DateTimeWithTimeZone.from_datetime(when)
    return when

ApplicationLogs_ScheduleTypeVar = IMPORT_typing.TypeVar('ApplicationLogs_ScheduleTypeVar', 'ApplicationLogs.WeakReference._Schedule', 'ApplicationLogs.WeakReference._WriterSchedule')
ApplicationLogs_IdempotentlyScheduleTypeVar = IMPORT_typing.TypeVar('ApplicationLogs_IdempotentlyScheduleTypeVar', 'ApplicationLogs.WeakReference._Schedule', 'ApplicationLogs.WeakReference._WriterSchedule')

ApplicationLogs_UntilCallableType = IMPORT_typing.TypeVar('ApplicationLogs_UntilCallableType')

class ApplicationLogsSingleton:
    Servicer: IMPORT_typing.TypeAlias = ApplicationLogsSingletonServicer


class ApplicationLogs:


    Servicer: IMPORT_typing.TypeAlias = ApplicationLogsServicer

    singleton: IMPORT_typing.TypeAlias = ApplicationLogsSingleton

    Effects: IMPORT_typing.TypeAlias = ApplicationLogsBaseServicer.Effects

    Authorizer: IMPORT_typing.TypeAlias = ApplicationLogsAuthorizer

    State: IMPORT_typing.TypeAlias = rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs

    __state_type_name__ = IMPORT_reboot_aio_types.StateTypeName("rbt.cloud.v1alpha1.logs.ApplicationLogs")

    class EnsureTask:
        """Represents a scheduled task running for the
        state. Note that this is not a coroutine because we are trying
        to convey the semantics that the task is already running (or
        will soon be).
        """

        @classmethod
        def retrieve(
            cls,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ):
            return cls(context, task_id=task_id)

        def __init__(
            self,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ) -> None:
            # Depending on the context type (inside or outside a Reboot application)
            # we may or may not know the application ID. If we don't know it, then
            # the `ExternalContext.gateway` will determine it.
            #
            # TODO: in the future we expect to support cross-application calls, in
            #       which case the developer may explicitly pass in an application ID
            #       here.
            self._application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId] = None
            if isinstance(context, IMPORT_reboot_aio_contexts.Context):
                self._application_id = context.application_id
            self._channel_manager = context.channel_manager
            self._task_id = task_id

        @property
        def task_id(self) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
            return self._task_id

        def __await__(self) -> IMPORT_typing.Generator[None, None, rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse]:
            """Awaits for task to finish and returns its response."""
            async def wait_for_task() -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
                channel = self._channel_manager.get_channel_to_state(
                    self._task_id.state_type,
                    IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                )

                stub = IMPORT_rbt_v1alpha1.tasks_pb2_grpc.TasksStub(channel)

                try:
                    call = IMPORT_reboot_aio_stubs.UnaryRetriedCall(
                        call=None,  # `RetriedCall` can create the call itself.
                        stub_method=stub.Wait,
                        method_name="Wait",
                        request=IMPORT_rbt_v1alpha1.tasks_pb2.WaitRequest(task_id=self._task_id),
                        metadata=IMPORT_reboot_aio_headers.Headers(
                            state_ref=IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                            application_id=self._application_id,
                        ).to_grpc_metadata(),
                        aborted_type=IMPORT_rebootdev.aio.aborted.SystemAborted,
                    )

                    wait_for_task_response = await call
                except IMPORT_rebootdev.aio.aborted.SystemAborted as error:
                    if error.code == IMPORT_grpc.StatusCode.NOT_FOUND:
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.UnknownTask()
                        ) from None

                    raise
                else:
                    response_or_error: IMPORT_typing.Optional[IMPORT_google_protobuf_any_pb2.Any] = None
                    is_error = False

                    if wait_for_task_response.response_or_error.WhichOneof("response_or_error") == "response":
                        response_or_error = wait_for_task_response.response_or_error.response
                    else:
                        is_error = True
                        response_or_error = wait_for_task_response.response_or_error.error

                    assert response_or_error is not None
                    assert response_or_error.TypeName() != ""

                    response = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse()

                    if (
                        not is_error and response_or_error.TypeName() != response.DESCRIPTOR.full_name
                    ):
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.InvalidArgument(),
                            message=
                            f"task with UUID {str(IMPORT_uuid.UUID(bytes=self._task_id.task_uuid))} "
                            f"has a response of type '{response_or_error.TypeName()}' "
                            "but expecting type 'rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse'; "
                            "are you waiting on a task of the correct method?",
                        ) from None

                    if is_error:
                        # Currently only cancelled error is supported.
                        raise IMPORT_asyncio.CancelledError("Task was cancelled by a TasksServicer")
                    else:
                        response_or_error.Unpack(response)
                        return response

            return wait_for_task().__await__()

    EnsureEffects: IMPORT_typing.TypeAlias = ApplicationLogsBaseServicer.EnsureEffects

    class EnsureAborted(IMPORT_rebootdev.aio.aborted.Aborted):


        Error = IMPORT_typing.Union[
            IMPORT_rebootdev.aio.aborted.GrpcError,
            IMPORT_rebootdev.aio.aborted.RebootError,
        ]

        METHOD_ERROR_TYPES: list[type[Error]] = [
        ]

        ERROR_TYPES: list[type[Error]] = (
            METHOD_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.REBOOT_ERROR_TYPES
        )

        _error: Error
        _code: IMPORT_grpc.StatusCode
        _message: IMPORT_typing.Optional[str]

        def __init__(
            self,
            error:  IMPORT_rebootdev.aio.aborted.GrpcError,
            *,
            message: IMPORT_typing.Optional[str] = None,
            # Do not set this value when constructing in order to
            # raise. This is only used internally when constructing
            # from aborted calls.
            error_types: list[type[Error]] = (
                METHOD_ERROR_TYPES + IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES
            ),
        ):
            super().__init__()

            IMPORT_reboot_aio_types.assert_type(error, error_types)

            self._error = error

            code = self.grpc_status_code_from_error(self._error)

            if code is None:
                # Must be a Reboot specific or declared method error.
                code = IMPORT_grpc.StatusCode.ABORTED

            self._code = code

            self._message = message

        @property
        def error(self) -> Error:
            return self._error

        @property
        def code(self) -> IMPORT_grpc.StatusCode:
            return self._code

        @property
        def message(self) -> IMPORT_typing.Optional[str]:
            return self._message

        @classmethod
        def from_status(cls, status: IMPORT_google_rpc_status_pb2.Status):
            error = cls.error_from_google_rpc_status_details(
                status,
                cls.ERROR_TYPES,
            )

            message = status.message if len(status.message) > 0 else None

            if error is not None:
                return cls(error, message=message, error_types=cls.ERROR_TYPES)

            error = cls.error_from_google_rpc_status_code(status)

            assert error is not None

            # TODO(benh): also consider getting the type names from
            # `status.details` and including that in `message` to make
            # debugging easier.

            return cls(error, message=message)

        @classmethod
        def from_grpc_aio_rpc_error(cls, aio_rpc_error: IMPORT_grpc.aio.AioRpcError):
            return cls(
                cls.error_from_grpc_aio_rpc_error(aio_rpc_error),
                message=aio_rpc_error.details(),
            )

        @classmethod
        def is_declared_error(cls, message: IMPORT_google_protobuf_message.Message) -> bool:
            return False

    class RegisterConsensusTask:
        """Represents a scheduled task running for the
        state. Note that this is not a coroutine because we are trying
        to convey the semantics that the task is already running (or
        will soon be).
        """

        @classmethod
        def retrieve(
            cls,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ):
            return cls(context, task_id=task_id)

        def __init__(
            self,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ) -> None:
            # Depending on the context type (inside or outside a Reboot application)
            # we may or may not know the application ID. If we don't know it, then
            # the `ExternalContext.gateway` will determine it.
            #
            # TODO: in the future we expect to support cross-application calls, in
            #       which case the developer may explicitly pass in an application ID
            #       here.
            self._application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId] = None
            if isinstance(context, IMPORT_reboot_aio_contexts.Context):
                self._application_id = context.application_id
            self._channel_manager = context.channel_manager
            self._task_id = task_id

        @property
        def task_id(self) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
            return self._task_id

        def __await__(self) -> IMPORT_typing.Generator[None, None, rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse]:
            """Awaits for task to finish and returns its response."""
            async def wait_for_task() -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
                channel = self._channel_manager.get_channel_to_state(
                    self._task_id.state_type,
                    IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                )

                stub = IMPORT_rbt_v1alpha1.tasks_pb2_grpc.TasksStub(channel)

                try:
                    call = IMPORT_reboot_aio_stubs.UnaryRetriedCall(
                        call=None,  # `RetriedCall` can create the call itself.
                        stub_method=stub.Wait,
                        method_name="Wait",
                        request=IMPORT_rbt_v1alpha1.tasks_pb2.WaitRequest(task_id=self._task_id),
                        metadata=IMPORT_reboot_aio_headers.Headers(
                            state_ref=IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                            application_id=self._application_id,
                        ).to_grpc_metadata(),
                        aborted_type=IMPORT_rebootdev.aio.aborted.SystemAborted,
                    )

                    wait_for_task_response = await call
                except IMPORT_rebootdev.aio.aborted.SystemAborted as error:
                    if error.code == IMPORT_grpc.StatusCode.NOT_FOUND:
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.UnknownTask()
                        ) from None

                    raise
                else:
                    response_or_error: IMPORT_typing.Optional[IMPORT_google_protobuf_any_pb2.Any] = None
                    is_error = False

                    if wait_for_task_response.response_or_error.WhichOneof("response_or_error") == "response":
                        response_or_error = wait_for_task_response.response_or_error.response
                    else:
                        is_error = True
                        response_or_error = wait_for_task_response.response_or_error.error

                    assert response_or_error is not None
                    assert response_or_error.TypeName() != ""

                    response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse()

                    if (
                        not is_error and response_or_error.TypeName() != response.DESCRIPTOR.full_name
                    ):
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.InvalidArgument(),
                            message=
                            f"task with UUID {str(IMPORT_uuid.UUID(bytes=self._task_id.task_uuid))} "
                            f"has a response of type '{response_or_error.TypeName()}' "
                            "but expecting type 'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse'; "
                            "are you waiting on a task of the correct method?",
                        ) from None

                    if is_error:
                        # Currently only cancelled error is supported.
                        raise IMPORT_asyncio.CancelledError("Task was cancelled by a TasksServicer")
                    else:
                        response_or_error.Unpack(response)
                        return response

            return wait_for_task().__await__()

    RegisterConsensusEffects: IMPORT_typing.TypeAlias = ApplicationLogsBaseServicer.RegisterConsensusEffects

    class RegisterConsensusAborted(IMPORT_rebootdev.aio.aborted.Aborted):


        Error = IMPORT_typing.Union[
            IMPORT_rebootdev.aio.aborted.GrpcError,
            IMPORT_rebootdev.aio.aborted.RebootError,
        ]

        METHOD_ERROR_TYPES: list[type[Error]] = [
        ]

        ERROR_TYPES: list[type[Error]] = (
            METHOD_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.REBOOT_ERROR_TYPES
        )

        _error: Error
        _code: IMPORT_grpc.StatusCode
        _message: IMPORT_typing.Optional[str]

        def __init__(
            self,
            error:  IMPORT_rebootdev.aio.aborted.GrpcError,
            *,
            message: IMPORT_typing.Optional[str] = None,
            # Do not set this value when constructing in order to
            # raise. This is only used internally when constructing
            # from aborted calls.
            error_types: list[type[Error]] = (
                METHOD_ERROR_TYPES + IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES
            ),
        ):
            super().__init__()

            IMPORT_reboot_aio_types.assert_type(error, error_types)

            self._error = error

            code = self.grpc_status_code_from_error(self._error)

            if code is None:
                # Must be a Reboot specific or declared method error.
                code = IMPORT_grpc.StatusCode.ABORTED

            self._code = code

            self._message = message

        @property
        def error(self) -> Error:
            return self._error

        @property
        def code(self) -> IMPORT_grpc.StatusCode:
            return self._code

        @property
        def message(self) -> IMPORT_typing.Optional[str]:
            return self._message

        @classmethod
        def from_status(cls, status: IMPORT_google_rpc_status_pb2.Status):
            error = cls.error_from_google_rpc_status_details(
                status,
                cls.ERROR_TYPES,
            )

            message = status.message if len(status.message) > 0 else None

            if error is not None:
                return cls(error, message=message, error_types=cls.ERROR_TYPES)

            error = cls.error_from_google_rpc_status_code(status)

            assert error is not None

            # TODO(benh): also consider getting the type names from
            # `status.details` and including that in `message` to make
            # debugging easier.

            return cls(error, message=message)

        @classmethod
        def from_grpc_aio_rpc_error(cls, aio_rpc_error: IMPORT_grpc.aio.AioRpcError):
            return cls(
                cls.error_from_grpc_aio_rpc_error(aio_rpc_error),
                message=aio_rpc_error.details(),
            )

        @classmethod
        def is_declared_error(cls, message: IMPORT_google_protobuf_message.Message) -> bool:
            return False

    class RegisterRevisionTask:
        """Represents a scheduled task running for the
        state. Note that this is not a coroutine because we are trying
        to convey the semantics that the task is already running (or
        will soon be).
        """

        @classmethod
        def retrieve(
            cls,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ):
            return cls(context, task_id=task_id)

        def __init__(
            self,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ) -> None:
            # Depending on the context type (inside or outside a Reboot application)
            # we may or may not know the application ID. If we don't know it, then
            # the `ExternalContext.gateway` will determine it.
            #
            # TODO: in the future we expect to support cross-application calls, in
            #       which case the developer may explicitly pass in an application ID
            #       here.
            self._application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId] = None
            if isinstance(context, IMPORT_reboot_aio_contexts.Context):
                self._application_id = context.application_id
            self._channel_manager = context.channel_manager
            self._task_id = task_id

        @property
        def task_id(self) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
            return self._task_id

        def __await__(self) -> IMPORT_typing.Generator[None, None, rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse]:
            """Awaits for task to finish and returns its response."""
            async def wait_for_task() -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
                channel = self._channel_manager.get_channel_to_state(
                    self._task_id.state_type,
                    IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                )

                stub = IMPORT_rbt_v1alpha1.tasks_pb2_grpc.TasksStub(channel)

                try:
                    call = IMPORT_reboot_aio_stubs.UnaryRetriedCall(
                        call=None,  # `RetriedCall` can create the call itself.
                        stub_method=stub.Wait,
                        method_name="Wait",
                        request=IMPORT_rbt_v1alpha1.tasks_pb2.WaitRequest(task_id=self._task_id),
                        metadata=IMPORT_reboot_aio_headers.Headers(
                            state_ref=IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                            application_id=self._application_id,
                        ).to_grpc_metadata(),
                        aborted_type=IMPORT_rebootdev.aio.aborted.SystemAborted,
                    )

                    wait_for_task_response = await call
                except IMPORT_rebootdev.aio.aborted.SystemAborted as error:
                    if error.code == IMPORT_grpc.StatusCode.NOT_FOUND:
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.UnknownTask()
                        ) from None

                    raise
                else:
                    response_or_error: IMPORT_typing.Optional[IMPORT_google_protobuf_any_pb2.Any] = None
                    is_error = False

                    if wait_for_task_response.response_or_error.WhichOneof("response_or_error") == "response":
                        response_or_error = wait_for_task_response.response_or_error.response
                    else:
                        is_error = True
                        response_or_error = wait_for_task_response.response_or_error.error

                    assert response_or_error is not None
                    assert response_or_error.TypeName() != ""

                    response = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse()

                    if (
                        not is_error and response_or_error.TypeName() != response.DESCRIPTOR.full_name
                    ):
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.InvalidArgument(),
                            message=
                            f"task with UUID {str(IMPORT_uuid.UUID(bytes=self._task_id.task_uuid))} "
                            f"has a response of type '{response_or_error.TypeName()}' "
                            "but expecting type 'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse'; "
                            "are you waiting on a task of the correct method?",
                        ) from None

                    if is_error:
                        # Currently only cancelled error is supported.
                        raise IMPORT_asyncio.CancelledError("Task was cancelled by a TasksServicer")
                    else:
                        response_or_error.Unpack(response)
                        return response

            return wait_for_task().__await__()

    RegisterRevisionEffects: IMPORT_typing.TypeAlias = ApplicationLogsBaseServicer.RegisterRevisionEffects

    class RegisterRevisionAborted(IMPORT_rebootdev.aio.aborted.Aborted):


        Error = IMPORT_typing.Union[
            IMPORT_rebootdev.aio.aborted.GrpcError,
            IMPORT_rebootdev.aio.aborted.RebootError,
        ]

        METHOD_ERROR_TYPES: list[type[Error]] = [
        ]

        ERROR_TYPES: list[type[Error]] = (
            METHOD_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.REBOOT_ERROR_TYPES
        )

        _error: Error
        _code: IMPORT_grpc.StatusCode
        _message: IMPORT_typing.Optional[str]

        def __init__(
            self,
            error:  IMPORT_rebootdev.aio.aborted.GrpcError,
            *,
            message: IMPORT_typing.Optional[str] = None,
            # Do not set this value when constructing in order to
            # raise. This is only used internally when constructing
            # from aborted calls.
            error_types: list[type[Error]] = (
                METHOD_ERROR_TYPES + IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES
            ),
        ):
            super().__init__()

            IMPORT_reboot_aio_types.assert_type(error, error_types)

            self._error = error

            code = self.grpc_status_code_from_error(self._error)

            if code is None:
                # Must be a Reboot specific or declared method error.
                code = IMPORT_grpc.StatusCode.ABORTED

            self._code = code

            self._message = message

        @property
        def error(self) -> Error:
            return self._error

        @property
        def code(self) -> IMPORT_grpc.StatusCode:
            return self._code

        @property
        def message(self) -> IMPORT_typing.Optional[str]:
            return self._message

        @classmethod
        def from_status(cls, status: IMPORT_google_rpc_status_pb2.Status):
            error = cls.error_from_google_rpc_status_details(
                status,
                cls.ERROR_TYPES,
            )

            message = status.message if len(status.message) > 0 else None

            if error is not None:
                return cls(error, message=message, error_types=cls.ERROR_TYPES)

            error = cls.error_from_google_rpc_status_code(status)

            assert error is not None

            # TODO(benh): also consider getting the type names from
            # `status.details` and including that in `message` to make
            # debugging easier.

            return cls(error, message=message)

        @classmethod
        def from_grpc_aio_rpc_error(cls, aio_rpc_error: IMPORT_grpc.aio.AioRpcError):
            return cls(
                cls.error_from_grpc_aio_rpc_error(aio_rpc_error),
                message=aio_rpc_error.details(),
            )

        @classmethod
        def is_declared_error(cls, message: IMPORT_google_protobuf_message.Message) -> bool:
            return False

    class LogsTask:
        """Represents a scheduled task running for the
        state. Note that this is not a coroutine because we are trying
        to convey the semantics that the task is already running (or
        will soon be).
        """

        @classmethod
        def retrieve(
            cls,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ):
            return cls(context, task_id=task_id)

        def __init__(
            self,
            context: IMPORT_reboot_aio_contexts.Context | IMPORT_reboot_aio_external.ExternalContext,
            *,
            task_id: IMPORT_rbt_v1alpha1.tasks_pb2.TaskId,
        ) -> None:
            # Depending on the context type (inside or outside a Reboot application)
            # we may or may not know the application ID. If we don't know it, then
            # the `ExternalContext.gateway` will determine it.
            #
            # TODO: in the future we expect to support cross-application calls, in
            #       which case the developer may explicitly pass in an application ID
            #       here.
            self._application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId] = None
            if isinstance(context, IMPORT_reboot_aio_contexts.Context):
                self._application_id = context.application_id
            self._channel_manager = context.channel_manager
            self._task_id = task_id

        @property
        def task_id(self) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
            return self._task_id

        def __await__(self) -> IMPORT_typing.Generator[None, None, rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
            """Awaits for task to finish and returns its response."""
            async def wait_for_task() -> rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse:
                channel = self._channel_manager.get_channel_to_state(
                    self._task_id.state_type,
                    IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                )

                stub = IMPORT_rbt_v1alpha1.tasks_pb2_grpc.TasksStub(channel)

                try:
                    call = IMPORT_reboot_aio_stubs.UnaryRetriedCall(
                        call=None,  # `RetriedCall` can create the call itself.
                        stub_method=stub.Wait,
                        method_name="Wait",
                        request=IMPORT_rbt_v1alpha1.tasks_pb2.WaitRequest(task_id=self._task_id),
                        metadata=IMPORT_reboot_aio_headers.Headers(
                            state_ref=IMPORT_reboot_aio_types.StateRef(self._task_id.state_ref),
                            application_id=self._application_id,
                        ).to_grpc_metadata(),
                        aborted_type=IMPORT_rebootdev.aio.aborted.SystemAborted,
                    )

                    wait_for_task_response = await call
                except IMPORT_rebootdev.aio.aborted.SystemAborted as error:
                    if error.code == IMPORT_grpc.StatusCode.NOT_FOUND:
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.UnknownTask()
                        ) from None

                    raise
                else:
                    response_or_error: IMPORT_typing.Optional[IMPORT_google_protobuf_any_pb2.Any] = None
                    is_error = False

                    if wait_for_task_response.response_or_error.WhichOneof("response_or_error") == "response":
                        response_or_error = wait_for_task_response.response_or_error.response
                    else:
                        is_error = True
                        response_or_error = wait_for_task_response.response_or_error.error

                    assert response_or_error is not None
                    assert response_or_error.TypeName() != ""

                    response = rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse()

                    if (
                        not is_error and response_or_error.TypeName() != response.DESCRIPTOR.full_name
                    ):
                        raise IMPORT_rebootdev.aio.aborted.SystemAborted(
                            IMPORT_rbt_v1alpha1.errors_pb2.InvalidArgument(),
                            message=
                            f"task with UUID {str(IMPORT_uuid.UUID(bytes=self._task_id.task_uuid))} "
                            f"has a response of type '{response_or_error.TypeName()}' "
                            "but expecting type 'rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse'; "
                            "are you waiting on a task of the correct method?",
                        ) from None

                    if is_error:
                        # Currently only cancelled error is supported.
                        raise IMPORT_asyncio.CancelledError("Task was cancelled by a TasksServicer")
                    else:
                        response_or_error.Unpack(response)
                        return response

            return wait_for_task().__await__()


    class LogsAborted(IMPORT_rebootdev.aio.aborted.Aborted):


        Error = IMPORT_typing.Union[
            IMPORT_rebootdev.aio.aborted.GrpcError,
            IMPORT_rebootdev.aio.aborted.RebootError,
        ]

        METHOD_ERROR_TYPES: list[type[Error]] = [
        ]

        ERROR_TYPES: list[type[Error]] = (
            METHOD_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES +
            IMPORT_rebootdev.aio.aborted.REBOOT_ERROR_TYPES
        )

        _error: Error
        _code: IMPORT_grpc.StatusCode
        _message: IMPORT_typing.Optional[str]

        def __init__(
            self,
            error:  IMPORT_rebootdev.aio.aborted.GrpcError,
            *,
            message: IMPORT_typing.Optional[str] = None,
            # Do not set this value when constructing in order to
            # raise. This is only used internally when constructing
            # from aborted calls.
            error_types: list[type[Error]] = (
                METHOD_ERROR_TYPES + IMPORT_rebootdev.aio.aborted.GRPC_ERROR_TYPES
            ),
        ):
            super().__init__()

            IMPORT_reboot_aio_types.assert_type(error, error_types)

            self._error = error

            code = self.grpc_status_code_from_error(self._error)

            if code is None:
                # Must be a Reboot specific or declared method error.
                code = IMPORT_grpc.StatusCode.ABORTED

            self._code = code

            self._message = message

        @property
        def error(self) -> Error:
            return self._error

        @property
        def code(self) -> IMPORT_grpc.StatusCode:
            return self._code

        @property
        def message(self) -> IMPORT_typing.Optional[str]:
            return self._message

        @classmethod
        def from_status(cls, status: IMPORT_google_rpc_status_pb2.Status):
            error = cls.error_from_google_rpc_status_details(
                status,
                cls.ERROR_TYPES,
            )

            message = status.message if len(status.message) > 0 else None

            if error is not None:
                return cls(error, message=message, error_types=cls.ERROR_TYPES)

            error = cls.error_from_google_rpc_status_code(status)

            assert error is not None

            # TODO(benh): also consider getting the type names from
            # `status.details` and including that in `message` to make
            # debugging easier.

            return cls(error, message=message)

        @classmethod
        def from_grpc_aio_rpc_error(cls, aio_rpc_error: IMPORT_grpc.aio.AioRpcError):
            return cls(
                cls.error_from_grpc_aio_rpc_error(aio_rpc_error),
                message=aio_rpc_error.details(),
            )

        @classmethod
        def is_declared_error(cls, message: IMPORT_google_protobuf_message.Message) -> bool:
            return False


    class WeakReference(IMPORT_typing.Generic[ApplicationLogs_ScheduleTypeVar]):

        _schedule_type: type[ApplicationLogs_ScheduleTypeVar]

        def __init__(
            self,
            # When application ID is None, refers to a state within the application given by the context.
            application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId],
            state_id: IMPORT_reboot_aio_types.StateId,
            *,
            schedule_type: type[ApplicationLogs_ScheduleTypeVar],
            bearer_token: IMPORT_typing.Optional[str] = None,
            servicer: IMPORT_typing.Optional[ApplicationLogsBaseServicer] = None,
        ):
            self._application_id = application_id
            self._state_ref = IMPORT_reboot_aio_types.StateRef.from_id(
              ApplicationLogs.__state_type_name__,
              state_id,
            )
            self._schedule_type = schedule_type
            self._idempotency_manager: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.IdempotencyManager] = None
            self._reader_stub: IMPORT_typing.Optional[ApplicationLogsReaderStub] = None
            self._writer_stub: IMPORT_typing.Optional[ApplicationLogsWriterStub] = None
            self._workflow_stub: IMPORT_typing.Optional[ApplicationLogsWorkflowStub] = None
            self._tasks_stub: IMPORT_typing.Optional[ApplicationLogsTasksStub] = None
            self._bearer_token = bearer_token
            self._servicer = servicer

        @property
        def state_id(self) -> IMPORT_reboot_aio_types.StateId:
            return self._state_ref.id

        def _reader(
            self,
            context: IMPORT_reboot_aio_contexts.ReaderContext | IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        ) -> ApplicationLogsReaderStub:
            if self._reader_stub is None:
                self._reader_stub = ApplicationLogsReaderStub(
                    context=context,
                    state_ref=self._state_ref,
                    bearer_token=self._bearer_token,
                )
            assert self._reader_stub is not None
            if self._idempotency_manager is None:
                self._idempotency_manager = context
            elif self._idempotency_manager != context:
                raise IMPORT_reboot_aio_call.MixedContextsError(
                    "This `WeakReference` for `ApplicationLogs` with ID "
                    f"'{self.state_id}' has previously been used by a "
                    "different `Context`. That is not allowed. "
                    "Instead create a new `WeakReference` for every `Context` by calling "
                    f"`ApplicationLogs.ref('{self.state_id}')`."
                )
            return self._reader_stub

        def _writer(
            self,
            context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        ) -> ApplicationLogsWriterStub:
            if self._writer_stub is None:
                self._writer_stub = ApplicationLogsWriterStub(
                    context=context,
                    state_ref=self._state_ref,
                    bearer_token=self._bearer_token,
                )
            assert self._writer_stub is not None
            if self._idempotency_manager is None:
                self._idempotency_manager = context
            elif self._idempotency_manager != context:
                raise IMPORT_reboot_aio_call.MixedContextsError(
                    "This `WeakReference` for `ApplicationLogs` with ID "
                    f"'{self.state_id}' has previously been used by a "
                    "different `Context`. That is not allowed. "
                    "Instead create a new `WeakReference` for every `Context` by calling "
                    f"`ApplicationLogs.ref('{self.state_id}')`."
                )
            return self._writer_stub

        def _workflow(
            self,
            context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        ) -> ApplicationLogsWorkflowStub:
            if self._workflow_stub is None:
                self._workflow_stub = ApplicationLogsWorkflowStub(
                    context=context,
                    state_ref=self._state_ref,
                    bearer_token=self._bearer_token,
                )
            assert self._workflow_stub is not None
            if self._idempotency_manager is None:
                self._idempotency_manager = context
            elif self._idempotency_manager != context:
                raise IMPORT_reboot_aio_call.MixedContextsError(
                    "This `WeakReference` for `ApplicationLogs` with ID "
                    f"'{self.state_id}' has previously been used by a "
                    "different `Context`. That is not allowed. "
                    "Instead create a new `WeakReference` for every `Context` by calling "
                    f"`ApplicationLogs.ref('{self.state_id}')`."
                )
            return self._workflow_stub

        def _tasks(
            self,
            context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        ) -> ApplicationLogsTasksStub:
            if self._tasks_stub is None:
                self._tasks_stub = ApplicationLogsTasksStub(
                    context=context,
                    state_ref=self._state_ref,
                    bearer_token=self._bearer_token,
                )
            assert self._tasks_stub is not None
            if self._idempotency_manager is None:
                self._idempotency_manager = context
            elif self._idempotency_manager != context:
                raise IMPORT_reboot_aio_call.MixedContextsError(
                    "This `WeakReference` for `ApplicationLogs` with ID "
                    f"'{self.state_id}' has previously been used by a "
                    "different `Context`. That is not allowed. "
                    "Instead create a new `WeakReference` for every `Context` by calling "
                    f"`ApplicationLogs.ref('{self.state_id}')`."
                )
            return self._tasks_stub

        class _Reactively:

            def __init__(
                self,
                *,
                application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId],
                state_ref: IMPORT_reboot_aio_types.StateRef,
                bearer_token: IMPORT_typing.Optional[str] = None,
            ):
                self._application_id = application_id
                self._state_ref = state_ref
                self._bearer_token = bearer_token


        def reactively(self):
            return ApplicationLogs.WeakReference._Reactively(
                application_id=self._application_id,
                state_ref=self._state_ref,
                bearer_token=self._bearer_token,
            )

        class _Idempotently(IMPORT_typing.Generic[ApplicationLogs_IdempotentlyScheduleTypeVar]):

            _weak_reference: ApplicationLogs.WeakReference[ApplicationLogs_IdempotentlyScheduleTypeVar]

            def __init__(
                self,
                *,
                weak_reference: ApplicationLogs.WeakReference[ApplicationLogs_IdempotentlyScheduleTypeVar],
                idempotency: IMPORT_reboot_aio_idempotency.Idempotency,
            ):
                self._weak_reference = weak_reference
                self._idempotency = idempotency

            def schedule(
                self,
                *,
                when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
            ) -> ApplicationLogs_IdempotentlyScheduleTypeVar:
                return self._weak_reference._schedule_type(
                    self._weak_reference._application_id,
                    self._weak_reference._tasks,
                    when=when,
                    idempotency=self._idempotency,
                )

            def spawn(
                self,
                *,
                when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
            ) -> ApplicationLogs.WeakReference._Spawn:
                return ApplicationLogs.WeakReference._Spawn(
                    self._weak_reference._application_id,
                    self._weak_reference._tasks,
                    when=when,
                    idempotency=self._idempotency,
                )

            async def Read(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
                if self._weak_reference._servicer is None:
                    raise RuntimeError(
                        "`Read()` is currently only supported within workflows; "
                        "Please reach out and let us know your use case if this "
                        "is important for you!"
                    )

                return await ApplicationLogsBaseServicer.WorkflowState._Idempotently._read(
                    self._weak_reference._servicer,
                    self._idempotency,
                    context,
                )

            @IMPORT_typing.overload
            async def Write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[None],
                *,
                type: type = type(None),
            ) -> None:
                ...

            @IMPORT_typing.overload
            async def Write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                *,
                type: type[ApplicationLogsBaseServicer.InlineWriterCallableResult],
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                ...

            async def Write(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
                *,
                type: type = type(None),
            ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
                if self._weak_reference._servicer is None:
                    raise RuntimeError(
                        "`Write()` is currently only supported within workflows; "
                        "Please reach out and let us know your use case if this "
                        "is important for you!"
                    )

                return await ApplicationLogsBaseServicer.WorkflowState._Idempotently._write_validating_effects(
                    self._weak_reference._servicer,
                    self._idempotency,
                    context,
                    writer,
                    type_result=type,
                    check_type=not self._idempotency.always,
                    unidempotently=self._idempotency.always,
                    checkpoint=context.checkpoint(),
                )

            async def Ensure(
                # In methods which are dealing with user input, (i.e.,
                # proto message field names), we should use '__double_underscored__'
                # variables to avoid any potential name conflicts with the method's
                # parameters.
                # The '__self__' parameter is a convention in Python to
                # indicate that this method is a bound method, so we use
                # '__this__' instead.
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)

                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    raise RuntimeError(
                        'Found redundant idempotency in `Options`'
                    )

                __options__ = IMPORT_dataclasses.replace(
                    __options__,
                    idempotency_key=__this__._idempotency.key,
                    idempotency_alias=__this__._idempotency.alias,
                    generate_idempotency=__this__._idempotency.generate,
                    generated_idempotency=__this__._idempotency.generated,
                )

                return await __this__._weak_reference.Ensure(
                    __context__,
                    __options__,
                )

            async def RegisterConsensus(
                # In methods which are dealing with user input, (i.e.,
                # proto message field names), we should use '__double_underscored__'
                # variables to avoid any potential name conflicts with the method's
                # parameters.
                # The '__self__' parameter is a convention in Python to
                # indicate that this method is a bound method, so we use
                # '__this__' instead.
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)

                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    raise RuntimeError(
                        'Found redundant idempotency in `Options`'
                    )

                __options__ = IMPORT_dataclasses.replace(
                    __options__,
                    idempotency_key=__this__._idempotency.key,
                    idempotency_alias=__this__._idempotency.alias,
                    generate_idempotency=__this__._idempotency.generate,
                    generated_idempotency=__this__._idempotency.generated,
                )

                return await __this__._weak_reference.RegisterConsensus(
                    __context__,
                    __options__,
                )

            async def RegisterRevision(
                # In methods which are dealing with user input, (i.e.,
                # proto message field names), we should use '__double_underscored__'
                # variables to avoid any potential name conflicts with the method's
                # parameters.
                # The '__self__' parameter is a convention in Python to
                # indicate that this method is a bound method, so we use
                # '__this__' instead.
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
                *,
                revision_number: IMPORT_typing.Optional[int] = None,
            ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)

                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    raise RuntimeError(
                        'Found redundant idempotency in `Options`'
                    )

                __options__ = IMPORT_dataclasses.replace(
                    __options__,
                    idempotency_key=__this__._idempotency.key,
                    idempotency_alias=__this__._idempotency.alias,
                    generate_idempotency=__this__._idempotency.generate,
                    generated_idempotency=__this__._idempotency.generated,
                )

                return await __this__._weak_reference.RegisterRevision(
                    __context__,
                    __options__,
                    revision_number=revision_number,
                )


        @IMPORT_typing.overload
        def idempotently(self, alias: IMPORT_typing.Optional[str] = None, *, each_iteration: bool = False) -> ApplicationLogs.WeakReference._Idempotently[ApplicationLogs_ScheduleTypeVar]:
            ...

        @IMPORT_typing.overload
        def idempotently(self, *, key: IMPORT_uuid.UUID, generated: bool = False) -> ApplicationLogs.WeakReference._Idempotently[ApplicationLogs_ScheduleTypeVar]:
            ...

        def idempotently(
            self,
            alias: IMPORT_typing.Optional[str] = None,
            *,
            key: IMPORT_typing.Optional[IMPORT_uuid.UUID] = None,
            each_iteration: IMPORT_typing.Optional[bool] = None,
            generated: bool = False,
        ) -> ApplicationLogs.WeakReference._Idempotently[ApplicationLogs_ScheduleTypeVar]:
            return ApplicationLogs.WeakReference._Idempotently(
                weak_reference=self,
                idempotency=IMPORT_reboot_aio_contexts.Context.idempotency(
                    alias=alias,
                    key=key,
                    each_iteration=each_iteration,
                    generated=generated,
                )
            )

        def per_workflow(self, alias: IMPORT_typing.Optional[str] = None):
            return self.idempotently(alias)

        def per_iteration(self, alias: IMPORT_typing.Optional[str] = None):
            return self.idempotently(alias, each_iteration=True)

        def always(self):
            return self.idempotently(key=IMPORT_uuid.uuid4(), generated=True)

        class _UntilChangesSatisfies(IMPORT_typing.Generic[ApplicationLogs_UntilCallableType]):

            _idempotency_alias: str
            _context: IMPORT_reboot_aio_contexts.WorkflowContext
            _callable: IMPORT_typing.Callable[[], IMPORT_typing.Awaitable[ApplicationLogs_UntilCallableType]]
            _type: type[ApplicationLogs_UntilCallableType]

            def __init__(
                self,
                *,
                idempotency_alias: str,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
                callable: IMPORT_typing.Callable[[], IMPORT_typing.Awaitable[ApplicationLogs_UntilCallableType]],
                type: type[ApplicationLogs_UntilCallableType],
            ):
                self._idempotency_alias = idempotency_alias
                self._context = context
                self._callable = callable
                self._type = type

            async def changes(self):
                return await IMPORT_reboot_aio_workflows.until_changes(
                    self._idempotency_alias,
                    self._context,
                    self._callable,
                    type=self._type,
                )

            async def satisfies(
                self,
                condition: IMPORT_typing.Callable[[ApplicationLogs_UntilCallableType], bool],
            ):

                async def converge():
                    response = await self._callable()
                    if condition(response):
                        return response
                    return False

                return await IMPORT_reboot_aio_workflows.until(
                    self._idempotency_alias,
                    self._context,
                    converge,
                    type=self._type,
                )

        class _Until:

            _weak_reference: ApplicationLogs.WeakReference
            _idempotency_alias: str

            def __init__(
                self,
                *,
                weak_reference: ApplicationLogs.WeakReference,
                idempotency_alias: str,
            ):
                self._weak_reference = weak_reference
                self._idempotency_alias = idempotency_alias

            def Read(
                self,
                context: IMPORT_reboot_aio_contexts.WorkflowContext,
            ) -> ApplicationLogs.WeakReference._UntilChangesSatisfies[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs]:
                IMPORT_reboot_aio_types.assert_type(
                    context,
                    [IMPORT_reboot_aio_contexts.WorkflowContext],
                )

                async def callable():
                    return await self._weak_reference.Read(context)

                return ApplicationLogs.WeakReference._UntilChangesSatisfies(
                    idempotency_alias=self._idempotency_alias,
                    context=context,
                    callable=callable,
                    type=rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
                )


        def until(self, alias: str):
            return ApplicationLogs.WeakReference._Until(
                weak_reference=self,
                idempotency_alias=alias,
            )

        def schedule(
            self,
            *,
            when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
        ) -> ApplicationLogs_ScheduleTypeVar:
            return self._schedule_type(self._application_id, self._tasks, when=when)

        class _Schedule:

            def __init__(
                self,
                application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId],
                tasks: IMPORT_typing.Callable[[IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext], ApplicationLogsTasksStub],
                *,
                when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
                idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
            ) -> None:
                self._application_id = application_id
                self._tasks = tasks
                self._when = ensure_has_timezone(when=when)
                self._idempotency = idempotency

            # ApplicationLogs callable tasks:
            async def Ensure(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.TransactionContext])

                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest(
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).Ensure(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return __task_id__

            async def RegisterConsensus(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.TransactionContext])

                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest(
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).RegisterConsensus(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return __task_id__

            async def RegisterRevision(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
                *,
                revision_number: IMPORT_typing.Optional[int] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.TransactionContext])

                if revision_number is not None and not isinstance(
                    revision_number,
                    int,
                ):
                    raise TypeError(
                        f"Can not construct protobuf message of type "
                        f"'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest': field 'revision_number' is not "
                        f"of required type 'int'"
                    )
                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest(
                    revision_number=revision_number,  # type: ignore[arg-type]
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).RegisterRevision(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return __task_id__


        # A `WriterContext` can not call any methods in `_Schedule` to
        # prevent a writer from doing a `Foo.ref()` and trying to
        # schedule. However, we want to allow a writer to schedule
        # when we are constructing a `WeakReference` from
        # `self.ref()` so instead we return a `_WriterSchedule` to
        # provide type safety that allows a `WriterContext` to
        # schedule (for itself).
        class _WriterSchedule:

            def __init__(
                self,
                application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId],
                tasks: IMPORT_typing.Callable[[IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext], ApplicationLogsTasksStub],
                *,
                when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
                idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
            ) -> None:
                self._tasks = tasks
                self._when = ensure_has_timezone(when=when)
                self._idempotency = idempotency

            # ApplicationLogs callable tasks:
            async def Ensure(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # Only `writer`s and `transaction`s should ``schedule()`, a
                # `workflow` should `spawn()`.
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WriterContext, IMPORT_reboot_aio_contexts.TransactionContext])

                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)

                # TODO: mypy-protobuf declares that
                # `google.protobuf.message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest(
                )
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WriterContext):
                    return (await ApplicationLogsServicerTasks(
                        context=__context__,
                        state_ref=__context__._state_ref,
                    ).Ensure(
                        __request__,
                        schedule=__this__._when,
                    )).task_id

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency is not None:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                return await __this__._tasks(
                    __context__
                ).Ensure(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

            async def RegisterConsensus(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # Only `writer`s and `transaction`s should ``schedule()`, a
                # `workflow` should `spawn()`.
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WriterContext, IMPORT_reboot_aio_contexts.TransactionContext])

                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)

                # TODO: mypy-protobuf declares that
                # `google.protobuf.message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest(
                )
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WriterContext):
                    return (await ApplicationLogsServicerTasks(
                        context=__context__,
                        state_ref=__context__._state_ref,
                    ).RegisterConsensus(
                        __request__,
                        schedule=__this__._when,
                    )).task_id

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency is not None:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                return await __this__._tasks(
                    __context__
                ).RegisterConsensus(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

            async def RegisterRevision(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
                *,
                revision_number: IMPORT_typing.Optional[int] = None,
            ) -> IMPORT_rbt_v1alpha1.tasks_pb2.TaskId:
                # Only `writer`s and `transaction`s should ``schedule()`, a
                # `workflow` should `spawn()`.
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WriterContext, IMPORT_reboot_aio_contexts.TransactionContext])

                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)

                if revision_number is not None and not isinstance(
                    revision_number,
                    int,
                ):
                    raise TypeError(
                        f"Can not construct protobuf message of type "
                        f"'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest': field 'revision_number' is not "
                        f"of required type 'int'"
                    )
                # TODO: mypy-protobuf declares that
                # `google.protobuf.message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest(
                    revision_number=revision_number,  # type: ignore[arg-type]
                )
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WriterContext):
                    return (await ApplicationLogsServicerTasks(
                        context=__context__,
                        state_ref=__context__._state_ref,
                    ).RegisterRevision(
                        __request__,
                        schedule=__this__._when,
                    )).task_id

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency is not None:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                return await __this__._tasks(
                    __context__
                ).RegisterRevision(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )


        def spawn(
            self,
            *,
            when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
        ) -> ApplicationLogs.WeakReference._Spawn:
            # Within a `workflow`, all "bare" `spawn()` calls are
            # syntactic sugar for `per_workflow()`, unless we're
            # within a control loop, in which case they are syntactic
            # sugar for `per_iteration()`.
            context = IMPORT_reboot_aio_contexts.Context.get()
            if context is not None:
                if isinstance(context, IMPORT_reboot_aio_contexts.WorkflowContext):
                    return (
                        self.per_iteration() if context.within_loop()
                        else self.per_workflow()
                    ).spawn(when=when)
                elif isinstance(context, IMPORT_reboot_aio_external.InitializeContext):
                    return self.idempotently().spawn(when=when)

            return ApplicationLogs.WeakReference._Spawn(
                self._application_id, self._tasks, when=when
            )

        class _Spawn:

            def __init__(
                self,
                application_id: IMPORT_typing.Optional[IMPORT_reboot_aio_types.ApplicationId],
                tasks: IMPORT_typing.Callable[[IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext], ApplicationLogsTasksStub],
                *,
                when: IMPORT_typing.Optional[IMPORT_datetime_datetime | IMPORT_datetime_timedelta] = None,
                idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None,
            ) -> None:
                self._application_id = application_id
                self._tasks = tasks
                self._when = ensure_has_timezone(when=when)
                self._idempotency = idempotency

            # ApplicationLogs callable tasks:
            async def Ensure(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> ApplicationLogs.EnsureTask:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])

                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest(
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).Ensure(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return ApplicationLogs.EnsureTask(
                    __context__,
                    task_id=__task_id__,
                )

            async def RegisterConsensus(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            ) -> ApplicationLogs.RegisterConsensusTask:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])

                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest(
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).RegisterConsensus(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return ApplicationLogs.RegisterConsensusTask(
                    __context__,
                    task_id=__task_id__,
                )

            async def RegisterRevision(
                __this__,
                __context__: IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
                __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
                *,
                revision_number: IMPORT_typing.Optional[int] = None,
            ) -> ApplicationLogs.RegisterRevisionTask:
                # UX improvement: check that neither positional argument was accidentally
                # given a gRPC request type.
                IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
                IMPORT_reboot_aio_types.assert_type(__context__, [IMPORT_reboot_aio_contexts.WorkflowContext, IMPORT_reboot_aio_external.ExternalContext])

                if revision_number is not None and not isinstance(
                    revision_number,
                    int,
                ):
                    raise TypeError(
                        f"Can not construct protobuf message of type "
                        f"'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest': field 'revision_number' is not "
                        f"of required type 'int'"
                    )
                # TODO: mypy-protobuf declares that
                # `IMPORT_google_protobuf_message.Message` constructor arguments are
                # always non-None, when in reality they are optional.
                __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest(
                    revision_number=revision_number,  # type: ignore[arg-type]
                )

                __schedule__: IMPORT_typing.Optional[IMPORT_reboot_time_DateTimeWithTimeZone] = (IMPORT_reboot_time_DateTimeWithTimeZone.now() + __this__._when) if isinstance(
                    __this__._when, IMPORT_datetime_timedelta
                ) else __this__._when

                __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
                __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = __this__._idempotency
                __bearer_token__: IMPORT_typing.Optional[str] = None

                if __options__ is not None:
                    IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                    if __options__.idempotency:
                        if __idempotency__ is not None:
                            raise RuntimeError(
                                'Found redundant idempotency in `Options`'
                            )
                        __idempotency__ = __options__.idempotency
                    if __options__.metadata is not None:
                        __metadata__ = __options__.metadata
                    if __options__.bearer_token is not None:
                        __bearer_token__ = __options__.bearer_token

                # Add scheduling information to the metadata.
                __metadata__ = (
                    (IMPORT_reboot_aio_headers.TASK_SCHEDULE,
                    __schedule__.isoformat() if __schedule__ else ''),
                ) + (__metadata__ or tuple())

                __task_id__ = await __this__._tasks(
                    __context__
                ).RegisterRevision(
                    __request__,
                    idempotency=__idempotency__,
                    metadata=__metadata__,
                    bearer_token=__bearer_token__,
                )

                return ApplicationLogs.RegisterRevisionTask(
                    __context__,
                    task_id=__task_id__,
                )


        async def Read(
            self,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs:
            return await (
                self.always() if context.within_until()
                else (
                    self.per_iteration() if context.within_loop()
                    else self.per_workflow()
                )
            ).Read(context)

        @IMPORT_typing.overload
        async def Write(
            self,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[None],
            *,
            type: type = type(None),
        ) -> None:
            ...

        @IMPORT_typing.overload
        async def Write(
            self,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
            *,
            type: type[ApplicationLogsBaseServicer.InlineWriterCallableResult],
        ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
            ...

        async def Write(
            self,
            context: IMPORT_reboot_aio_contexts.WorkflowContext,
            writer: ApplicationLogsBaseServicer.InlineWriterCallable[ApplicationLogsBaseServicer.InlineWriterCallableResult],
            *,
            type: type = type(None),
        ) -> ApplicationLogsBaseServicer.InlineWriterCallableResult:
            """Perform an "inline write" within a workflow."""
            return await (
                self.always() if context.within_until()
                else (
                    self.per_iteration() if context.within_loop()
                    else self.per_workflow()
                )
            ).Write(
                context, writer, type=type
            )

        # ApplicationLogs specific methods:
        async def Ensure(
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
            # UX improvement: check that neither positional argument was accidentally
            # given a gRPC request type.
            IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)
            IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest)

            # Within a `workflow`, all "bare" calls are
            # `per_workflow()` calls, unless we're within a control
            # loop, in which case they are syntactic sugar for
            # `per_iteration()`.
            if __options__ is None or __options__.idempotency is None:
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WorkflowContext):
                    return await (
                        __this__.per_iteration() if __context__.within_loop()
                        else __this__.per_workflow()
                    ).Ensure(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                    )
                elif isinstance(__context__, IMPORT_reboot_aio_external.InitializeContext):
                    return await __this__.idempotently().Ensure(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                    )

            # TODO: mypy-protobuf declares that
            # `google.protobuf.message.Message` constructor arguments are
            # always non-None, when in reality they are optional.
            __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest(
            )
            __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None
            __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
            __bearer_token__: IMPORT_typing.Optional[str] = None
            if __options__ is not None:
                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    __idempotency__ = __options__.idempotency
                if __options__.metadata is not None:
                    __metadata__ = __options__.metadata
                if __options__.bearer_token is not None:
                    __bearer_token__ = __options__.bearer_token

            return await __this__._writer(__context__).Ensure(
                __request__,
                idempotency=__idempotency__,
                metadata=__metadata__,
                bearer_token=__bearer_token__,
            )

        async def RegisterConsensus(
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
            # UX improvement: check that neither positional argument was accidentally
            # given a gRPC request type.
            IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)
            IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest)

            # Within a `workflow`, all "bare" calls are
            # `per_workflow()` calls, unless we're within a control
            # loop, in which case they are syntactic sugar for
            # `per_iteration()`.
            if __options__ is None or __options__.idempotency is None:
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WorkflowContext):
                    return await (
                        __this__.per_iteration() if __context__.within_loop()
                        else __this__.per_workflow()
                    ).RegisterConsensus(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                    )
                elif isinstance(__context__, IMPORT_reboot_aio_external.InitializeContext):
                    return await __this__.idempotently().RegisterConsensus(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                    )

            # TODO: mypy-protobuf declares that
            # `google.protobuf.message.Message` constructor arguments are
            # always non-None, when in reality they are optional.
            __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest(
            )
            __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None
            __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
            __bearer_token__: IMPORT_typing.Optional[str] = None
            if __options__ is not None:
                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    __idempotency__ = __options__.idempotency
                if __options__.metadata is not None:
                    __metadata__ = __options__.metadata
                if __options__.bearer_token is not None:
                    __bearer_token__ = __options__.bearer_token

            return await __this__._writer(__context__).RegisterConsensus(
                __request__,
                idempotency=__idempotency__,
                metadata=__metadata__,
                bearer_token=__bearer_token__,
            )

        async def RegisterRevision(
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            *,
            revision_number: IMPORT_typing.Optional[int] = None,
        ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
            # UX improvement: check that neither positional argument was accidentally
            # given a gRPC request type.
            IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)
            IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest)

            # Within a `workflow`, all "bare" calls are
            # `per_workflow()` calls, unless we're within a control
            # loop, in which case they are syntactic sugar for
            # `per_iteration()`.
            if __options__ is None or __options__.idempotency is None:
                if isinstance(__context__, IMPORT_reboot_aio_contexts.WorkflowContext):
                    return await (
                        __this__.per_iteration() if __context__.within_loop()
                        else __this__.per_workflow()
                    ).RegisterRevision(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                        revision_number=revision_number,
                    )
                elif isinstance(__context__, IMPORT_reboot_aio_external.InitializeContext):
                    return await __this__.idempotently().RegisterRevision(
                        __context__,
                        __options__ or IMPORT_reboot_aio_call.Options(),
                        revision_number=revision_number,
                    )

            if revision_number is not None and not isinstance(
                revision_number,
                int,
            ):
                raise TypeError(
                    f"Can not construct protobuf message of type "
                    f"'rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest': field 'revision_number' is not "
                    f"of required type 'int'"
                )
            # TODO: mypy-protobuf declares that
            # `google.protobuf.message.Message` constructor arguments are
            # always non-None, when in reality they are optional.
            __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest(
                revision_number=revision_number,  # type: ignore[arg-type]
            )
            __idempotency__: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None
            __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
            __bearer_token__: IMPORT_typing.Optional[str] = None
            if __options__ is not None:
                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.idempotency is not None:
                    __idempotency__ = __options__.idempotency
                if __options__.metadata is not None:
                    __metadata__ = __options__.metadata
                if __options__.bearer_token is not None:
                    __bearer_token__ = __options__.bearer_token

            return await __this__._writer(__context__).RegisterRevision(
                __request__,
                idempotency=__idempotency__,
                metadata=__metadata__,
                bearer_token=__bearer_token__,
            )

        async def Logs(
            __this__,
            __context__: IMPORT_reboot_aio_contexts.ReaderContext | IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_typing.Optional[IMPORT_reboot_aio_call.Options] = None,
            *,
            last: IMPORT_typing.Optional[int] = None,
            follow: IMPORT_typing.Optional[bool] = None,
            revision_numbers: IMPORT_typing.Optional[IMPORT_typing.Iterable[int]] = None,
            sources: IMPORT_typing.Optional[IMPORT_typing.Iterable[int]] = None,
        ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
            # UX improvement: check that neither positional argument was accidentally
            # given a gRPC request type.
            IMPORT_reboot_aio_types.assert_not_request_type(__context__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest)
            IMPORT_reboot_aio_types.assert_not_request_type(__options__, request_type=rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest)


            if last is not None and not isinstance(
                last,
                int,
            ):
                raise TypeError(
                    f"Can not construct protobuf message of type "
                    f"'rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest': field 'last' is not "
                    f"of required type 'int'"
                )
            if follow is not None and not isinstance(
                follow,
                bool,
            ):
                raise TypeError(
                    f"Can not construct protobuf message of type "
                    f"'rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest': field 'follow' is not "
                    f"of required type 'bool'"
                )
            if revision_numbers is not None and not isinstance(
                revision_numbers,
                IMPORT_typing.Iterable,
            ):
                raise TypeError(
                    f"Can not construct protobuf message of type "
                    f"'rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest': field 'revision_numbers' is not "
                    f"of required type 'typing.Iterable[int]'"
                )
            if sources is not None and not isinstance(
                sources,
                IMPORT_typing.Iterable,
            ):
                raise TypeError(
                    f"Can not construct protobuf message of type "
                    f"'rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest': field 'sources' is not "
                    f"of required type 'typing.Iterable[int]'"
                )
            # TODO: mypy-protobuf declares that
            # `google.protobuf.message.Message` constructor arguments are
            # always non-None, when in reality they are optional.
            __request__ = rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest(
                last=last,  # type: ignore[arg-type]
                follow=follow,  # type: ignore[arg-type]
                revision_numbers=revision_numbers,  # type: ignore[arg-type]
                sources=sources,  # type: ignore[arg-type]
            )
            __metadata__: IMPORT_typing.Optional[IMPORT_reboot_aio_types.GrpcMetadata] = None
            __bearer_token__: IMPORT_typing.Optional[str] = None
            if __options__ is not None:
                IMPORT_reboot_aio_types.assert_type(__options__, [IMPORT_reboot_aio_call.Options])
                if __options__.metadata is not None:
                    __metadata__ = __options__.metadata
                if __options__.bearer_token is not None:
                    __bearer_token__ = __options__.bearer_token
            __call__ = __this__._reader(__context__).Logs(
                __request__,
                metadata=__metadata__,
            )
            async for __response__ in __call__:
                yield __response__

    class _Forall:

        _ids: list[str]

        def __init__(self, ids: list[str]):
            self._ids = ids

        async def Ensure(
            # In methods which are dealing with user input, (i.e.,
            # proto message field names), we should use '__double_underscored__'
            # variables to avoid any potential name conflicts with the method's
            # parameters.
            # The '__self__' parameter is a convention in Python to
            # indicate that this method is a bound method, so we use
            # '__this__' instead.
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
        ) -> list[rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse]:
            return await IMPORT_asyncio.gather(
                *[
                    ApplicationLogs.ref(
                        id
                    ).Ensure(
                        __context__,
                        __options__,
                    ) for id in __this__._ids
                ]
            )

        async def RegisterConsensus(
            # In methods which are dealing with user input, (i.e.,
            # proto message field names), we should use '__double_underscored__'
            # variables to avoid any potential name conflicts with the method's
            # parameters.
            # The '__self__' parameter is a convention in Python to
            # indicate that this method is a bound method, so we use
            # '__this__' instead.
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
        ) -> list[rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse]:
            return await IMPORT_asyncio.gather(
                *[
                    ApplicationLogs.ref(
                        id
                    ).RegisterConsensus(
                        __context__,
                        __options__,
                    ) for id in __this__._ids
                ]
            )

        async def RegisterRevision(
            # In methods which are dealing with user input, (i.e.,
            # proto message field names), we should use '__double_underscored__'
            # variables to avoid any potential name conflicts with the method's
            # parameters.
            # The '__self__' parameter is a convention in Python to
            # indicate that this method is a bound method, so we use
            # '__this__' instead.
            __this__,
            __context__: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
            __options__: IMPORT_reboot_aio_call.Options = IMPORT_reboot_aio_call.Options(),
            *,
            revision_number: IMPORT_typing.Optional[int] = None,
        ) -> list[rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse]:
            return await IMPORT_asyncio.gather(
                *[
                    ApplicationLogs.ref(
                        id
                    ).RegisterRevision(
                        __context__,
                        __options__,
                        revision_number=revision_number,
                    ) for id in __this__._ids
                ]
            )


    @classmethod
    def forall(cls, ids: list[str]) -> ApplicationLogs._Forall:
        return ApplicationLogs._Forall(ids)

    @classmethod
    def ref(
        cls,
        state_id: IMPORT_reboot_aio_types.StateId,
        *,
        bearer_token: IMPORT_typing.Optional[str] = None,
    ) -> ApplicationLogs.WeakReference[ApplicationLogs.WeakReference._Schedule]:
        return ApplicationLogs.WeakReference(
            # TODO(https://github.com/reboot-dev/mono/issues/3226): add support for calling other applications.
            # For now this always stays within the application that creates the context.
            application_id=None,
            state_id=state_id,
            schedule_type=ApplicationLogs.WeakReference._Schedule,
            bearer_token=bearer_token,
        )


    @IMPORT_typing.overload
    @classmethod
    def idempotently(cls, alias: IMPORT_typing.Optional[str] = None, *, each_iteration: bool = False) -> ApplicationLogs._ConstructIdempotently:
        ...

    @IMPORT_typing.overload
    @classmethod
    def idempotently(cls, *, key: IMPORT_uuid.UUID, generated: bool = False) -> ApplicationLogs._ConstructIdempotently:
        ...

    @classmethod
    def idempotently(
        cls,
        alias: IMPORT_typing.Optional[str] = None,
        *,
        key: IMPORT_typing.Optional[IMPORT_uuid.UUID] = None,
        each_iteration: IMPORT_typing.Optional[bool] = None,
        generated: bool = False,
    ) -> ApplicationLogs._ConstructIdempotently:
        return ApplicationLogs._ConstructIdempotently(
            _idempotency=IMPORT_reboot_aio_contexts.Context.idempotency(
                alias=alias,
                key=key,
                each_iteration=each_iteration,
                generated=generated,
            ),
        )

    @classmethod
    def per_workflow(
        cls,
        alias: IMPORT_typing.Optional[str] = None,
    ):
        return cls.idempotently(alias)

    @classmethod
    def per_iteration(
        cls,
        alias: IMPORT_typing.Optional[str] = None,
    ):
        return cls.idempotently(alias, each_iteration=True)

    @classmethod
    def always(cls):
        return cls.idempotently(key=IMPORT_uuid.uuid4(), generated=True)

    @IMPORT_dataclasses.dataclass(frozen=True)
    class _ConstructIdempotently:

        _idempotency: IMPORT_reboot_aio_idempotency.Idempotency



############################ Servicer Node adapters ############################
# Used by Node.js servicer implementations to access Python code and vice-versa.
# Relevant to servicers, irrelevant to clients.

class ApplicationLogsServicerNodeAdaptor(ApplicationLogs.singleton.Servicer):

    async def _wait_for_cancelled(
        self,
        future: IMPORT_asyncio.Future,
        method: str,
    ):
        while True:
            done, pending = await IMPORT_asyncio.wait(
                [future],
                timeout=5,  # seconds
            )
            # Check if we've timed out and log a warning that their
            # call has been cancelled but it is still running.
            if len(done) == 0:
                logger.warning(
                    f"Call to method '{method}' has been cancelled by the caller, "
                    "BUT WE ARE STILL WAITING for it complete. You can use the promise "
                    "`context.cancelled` to check if the caller has cancelled so you "
                    "don't do unnecessary work or wait for something that may never occur."
                )
                continue
            break

        # Now need to actually `await` the future so that we don't
        # have an unretrieved exception that gets logged.
        #
        # NOTE: this will raise an exception if the method raised even
        # though the call has already been cancelled but it makes it
        # more clear that the method raised so that is why we're not
        # catching and swallowing any exception.
        await future

    def __init__(self):
        self._js_servicer_reference = self._construct_js_servicer()  # type: ignore[attr-defined]

    def authorizer(self) -> IMPORT_typing.Optional[IMPORT_rebootdev.aio.auth.authorizers.Authorizer]:
        return self._construct_authorizer(self._js_servicer_reference)  # type: ignore[attr-defined]

    async def _read(
        self,
        context: IMPORT_reboot_aio_contexts.WorkflowContext,
        json_options: str,
    ) -> str:
        options = IMPORT_json.loads(json_options)

        alias = options.get('alias')

        assert 'how' in options
        how = options['how']
        if how == IMPORT_reboot_aio_workflows.ALWAYS:
            assert alias is None
            return IMPORT_google_protobuf_json_format.MessageToJson(
                await super().state.always().read(context)
            )

        assert how in [
            IMPORT_reboot_aio_workflows.PER_WORKFLOW,
            IMPORT_reboot_aio_workflows.PER_ITERATION,
        ]

        return IMPORT_google_protobuf_json_format.MessageToJson(
            await (
                super().state.per_workflow(alias)
                if how == IMPORT_reboot_aio_workflows.PER_WORKFLOW
                else super().state.per_iteration(alias)
            ).read(context)
        )

    async def _write(
        self,
        context: IMPORT_reboot_aio_contexts.WorkflowContext,
        writer: IMPORT_typing.Callable[[str], IMPORT_typing.Awaitable[str]],
        json_options: str,
    ) -> str:

        async def _writer(state: IMPORT_google_protobuf_message.Message):
            with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="_writer on NodeAdaptor",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
            ):
                json_result_state = await writer(
                    IMPORT_google_protobuf_json_format.MessageToJson(state)
                )

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="_write - State Copy on NodeAdaptor",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    result_state = IMPORT_json.loads(json_result_state)

                    state.CopyFrom(
                        IMPORT_google_protobuf_json_format.ParseDict(
                            result_state['state'],
                            self.__state_type__(),
                        )
                    )

                    assert 'result' in result_state
                    result = result_state['result']
                    assert type(result) == str
                    return result

        options = IMPORT_json.loads(json_options)

        alias = options.get('alias')

        assert 'how' in options
        how = options['how']

        if how == IMPORT_reboot_aio_workflows.ALWAYS:
            assert alias is None
            return await super().state.always().write(
                context,
                _writer,
            )

        assert how in [
            IMPORT_reboot_aio_workflows.PER_WORKFLOW,
            IMPORT_reboot_aio_workflows.PER_ITERATION,
        ]

        return await (
            super().state.per_workflow(alias)
            if how == IMPORT_reboot_aio_workflows.PER_WORKFLOW
            else super().state.per_iteration(alias)
        ).write(context, _writer, type=str)

    # ApplicationLogs specific methods:
    async def Ensure(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.EnsureRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse:
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="NodeAdaptor Ensure",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
        ):
            with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="Create and serialize `TrampolineCall`",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
            ):
                bytes_call = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineCall(
                    kind=IMPORT_rbt_v1alpha1_nodejs_pb2.writer,
                    context=IMPORT_rbt_v1alpha1_nodejs_pb2.Context(
                        method='Ensure',
                        state_id=context.state_id,
                        state_type_name=context.state_type_name,
                        caller_bearer_token=context.caller_bearer_token,
                        cookie=context.cookie,
                        app_internal=context.app_internal,
                        auth=(
                            None if context.auth is None
                            else context.auth.to_proto_bytes()
                        ),
                    ),
                    state=state.SerializeToString(),
                    request=request.SerializeToString(),
                ).SerializeToString()

            cancelled: IMPORT_asyncio.Future[None] = IMPORT_asyncio.Future()

            bytes_result_future: IMPORT_typing.Optional[IMPORT_asyncio.Future[str]] = None

            try:
                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="trampoline",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    bytes_result_future = self._trampoline(  # type: ignore[attr-defined]
                        self._js_servicer_reference,
                        context,
                        cancelled,
                        bytes_call,
                    )
                    # NOTE: we need to `asyncio.shield` so that we can still
                    # correctly wait for this future to complete even if we
                    # are cancelled.
                    assert bytes_result_future is not None
                    bytes_result = await IMPORT_asyncio.shield(bytes_result_future)
            except IMPORT_asyncio.CancelledError:
                cancelled.set_result(None)

                # NOTE: we MUST wait for `bytes_result_future` because this
                # is a `writer` or `transaction` and we CAN NOT execute
                # multiple simultaneously.
                if bytes_result_future is not None:
                    await self._wait_for_cancelled(
                        bytes_result_future,
                        'ApplicationLogs.Ensure',
                    )

                raise
            except:
                # Make sure we cancel the `cancelled` future either if an
                # exception is thrown or if the result is reeturned so
                # that we don't keep around resources related to it that
                # might cause us to run out of memory or worse, keep Node
                # from exiting because it is waiting for Python.
                cancelled.cancel()
                raise
            else:
                cancelled.cancel()

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="result ParseFromString",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    result = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineResult.FromString(
                        bytes_result
                    )

                if result.HasField('state'):
                    with IMPORT_reboot_aio_tracing.span(
                        state_name=f"{context.state_type_name}('{context.state_id}')",
                        span_name="state ParseFromString",
                        # The naming above matches Python, but not TypeScript.
                        python_specific=True,
                        level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    ):
                        state.CopyFrom(
                            rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs.FromString(
                                result.state
                            )
                        )

                if result.HasField('status_json'):
                    raise (
                        ApplicationLogs
                        .EnsureAborted
                        .from_status(
                            IMPORT_google_protobuf_json_format.Parse(
                                result.status_json,
                                IMPORT_google_rpc_status_pb2.Status(),
                            )
                        )
                    )

                assert result.HasField('response')

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="response ParseFromString",
                ):
                    return rbt.cloud.v1alpha1.logs.logs_pb2.EnsureResponse.FromString(result.response)
        raise RuntimeError("Unexpected result from Ensure")

    async def RegisterConsensus(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse:
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="NodeAdaptor RegisterConsensus",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
        ):
            with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="Create and serialize `TrampolineCall`",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
            ):
                bytes_call = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineCall(
                    kind=IMPORT_rbt_v1alpha1_nodejs_pb2.writer,
                    context=IMPORT_rbt_v1alpha1_nodejs_pb2.Context(
                        method='RegisterConsensus',
                        state_id=context.state_id,
                        state_type_name=context.state_type_name,
                        caller_bearer_token=context.caller_bearer_token,
                        cookie=context.cookie,
                        app_internal=context.app_internal,
                        auth=(
                            None if context.auth is None
                            else context.auth.to_proto_bytes()
                        ),
                    ),
                    state=state.SerializeToString(),
                    request=request.SerializeToString(),
                ).SerializeToString()

            cancelled: IMPORT_asyncio.Future[None] = IMPORT_asyncio.Future()

            bytes_result_future: IMPORT_typing.Optional[IMPORT_asyncio.Future[str]] = None

            try:
                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="trampoline",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    bytes_result_future = self._trampoline(  # type: ignore[attr-defined]
                        self._js_servicer_reference,
                        context,
                        cancelled,
                        bytes_call,
                    )
                    # NOTE: we need to `asyncio.shield` so that we can still
                    # correctly wait for this future to complete even if we
                    # are cancelled.
                    assert bytes_result_future is not None
                    bytes_result = await IMPORT_asyncio.shield(bytes_result_future)
            except IMPORT_asyncio.CancelledError:
                cancelled.set_result(None)

                # NOTE: we MUST wait for `bytes_result_future` because this
                # is a `writer` or `transaction` and we CAN NOT execute
                # multiple simultaneously.
                if bytes_result_future is not None:
                    await self._wait_for_cancelled(
                        bytes_result_future,
                        'ApplicationLogs.RegisterConsensus',
                    )

                raise
            except:
                # Make sure we cancel the `cancelled` future either if an
                # exception is thrown or if the result is reeturned so
                # that we don't keep around resources related to it that
                # might cause us to run out of memory or worse, keep Node
                # from exiting because it is waiting for Python.
                cancelled.cancel()
                raise
            else:
                cancelled.cancel()

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="result ParseFromString",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    result = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineResult.FromString(
                        bytes_result
                    )

                if result.HasField('state'):
                    with IMPORT_reboot_aio_tracing.span(
                        state_name=f"{context.state_type_name}('{context.state_id}')",
                        span_name="state ParseFromString",
                        # The naming above matches Python, but not TypeScript.
                        python_specific=True,
                        level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    ):
                        state.CopyFrom(
                            rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs.FromString(
                                result.state
                            )
                        )

                if result.HasField('status_json'):
                    raise (
                        ApplicationLogs
                        .RegisterConsensusAborted
                        .from_status(
                            IMPORT_google_protobuf_json_format.Parse(
                                result.status_json,
                                IMPORT_google_rpc_status_pb2.Status(),
                            )
                        )
                    )

                assert result.HasField('response')

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="response ParseFromString",
                ):
                    return rbt.cloud.v1alpha1.logs.logs_pb2.RegisterConsensusResponse.FromString(result.response)
        raise RuntimeError("Unexpected result from RegisterConsensus")

    async def RegisterRevision(
        self,
        context: IMPORT_reboot_aio_contexts.WriterContext,
        state: rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs,
        request: rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionRequest,
    ) -> rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse:
        with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="NodeAdaptor RegisterRevision",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
        ):
            with IMPORT_reboot_aio_tracing.span(
                state_name=f"{context.state_type_name}('{context.state_id}')",
                span_name="Create and serialize `TrampolineCall`",
                # The naming above matches Python, but not TypeScript.
                python_specific=True,
                level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
            ):
                bytes_call = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineCall(
                    kind=IMPORT_rbt_v1alpha1_nodejs_pb2.writer,
                    context=IMPORT_rbt_v1alpha1_nodejs_pb2.Context(
                        method='RegisterRevision',
                        state_id=context.state_id,
                        state_type_name=context.state_type_name,
                        caller_bearer_token=context.caller_bearer_token,
                        cookie=context.cookie,
                        app_internal=context.app_internal,
                        auth=(
                            None if context.auth is None
                            else context.auth.to_proto_bytes()
                        ),
                    ),
                    state=state.SerializeToString(),
                    request=request.SerializeToString(),
                ).SerializeToString()

            cancelled: IMPORT_asyncio.Future[None] = IMPORT_asyncio.Future()

            bytes_result_future: IMPORT_typing.Optional[IMPORT_asyncio.Future[str]] = None

            try:
                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="trampoline",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    bytes_result_future = self._trampoline(  # type: ignore[attr-defined]
                        self._js_servicer_reference,
                        context,
                        cancelled,
                        bytes_call,
                    )
                    # NOTE: we need to `asyncio.shield` so that we can still
                    # correctly wait for this future to complete even if we
                    # are cancelled.
                    assert bytes_result_future is not None
                    bytes_result = await IMPORT_asyncio.shield(bytes_result_future)
            except IMPORT_asyncio.CancelledError:
                cancelled.set_result(None)

                # NOTE: we MUST wait for `bytes_result_future` because this
                # is a `writer` or `transaction` and we CAN NOT execute
                # multiple simultaneously.
                if bytes_result_future is not None:
                    await self._wait_for_cancelled(
                        bytes_result_future,
                        'ApplicationLogs.RegisterRevision',
                    )

                raise
            except:
                # Make sure we cancel the `cancelled` future either if an
                # exception is thrown or if the result is reeturned so
                # that we don't keep around resources related to it that
                # might cause us to run out of memory or worse, keep Node
                # from exiting because it is waiting for Python.
                cancelled.cancel()
                raise
            else:
                cancelled.cancel()

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="result ParseFromString",
                    # The naming above matches Python, but not TypeScript.
                    python_specific=True,
                    level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                ):
                    result = IMPORT_rbt_v1alpha1_nodejs_pb2.TrampolineResult.FromString(
                        bytes_result
                    )

                if result.HasField('state'):
                    with IMPORT_reboot_aio_tracing.span(
                        state_name=f"{context.state_type_name}('{context.state_id}')",
                        span_name="state ParseFromString",
                        # The naming above matches Python, but not TypeScript.
                        python_specific=True,
                        level=IMPORT_reboot_aio_tracing.TraceLevel.CUSTOMER,
                    ):
                        state.CopyFrom(
                            rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs.FromString(
                                result.state
                            )
                        )

                if result.HasField('status_json'):
                    raise (
                        ApplicationLogs
                        .RegisterRevisionAborted
                        .from_status(
                            IMPORT_google_protobuf_json_format.Parse(
                                result.status_json,
                                IMPORT_google_rpc_status_pb2.Status(),
                            )
                        )
                    )

                assert result.HasField('response')

                with IMPORT_reboot_aio_tracing.span(
                    state_name=f"{context.state_type_name}('{context.state_id}')",
                    span_name="response ParseFromString",
                ):
                    return rbt.cloud.v1alpha1.logs.logs_pb2.RegisterRevisionResponse.FromString(result.response)
        raise RuntimeError("Unexpected result from RegisterRevision")

    async def Logs(
        self,
        context: IMPORT_reboot_aio_contexts.ReaderContext,
        states: IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.ApplicationLogs],
        request: rbt.cloud.v1alpha1.logs.logs_pb2.LogsRequest,
    ) -> IMPORT_typing.AsyncIterable[rbt.cloud.v1alpha1.logs.logs_pb2.LogsResponse]:
        raise NotImplementedError
        yield  # Necessary for type checking.
        raise RuntimeError("Unexpected result from Logs")



############################ Reference Node adapters ############################
# Used by Node.js WeakReference implementations to access Python code and
# vice-versa. Relevant to clients.

class ApplicationLogsWeakReferenceNodeAdaptor(ApplicationLogs.WeakReference[ApplicationLogs.WeakReference._Schedule]):

    async def _call(  # type: ignore[override]
        self,
        *,
        callable: IMPORT_typing.Callable[[IMPORT_google_protobuf_message.Message], IMPORT_typing.Awaitable],
        aborted_type: type[IMPORT_rebootdev.aio.aborted.Aborted],
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
    ) -> str:
        request = request_type()

        try:
            IMPORT_google_protobuf_json_format.Parse(json_request, request)
            response = await callable(request)
        except IMPORT_google_protobuf_json_format.ParseError as parse_error:
            aborted_error = IMPORT_rebootdev.aio.aborted.SystemAborted(
                IMPORT_rbt_v1alpha1.errors_pb2.Unknown(),
                message=f"{parse_error}; "
                       "This is usually caused by a deeply nested protobuf message, which is not supported by protobuf.\n"
                        "See the limits here: https://protobuf.dev/programming-guides/proto-limits/"
                )

            return IMPORT_json.dumps(
                {
                    'status': IMPORT_google_protobuf_json_format.MessageToDict(
                        aborted_error.to_status()
                    )
                }
            )
        except BaseException as exception:
            if isinstance(exception, aborted_type):
                return IMPORT_json.dumps(
                    {
                        'status': IMPORT_google_protobuf_json_format.MessageToDict(
                            exception.to_status()
                        )
                    }
                )
            raise
        else:
            return IMPORT_json.dumps(
                {
                    'response': IMPORT_google_protobuf_json_format.MessageToDict(
                        response
                    )
                }
            )

    async def _schedule(  # type: ignore[override]
        self,
        *,
        method: str,
        context: IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        schedule: IMPORT_reboot_time_DateTimeWithTimeZone,
        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency],
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
    ) -> str:
        request = request_type()

        IMPORT_google_protobuf_json_format.Parse(json_request, request)

        if isinstance(context, IMPORT_reboot_aio_contexts.WriterContext):
            task = await getattr(
                ApplicationLogsServicerTasks(
                    context=context,
                    state_ref=context._state_ref,
                ),
                method,
            )(request, schedule=schedule)

            return IMPORT_json.dumps(
                {
                    'taskId': IMPORT_google_protobuf_json_format.MessageToDict(
                        task.task_id
                    )
                }
            )

        # Add scheduling information to the metadata.
        metadata: IMPORT_reboot_aio_types.GrpcMetadata = (
            (IMPORT_reboot_aio_headers.TASK_SCHEDULE, schedule.isoformat()),
        )

        task_id = await getattr(super()._tasks(context), method)(
            request,
            idempotency=idempotency,
            metadata=metadata,
        )

        return IMPORT_json.dumps(
            {
                'taskId': IMPORT_google_protobuf_json_format.MessageToDict(task_id)
            }
        )

    async def _reader(  # type: ignore[override]
        self,
        method: str,
        context: IMPORT_reboot_aio_contexts.ReaderContext | IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
        json_options: str,
    ) -> str:
        options = IMPORT_json.loads(json_options)

        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None

        if 'idempotency' in options:
            idempotency = IMPORT_reboot_aio_contexts.Context.idempotency(
                alias=options['idempotency'].get('alias'),
                key=options['idempotency'].get('key'),
                each_iteration=options['idempotency'].get('eachIteration'),
                generated=options['idempotency'].get('generated', False),
            )

        method_handle = IMPORT_functools.partial(
            getattr(super()._reader(context), method),
            bearer_token=options.get("bearerToken"),
            idempotency=idempotency,
        )
        return await self._call(
            callable=method_handle,
            aborted_type=getattr(
                ApplicationLogs, method + 'Aborted'
            ),
            request_type=request_type,
            json_request=json_request,
        )

    async def _writer(  # type: ignore[override]
        self,
        method: str,
        context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
        json_options: str,
    ) -> str:
        options = IMPORT_json.loads(json_options)

        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None

        if 'idempotency' in options:
            idempotency = IMPORT_reboot_aio_contexts.Context.idempotency(
                alias=options['idempotency'].get('alias'),
                key=options['idempotency'].get('key'),
                each_iteration=options['idempotency'].get('eachIteration'),
                generated=options['idempotency'].get('generated', False),
            )

        if 'schedule' in options:
            when = IMPORT_google_protobuf_timestamp_pb2.Timestamp()
            when.FromJsonString(options['schedule']['when'])
            return await self._schedule(
                method=method,
                context=context,
                schedule=IMPORT_reboot_time_DateTimeWithTimeZone.from_protobuf_timestamp(when),
                idempotency=idempotency,
                request_type=request_type,
                json_request=json_request,
            )

        method_handle = IMPORT_functools.partial(
            getattr(super()._writer(context), method),
            idempotency=idempotency,
            bearer_token=options.get("bearerToken"),
        )
        return await self._call(
            callable=method_handle,
            aborted_type=getattr(
                ApplicationLogs, method + 'Aborted'
            ),
            request_type=request_type,
            json_request=json_request,
        )

    async def _transaction(  # type: ignore[override]
        self,
        method: str,
        context: IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
        json_options: str,
    ) -> str:
        options = IMPORT_json.loads(json_options)

        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None

        if 'idempotency' in options:
            idempotency = IMPORT_reboot_aio_contexts.Context.idempotency(
                alias=options['idempotency'].get('alias'),
                key=options['idempotency'].get('key'),
                each_iteration=options['idempotency'].get('eachIteration'),
                generated=options['idempotency'].get('generated', False),
            )

        if 'schedule' in options:
            when = IMPORT_google_protobuf_timestamp_pb2.Timestamp()
            when.FromJsonString(options['schedule']['when'])
            return await self._schedule(
                method=method,
                context=context,
                schedule=IMPORT_reboot_time_DateTimeWithTimeZone.from_protobuf_timestamp(when),
                idempotency=idempotency,
                request_type=request_type,
                json_request=json_request,
            )

        method_handle = IMPORT_functools.partial(
            getattr(super()._workflow(context), method),
            idempotency=idempotency,
            bearer_token=options.get("bearerToken"),
        )
        return await self._call(
            callable=method_handle,
            aborted_type=getattr(
                ApplicationLogs, method + 'Aborted'
            ),
            request_type=request_type,
            json_request=json_request,
        )

    async def _workflow(  # type: ignore[override]
        self,
        method: str,
        context: IMPORT_reboot_aio_contexts.WriterContext | IMPORT_reboot_aio_contexts.TransactionContext | IMPORT_reboot_aio_contexts.WorkflowContext | IMPORT_reboot_aio_external.ExternalContext,
        request_type: type[IMPORT_google_protobuf_message.Message],
        json_request: str,
        json_options: str,
    ) -> str:
        options = IMPORT_json.loads(json_options)

        idempotency: IMPORT_typing.Optional[IMPORT_reboot_aio_idempotency.Idempotency] = None

        if 'idempotency' in options:
            idempotency = IMPORT_reboot_aio_contexts.Context.idempotency(
                alias=options['idempotency'].get('alias'),
                key=options['idempotency'].get('key'),
                each_iteration=options['idempotency'].get('eachIteration'),
                generated=options['idempotency'].get('generated', False),
            )

        assert 'schedule' in options

        when = IMPORT_google_protobuf_timestamp_pb2.Timestamp()
        when.FromJsonString(options['schedule']['when'])

        return await self._schedule(
            method=method,
            context=context,
            schedule=IMPORT_reboot_time_DateTimeWithTimeZone.from_protobuf_timestamp(when),
            idempotency=idempotency,
            request_type=request_type,
            json_request=json_request,
        )

# yapf: enable
