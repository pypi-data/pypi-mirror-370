# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import enum
import functools
import hashlib
import inspect
import logging
from collections.abc import Callable
from typing import Any

import attrs
import numpy
import pyarrow as pa
from lance.blob import BlobFile

import geneva.cloudpickle as pickle

_LOG = logging.getLogger(__name__)

# special column name used to mark the rows that were not selected
# for backfilling.  This is used to avoid calling expensive UDFs
# on rows that are not selected.
BACKFILL_SELECTED = "__geneva_backfill_selected"


class UDFArgType(enum.Enum):
    """
    The type of arguments that the UDF expects.
    """

    # Scalar Batch
    SCALAR = 0
    # Array mode
    ARRAY = 1
    # Pass a pyarrow RecordBatch
    RECORD_BATCH = 2


@attrs.define
class UDF(Callable[[pa.RecordBatch], pa.Array]):  # type: ignore
    """User-defined function (UDF) to be applied to a Lance Table."""

    # The reference to the callable
    func: Callable = attrs.field()

    name: str = attrs.field()

    cuda: bool = attrs.field(default=False)

    num_cpus: float = attrs.field(default=1.0, converter=float)

    memory: int | None = attrs.field(default=None)

    batch_size: int | None = attrs.field(default=None)

    @name.default
    def _name_default(self) -> str:
        if inspect.isfunction(self.func):
            return self.func.__name__
        elif isinstance(self.func, Callable):
            return self.func.__class__.__name__
        else:
            raise ValueError(f"func must be a function or a callable, got {self.func}")

    def _record_batch_input(self) -> bool:
        sig = inspect.signature(self.func)
        if len(sig.parameters) == 1:
            param = list(sig.parameters.values())[0]
            return param.annotation == pa.RecordBatch
        return False

    @property
    def arg_type(self) -> UDFArgType:
        if self._record_batch_input():
            return UDFArgType.RECORD_BATCH
        if _is_batched_func(self.func):
            return UDFArgType.ARRAY
        return UDFArgType.SCALAR

    input_columns: list[str] | None = attrs.field()

    @input_columns.default
    def _input_columns_default(self) -> list[str] | None:
        sig = inspect.signature(self.func)
        params = list(sig.parameters.keys())
        if self._record_batch_input():
            return None
        return params

    @input_columns.validator
    def _input_columns_validator(self, attribute, value) -> None:
        if self.arg_type == UDFArgType.RECORD_BATCH:
            if value is not None:
                raise ValueError(
                    "RecordBatch input UDF must not declare any input columns."
                    " Consider using a stateful RecordBatch UDF and parameterize it or"
                    " use UDF with Array inputs."
                )
            return
        if value is None:
            raise ValueError("Array and Scalar input UDF must declare input column")

    data_type: pa.DataType = attrs.field()

    @data_type.validator
    def _data_type_validator(self, attribute, value) -> None:
        if value is None:
            raise ValueError("data_type must be set")
        if not isinstance(value, pa.DataType):
            raise ValueError(f"data_type must be a pyarrow.DataType, got {value}")

    @data_type.default
    def _data_type_default(self) -> pa.DataType:
        if self.arg_type != UDFArgType.SCALAR:
            raise ValueError(
                "batched UDFs do not support data_type inference yet,"
                " please specify data_type",
            )
        return _infer_func_arrow_type(self.func, None)

    version: str = attrs.field()

    @version.default
    def _version_default(self) -> str:
        # don't use hash(), which is randomly seeded every process startup
        hasher = hashlib.md5()
        # it is fairly safe to to use cloudpickle here because we are using
        # dockerize environments, so the environment should be consistent
        # across all processes
        hasher.update(pickle.dumps(self.func))
        return hasher.hexdigest()

    checkpoint_key: str = attrs.field()

    @checkpoint_key.default
    def _checkpoint_key_default(self) -> str:
        return f"{self.name}:{self.version}"

    field_metadata: dict[str, str] = attrs.field(default={})

    def _scalar_func_record_batch_call(self, record_batch: pa.RecordBatch) -> pa.Array:
        """
        We use this when the UDF uses single call like
        `func(x_int, y_string, ...) -> type`

        this function automatically dispatches rows to the func and returns `pa.Array`
        """

        # this let's us avoid having to allocate a list in python
        # to hold the results. PA will allocate once for us
        def _iter():  # noqa: ANN202
            batches = (
                record_batch.to_pylist()
                if isinstance(record_batch, pa.RecordBatch)
                else record_batch
            )
            for item in batches:
                # we know inputs_columns is not none here
                if BACKFILL_SELECTED not in item or item.get(BACKFILL_SELECTED):
                    # we know input_columns is not none here
                    args = [item[col] for col in self.input_columns]  # type: ignore
                    yield self.func(*args)
                else:
                    # item was not selected, so do not compute
                    yield None

        arr = pa.array(
            _iter(),
            type=self.data_type,
        )
        # this should always by an Array, never should we get a ChunkedArray back here
        assert isinstance(arr, pa.Array)
        return arr

    def __call__(self, *args, use_applier: bool = False, **kwargs) -> pa.Array:
        # dispatch coming from Applier or user calling with a `RecordBatch`
        if use_applier or (len(args) == 1 and isinstance(args[0], pa.RecordBatch)):
            record_batch = args[0]
            match self.arg_type:
                case UDFArgType.SCALAR:
                    return self._scalar_func_record_batch_call(record_batch)
                case UDFArgType.ARRAY:
                    arrs = [record_batch[col] for col in self.input_columns]  # type:ignore
                    return self.func(*arrs)
                case UDFArgType.RECORD_BATCH:
                    if isinstance(record_batch, pa.RecordBatch):
                        return self.func(record_batch)
                    # a list of dicts with BlobFiles that need to de-ref'ed
                    assert isinstance(record_batch, list)
                    rb_list = []
                    for row in record_batch:
                        new_row = {}
                        for k, v in row.items():
                            if isinstance(v, BlobFile):
                                # read the blob file into memory
                                new_row[k] = v.readall()
                                continue
                            new_row[k] = v
                        rb_list.append(new_row)

                    rb = pa.RecordBatch.from_pylist(rb_list)

                    return self.func(rb)
        # dispatch is trying to access the function's original pattern
        return self.func(*args, **kwargs)


def udf(
    func: Callable | None = None,
    *,
    data_type: pa.DataType | None = None,
    version: str | None = None,
    cuda: bool = False,
    field_metadata: dict[str, str] | None = None,
    input_columns: list[str] | None = None,
    num_cpus: int | float | None = None,
    **kwargs,
) -> UDF | functools.partial:
    """Decorator of a User Defined Function ([UDF][geneva.transformer.UDF]).

    Parameters
    ----------
    func: Callable
        The callable to be decorated. If None, returns a partial function.
    data_type: pa.DataType, optional
        The data type of the output PyArrow Array from the UDF.
        If None, it will be inferred from the function signature.
    version: str, optional
        A version string to manage the changes of function.
        If not provided, it will use the hash of the serialized function.
    cuda: bool, optional
        If true, load CUDA optimized kernels
    field_metadata: dict[str, str], optional
        A dictionary of metadata to be attached to the output `pyarrow.Field`.
    input_columns: list[str], optional
        A list of input column names for the UDF. If not provided, it will be
        inferred from the function signature. Or scan all columns.
    num_cpus: int, float, optional
        The (fraction) number of CPUs to acquire to run the job.
    """
    if inspect.isclass(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs) -> UDF | functools.partial:
            callable_obj = func(*args, **kwargs)
            return udf(
                callable_obj,
                cuda=cuda,
                data_type=data_type,
                version=version,
                field_metadata=field_metadata,
                input_columns=input_columns,
                num_cpus=num_cpus,
            )

        return _wrapper  # type: ignore

    if func is None:
        return functools.partial(
            udf,
            cuda=cuda,
            data_type=data_type,
            version=version,
            field_metadata=field_metadata,
            input_columns=input_columns,
            num_cpus=num_cpus,
            **kwargs,
        )

    # we depend on default behavior of attrs to infer the output schema
    def _include_if_not_none(name, value) -> dict[str, Any]:
        if value is not None:
            return {name: value}
        return {}

    args = {
        "func": func,
        "cuda": cuda,
        **_include_if_not_none("data_type", data_type),
        **_include_if_not_none("version", version),
        **_include_if_not_none("field_metadata", field_metadata),
        **_include_if_not_none("input_columns", input_columns),
        **_include_if_not_none("num_cpus", num_cpus),
    }
    # can't use functools.update_wrapper because attrs makes certain assumptions
    # and attributes read-only. We will figure out docs and stuff later
    return UDF(**args)


def _get_annotations(func: Callable) -> dict[str, type]:
    if inspect.isfunction(func):
        return inspect.get_annotations(func)
    elif isinstance(func, Callable):
        return inspect.get_annotations(func.__call__)
    raise ValueError(f"func must be a function or a callable, got {func}")


def _is_batched_func(func: Callable) -> bool:
    annotations = _get_annotations(func)
    if "return" not in annotations:
        return False

    ret_type = annotations["return"]
    if ret_type != pa.Array and not isinstance(ret_type, pa.DataType):
        return False

    input_keys = list(annotations.keys() - {"return"})
    if len(input_keys) == 1:
        return all(
            annotations[input_key] in [pa.RecordBatch, pa.Array]
            for input_key in input_keys
        )

    if any(annotations[input_key] == pa.RecordBatch for input_key in input_keys):
        raise ValueError(
            "UDF can not have multiple parameters with 'pa.RecordBatch' type"
        )
    return all(annotations[input_key] in [pa.Array] for input_key in input_keys)


def _infer_func_arrow_type(func: Callable, input_schema: pa.Schema) -> pa.DataType:
    """Infer the output schema of a UDF

    currently independent of the input schema, in the future we may want to
    infer the output schema based on the input schema, or the UDF itself could
    request the input schema to be passed in.
    """
    if isinstance(func, UDF):
        return func.data_type

    annotations = _get_annotations(func)
    if "return" not in annotations:
        raise ValueError(f"UDF {func} does not have a return type annotation")

    data_type = annotations["return"]
    # do dispatch to handle different types of output types
    # e.g. pydantic -> pyarrow type inference
    if isinstance(data_type, pa.DataType):
        return data_type

    if t := {
        bool: pa.bool_(),
        bytes: pa.binary(),
        float: pa.float32(),
        int: pa.int64(),
        str: pa.string(),
        numpy.bool_: pa.bool_(),
        numpy.bool: pa.bool_(),
        numpy.uint8: pa.uint8(),
        numpy.uint16: pa.uint16(),
        numpy.uint32: pa.uint32(),
        numpy.uint64: pa.uint64(),
        numpy.int8: pa.int8(),
        numpy.int16: pa.int16(),
        numpy.int32: pa.int32(),
        numpy.int64: pa.int64(),
        numpy.float16: pa.float16(),
        numpy.float32: pa.float32(),
        numpy.float64: pa.float64(),
        numpy.str_: pa.string(),
    }.get(data_type):
        return t

    raise ValueError(f"UDF {func} has an invalid return type annotation {data_type}")
