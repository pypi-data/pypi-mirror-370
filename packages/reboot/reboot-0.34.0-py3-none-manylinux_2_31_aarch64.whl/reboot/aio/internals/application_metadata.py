import aiofiles.os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from log.log import get_logger
from pathlib import Path
from rbt.v1alpha1 import application_metadata_pb2
from reboot.controller.application_config import ApplicationConfig
from rebootdev.aio.exceptions import InputError
from rebootdev.aio.types import ApplicationId
from rebootdev.consensus.service_descriptor_validator import (
    validate_descriptor_sets_are_backwards_compatible,
)
from typing import AsyncIterator

logger = get_logger(__name__)


@dataclass(frozen=True)
class ApplicationMetadata:
    """Manages per-Application metadata, which is stored outside of per-consensus state management."""

    # Directory below which the application stores state.
    state_directory: Path
    # The ApplicationId that metadata is being stored for.
    application_id: ApplicationId

    def application_state_directory(self) -> Path:
        return self.state_directory / self.application_id

    @asynccontextmanager
    async def _metadata(
        self
    ) -> AsyncIterator[application_metadata_pb2.ApplicationMetadata]:
        """A context manager that provides the current metadata for in-place update."""
        application_state_directory = self.application_state_directory()
        await aiofiles.os.makedirs(application_state_directory, exist_ok=True)

        metadata = application_metadata_pb2.ApplicationMetadata()
        async with aiofiles.open(
            application_state_directory / "__metadata", mode="a+b"
        ) as f:
            await f.seek(0)
            content = await f.read()
            if content:
                metadata.ParseFromString(content)

            yield metadata

            await f.seek(0)
            await f.truncate()
            await f.write(metadata.SerializeToString())
            await f.flush()

    async def validate_stable_consensus_count(
        self, consensus_count: int
    ) -> None:
        async with self._metadata() as metadata:
            if metadata.consensus_count == 0:
                metadata.consensus_count = consensus_count
            elif metadata.consensus_count != consensus_count:
                raise InputError(
                    "Cannot change the number of partitions for "
                    f"an application. There were "
                    f"{metadata.consensus_count}, and now there are "
                    f"{consensus_count}."
                )

    async def validate_schema_backwards_compatibility(
        self, config: ApplicationConfig
    ) -> None:
        file_descriptor_set = FileDescriptorSet()
        file_descriptor_set.ParseFromString(config.spec.file_descriptor_set)
        async with self._metadata() as metadata:
            if metadata.HasField('file_descriptor_set'):
                validate_descriptor_sets_are_backwards_compatible(
                    metadata.file_descriptor_set,
                    file_descriptor_set,
                )
            metadata.file_descriptor_set.CopyFrom(file_descriptor_set)
