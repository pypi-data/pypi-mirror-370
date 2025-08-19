import argparse

import ray
from lancedb.table import LanceTable as LanceLocalTable
from pyarrow.fs import FileSystem

import geneva
from geneva import LanceCheckpointStore
from geneva.packager import DockerUDFPackager, UDFSpec
from geneva.runners.ray.pipeline import run_ray_add_column
from geneva.table import Table


def run_ray_job() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_uri", type=str, required=True)
    parser.add_argument("--table_name", type=str, required=True)
    parser.add_argument("--checkpoint_store", type=str, required=True)
    parser.add_argument("--column", type=str, required=True)
    args = parser.parse_args()

    conn = geneva.connect(args.db_uri)
    table = conn.open_table(args.table_name)

    udf_spec = fetch_udf(table, args.column)

    # TODO: maybe the class here should be infered from the backend arg
    packager = DockerUDFPackager(runtime_backend="ray")
    udf = packager.unmarshal(udf_spec)

    if udf.input_columns is None:
        raise ValueError("UDF must have input columns for add_column job")

    checkpoint_store = LanceCheckpointStore(args.checkpoint_store)
    run_ray_add_column(
        table.get_reference(),
        udf.input_columns,
        {
            args.column: udf,
        },
        checkpoint_store,
        batch_size=8,
    )


def ds_uri(table: Table) -> str:
    if not isinstance(table._ltbl, LanceLocalTable):
        raise ValueError(
            f"Table {table} is not a local table. Currently only local tables are supported."  # noqa E501
        )
    ds = table._ltbl.to_lance()
    return ds.uri


def fetch_udf(table: Table, column_name: str) -> UDFSpec:
    schema = table._ltbl.schema
    field = schema.field(column_name)
    if field is None:
        raise ValueError(f"Column {column_name} not found in table {table}")

    udf_path = metadata_value("virtual_column.udf", field.metadata)
    fs, root_uri = FileSystem.from_uri(ds_uri(table))
    udf_payload = fs.open_input_file(f"{root_uri}/{udf_path}").read()

    udf_name = metadata_value("virtual_column.udf_name", field.metadata)
    udf_backend = metadata_value("virtual_column.udf_backend", field.metadata)

    return UDFSpec(
        name=udf_name,
        backend=udf_backend,
        udf_payload=udf_payload,
    )


def metadata_value(key: str, metadata: dict[bytes, bytes]) -> str:
    value = metadata.get(key.encode("utf-8"))
    if value is None:
        raise ValueError(f"Metadata key {key} not found in metadata {metadata}")
    return value.decode("utf-8")


if __name__ == "__main__":
    ray.init()
    run_ray_job()
