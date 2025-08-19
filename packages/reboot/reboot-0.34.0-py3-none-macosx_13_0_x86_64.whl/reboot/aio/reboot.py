import asyncio
import os
import rebootdev.aio.tracing
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from log.log import get_logger
from pathlib import Path
from reboot.aio.http import WebFramework
from reboot.aio.internals.application_metadata import ApplicationMetadata
from reboot.aio.monitoring import monitor_event_loop_lag
from reboot.aio.multiprocessing import (
    initialize_multiprocessing_start_method_once,
)
from reboot.aio.servers import run_application_initializer
from reboot.controller.application_config import ApplicationConfig
from reboot.controller.application_config_trackers import (
    LocalApplicationConfigTracker,
)
from reboot.controller.config_extractor import LocalConfigExtractor
from reboot.controller.consensus_managers import LocalConsensusManager
from reboot.controller.consensuses import Consensus
from reboot.controller.placement_planner import PlacementPlanner
from reboot.naming import get_local_application_id
from rebootdev.aio.auth.token_verifiers import TokenVerifier
from rebootdev.aio.contexts import EffectValidation
from rebootdev.aio.external import ExternalContext, InitializeContext
from rebootdev.aio.internals.channel_manager import _ChannelManager
from rebootdev.aio.placement import PlanOnlyPlacementClient
from rebootdev.aio.resolvers import DirectResolver
from rebootdev.aio.servicers import Serviceable, Servicer
from rebootdev.aio.tracing import function_span
from rebootdev.aio.types import ConsensusId, ServiceName, StateRef
from rebootdev.run_environments import in_nodejs, on_cloud
from rebootdev.settings import (
    ENVVAR_LOCAL_ENVOY_MODE,
    ENVVAR_LOCAL_ENVOY_USE_TLS,
)
from typing import Awaitable, Callable, Optional, overload

# Picked so that we don't get a huge amount of load on the system, but are
# more likely to discover any multi-consensus-related bugs in unit tests.
#
# Note that this number does NOT influence the number of partitions in a Reboot
# Cloud deployment, since it gets its `ApplicationConfig` from elsewhere. It may
# still follow `reboot.controller.plan_makers.DEFAULT_NUM_PARTITIONS`.
DEFAULT_NUM_PARTITIONS = 4

logger = get_logger(__name__)


@dataclass(kw_only=True)
class ApplicationRevision:
    config: ApplicationConfig


class Reboot:

    def __init__(
        self,
        *,
        application_name: Optional[str] = None,
        state_directory: Optional[Path] = None,
        # When starting a new consensus, we don't want to start tracing
        # in that process for the 'Reboot' class.
        # A separate tracing context will be started in the
        # 'consensus_managers.py'.
        initialize_tracing: bool = True,
    ):
        """
        state_directory: directory below which applications will store state.
        """
        # Monitor the "parent" event loop; this is in addition to similar
        # monitoring that gets set up for the consensus processes.
        self._monitor_event_loop_lag_task = asyncio.create_task(
            monitor_event_loop_lag()
        )

        self._local_envoy_tls: Optional[bool] = None
        self._local_envoy_picked_port: Optional[int] = None

        # We use 'multiprocessing' to start a new consensus only, but that is
        # applicable only when running in Python. When running in Node.js, we
        # call back to the Node.js to start a new consensus and there are no
        # need to initialize 'multiprocessing' and start a 'forkserver'.
        # See https://github.com/reboot-dev/mono/issues/4420
        if not in_nodejs():
            initialize_multiprocessing_start_method_once()

        self._application_name = application_name or "Reboot"
        self._application_id = get_local_application_id(self._application_name)

        # Tracing can only start after multiprocessing has been initialized,
        # because tracing spawns threads.
        if initialize_tracing:
            rebootdev.aio.tracing.start(process_name=self._application_name)

        if state_directory is None:
            # We create a single temporary directory that we put each
            # application's subdirectories within to make it easier
            # to clean up all of them. Note that we explicitly _do not_
            # want to clean up each state manager's directory after
            # deleting its corresponding consensus because it is possible
            # that the same consensus (i.e., a consensus with the same
            # name) will be (re)created in the future and it needs its
            # directory!
            self._tmp_directory = tempfile.TemporaryDirectory()
            state_directory = Path(self._tmp_directory.name)
        elif not state_directory.is_dir():
            raise ValueError(
                f"Base directory at '{state_directory}' "
                "does not exist, or is not a directory."
            )

        self._application_metadata = ApplicationMetadata(
            state_directory, self._application_id
        )
        self._consensus_manager = LocalConsensusManager(
            self._application_metadata
        )
        self._config_tracker = LocalApplicationConfigTracker()
        self._config_extractor = LocalConfigExtractor(self._application_id)

        self._placement_planner = PlacementPlanner(
            self._config_tracker,
            self._consensus_manager,
            # Let the PlacementPlanner choose its own port locally, in
            # case we are running multiple PlacementPlanners on the
            # same host (for example, running multiple unit tests in
            # parallel).
            '127.0.0.1:0'
        )

        self._consensus_manager.register_placement_planner_address(
            self._placement_planner.address()
        )

        self._placement_client = PlanOnlyPlacementClient(
            self._placement_planner.address()
        )
        self._resolver = DirectResolver(self._placement_client)
        self._channel_manager = _ChannelManager(
            self._resolver,
            # Not using a secure channel, since this will all be localhost
            # traffic that does not flow through the gateway, which is the
            # only place we do `localhost.direct` SSL termination.
            secure=False,
        )

    async def start(self):
        await self._placement_planner.start()
        await self._placement_client.start()
        await self._resolver.start()

    def create_external_context(
        self,
        *,
        name: str,
        bearer_token: Optional[str] = None,
        idempotency_seed: Optional[uuid.UUID] = None,
        idempotency_required: bool = False,
        idempotency_required_reason: Optional[str] = None,
        app_internal: bool = False,
    ) -> ExternalContext:
        """ Create an `ExternalContext` for use in tests.

        app_internal: When true, the context is being used to
          represent a client internal to the application: essentially, to mock
          traffic from another servicer in the same application. A
          per-application secret will be passed as a header in the call.
        """
        app_internal_authorization: Optional[str] = None
        if app_internal:
            app_internal_authorization = self._consensus_manager.app_internal_api_key_secret
            if app_internal_authorization is None:
                raise ValueError(
                    "Application not found. Did you call `Reboot.up`?"
                )
        return ExternalContext(
            name=name,
            channel_manager=self._channel_manager,
            bearer_token=bearer_token,
            idempotency_seed=idempotency_seed,
            idempotency_required=idempotency_required,
            idempotency_required_reason=idempotency_required_reason,
            app_internal_authorization=app_internal_authorization,
        )

    def create_initialize_context(
        self,
        *,
        name: str,
        bearer_token: Optional[str] = None,
        idempotency_seed: Optional[uuid.UUID] = None,
    ) -> ExternalContext:
        """ Create an `ExternalContext` for use in tests.

        app_internal: When true, the context is being used to
          represent a client internal to the application: essentially, to mock
          traffic from another servicer in the same application. A
          per-application secret will be passed as a header in the call.
        """
        # Initializers are application-internal code, and should
        # authenticate as such.
        #
        # TODO(rjh, stuhood): when it becomes possible to call other
        #                     applications during `initialize`,
        #                     ensure that these credentials don't
        #                     get forwarded to other applications.
        app_internal_authorization: Optional[str] = None
        if bearer_token is None:
            app_internal_authorization = self._consensus_manager.app_internal_api_key_secret
            assert app_internal_authorization is not None

        return InitializeContext(
            name=name,
            channel_manager=self._channel_manager,
            bearer_token=bearer_token,
            idempotency_seed=idempotency_seed,
            idempotency_required=True,
            idempotency_required_reason=
            'Calls to mutators from within your initialize function must use idempotency',
            app_internal_authorization=app_internal_authorization,
        )

    @overload
    async def up(
        self,
        *,
        revision: Optional[ApplicationRevision] = None,
    ) -> ApplicationRevision:
        ...

    @overload
    async def up(
        self,
        *,
        servicers: list[type[Servicer]],
        # A legacy gRPC servicer type can't be more specific than `type`,
        # because legacy gRPC servicers (as generated by the gRPC `protoc`
        # plugin) do not share any common base class other than `object`.
        legacy_grpc_servicers: Optional[list[type]] = None,
        web_framework: WebFramework,
        token_verifier: Optional[TokenVerifier] = None,
        initialize: Optional[Callable[[ExternalContext],
                                      Awaitable[None]]] = None,
        initialize_bearer_token: Optional[str] = None,
        local_envoy: bool = False,
        local_envoy_port: int = 0,
        local_envoy_tls: Optional[bool] = None,
        partitions: Optional[int] = None,
        effect_validation: Optional[EffectValidation] = None,
        in_process: bool = False,
    ) -> ApplicationRevision:
        ...

    @function_span()
    async def up(
        self,
        *,
        servicers: Optional[list[type[Servicer]]] = None,
        # A legacy gRPC servicer type can't be more specific than `type`,
        # because legacy gRPC servicers (as generated by the gRPC `protoc`
        # plugin) do not share any common base class other than `object`.
        legacy_grpc_servicers: Optional[list[type]] = None,
        web_framework: Optional[WebFramework] = None,
        token_verifier: Optional[TokenVerifier] = None,
        initialize: Optional[Callable[[ExternalContext],
                                      Awaitable[None]]] = None,
        initialize_bearer_token: Optional[str] = None,
        local_envoy: bool = False,
        local_envoy_port: int = 0,
        local_envoy_tls: Optional[bool] = None,
        partitions: Optional[int] = None,
        effect_validation: Optional[EffectValidation] = None,
        in_process: bool = False,
        revision: Optional[ApplicationRevision] = None,
    ) -> ApplicationRevision:
        """
        Bring up this in-memory Reboot application.

        Callers may specify a list of servicers to bring up, or they may provide
        an `ApplicationRevision` produced by a previous call to `up()` to restore
        the application to a previous revision.

        Making multiple calls to `up()` is supported, but only if `down()` is
        called in between. The different `up()` calls can use different
        configurations, allowing tests to modify an application's configuration.

        in_process: If False, bring up Reboot in a separate process - to prevent
        user-facing log spam from gRPC. gRPC has an issue
        [#25364](https://github.com/grpc/grpc/issues/25364), open since Feb
        2021, that logs errant BlockingIOErrors if gRPC is in a multi-process
        Python context. If True, servicers are brought up in the current process
        and users will have to know to just ignore BlockingIOErrors.

        local_envoy: If True, bring up a LocalEnvoy proxy for our Reboot
        services.

        local_envoy_port: port on which to connect to Envoy, defaults to 0
        (picked dynamically by the OS).

        effect_validation: sets EffectValidation for these servicers. By
        default, effect validation is:
          1. Enabled in unit tests, but controllable by this argument.
          2. Enabled in `rbt dev run`, but controllable via the
             `--effect-validation` flag.
          3. Disabled in production.

        partitions: the number of logical partitions (also known as "shards")
          of state machines to create. Must be stable for one application over
          time.
        """
        # There should be no code path where this is run on Reboot Cloud.
        assert not on_cloud()

        if len(await self._config_tracker.get_application_configs()) > 0:
            raise ValueError(
                "This application is already up; if you'd like to update it "
                "call `down()` before calling `up()` again"
            )

        if revision is not None:
            if revision.config.application_id() != self._application_id:
                raise ValueError(
                    "Revision config is for a different application than the one "
                    "run by this Reboot instance"
                )

            if servicers is not None or legacy_grpc_servicers is not None:
                raise ValueError(
                    "Only pass one of ('servicers' and/or 'legacy_grpc_servicers') "
                    "or 'revision'"
                )
            elif partitions is not None:
                raise ValueError(
                    "Passing 'partitions' is not valid when passing 'revision'"
                )

        if servicers is None and legacy_grpc_servicers is None and revision is None:
            raise ValueError(
                "One of 'servicers', 'legacy_grpc_servicers', or 'revision' must "
                "be passed"
            )

        if servicers is not None and web_framework is None:
            raise ValueError(
                "Expecting 'web_framework' when passing 'servicers'"
            )

        if local_envoy:
            # 'Reboot' is part of 'Application', which users will call to run
            # the backend, so we don't want to override the environment variable
            # if it's already set by 'rbt dev run' or 'rbt serve'.
            if os.environ.get(ENVVAR_LOCAL_ENVOY_MODE) is None:
                if shutil.which('docker') is not None:
                    # We prefer to use Docker to run the local Envoy, since that
                    # way we're confident that its version matches exactly what
                    # we expect.
                    os.environ[ENVVAR_LOCAL_ENVOY_MODE] = 'docker'
                elif shutil.which('envoy') is not None:
                    # If Docker isn't available, for example on GitHub MacOS X
                    # actions runners that are used in CI, we are able to fall
                    # back to a locally-installed Envoy executable.
                    os.environ[ENVVAR_LOCAL_ENVOY_MODE] = 'executable'
                else:
                    raise ValueError(
                        "You must have either Envoy or Docker installed to run "
                        "Reboot with `local_envoy=True`. Neither was found."
                    )

            tls_envvar = os.environ.get(ENVVAR_LOCAL_ENVOY_USE_TLS)
            if local_envoy_tls is not None:
                if tls_envvar is not None:
                    raise ValueError(
                        "Local envoy TLS setting was provided from both env "
                        f"var ('{ENVVAR_LOCAL_ENVOY_USE_TLS}') and parameter "
                        "('local_envoy_tls'); please set only one of these"
                    )
            else:
                if tls_envvar is not None:
                    local_envoy_tls = tls_envvar.lower() == "true"
                else:
                    # No TLS preference given; default to not using TLS.
                    local_envoy_tls = False

            assert local_envoy_tls is not None
            self._local_envoy_tls = local_envoy_tls

            if (
                local_envoy_port <= 0 and
                self._local_envoy_picked_port is not None
            ):
                # If we had a port that was picked by Envoy in a
                # previous run, and the user didn't specify differently,
                # reuse that port. This is useful in tests, because it
                # allows a previous `ExternalContext` to stay valid
                # between simulated restarts of the backend. Reusing the
                # port is safe, since odds of the ephemeral port having
                # already been reused are very low; see:
                #   https://dataplane.org/analysis/ephemeralports.html
                local_envoy_port = self._local_envoy_picked_port

        # Determine "serviceables" from the set of servicers and
        # legacy gRPC servicers after first deduplicating the
        # servicers and legacy gRPC servicers. We deduplicate because
        # we'll often have libraries depending on libraries depending
        # on servicers and it's not reasonable to expect the user to
        # deduplicate the list themselves.
        servicers = list(set(servicers)) if servicers is not None else None
        legacy_grpc_servicers = list(
            set(legacy_grpc_servicers)
        ) if legacy_grpc_servicers is not None else None

        serviceables: list[Serviceable] = []

        for servicer in servicers or []:
            serviceables.append(Serviceable.from_servicer_type(servicer))
        for legacy_grpc_servicer in legacy_grpc_servicers or []:
            serviceables.append(
                Serviceable.from_servicer_type(legacy_grpc_servicer)
            )

        # To ensure we only use `serviceables` at this point and
        # prevent accidentally using `servicers` or
        # `legacy_grpc_servicers` we delete them (which mypy should
        # also catch).
        del servicers
        del legacy_grpc_servicers

        if len(serviceables) > 0:
            # We can only host each service once in a Reboot application.
            service_names: set[ServiceName] = set()
            for serviceable in serviceables:
                for service_name in serviceable.service_names():
                    if service_name in service_names:
                        raise ValueError(
                            f"Servicer '{service_name}' was requested twice"
                        )

            assert web_framework is not None

            self._consensus_manager.register_revision(
                serviceables=serviceables,
                web_framework=web_framework,
                token_verifier=token_verifier,
                in_process=in_process,
                local_envoy=local_envoy,
                local_envoy_port=local_envoy_port,
                local_envoy_use_tls=self._local_envoy_tls or False,
                effect_validation=effect_validation,
            )

            partitions = partitions or DEFAULT_NUM_PARTITIONS
            config = self._config_extractor.config_from_serviceables(
                serviceables,
                # NOTE: Consensuses are exposed to users as partitions.
                consensuses=partitions,
            )
            await self._application_metadata.validate_schema_backwards_compatibility(
                config
            )
            revision = ApplicationRevision(config=config)

        assert revision is not None

        # This addition will trigger a new plan being made: then, wait for it
        # to have been observed.
        await self._config_tracker.add_config(revision.config)
        await self._wait_for_local_plan_sync()

        if local_envoy:
            # Record the port this application is running on, so that if
            # we restart the application it can be restarted on the same
            # port.
            self._local_envoy_picked_port = self.envoy_port()

        # Handle the initialize function if present.
        if initialize is not None:
            await run_application_initializer(
                application_id=revision.config.application_id(),
                initialize=initialize,
                context=self.create_initialize_context(
                    name='initialize',
                    bearer_token=initialize_bearer_token,
                    # We pass a `seed` so that we can
                    # re-execute `initialize` idempotently!
                    idempotency_seed=uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        'anonymous.rbt.dev',
                    ),
                )
            )

        return revision

    def url(self, path: str = '') -> str:
        """A URL to use to connect to the running Reboot application.

        This method is only supported when `up(..., local_envoy=True)`.
        """
        if self._local_envoy_tls:
            return self.https_localhost_direct_url(path)

        return self.http_localhost_url(path)

    def https_localhost_direct_url(self, path: str = '') -> str:
        assert self._local_envoy_tls
        return f"https://{self.localhost_direct_endpoint()}{path}"

    def localhost_direct_endpoint(self) -> str:
        """Returns the Envoy proxy endpoint."""
        assert self._local_envoy_tls
        return f'dev.localhost.direct:{self.envoy_port()}'

    def http_localhost_url(self, path: str = '') -> str:
        assert not self._local_envoy_tls
        return f'http://localhost:{self.envoy_port()}{path}'

    def envoy_port(self) -> int:
        """Returns the Envoy proxy port."""
        envoy = self._consensus_manager.local_envoy

        if envoy is None:
            raise ValueError(
                "No local Envoy was launched; did you forget to pass "
                "'local_envoy=True'?"
            )

        return envoy.port

    @rebootdev.aio.tracing.function_span()
    async def _wait_for_local_plan_sync(self) -> None:
        """Waits for our placement client to have seen the most recent plan.

        NOTE: This is not equivalent to having waited for _all_ clients to have
        seen the most recent version, but should be sufficient for most tests.
        """
        plan_version = self._placement_planner.current_version
        assert plan_version is not None
        await self._placement_client.wait_for_version(plan_version)

    async def unique_consensuses(
        self,
        state_ref_1: StateRef,
        state_ref_2: StateRef,
    ) -> tuple[ConsensusId, ConsensusId]:
        """Given two StateRefs, look up their unique owning consensuses.

        Fails if both StateRefs are owned by the same consensus.
        """
        application_configs = await self._config_tracker.get_application_configs(
        )
        if len(application_configs) != 1:
            # TODO: See https://github.com/reboot-dev/mono/issues/3356.
            raise ValueError(
                "Only supported when a single application is running."
            )
        application_id = next(iter(application_configs.keys()))
        consensus_id_1 = self._placement_client.consensus_for_actor(
            application_id,
            state_ref_1,
        )
        consensus_id_2 = self._placement_client.consensus_for_actor(
            application_id,
            state_ref_2,
        )
        assert consensus_id_1 != consensus_id_2, (
            f"{state_ref_1=} and {state_ref_2=} are hosted by the same consensus: "
            f"{consensus_id_1}"
        )
        return consensus_id_1, consensus_id_2

    async def consensus_stop(self, consensus_id: ConsensusId) -> Consensus:
        return await self._consensus_manager.consensus_stop(consensus_id)

    async def consensus_start(self, consensus: Consensus) -> None:
        # Restart the consensus.
        await self._consensus_manager.consensus_start(consensus)
        # TODO: We need to poke the ConfigTracker to tell the
        # PlacementPlanner to make a new plan after a consensus has changed
        # addresses. See https://github.com/reboot-dev/mono/issues/3356
        # about removing some of this complexity for local runs.
        await self._config_tracker.refresh()
        await self._wait_for_local_plan_sync()

    async def stop(self) -> None:
        """Bring down all servicers and shut down the Reboot instance such
        that no more servicers can be brought up. """
        try:
            await self.down()
        finally:
            try:
                await self._resolver.stop()
            finally:
                await self._placement_planner.stop()

    @rebootdev.aio.tracing.function_span()
    async def down(self) -> None:
        """Bring down this Reboot application."""
        # Delete all configs so that the PlacementPlanner will bring down
        # all consensuses.
        assert len(await self._config_tracker.get_application_configs()) <= 1
        await self._config_tracker.delete_all_configs()
        await self._wait_for_local_plan_sync()
        rebootdev.aio.tracing.force_flush()
