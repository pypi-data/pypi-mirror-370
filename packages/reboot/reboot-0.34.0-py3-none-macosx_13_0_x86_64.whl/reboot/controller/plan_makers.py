import math
import time
from log.log import get_logger
from rbt.v1alpha1 import placement_planner_pb2
from reboot.aio.servers import _ServiceServer
from reboot.controller.application_config import ApplicationConfig
from reboot.naming import make_consensus_id
from rebootdev.aio.exceptions import InputError
from rebootdev.aio.types import ServiceName, StateTypeName
from typing import Iterable, Optional

logger = get_logger(__name__)

# The default number of consensuses must remain 1, to remain backwards
# compatible with existing applications - adding more consensuses is a
# breaking change.
DEFAULT_NUM_CONSENSUSES = 1

_NUM_BYTE_VALUES = 256


def validate_num_consensuses(num_consensuses: int, description: str) -> None:
    if num_consensuses > _NUM_BYTE_VALUES:
        raise InputError(
            f"'{description}' must be less than or equal to "
            f"{_NUM_BYTE_VALUES}; got {num_consensuses}."
        )
    if not math.log2(num_consensuses).is_integer():
        raise InputError(
            f"'{description}' must be a power of 2; got {num_consensuses}."
        )


def _shard_first_keys(num_consensuses: int) -> list[bytes]:
    validate_num_consensuses(
        num_consensuses, "ApplicationConfig.spec.consensuses"
    )
    shard_size = _NUM_BYTE_VALUES // num_consensuses
    # The first shard always begins at the very beginning of the key range.
    return [b""] + [bytes([i * shard_size]) for i in range(1, num_consensuses)]


class PlanMaker:
    """
    Logic to construct a placement Plan based on a set of currently valid
    ApplicationConfigs. Designed to be extendable for different Plan structures.
    """

    last_version: Optional[int] = None

    def make_plan(
        self,
        application_configs: Iterable[ApplicationConfig],
    ) -> placement_planner_pb2.Plan:
        """
        Construct a Plan for consensuses that will serve the given list of
        ApplicationConfigs.
        """
        applications: list[placement_planner_pb2.Plan.Application] = []
        for application_config in application_configs:
            application_id = application_config.application_id()
            num_consensuses = (
                application_config.spec.consensuses
                if application_config.spec.HasField('consensuses') else
                DEFAULT_NUM_CONSENSUSES
            )

            # NOTE: We are deliberately using a `list` here instead of a `set`
            # to avoid issues with change of ordering. Some tests rely on the
            # ordering and `set` order elements internally by hash value, which
            # is not stable between platforms.
            unique_service_names: list[ServiceName] = []
            state_type_and_service_name_pairs: list[tuple[StateTypeName,
                                                          ServiceName]] = []
            for state in application_config.spec.states:
                state_type_name = StateTypeName(state.state_type_full_name)
                for service_full_name in state.service_full_names:
                    service_name = ServiceName(service_full_name)
                    if service_name in unique_service_names:
                        logger.warning(
                            "Service name '%s' is duplicated in application '%s'",
                            service_name,
                            application_id,
                        )
                        continue
                    # Ignore system services which exist on every consensus.
                    if service_name in _ServiceServer.SYSTEM_SERVICE_NAMES:
                        continue
                    unique_service_names.append(service_name)
                    state_type_and_service_name_pairs.append(
                        (state_type_name, service_name)
                    )
            for legacy_grpc_service_full_name in application_config.spec.legacy_grpc_service_full_names:
                legacy_grpc_service_name = ServiceName(
                    legacy_grpc_service_full_name
                )
                if legacy_grpc_service_name in unique_service_names:
                    logger.warning(
                        "Service name '%s' is duplicated in application '%s'",
                        legacy_grpc_service_name,
                        application_id,
                    )
                    continue
                # Ignore system services which exist on every consensus.
                if legacy_grpc_service_name in _ServiceServer.SYSTEM_SERVICE_NAMES:
                    continue
                unique_service_names.append(legacy_grpc_service_name)
                state_type_and_service_name_pairs.append(
                    (
                        StateTypeName(
                            ""
                        ),  # Legacy gRPC service names have no state name.
                        legacy_grpc_service_name
                    )
                )

            # One consensus per shard.
            applications.append(
                placement_planner_pb2.Plan.Application(
                    id=application_id,
                    services=[
                        placement_planner_pb2.Plan.Application.Service(
                            full_name=service_name,
                            state_type_full_name=state_type_name,
                        ) for state_type_name, service_name in
                        state_type_and_service_name_pairs
                    ],
                    # We'll only have one shard for t
                    # he whole application.
                    shards=[
                        placement_planner_pb2.Plan.Application.Shard(
                            # The ID must be unique across all shards in the
                            # system, so we prefix it with the application ID.
                            # By using a shard index suffix with 9 digits we can
                            # have up to 1 billion shards per application, which
                            # should be a comfortable overkill.
                            id=f"{application_id}-s{shard_index:09d}",
                            consensus_id=make_consensus_id(
                                application_id=application_id,
                                # For now we'll just have one consensus per shard.
                                consensus_index=shard_index,
                            ),
                            range=placement_planner_pb2.Plan.Application.Shard.
                            KeyRange(first_key=shard_first_key),
                        ) for shard_index, shard_first_key in
                        enumerate(_shard_first_keys(num_consensuses))
                    ]
                )
            )

        return placement_planner_pb2.Plan(
            version=self.get_version(),
            applications=applications,
        )

    def get_version(self) -> int:
        """
        Return a valid version number that is (expected to be) greater than
        whatever was previously returned or used.
        We use a timestamp (in ns from epoch) to ensure that version numbers
        increase, and further verify that time has not somehow gone backwards.
        """
        timestamp = time.time_ns()
        if self.last_version is not None and timestamp <= self.last_version:
            raise RuntimeError(
                f'Time is not moving forward as expected! '
                f'New timestamp {timestamp} is not after '
                f'old timestamp {self.last_version}.'
            )
        self.last_version = timestamp
        return timestamp
