# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

"""Checkpoint Store for Geneva Pipeline"""

import abc
import logging
import os
import tempfile
from collections.abc import Iterator
from enum import Enum

import attrs
import pyarrow as pa
from lance.file import LanceFileReader, LanceFileWriter
from pyarrow import fs

from geneva.config import ConfigBase

_LOG = logging.getLogger(__name__)


class CheckpointStore(abc.ABC):
    """Abstract class for checkpoint store, which is used to store intermediate results
      of Geneva pipelines.

    It is implemented as a key-value store of :class:`pyarrow.RecordBatch` objects.

    This is a lighter weight version of collections.abc.MutableMapping
    where we don't expose length or deletion operations
    """

    @abc.abstractmethod
    def __contains__(self, item: str) -> bool:
        pass

    @abc.abstractmethod
    def __getitem__(self, item: str) -> pa.RecordBatch:
        pass

    @abc.abstractmethod
    def __setitem__(self, key: str, value: pa.RecordBatch) -> None:
        pass

    @abc.abstractmethod
    def list_keys(self, prefix: str = "") -> Iterator[str]:
        """List all the available keys for check point."""

    @classmethod
    def from_uri(cls, uri: str) -> "CheckpointStore":
        """Construct a CheckpointStore from a URI."""
        if uri == "memory":
            return InMemoryCheckpointStore()
        try:
            return LanceCheckpointStore(uri)
        except Exception as e:
            raise ValueError(f"Invalid checkpoint store uri: {uri}") from e


class InMemoryCheckpointStore(CheckpointStore):
    """In memory checkpoint store for testing purposes."""

    def __init__(self) -> None:
        self._store = {}

    def __repr__(self) -> str:
        return self._store.__repr__()

    def __contains__(self, item: str) -> bool:
        return item in self._store

    def __getitem__(self, item: str) -> pa.RecordBatch:
        return self._store[item]

    def __setitem__(self, key: str, value: pa.RecordBatch) -> None:
        self._store[key] = value

    def list_keys(self, prefix: str = "") -> Iterator[str]:
        for key in self._store:
            if key.startswith(prefix):
                yield key


class LanceCheckpointStore(CheckpointStore):
    """
    Stores checkpoint data as Lance formatted files

    The API mimics a dictionary.

    NOTE: The dict keys are actual paths in a file system and can be vulnerable to
    filesystem traversal attacks.
    """

    def __init__(self, root: str) -> None:
        self.fs, self.path = fs.FileSystem.from_uri(root)  # type: ignore
        self.root = root

    def __contains__(self, key: str) -> bool:
        _LOG.debug("contains: %s", key)
        path = os.path.join(self.path, f"{key}.lance")
        info = self.fs.get_file_info(path)
        return info.type != fs.FileType.NotFound

    def __getitem__(self, key: str) -> pa.RecordBatch:
        _LOG.debug("get: %s", key)
        path = os.path.join(self.root, f"{key}.lance")
        reader = LanceFileReader(path)
        return reader.read_all().to_table().combine_chunks().to_batches()[0]

    def __setitem__(self, key: str, value: pa.RecordBatch) -> None:
        _LOG.debug("set: %s", key)
        path = os.path.join(self.root, f"{key}.lance")
        with LanceFileWriter(path, value.schema) as writer:
            writer.write_batch(value)

    def list_keys(self, prefix: str = "") -> Iterator[str]:
        _LOG.debug("list_keys: %s", prefix)
        selector = fs.FileSelector(os.path.join(self.path, prefix))
        for file in self.fs.get_file_info(selector):
            yield file.path.removeprefix(self.path).lstrip("/").rstrip(".lance")


class CheckpointMode(Enum):
    OBJECT_STORE = "object_store"

    # Store checkpoints in temporary files, for local development
    # and testing.
    # It can be shared between process, i.e., local ray actors.
    TEMPFILE = "tempfile"

    # for testing only
    IN_MEMORY = "in_memory"

    @staticmethod
    def from_str(s: str) -> "CheckpointMode":
        if isinstance(s, CheckpointMode):
            return s
        return CheckpointMode(s)


@attrs.define
class ObjectStoreCheckpointConfig(ConfigBase):
    path: str

    @classmethod
    def name(cls) -> str:
        return "object_store"

    def make(self) -> CheckpointStore:
        return LanceCheckpointStore(self.path)


@attrs.define
class CheckpointConfig(ConfigBase):
    mode: CheckpointMode = attrs.field(
        default=CheckpointMode.OBJECT_STORE, converter=CheckpointMode.from_str
    )

    object_store: ObjectStoreCheckpointConfig | None = attrs.field(default=None)

    @classmethod
    def name(cls) -> str:
        return "checkpoint"

    def make(self) -> CheckpointStore:
        match self.mode:
            case CheckpointMode.TEMPFILE:
                temp_dir = tempfile.mkdtemp()
                _LOG.info("Create checkpoint store on %s", temp_dir)
                return LanceCheckpointStore(temp_dir)
            case CheckpointMode.OBJECT_STORE:
                if self.object_store is None:
                    raise ValueError("CheckpointConfig::object_store is required")
                return LanceCheckpointStore(self.object_store.path)
            case CheckpointMode.IN_MEMORY:
                return InMemoryCheckpointStore()
            case _:
                raise ValueError(f"Unknown checkpoint mode {self.mode}")
