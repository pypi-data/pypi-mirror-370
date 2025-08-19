# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import attrs
import emoji
import pyarrow.fs as fs

from geneva.config import ConfigBase
from geneva.tqdm import tqdm

_LOG = logging.getLogger(__name__)


@attrs.define
class Uploader(ConfigBase):
    """
    This class is used to upload files to a specified directory.

    TODO: I'm too lazy to make a whole interface and wire things up
    right now. So just pyarrow.fs implementation for now
    """

    upload_dir: str = attrs.field(converter=lambda x: x.removesuffix("/"))

    @classmethod
    def name(cls) -> str:
        return "uploader"

    @property
    def fs_and_path(self) -> tuple[fs.FileSystem, str]:
        return fs.FileSystem.from_uri(self.upload_dir)

    def _upload_gcs(self, f: Path) -> str:
        """
        Upload to GCS -- dispatch here when we detect the dir is GCS
        Because the google client is much more performant than pyarrow
        """
        # optional dependency so don't import at the top
        from google.cloud import storage

        # we don't call this frequently so just create client on the fly
        storage_client = storage.Client()

        path = self.upload_dir.removeprefix("gs://")
        bucket_name, destination_blob_prefix = path.split("/", 1)
        destination_blob_name = f"{destination_blob_prefix}/{f.name}"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        # determine upload strategy
        # if the file is small enough, we can just upload it directly
        # otherwise we will upload in chunks
        # and then compose the chunks together
        # this lets us maximize upload bandwidth for large files
        if f.stat().st_size < 1024 * 1024 * 1024:  # 1GiB
            blob.upload_from_filename(f.as_posix())
        else:
            # we will upload in 32 chunks, which is the maximum number of
            # chunks allowed for composing blobs
            chunk_size = -(-f.stat().st_size // 32)

            pbar = tqdm(
                total=f.stat().st_size, unit="B", unit_scale=True, unit_divisor=1024
            )
            pbar.set_description(
                emoji.emojize(f":cloud: uploading {f.name:5.5} to {self.upload_dir}")
            )

            def _upload_part(idx: int) -> storage.Blob:
                start = idx * chunk_size
                end = min(start + chunk_size, f.stat().st_size)

                length = end - start
                part = bucket.blob(f"{destination_blob_name}-{idx}")
                with (
                    part.open("wb") as f_out,
                    open(f, "rb") as f_in,
                ):
                    f_in.seek(start)
                    while length:
                        read_size = min(length, 1024 * 64)
                        data = f_in.read(read_size)
                        f_out.write(data)
                        length -= read_size
                        pbar.update(read_size)
                return part

            # int_divceil
            num_chunks = -(-f.stat().st_size // chunk_size)
            with ThreadPoolExecutor(max_workers=8) as executor:
                parts = executor.map(_upload_part, range(num_chunks))

            pbar.close()
            blob.compose(list(parts))

        return f"gs://{bucket_name}/{destination_blob_name}"

    def _file_exists(self, f: Path) -> bool:
        handle, prefix = self.fs_and_path
        upload_path = str(Path(prefix) / f.name)
        try:
            return handle.get_file_info(upload_path).type == fs.FileType.File
        except Exception:
            _LOG.exception(f"Failed to check if file exists: {upload_path}")
            return False

    def upload(self, f: Path) -> str:
        """
        Upload a file to the specified directory.

        The name of the object will be in the form of
        <path_to_upload_dir>/<name_of_file>
        """
        if self._file_exists(f):
            _LOG.debug(
                f"File {f.name} already exists in {self.upload_dir}, skipping upload"
            )
            return f"{self.upload_dir}/{f.name}"

        # fast path for gcs
        if self.upload_dir.startswith("gs://"):
            return self._upload_gcs(f)

        handle, prefix = self.fs_and_path
        upload_path = str(Path(prefix) / f.name)

        with (
            handle.open_output_stream(upload_path, buffer_size=1024 * 1024 * 64) as out,
            tqdm(
                total=f.stat().st_size, unit="B", unit_scale=True, unit_divisor=1024
            ) as pbar,
            f.open("rb") as f_in,
        ):
            pbar.set_description(
                emoji.emojize(f":cloud: uploading {f.name} to {self.upload_dir}")
            )
            chunk_size = 1024 * 1024 * 8  # 8MiB chunks

            while data := f_in.read(chunk_size):
                out.write(data)
                pbar.update(len(data))

        # This isn't great :(
        # it would be nice to have a way to format the URI directly from pyarrow
        protocol = self.upload_dir.split("://", 1)[0]

        return f"{protocol}://{upload_path}"
