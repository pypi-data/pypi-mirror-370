import asyncio
import grpc
import rebootdev.aio.tracing
from concurrent import futures
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from log.log import ERROR, get_logger
from rbt.v1alpha1 import (
    placement_planner_pb2,
    placement_planner_pb2_grpc,
    sidecar_pb2,
)
from reboot.controller.application_config import ApplicationConfig
from reboot.controller.application_config_trackers import (
    ApplicationConfigTracker,
)
from reboot.controller.consensus_managers import ConsensusManager
from reboot.controller.consensuses import Consensus
from reboot.controller.plan_makers import PlanMaker
from reboot.naming import ApplicationId
from rebootdev.aio.types import ConsensusId, RevisionNumber
from typing import AsyncGenerator, Awaitable, Callable, Optional

logger = get_logger(__name__)
# TODO(rjh, benh): set up a logging system that allows us to increase
# the verbosity level of the logs by environment variable.
logger.setLevel(ERROR)


class PlacementPlanner(placement_planner_pb2_grpc.PlacementPlannerServicer):

    def __init__(
        self, config_tracker: ApplicationConfigTracker,
        consensus_manager: ConsensusManager, address: str
    ) -> None:
        self.plan_maker = PlanMaker()
        self.config_tracker = config_tracker
        self.consensus_manager = consensus_manager
        # Use pubsub queues to be sure to notify all plan listeners whenever
        # there's a new plan.
        self.listener_queues: set[asyncio.Queue[
            placement_planner_pb2.ListenForPlanResponse]] = set()

        # Public set of callbacks that are called with the new PlanWithLocations
        # whenever one becomes available. Clients that want callbacks should add
        # their callbacks directly to this set.
        self.plan_change_callbacks: set[
            Callable[[placement_planner_pb2.ListenForPlanResponse],
                     Awaitable[None]]] = set()

        self._started = False

        self._server = grpc.aio.server(
            futures.ThreadPoolExecutor(max_workers=10)
        )

        placement_planner_pb2_grpc.add_PlacementPlannerServicer_to_server(
            self, self._server
        )

        self._port = self._server.add_insecure_port(address)
        self._host = address.split(':')[0]

        # Get notified when we need a new plan, either because the set of
        # ApplicationConfigs has changed or because consensuses have moved.
        self.config_tracker.on_configs_change(self.make_plan)

        self.current_version: Optional[int] = None
        self.current_plan_with_consensuses: Optional[
            placement_planner_pb2.ListenForPlanResponse] = None

    async def start(self) -> None:
        """
        Start a gRPC server at the given address to host the ListenForPlan
        endpoint.
        """
        await self.make_plan()
        await self._server.start()
        self._started = True
        logger.info(f"PlacementPlanner server started on port {self._port}")

    def port(self) -> int:
        return self._port

    def address(self) -> str:
        return f'{self._host}:{self._port}'

    async def stop(self) -> None:
        """Stop the gRPC server that was started."""
        if self._started:
            await self._server.stop(grace=None)
            logger.info('PlacementPlanner server stopped')

    @rebootdev.aio.tracing.function_span()
    async def make_plan(self) -> None:
        """
        Generate a new placement plan based on the currently valid set of
        ApplicationConfigs, update cluster resources to match the updated plan,
        and send the updated plan information out to all subscribed listeners.
        """
        application_configs: dict[
            ApplicationId, ApplicationConfig
        ] = await self.config_tracker.get_application_configs()
        logger.info(
            f'Making new plan based on {len(application_configs)} application '
            f'configs: {list(application_configs.keys())}'
        )

        new_plan = self.plan_maker.make_plan(application_configs.values())

        ###
        # Create the consensuses before disseminating the plan and the
        # information about the consensuses together.
        #
        # TODO(rjh, stuhood): instead of creating consensuses here, disseminate
        #                     the plan (including info about the consensuses
        #                     that are _planned_ to exist), and have that
        #                     trigger a different process that creates the
        #                     consensuses? Think: Kubernetes-style design, with
        #                     many controllers working together to refine
        #                     high-level information into finer-grained
        #                     information and actions.

        # Combine the Plan and the ApplicationConfigs into Consensuses. The same
        # consensus may host many shards, so we may see it many times - use a
        # dict to implicitly de-duplicate so that each consensus is listed only
        # once.
        consensuses: dict[ConsensusId, Consensus] = {}
        for application in new_plan.applications:
            assert application.id != ""
            application_config = application_configs[application.id]
            file_descriptor_set = FileDescriptorSet()
            file_descriptor_set.ParseFromString(
                application_config.spec.file_descriptor_set
            )
            for shard in application.shards:
                consensuses[shard.consensus_id] = Consensus(
                    id=shard.consensus_id,
                    shards=[
                        sidecar_pb2.ShardInfo(
                            shard_id=shard.id,
                            shard_first_key=shard.range.first_key,
                        )
                    ],
                    container_image_name=application_config.spec.
                    container_image_name,
                    namespace=application_config.metadata.namespace,
                    service_names=application_config.spec.service_names,
                    file_descriptor_set=file_descriptor_set,
                    application_id=application.id,
                    revision_number=RevisionNumber(
                        application_config.spec.revision_number
                    ),
                )

        logger.info(
            f'Plan version {new_plan.version} consensuses: {consensuses.keys()}'
        )

        consensus_protos = await self.consensus_manager.set_consensuses(
            list(consensuses.values()),
        )

        assert len(consensus_protos) == len(consensuses)

        self.current_version = new_plan.version
        self.current_plan_with_consensuses = placement_planner_pb2.ListenForPlanResponse(
            plan=new_plan,
            consensuses=consensus_protos,
        )

        for queue in self.listener_queues:
            await queue.put(self.current_plan_with_consensuses)

        # Execute all callbacks for everyone.
        await asyncio.gather(
            *[
                callback(self.current_plan_with_consensuses)
                for callback in self.plan_change_callbacks
            ]
        )

        logger.info(f'Plan version {new_plan.version} active')

    async def ListenForPlan(
        self, request: placement_planner_pb2.ListenForPlanRequest, context
    ) -> AsyncGenerator[placement_planner_pb2.ListenForPlanResponse, None]:
        """
        Serve the current plan immediately, then send an update every time a
        new plan is generated.
        """
        queue: asyncio.Queue[placement_planner_pb2.ListenForPlanResponse
                            ] = asyncio.Queue()
        self.listener_queues.add(queue)

        if self.current_plan_with_consensuses is not None:
            # Clients should immediately get the current plan.
            await queue.put(self.current_plan_with_consensuses)

        while True:
            next_response = await queue.get()
            try:
                yield next_response
            except GeneratorExit:
                # When the client disconnects, we will eventually get a
                # GeneratorExit thrown. We should clean up the state associated
                # with this client before returning.
                self.listener_queues.remove(queue)
                return
