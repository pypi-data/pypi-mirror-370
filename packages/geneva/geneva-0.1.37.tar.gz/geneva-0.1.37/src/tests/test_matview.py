# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import pyarrow as pa
import pytest

from geneva import connect
from geneva.db import Connection
from geneva.packager import DockerUDFPackager
from geneva.query import GenevaQuery
from geneva.table import Table
from geneva.transformer import udf


@pytest.fixture
def db_and_table(tmp_path) -> (Connection, Table):
    packager = DockerUDFPackager(prebuilt_docker_img="test-image:latest")
    db = connect(tmp_path, packager=packager)
    tbl = pa.Table.from_pydict({"video_uri": ["a", "b", "c", "d", "e", "f"]})
    table = db.create_table("table", tbl)
    return db, table


def test_create_materialized_view(db_and_table) -> None:
    (db, table) = db_and_table

    @udf(data_type=pa.binary())
    def load_video(video_uri: pa.Array) -> pa.Array:
        videos = [str(i).encode("utf-8") for i in video_uri]
        return pa.array(videos)

    view_table = (
        table.search(None)
        .shuffle(seed=42)
        .select(
            {
                "video_uri": "video_uri",
                "video": load_video,
            }
        )
        .create_materialized_view(db, "table_view")
    )

    # Initially, view table is empty except for __source_row_id and __is_set
    assert view_table.to_arrow() == pa.table(
        {
            "__source_row_id": pa.array([3, 2, 5, 4, 1, 0]),
            "__is_set": pa.array([False] * 6),
            "video_uri": pa.array([None] * 6, pa.string()),
            "video": pa.array([None] * 6, pa.binary()),
        }
    )

    metadata = view_table.schema.metadata
    query = metadata[b"geneva::view::query"]

    query = GenevaQuery.model_validate_json(query)
    assert query.shuffle
    assert query.shuffle_seed == 42
    assert len(query.column_udfs) == 1
    assert query.column_udfs[0].output_name == "video"
    assert query.column_udfs[0].udf.name == "load_video"


def test_create_matview_column_not_in_select(db_and_table) -> None:
    (db, table) = db_and_table

    @udf(data_type=pa.utf8())
    def echo(video_uris: pa.Array) -> pa.Array:
        return video_uris

    view_table = (
        table.search(None)
        .select({"echo": echo})
        .create_materialized_view(db, "tbl_view")
    )

    assert view_table.to_arrow() == pa.table(
        {
            "__source_row_id": pa.array([0, 1, 2, 3, 4, 5]),
            "__is_set": pa.array([False] * 6),
            "echo": pa.array([None] * 6, pa.string()),
        }
    )


def test_fail_create_matview_nosearch(db_and_table) -> None:
    """Reject attempts to create materialized view from a vector search query"""
    (db, table) = db_and_table

    @udf(data_type=pa.utf8())
    def echo(video_uris: pa.Array) -> pa.Array:
        return video_uris

    fts_q = table.search("foo", query_type="fts").select({"echo": echo})

    with pytest.raises(AttributeError, match="no attribute 'create_materialized_view'"):
        fts_q.create_materialized_view(db, "tbl_view")

    with pytest.raises(
        ValueError, match="Materialized views only support plain queries"
    ):
        db.create_materialized_view("tbl_view", fts_q)

    vec_q = table.search([1, 2, 3], vector_column_name="video_uri").select(
        {"echo": echo}
    )

    with pytest.raises(AttributeError, match="no attribute 'create_materialized_view'"):
        (vec_q.create_materialized_view(db, "tbl_view"))

    with pytest.raises(
        ValueError, match="Materialized views only support plain queries"
    ):
        db.create_materialized_view("tbl_view", fts_q)
