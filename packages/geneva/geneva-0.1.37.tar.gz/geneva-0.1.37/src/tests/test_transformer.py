# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pytest

from geneva import connect, udf
from geneva.transformer import UDF, UDFArgType


def test_udf_fsl(tmp_path: Path) -> None:
    @udf(data_type=pa.list_(pa.float32(), 4))
    def gen_fsl(b: pa.RecordBatch) -> pa.Array:
        arr = pa.array([b * 1.0 for b in range(8)])
        fsl = pa.FixedSizeListArray.from_arrays(arr, 4)
        return fsl

    assert gen_fsl.data_type == pa.list_(pa.float32(), 4)

    db = connect(tmp_path)
    tbl = pa.table({"a": [1, 2]})
    tbl = db.create_table("t1", tbl)

    tbl.add_columns(
        {"embed": (gen_fsl, ["a"])},  # explcit udf arg name mapping
    )

    tbl = db.open_table("t1")
    assert tbl.schema == pa.schema(
        [
            pa.field("a", pa.int64()),
            pa.field("embed", pa.list_(pa.float32(), 4)),
        ],
    )


def test_udf_data_type_inference() -> None:
    @udf
    def foo(x: int, y: int) -> int:
        return x + y

    assert foo.data_type == pa.int64()
    assert foo.arg_type is UDFArgType.SCALAR

    for np_dtype in [
        np.bool,
        np.bool_,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.float16,
        np.float32,
        np.float64,
    ]:

        @udf
        def foo_np(x: int, np_dtype=np_dtype) -> np_dtype:
            return np_dtype(x)

        assert foo_np.data_type == pa.from_numpy_dtype(np_dtype)
        assert foo_np.arg_type is UDFArgType.SCALAR

    @udf
    def bool_val(x: int) -> bool:
        return x % 2 == 0

    assert bool_val.data_type == pa.bool_()
    assert bool_val.arg_type is UDFArgType.SCALAR

    @udf
    def foo_str(x: int) -> str:
        return str(x)

    assert foo_str.data_type == pa.string()
    assert foo_str.arg_type is UDFArgType.SCALAR

    @udf
    def np_bool(x: int) -> np.bool_:
        return np.bool_(x % 2 == 0)

    assert np_bool.data_type == pa.bool_()
    assert np_bool.arg_type is UDFArgType.SCALAR


def test_udf_as_regular_functions() -> None:
    @udf
    def add_three_numbers(a: int, b: int, c: int) -> int:
        return a + b + c

    assert add_three_numbers(1, 2, 3) == 6
    assert add_three_numbers(10, 20, 30) == 60
    assert add_three_numbers.arg_type is UDFArgType.SCALAR
    assert add_three_numbers.data_type == pa.int64()

    @udf
    def make_string(x: int, y: str) -> str:
        return f"{y}-{x}"

    assert make_string(42, "answer") == "answer-42"
    assert make_string.arg_type is UDFArgType.SCALAR
    assert make_string.data_type == pa.string()

    @udf(data_type=pa.float32())
    def multi_by_two(batch: pa.RecordBatch) -> pa.Array:
        arr = pc.multiply(batch.column(0), 2)
        return arr

    rb = pa.RecordBatch.from_arrays([pa.array([1, 2, 3])], ["col"])
    assert multi_by_two(rb) == pa.array([2, 4, 6])
    assert multi_by_two.arg_type is UDFArgType.RECORD_BATCH

    # Confirm direct calls with multiple arguments still work as expected
    assert make_string(7, "num") == "num-7"
    assert add_three_numbers(2, 3, 4) == 9


def test_udf_with_batch_mode() -> None:
    """Test using a scalar UDF, but filled with batch model"""

    @udf
    def powers(a: int, b: int) -> int:
        return a**b

    # a RecordBatch with a and b columns
    rb = pa.RecordBatch.from_arrays(
        [pa.array([1, 2, 3]), pa.array([4, 5, 6])],
        ["a", "b"],
    )
    result = powers(rb)
    assert result == pa.array([1, 2**5, 3**6])


def test_stateful_callable() -> None:
    @udf
    class StatefulFn:
        def __init__(self) -> None:
            self.state = 0

        def __call__(self, x: int) -> int:
            self.state += x
            return self.state

    stateful_fn = StatefulFn()
    assert isinstance(stateful_fn, UDF)
    assert stateful_fn(1) == 1
    assert stateful_fn.arg_type is UDFArgType.SCALAR
    assert stateful_fn.data_type == pa.int64()
    assert stateful_fn.input_columns == ["x"]

    @udf(data_type=pa.int64())
    class StatefulBatchFn:
        def __init__(self) -> None:
            self.state = 0

        def __call__(self, batch: pa.RecordBatch) -> pa.Array:
            self.state += sum(batch.column(0).to_pylist())
            return pa.array([self.state] * batch.num_rows)

    stateful_batch_fn = StatefulBatchFn()
    assert isinstance(stateful_batch_fn, UDF)
    assert stateful_batch_fn.arg_type is UDFArgType.RECORD_BATCH
    assert stateful_batch_fn.data_type == pa.int64()


def test_batched_udf_with_explicity_columns() -> None:
    @udf(data_type=pa.int64())
    def add_columns(a: pa.Array, b: pa.Array) -> pa.Array:
        return pc.add(a, b)

    assert add_columns.arg_type is UDFArgType.ARRAY
    assert add_columns.data_type == pa.int64()
    assert add_columns.input_columns == ["a", "b"]

    with pytest.raises(
        ValueError, match="multiple parameters with 'pa.RecordBatch' type"
    ):

        @udf
        def bad_udf(a: pa.RecordBatch, b: pa.RecordBatch) -> pa.Array:
            return pc.add(a.column(0), b.column(0))
