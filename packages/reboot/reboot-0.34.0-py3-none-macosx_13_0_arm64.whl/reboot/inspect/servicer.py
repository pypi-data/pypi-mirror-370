import asyncio
import google
import grpc
import json
import os
import sys
import traceback
from collections import defaultdict
from google.api.httpbody_pb2 import HttpBody
from google.protobuf.struct_pb2 import Struct
from log.log import get_logger
from pathlib import Path
from rbt.v1alpha1.inspect import inspect_pb2_grpc
from rbt.v1alpha1.inspect.inspect_pb2 import (
    GetAllStatesRequest,
    GetAllStatesResponse,
    WebDashboardRequest,
)
from reboot.aio.auth.admin_auth import (
    AdminAuthMixin,
    auth_metadata_from_metadata,
)
from rebootdev.aio.internals.channel_manager import _ChannelManager
from rebootdev.aio.internals.middleware import Middleware
from rebootdev.aio.placement import PlacementClient
from rebootdev.aio.state_managers import StateManager
from rebootdev.aio.types import (
    ApplicationId,
    ConsensusId,
    StateId,
    StateRef,
    StateTypeName,
)
from typing import AsyncIterator, Optional

logger = get_logger(__name__)


async def chunks(
    struct: Struct,
    *,
    chunk_size_bytes: int = int(1 * 1024 * 1024),
) -> AsyncIterator[GetAllStatesResponse]:
    """Helper to chunk up `struct` into `chunk_size_bytes` to avoid any
    max message sizes along the way, i.e., 4MB by default for gRPC.
    """
    data = struct.SerializeToString()
    total = (len(data) + chunk_size_bytes - 1) // chunk_size_bytes
    # Even if `data` is empty we still need to send 1 chunk so set
    # `total` to 1 which will just send an empty `data`.
    total = 1 if total == 0 else total
    for chunk in range(0, total):
        offset = chunk * chunk_size_bytes
        yield GetAllStatesResponse(
            chunk=chunk,
            total=total,
            data=data[offset:offset + chunk_size_bytes],
        )


async def accumulate(call) -> Struct:
    """Helper to accumulate `GetAllStatesResponse` responses into a single
    `Struct`.
    """
    data: list[bytes] = []
    while True:
        response = await anext(aiter(call))

        data.append(response.data)

        # Check if there are more chunks.
        if response.chunk < response.total - 1:
            continue

        accumulated = b''.join(data)

        struct = Struct()
        struct.ParseFromString(accumulated)

        return struct


class InspectServicer(
    AdminAuthMixin,
    inspect_pb2_grpc.InspectServicer,
):

    def __init__(
        self,
        application_id: ApplicationId,
        consensus_id: ConsensusId,
        state_manager: StateManager,
        placement_client: PlacementClient,
        channel_manager: _ChannelManager,
        middleware_by_state_type_name: dict[StateTypeName, Middleware],
    ):
        super().__init__()
        self._application_id = application_id
        self._consensus_id = consensus_id
        self._state_manager = state_manager
        self._placement_client = placement_client
        self._channel_manager = channel_manager
        self._middleware_by_state_type_name = middleware_by_state_type_name

    def add_to_server(self, server: grpc.aio.Server) -> None:
        inspect_pb2_grpc.add_InspectServicer_to_server(self, server)

    async def _aggregate_all_actors(
        self,
        grpc_context: grpc.aio.ServicerContext,
        only_consensus_id: ConsensusId,
    ) -> AsyncIterator[GetAllStatesResponse]:

        async def call_other_consensus(
            consensus_id: ConsensusId,
            parts: dict[ConsensusId, Struct],
            part_changed: asyncio.Event,
        ):
            """
            Calls `GetAllStates` on the given consensus, and updates its entry
            in `parts` every time a new response is sent.
            """
            channel = self._channel_manager.get_channel_to(
                self._placement_client.address_for_consensus(consensus_id)
            )
            stub = inspect_pb2_grpc.InspectStub(channel)

            call = stub.GetAllStates(
                GetAllStatesRequest(only_consensus_id=consensus_id),
                metadata=auth_metadata_from_metadata(grpc_context),
            )

            # Loop getting next accumulated struct and update `parts`.
            while True:
                struct = await accumulate(call)

                parts[consensus_id] = struct
                part_changed.set()

        # ASSUMPTION: the list of known consensuses is stable.
        parts: dict[ConsensusId, Struct] = {}
        parts_changed = asyncio.Event()

        # In the background, ask all of the consensuses about their part of
        # the total set of actors.
        consensus_ids = self._placement_client.known_consensuses(
            self._application_id
        ) if only_consensus_id == "" else [only_consensus_id]
        tasks = [
            asyncio.create_task(
                call_other_consensus(consensus_id, parts, parts_changed),
                name=f'call_other_consensus({consensus_id}, ...) in {__name__}',
            ) for consensus_id in consensus_ids
        ]

        all_tasks = tasks
        try:
            while True:
                # Every time any of the parts change, recompute the total view
                # of all actors. However we simultaneously also watch 'tasks',
                # so we hear if there's a failure gathering any of the parts.
                parts_changed_task = asyncio.create_task(
                    parts_changed.wait(),
                    name=f'parts_changed.wait() in {__name__}',
                )

                all_tasks = [parts_changed_task] + tasks

                done, pending = await asyncio.wait(
                    all_tasks, return_when=asyncio.FIRST_COMPLETED
                )

                # The `tasks` will never finish without an exception,
                # so if `parts_changed_task` is not the _only_ thing
                # in `done` then an exception must have been raised
                # and we should use `asyncio.gather(...)` to get it to
                # propagate.
                if parts_changed_task not in done or len(done) != 1:
                    await asyncio.gather(*tasks)

                assert parts_changed_task.done()
                parts_changed.clear()

                # Only send an overview once we've heard from all consensuses;
                # we try to avoid sending incomplete results so clients are
                # easier to write.
                if len(parts) < len(consensus_ids):
                    continue

                # Assemble an overview of all actors from the parts.
                struct = Struct()
                for part in parts.values():
                    for service_name, fields in part.items():
                        # NOTE: if `struct` is "empty we can't just
                        # check if `service_name not in struct`
                        # because that causes the protobuf library to
                        # hard crash! Hence the check here for
                        # `len(struct.keys()) == 0`.
                        if (
                            len(struct.keys()) == 0 or
                            service_name not in struct
                        ):
                            struct[service_name] = Struct()
                        struct[service_name].update(fields)

                async for chunk in chunks(struct):
                    yield chunk
        finally:
            for task in all_tasks:
                if not task.done():
                    task.cancel()
            # We need to explicitly `await` or call `.result()` on
            # each task otherwise we'll get 'Task exception was never
            # retrieved'.
            for task in all_tasks:
                try:
                    await task
                except:
                    # We'll let what ever other exception has been
                    # raised propagate instead of this exception which
                    # might just be `CancelledError` from us
                    # cancelling the task.
                    pass

    async def GetAllStates(
        self,
        request: GetAllStatesRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[GetAllStatesResponse]:
        await self.ensure_admin_auth_or_fail(grpc_context)

        # If this call is not specifically for this consensus, act as an
        # aggregator.
        if request.only_consensus_id != self._consensus_id:
            # Act as (only) an aggregator.
            #
            # TODO(rjh): consider limiting the response size (e.g. to top N
            #            actors, with paging?).
            async for response in self._aggregate_all_actors(
                grpc_context, request.only_consensus_id
            ):
                yield response
            return

        # Dictionary representing the state_types and actors that we will
        # convert to JSON.
        state_types_and_actors: defaultdict[StateTypeName,
                                            dict[StateId,
                                                 object]] = defaultdict(dict)

        # Event indicating that our first loads have all completed, and that we
        # can send a first JSON version of our state over the network. Note that
        # this first load may have touched _no_ actors.
        first_loads_or_exceptions_complete = asyncio.Event()

        # Event indicating that our dictionary has changed and we
        # should send another JSON version of it over the network.
        state_types_and_actors_modified = asyncio.Event()

        async def watch_actor(
            state_type: StateTypeName,
            state_ref: StateRef,
            middleware: Middleware,
            first_load_or_exception: asyncio.Event,
        ):
            """Helper that watches for state updates on a specific actor."""
            try:
                # For every state update, save a representation of the
                # state that can be converted into JSON.
                async for state in middleware.inspect(state_ref):
                    # We convert our message to JSON, and then back to an
                    # `object`, so that when we do the final conversion to
                    # JSON we'll only have the fields from the initial
                    # conversion.
                    state_types_and_actors[state_type][state_ref.id] = (
                        json.loads(
                            google.protobuf.json_format.MessageToJson(
                                state,
                                preserving_proto_field_name=True,
                                ensure_ascii=True,
                            )
                        )
                    )

                    state_types_and_actors_modified.set()
                    first_load_or_exception.set()
            except asyncio.CancelledError:
                # This is routine; it probably just means the caller went away.
                pass
            except BaseException as exception:
                logger.warning(
                    "An unexpected error was encountered: "
                    f"{type(exception).__name__}: {exception}\n" +
                    traceback.format_exc() +
                    "\nPlease report this to the maintainers!"
                )

                # Make sure sure we trigger `first_load_or_exception`
                # if an exception gets raised so that we send at least
                # some data back to the user.
                first_load_or_exception.set()

                raise

        async def watch_actors():
            """Helper that watches for updates from the state manager for the set
            of running actors."""
            # Tasks that are running our `watch_actor(...)` helper.
            watch_actor_tasks: defaultdict[StateTypeName, dict[
                StateRef, asyncio.Task]] = defaultdict(dict)

            try:
                async for actors in self._state_manager.actors():
                    # Start watching any actors that we aren't already watching.
                    first_loads_or_exceptions: list[asyncio.Event] = []
                    for (state_type, state_refs) in actors.items():
                        for state_ref in state_refs:
                            if state_ref not in watch_actor_tasks[state_type]:
                                # If the state type no longer exists
                                # don't bother creating a watch task.
                                middleware: Optional[Middleware] = (
                                    self._middleware_by_state_type_name.
                                    get(state_type)
                                )

                                if middleware is None:
                                    continue

                                first_load_or_exception = asyncio.Event()

                                watch_actor_tasks[state_type][
                                    state_ref
                                ] = asyncio.create_task(
                                    watch_actor(
                                        state_type,
                                        state_ref,
                                        middleware,
                                        first_load_or_exception,
                                    ),
                                    name=
                                    f'watch_actor({state_type}, {state_ref}, ...) in {__name__}',
                                )

                                if not first_loads_or_exceptions_complete.is_set(
                                ):
                                    first_loads_or_exceptions.append(
                                        first_load_or_exception
                                    )

                    # TODO(benh): stop watching any actors that we are
                    # already watching.
                    for state_type in watch_actor_tasks:
                        for state_ref in watch_actor_tasks[state_type]:
                            if state_type not in actors or state_ref not in actors[
                                state_type]:
                                raise NotImplementedError(
                                    'Removing actors is not yet implemented'
                                )

                    if not first_loads_or_exceptions_complete.is_set():
                        if len(first_loads_or_exceptions) > 0:
                            await asyncio.gather(
                                *[f.wait() for f in first_loads_or_exceptions]
                            )
                        first_loads_or_exceptions_complete.set()
                        first_loads_or_exceptions.clear()
            finally:
                # Clean up after ourselves and stop watching actors.
                for tasks in watch_actor_tasks.values():
                    for task in tasks.values():
                        task.cancel()
                    # We need to explicitly `await` or call
                    # `.result()` on each task otherwise we'll get
                    # 'Task exception was never retrieved'.
                    for task in tasks.values():
                        try:
                            await task
                        except:
                            # We'll let what ever other exception has
                            # been raised propagate instead of this
                            # exception which might just be
                            # `CancelledError` from us cancelling the
                            # task.
                            pass

        watch_actors_task = asyncio.create_task(
            watch_actors(),
            name=f'watch_actors() in {__name__}',
        )

        try:
            # Wait for all of the actors that were already known when this call
            # started to be loaded before communicating the first result. That
            # helps ensure that the first response from `Inspect()` is complete,
            # making clients easier to write.
            await first_loads_or_exceptions_complete.wait()
            while True:
                state_types_and_actors_modified.clear()
                struct = Struct()
                struct.update(state_types_and_actors)
                async for chunk in chunks(struct):
                    yield chunk
                await state_types_and_actors_modified.wait()
        finally:
            # Clean up after ourselves and stop watching for new
            # actors (which also will stop watching individual
            # actors).
            try:
                watch_actors_task.cancel()
                await watch_actors_task
            except asyncio.CancelledError:
                pass
            except:
                # Print a stacktrace here but don't bother raising as
                # we don't care about this task any more.
                print(
                    'Failed trying to watch for new/removed actors',
                    file=sys.stderr
                )
                traceback.print_exc()

    async def WebDashboard(
        self,
        request: WebDashboardRequest,
        grpc_context: grpc.aio.ServicerContext,
    ) -> HttpBody:
        file = request.file or 'index.html'

        # Some files that may be requested by the browser are simply not there.
        # No need to print warnings about it.
        KNOWN_ABSENT_FILENAMES = [
            'bundle.css.map',
        ]
        if file in KNOWN_ABSENT_FILENAMES:
            await grpc_context.abort(grpc.StatusCode.NOT_FOUND)
            raise RuntimeError('This code is unreachable')

        # Some paths are rewritten to `index.html`; these are the
        # different routes presented by our single-page app.
        REWRITE_PATHS = {
            'tasks': 'index.html',
            'states': 'index.html',
        }
        if file in REWRITE_PATHS:
            file = REWRITE_PATHS[file]

        # The following files are expected to be served by this endpoint; they
        # should be served with the appropriate content type.
        CONTENT_TYPE_BY_FILE = {
            'index.html': 'text/html',
            'bundle.js': 'text/javascript',
            'bundle.js.map': 'application/json',
            'bundle.css': 'text/css',
        }
        if file not in CONTENT_TYPE_BY_FILE:
            logger.warning(f"Request for unexpected file: '{file}'")
            await grpc_context.abort(grpc.StatusCode.NOT_FOUND)
            raise RuntimeError('This code is unreachable')

        path = Path(os.path.join(os.path.dirname(__file__), file))
        return HttpBody(
            content_type=f'{CONTENT_TYPE_BY_FILE[file]}; charset=utf-8',
            data=path.read_text().encode('utf-8'),
        )
