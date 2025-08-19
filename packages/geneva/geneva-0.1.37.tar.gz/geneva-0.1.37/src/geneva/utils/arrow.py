# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import datetime
import enum
import typing

import attr
import pyarrow as pa
from pyarrow import DataType


def datafusion_type_name(data_type: DataType) -> str:
    arrow_type_name = str(data_type)
    # see https://datafusion.apache.org/user-guide/sql/data_types.html
    # TODO: add more types. Note that we only support certain types in lance
    # https://github.com/lancedb/lance/blob/644213b9a63e2b143d62cda79e108df831bc5054/rust/lance-datafusion/src/planner.rs#L426-L441
    df_type_name = {
        "int8": "TINYINT",
        "uint8": "TINYINT UNSIGNED",
        "int16": "SMALLINT",
        "uint16": "SMALLINT UNSIGNED",
        "int32": "INT",
        "uint32": "INT UNSIGNED",
        "int64": "BIGINT",
        "uint64": "BIGINT UNSIGNED",
        "float32": "FLOAT",
        "float64": "DOUBLE",
        "string": "STRING",
        "binary": "BINARY",
        "boolean": "BOOLEAN",
    }.get(arrow_type_name)

    if df_type_name is None:
        raise ValueError(f"unsupported arrow type {arrow_type_name}")

    return df_type_name


def pa_type_from_py(py_type) -> DataType:
    """Map a Python/typing annotation to a PyArrow DataType."""
    origin = typing.get_origin(py_type)
    # Handle Optional[T]
    if origin is typing.Union and type(None) in typing.get_args(py_type):
        inner = [t for t in typing.get_args(py_type) if t is not type(None)][0]
        return pa_type_from_py(inner).with_nullable(True)
    # Handle List[T]
    if origin is list:
        subtype = typing.get_args(py_type)[0]
        return pa.list_(pa_type_from_py(subtype))

    if isinstance(py_type, type) and issubclass(py_type, enum.Enum):
        return pa.string()  # Enums are treated as strings

    # Primitives
    if py_type is int:
        return pa.int64()
    if py_type is float:
        return pa.float64()
    if py_type is bool:
        return pa.bool_()
    if py_type is str:
        return pa.string()
    if py_type is datetime.datetime:
        return pa.timestamp("us")
    if py_type is datetime.date:
        return pa.date32()
    # Fallback
    return pa.string()


def schema_from_attrs(cls) -> pa.Schema:
    """Build a pyarrow.Schema from an attrs-decorated class."""
    fields = []
    for attribute in attr.fields(cls):
        name = attribute.name
        annotation = attribute.type
        pa_dtype = pa_type_from_py(annotation)
        fields.append(pa.field(name, pa_dtype))
    return pa.schema(fields)
