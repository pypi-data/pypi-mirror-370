# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import logging
import sys
from pathlib import Path
from typing import cast

import pyarrow as pa
import pytest

from geneva import connect, udf
from geneva.db import Connection
from geneva.table import Table

_LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, force=True)
sys.stderr.reconfigure(line_buffering=True)

try:
    import ray  # noqa: F401

    from geneva.runners.ray.pipeline import run_ray_copy_table
except ImportError:
    pytest.skip("failed to import geneva.runners.ray", allow_module_level=True)

TABLE = "table"


@pytest.fixture
def db(tmp_path: Path) -> Connection:
    return connect(tmp_path)


@pytest.fixture
def video_table(db) -> Table:
    tbl = pa.Table.from_pydict(
        {
            "video_uri": ["a", "b", "c", "d", "e", "f"],
            "rating": ["g", "nr", "pg", "pg-13", "r", "t"],
        }
    )
    table = db.create_table(TABLE, tbl)
    return table


def test_db_create_materialized_view(db, video_table) -> None:
    @udf(data_type=pa.binary())
    def load_video(video_uri: pa.Array) -> pa.Array:
        videos = [str(i).encode("utf-8") for i in video_uri]
        return cast("pa.Array", pa.array(videos))

    _LOG.info(video_table.to_arrow())

    q = (
        video_table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
    )

    dl_view = db.create_materialized_view("dl_view", q)
    udf_field = dl_view.schema.field("video")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"load_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    cnt_not_null = dl_view.count_rows(filter="video is not null")
    assert cnt_not_null == 0

    dl_view.refresh()

    cnt_null = dl_view.count_rows(filter="video is null")
    _LOG.info(dl_view.to_arrow())
    assert cnt_null == 0


def test_create_materialized_view(db, video_table) -> None:
    @udf(data_type=pa.binary())
    def load_video(video_uri: pa.Array) -> pa.Array:
        videos = [str(i).encode("utf-8") for i in video_uri]
        return cast("pa.Array", pa.array(videos))

    view_table = (
        video_table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "dl_view")
    )
    udf_field = view_table.schema.field("video")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"load_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    dl_view = db.open_table("dl_view")
    cnt_not_null = dl_view.count_rows(filter="video is not null")
    assert cnt_not_null == 0

    dl_view.refresh()

    cnt_null = dl_view.count_rows(filter="video is null")
    _LOG.info(dl_view.to_arrow())
    assert cnt_null == 0


def test_create_materialized_view_of_view_ints(db) -> None:
    tbl = pa.Table.from_pydict({"video_uri": [0, 1, 2, 3, 4, 5]})
    video_table = db.create_table(TABLE, tbl)

    @udf
    def load_video(video_uri: int) -> int:  # avoiding binary for now
        return video_uri * 10

    _LOG.info(f"original video_table: {video_table.to_arrow()}")

    dl_view = (
        video_table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "dl_view")
    )

    udf_field = dl_view.schema.field("video")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"load_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    @udf
    def caption_video(video: int) -> int:
        return video * 10

    q = (
        dl_view.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": "video",
                "caption": caption_video,
            }
        )
    )

    _LOG.info(f"query: table: {q._table} udf_cols: {q._column_udfs}")

    caption_view = q.create_materialized_view(db, "caption_view")

    # caption should be a UDF
    udf_field = caption_view.schema.field("caption")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"caption_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    # video in matview should a copy of the values from the source UDF col, and not
    # the UDF
    udf_field = caption_view.schema.field("video")
    assert udf_field.metadata is None

    # Nothing has been refresh so no data in matview
    _LOG.info(f"dl_view before refresh: {dl_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is not null")
    assert cnt_null == 0

    dl_view.refresh()

    # refreshed source table but not refreshed to matview yet
    _LOG.info(f"dl_view after refresh: {dl_view.to_arrow()}")
    _LOG.info(f"caption mv before refresh: {caption_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is not null")
    assert cnt_null == 0

    caption_view.refresh()

    # Now all values should be in matview
    _LOG.info(f"caption mv after refresh: {caption_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is null")
    assert cnt_null == 0


def test_create_materialized_view_of_view(db, video_table) -> None:
    @udf
    def load_video(video_uri: str) -> bytes:
        return str(video_uri).encode("utf-8")

    _LOG.info(f"original video_table: {video_table.to_arrow()}")

    dl_view = (
        video_table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "dl_view")
    )

    udf_field = dl_view.schema.field("video")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"load_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    @udf
    def caption_video(video: bytes) -> str:
        return f"this is video {video.decode('utf-8')}"

    q = (
        dl_view.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": "video",
                "caption": caption_video,
            }
        )
    )

    _LOG.info(f"query: table: {q._table} udf_cols: {q._column_udfs}")

    caption_view = q.create_materialized_view(db, "caption_view")

    # caption should be a UDF
    udf_field = caption_view.schema.field("caption")
    assert udf_field.metadata.get(b"virtual_column") == b"true"
    assert udf_field.metadata.get(b"virtual_column.udf_inputs") is not None
    assert udf_field.metadata.get(b"virtual_column.udf_name") == b"caption_video"
    assert udf_field.metadata.get(b"virtual_column.udf_backend") is not None
    assert udf_field.metadata.get(b"virtual_column.udf") is not None

    # video in matview should a copy of the values from the source UDF col, and not
    # the UDF
    udf_field = caption_view.schema.field("video")
    assert udf_field.metadata is None

    # Nothing has been refresh so no data in matview
    _LOG.info(f"dl_view before refresh: {dl_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is not null")
    assert cnt_null == 0

    dl_view.refresh()

    # refreshed source table but not refreshed to matview yet
    _LOG.info(f"dl_view after refresh: {dl_view.to_arrow()}")
    _LOG.info(f"caption mv before refresh: {caption_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is not null")
    assert cnt_null == 0

    caption_view.refresh()

    # Now all values should be in matview
    _LOG.info(f"caption mv after refresh: {caption_view.to_arrow()}")
    cnt_null = caption_view.count_rows(filter="video is null")
    assert cnt_null == 0


def test_ray_materialized_view(db, video_table) -> None:
    @udf(data_type=pa.binary())
    def load_video(video_uri: pa.Array) -> pa.Array:
        videos = [str(i).encode("utf-8") for i in video_uri]
        return cast("pa.Array", pa.array(videos))

    view_table = (
        video_table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "table_view")
    )

    run_ray_copy_table(view_table.get_reference(), db._packager, db._checkpoint_store)

    view_table.checkout_latest()
    assert view_table.to_arrow() == pa.Table.from_pydict(
        {
            "__source_row_id": [3, 2, 5, 4, 1, 0],
            "__is_set": [False] * 6,
            "video_uri": ["d", "c", "f", "e", "b", "a"],
            "video": [b"d", b"c", b"f", b"e", b"b", b"a"],
        }
    )
