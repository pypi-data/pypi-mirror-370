# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# tests for sqlitekv.py

import tempfile

import pytest

from geneva.utils.sqlitekv import SQLiteKV


def test_sqlitekv() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        kv = SQLiteKV(db_path=f"{tmpdir}/kv.sqlite")
        kv["key"] = "value"
        assert kv["key"] == "value"
        assert len(kv) == 1
        assert list(kv) == ["key"]
        del kv["key"]
        assert len(kv) == 0
        with pytest.raises(KeyError):
            kv["key"]


def test_sqlitekv_disk_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        kv = SQLiteKV(db_path=f"{tmpdir}/kv.sqlite")
        kv["key"] = "value"

        # reopens the database
        kv = SQLiteKV(db_path=f"{tmpdir}/kv.sqlite")
        assert kv["key"] == "value"
        assert len(kv) == 1
        assert list(kv) == ["key"]
        del kv["key"]
        assert len(kv) == 0
        with pytest.raises(KeyError):
            kv["key"]


def test_sqlitekv_duplicated_handle() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        kv1 = SQLiteKV(db_path=f"{tmpdir}/kv.sqlite")
        kv2 = SQLiteKV(db_path=f"{tmpdir}/kv.sqlite")

        kv1["key"] = "value"
        assert kv2["key"] == "value"
        del kv1["key"]
        with pytest.raises(KeyError):
            kv2["key"]
