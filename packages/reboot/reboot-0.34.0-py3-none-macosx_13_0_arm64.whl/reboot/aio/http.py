import asyncio
import contextlib
import uvicorn  # type: ignore[import]
from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi import Depends, FastAPI, Request  # type: ignore[import]
from rebootdev.aio.external import ExternalContext
from rebootdev.aio.internals.channel_manager import _ChannelManager
from rebootdev.aio.types import ConsensusId
from typing import Any, Awaitable, Callable, Generator, Optional


class WebFramework(ABC):
    """Web framework for HTTP endpoints in a Reboot application."""

    @abstractmethod
    async def start(
        self,
        consensus_id: ConsensusId,
        port: Optional[int],
        channel_manager: _ChannelManager,
    ) -> int:
        raise NotImplementedError()

    @abstractmethod
    async def stop(self, consensus_id: ConsensusId):
        raise NotImplementedError()


def external_context(request: Request) -> ExternalContext:
    return request.state.reboot_external_context


InjectExternalContext = Depends(external_context)


class PythonWebFramework(WebFramework):

    @dataclass(kw_only=True, frozen=True)
    class APIRoute:
        """Encapsulates details for an API route."""
        path: str
        kwargs: dict
        endpoint: Callable[..., Any]

    class HTTP:
        """Interface for decorating functions as API routes.

        NOTE: we can't just have developers directly use `FastAPI`
        because we need to actually capture each API route so that it
        can be pickled too each consensus process that we
        create. Moreover, we want to control the surface area that we
        expose so we can make sure that it works correctly.
        """

        def __init__(self):
            self._api_routes: list[PythonWebFramework.APIRoute] = []
            self._channel_manager = None

        def _api_route(self, path: str, **kwargs):
            # TODO: add type annotations for `endpoint` so that what
            # we take in is exactly what we return.
            def decorator(endpoint):
                # NOTE: we need to store the API route for later once
                # within the consensus process we call start only
                # _then_ can we add the route to the `FastAPI`
                # instance. This is further complicated by the fact
                # that we need to store the information in a
                # `APIRoute` object so that everything can be properly
                # pickled.
                self._api_routes.append(
                    PythonWebFramework.APIRoute(
                        path=path,
                        endpoint=endpoint,
                        kwargs=kwargs,
                    )
                )
                return endpoint

            return decorator

        def get(self, path: str, **kwargs):
            # Rather than list out all of the possible keyword args
            # that `FastAPI` expects we'll just pass along any that
            # are passed to us, but we don't expect `methods` as we
            # override that below.
            assert "methods" not in kwargs
            return self._api_route(path, methods=["GET"], **kwargs)

        def post(self, path: str, **kwargs):
            # Rather than list out all of the possible keyword args
            # that `FastAPI` expects we'll just pass along any that
            # are passed to us, but we don't expect `methods` as we
            # override that below.
            assert "methods" not in kwargs
            return self._api_route(path, methods=["POST"], **kwargs)

    def __init__(self):
        self._http = PythonWebFramework.HTTP()

        self._servers: dict[
            ConsensusId,
            tuple[uvicorn.Server, asyncio.Task],
        ] = {}

    @property
    def http(self) -> HTTP:
        return self._http

    async def start(
        self,
        consensus_id: ConsensusId,
        port: Optional[int],
        channel_manager: _ChannelManager,
    ) -> int:
        assert consensus_id not in self._servers

        fastapi = FastAPI()

        @fastapi.middleware("http")
        async def external_context(request: Request, call_next):
            # Check if we have an `Authorization: bearer <token>`
            # header and if so pass on the bearer token so every
            # developer doesn't have to do it themselves.
            #
            # TODO: consider making this a feature that
            # can be turned off via a kwarg passed when
            # decorating.
            bearer_token: Optional[str] = None

            authorization: Optional[str] = request.headers.get("Authorization")

            if authorization is not None:
                parts = authorization.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    bearer_token = parts[1]

            # Namespace this so that any other middleware doesn't
            # clash on `request.state`.
            request.state.reboot_external_context = ExternalContext(
                name=f"HTTP {request.method} '{request.url.path}'",
                channel_manager=channel_manager,
                bearer_token=bearer_token,
                # NOTE: WE DO NOT SET `app_internal_authorization` as
                # this context is _not_ meant to be app internal!  We
                # pass on the `bearer_token` above but otherwise this
                # must be considered _external_ because we have no
                # other authorization that Reboot is performing (a
                # developer might add their own, or just rely on the
                # authorization that they set up for their Reboot
                # servicers).
            )

            return await call_next(request)

        for api_route in self._http._api_routes:
            fastapi.add_api_route(
                api_route.path,
                api_route.endpoint,
                **api_route.kwargs,
            )

        config = uvicorn.Config(
            fastapi,
            host="0.0.0.0",
            port=port or 0,
            log_level="warning",
            reload=False,  # This is handled by Reboot.
            workers=1,
        )

        class Server(uvicorn.Server):
            """We need to override the installation of signal handlers as Reboot
            is already handling this itself.
            """

            @contextlib.contextmanager
            def capture_signals(self) -> Generator[None, None, None]:
                # Do nothing
                yield

        server = Server(config)

        async def uvicorn_run():
            try:
                assert server is not None
                await server.serve()
            except asyncio.CancelledError:
                raise
            except:
                import traceback
                traceback.print_exc()

        uvicorn_run_task = asyncio.create_task(uvicorn_run())

        self._servers[consensus_id] = (server, uvicorn_run_task)

        # Look up port if it wasn't passed.
        if port is None:
            while not server.started:
                await asyncio.sleep(0.1)
            assert len(server.servers) == 1
            assert len(server.servers[0].sockets) == 1
            return server.servers[0].sockets[0].getsockname()[1]
        else:
            return port

    async def stop(self, consensus_id: ConsensusId):
        if consensus_id in self._servers:
            server, uvicorn_run_task = self._servers[consensus_id]
            # NOTE: this is the recommended way to stop a uvicorn
            # server! Calling `uvicorn_run_task.cancel()` produces
            # gross stack traces.
            server.should_exit = True
            try:
                await uvicorn_run_task
            except:
                pass
            del self._servers[consensus_id]


class NodeWebFramework(WebFramework):

    def __init__(
        self,
        *,
        start: Callable[
            [ConsensusId, Optional[int], _ChannelManager],
            Awaitable[int],
        ],
        stop: Callable[[ConsensusId], Awaitable[None]],
    ):
        self._start = start
        self._stop = stop

    async def start(
        self,
        consensus_id: ConsensusId,
        port: Optional[int],
        channel_manager: _ChannelManager,
    ) -> int:
        return await self._start(consensus_id, port, channel_manager)

    async def stop(self, consensus_id: ConsensusId):
        await self._stop(consensus_id)
