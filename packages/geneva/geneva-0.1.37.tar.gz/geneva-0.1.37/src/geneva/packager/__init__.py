# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# module for packaging workspace and UDFs
# also data spec for persisting the artifacts

import abc
import base64
import hashlib
import json
import logging
from pathlib import Path

import attrs
from pyarrow.fs import FileSystem, FileType
from typing_extensions import Self

import geneva.cloudpickle as cloudpickle
from geneva.config import ConfigBase
from geneva.packager.zip import WorkspaceZipper
from geneva.transformer import UDF

_LOG = logging.getLogger(__name__)


class UDFBackend(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def packager(cls) -> "UDFPackager":
        """Return the packager for this backend."""

    def to_bytes(self) -> bytes:
        return json.dumps(attrs.asdict(self)).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        return cls(**json.loads(data.decode()))


@attrs.define
class UDFSpec:
    """Specification for a user-defined function.

    This is an holder of an arbitrary user-defined function,
    which can use an backend for marshalling.

    The most common is likely Docker + some kind of workspace
    persistence. However, we want to support more than just
    Docker, so we create this "out most" abstraction to allow
    for more flexibility.
    """

    # the name of the udf
    name: str = attrs.field()

    @name.validator
    def _validate_name(self, attribute, value) -> None:
        if not value:
            raise ValueError("UDF name must not be empty.")
        if len(value) < 1:
            raise ValueError("UDF name must be at least 1 character long.")

    # the packaging backend for the udf
    backend: str = attrs.field()

    @backend.validator
    def _validate_backend(self, attribute, value) -> None:
        backend_names = [cls.__name__ for cls in UDFBackend.__subclasses__()]
        unique_backend_names = set(backend_names)

        # ruff: noqa: ERA001
        # TODO - deduplication not working right sometimes
        # if len(backend_names) != len(unique_backend_names):
        #     duplicates = []
        #     while unique_backend_names:
        #         name = backend_names.pop()
        #         if name not in unique_backend_names:
        #             duplicates.append(name)
        #         else:
        #             unique_backend_names.discard(name)
        #     raise ValueError(
        #         "Duplicate backend names found, "
        #         "please don't define the same backend name twice."
        #         f"\nDuplicates: {duplicates}"
        #     )

        if value not in unique_backend_names:
            raise ValueError(f"Unknown backend: {value}")

    udf_payload: bytes = attrs.field()

    # the payload for the runner -- This is a HACK for allowing phalanx knowing
    # how to dispatch the UDF job. Make sure changes here are compatible to
    # parsing in phalanx.
    runner_payload: bytes | None = attrs.field(default=None)

    @classmethod
    def udf_from_spec(cls, data) -> UDF:
        # TODO: load the spec and find the backend,
        # then call the packager to do the next level unmarshalling
        pass


@attrs.define
class DockerUDFSpecV1(UDFBackend):
    """Specification for a user-defined function that runs in a Docker container.
    -- Version 1

    In this packaging spec, the python interpreter is assumed to be correctly
    setup in the container, and the user-defined function is expected to load
    using cloudpickle. With the option of downloading additional workspace
    files from a remote location (S3, GCS, etc).
    """

    # the image to run the udf in
    image: str = attrs.field()

    # the tag of the image
    tag: str | None = attrs.field()

    # spec from https://docs.docker.com/reference/cli/docker/image/tag/#description
    @tag.validator
    def _validate_tag(self, attribute, value: str | None) -> None:
        if value is None:
            return
        if len(value) > 128:
            raise ValueError("Tag must be less than 128 characters.")
        if not all(c.isalpha() or c.isnumeric or c in {"_", ".", "-"} for c in value):
            raise ValueError("Tag must be valid alphanumeric.")

    # optionally have a zip of the workspace and store it separately
    # this should be the path to the zip file on (S3, GCS, etc)
    workspace_zip: str | None = attrs.field()

    # the checksum of the workspace zip
    workspace_checksum: str | None = attrs.field()

    @workspace_checksum.validator
    def _validate_workspace_checksum(self, attribute, value) -> None:
        if self.workspace_zip and not value:
            raise ValueError(
                "Workspace checksum must not be empty when a workspace is provided."
            )

    # the udf pickle to run
    udf_pickle: bytes = attrs.field()

    @udf_pickle.validator
    def _validate_udf_pickle(self, attribute, value) -> None:
        if not value:
            raise ValueError("UDF pickle must not be empty.")
        udf = cloudpickle.loads(value)
        if not isinstance(udf, UDF):
            raise ValueError("UDF pickle must contain a UDF object.")

    # the checksum of the udf pickle
    udf_checksum: str = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.udf_checksum = hashlib.sha256(self.udf_pickle).hexdigest()

    @classmethod
    def packager(cls) -> "UDFPackager":
        return DockerUDFPackager()

    def to_bytes(self) -> bytes:
        self_as_dict = attrs.asdict(self)
        self_as_dict["udf_pickle"] = base64.b64encode(
            self_as_dict["udf_pickle"]
        ).decode("utf-8")
        return json.dumps(self_as_dict).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        self_as_dict = json.loads(data.decode())
        self_as_dict["udf_pickle"] = base64.b64decode(
            self_as_dict["udf_pickle"].encode("utf-8")
        )

        checksum = self_as_dict.pop("udf_checksum")  # not part of the init
        val = cls(**self_as_dict)
        val.udf_checksum = checksum

        return val


class UDFPackager(abc.ABC):
    """Packager for user-defined functions."""

    @abc.abstractmethod
    def marshal(self, udf: UDF) -> UDFSpec:
        """Marshal a user-defined function."""

    @abc.abstractmethod
    def unmarshal(self, spec: UDFSpec) -> UDF:
        """Unmarshal a user-defined function."""


@attrs.define
class _DockerUDFPackagerConfig(ConfigBase):
    prebuilt_docker_img: str | None = attrs.field(default=None)

    # the backend the image will eventually run on. Gets passed ot the
    # docker workspace packager it can know which base image/dockerfile
    # template to use
    runtime_backend: str | None = attrs.field(default=None)

    workspace_upload_location: str | None = attrs.field(default=None)

    @classmethod
    def name(cls) -> str:
        return "docker"


@attrs.define
class _UDFPackagerConfig(ConfigBase):
    docker: _DockerUDFPackagerConfig = attrs.field(default=_DockerUDFPackagerConfig())

    @classmethod
    def name(cls) -> str:
        return "udf"


@attrs.define
class DockerUDFPackager(UDFPackager):
    # If the user wants to use an prebuilt docker image, they can provide the
    # image name:tag here. This will be used instead of building and pushing a
    # new image.
    prebuilt_docker_img: str | None = attrs.field()

    @prebuilt_docker_img.default
    def _prebuilt_docker_img_default(self) -> str | None:
        config = _UDFPackagerConfig.get()
        if config.docker is None:
            return None
        return config.docker.prebuilt_docker_img

    # the location to upload the zipped workspace to
    # this should be the path to some directory on object storage (S3, GCS, etc)
    workspace_upload_location: str | None = attrs.field()

    @workspace_upload_location.default
    def _workspace_upload_location_default(self) -> str | None:
        config = _UDFPackagerConfig.get()
        if config.docker is None:
            return None
        return config.docker.workspace_upload_location

    # provide a zipper implementation with the correct configuration for how to
    # to zip the workspace. If workspace_zip is supplied and this is not, then
    # the packager will use the default WorkspaceZipper.
    zip_workspace_packager: WorkspaceZipper | None = attrs.field()

    @zip_workspace_packager.default
    def _zip_workspace_packager_default(self) -> WorkspaceZipper | None:
        if self.workspace_upload_location:
            return WorkspaceZipper(path=Path("."))

    def marshal(self, udf: UDF) -> UDFSpec:
        image_name, tag = "test-image", "latest"

        workspace_zip = None
        workspace_checksum = None
        if self.zip_workspace_packager:
            _LOG.info("Packaging zipped workspace")
            zip_path, checksum = self.zip_workspace_packager.zip()
            _LOG.info("Uploading zipped workspace")

            upload_location = self.workspace_upload_location
            if upload_location[-1] != "/":
                upload_location += "/"

            remote_fs, root_path = FileSystem.from_uri(upload_location)
            out_path = f"{root_path}/{checksum}.zip"
            curr_remote_file_info = remote_fs.get_file_info(out_path)
            if curr_remote_file_info.type == FileType.NotFound:
                _LOG.info(
                    f"Workspace zip does not exist, uploading {zip_path} to {out_path}"
                )
                local_fs, _local_root = FileSystem.from_uri(
                    zip_path.absolute().parent.as_uri()
                )

                with (
                    local_fs.open_input_stream(str(zip_path)) as in_file,
                    remote_fs.open_output_stream(out_path) as out_file,
                ):
                    bath_size = 1024 * 1024
                    while True:
                        buf = in_file.read(bath_size)
                        if buf:
                            out_file.write(buf)
                        else:
                            break

                _LOG.info(f"Uploaded workspace zip to {out_path}")
            else:
                _LOG.info("Workspace zip already exists, skipping upload")

            workspace_zip = f"{upload_location}{checksum}.zip"
            workspace_checksum = checksum

        udf_pickle = cloudpickle.dumps(udf)

        return UDFSpec(
            name=udf.name,
            backend=DockerUDFSpecV1.__name__,
            udf_payload=DockerUDFSpecV1(
                image=image_name,
                tag=tag,
                workspace_zip=workspace_zip,
                workspace_checksum=workspace_checksum,
                udf_pickle=udf_pickle,
            ).to_bytes(),
            runner_payload=json.dumps(
                {
                    "image": image_name + ":" + tag,
                }
            ).encode(),
        )

    def unmarshal(self, spec: UDFSpec) -> UDF:
        docker_spec = self.backend(spec)
        udf = cloudpickle.loads(docker_spec.udf_pickle)
        if not isinstance(udf, UDF):
            raise ValueError("UDF pickle must contain a UDF object.")
        return udf

    def backend(self, spec: UDFSpec) -> DockerUDFSpecV1:
        if spec.backend != DockerUDFSpecV1.__name__:
            raise ValueError("Invalid backend for UDF spec.")

        return DockerUDFSpecV1.from_bytes(spec.udf_payload)
