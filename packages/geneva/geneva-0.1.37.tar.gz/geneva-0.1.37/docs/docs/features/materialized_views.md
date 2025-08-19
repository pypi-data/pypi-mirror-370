# Materialized views with UDFs

Geneva provides a materialized view feature that can be used to declaratively manage “batch” updates of expensive operations such as populating udf columns.   These updates are triggered via `refresh` operation.  This can be used to optimize data layouts for training and to simplify some operations that traditionally may require external procedural orchestration (airflow, prefect, dagster). 

!!! note

    This is similar to how traditional database offer a materialized view feature to declaratively manage expensive aggregation and join operations.

The process is straightforward.

1. Define a query on table, optionally including UDFs in the select clause.
2. Create the materialized view using `db.create_materialized_view(...)`. 
3. Populate the new materialized view table using the `refresh` operation.

Just like with backfills, this operation is **incremental**, checkpointed, and run in a distributed manner.  

# An Example: 

Let's walk thorugh an example using a raw video table as a base.  We want to create a materialized view off the table that adds transcirption columns to a subset of the values.

```python
from lancedb import connect
import pyarrow as pa

db = connect("/path/to/lancedb")
schema = pa.schema([
    pa.field("video_id",   pa.int64(),            nullable=False),
    pa.field("video_uri",  pa.string(),           nullable=False),
    pa.field("upload_ts",  pa.timestamp("us"),    nullable=False),
    pa.field("metadata",   pa.json(),             nullable=True),
])
raw_videos = db.create_table(
    "raw_videos",
    schema=schema,
    primary_key="video_id"
)
```

Here's our UDFs, and a the creation of a new empty materialized view.

```python
@udf
def transcribe(video_uri) -> str:
  from whisper import load_model
  model = load_model("base")
  return model.transcribe(uri)["text"]

@udf(data_type=pa.binary())
def load_video(video_uri: pa.Array) -> pa.Array:
    videos = <expensive stuff>
    return ...

q = raw_videos.search(None)
    .shuffle(seed=42)
    .select(
        {
            "video_uri": "video_uri",
            "video": load_video,
            "transcription": transcribe,
        }
    )

view_table = db.create_materialized_view("table_view", q)
```

To populate the values, we call `refresh`.


```python

# explicitly copy values from the source table, applying UDF on cols.
db.refresh(“table_view”)  
```

Note that the UDF is stored on the detiniation materialized view table.

```python
raw_table.add(...)
db.refresh("table_view")  # only materialize new or modified rows.
```

The operaiton is *incrmental*.  So the next time refresh on the table is called, only new fragments with new data get materialized into the materialized view table.

Materialized views are just tables so you can query them as well as modify them by adding new `add_columns`, `backfill` paritcular columns and deriving other materialized views or views from them. 

## API

::: geneva.db.Connection.create_materialized_view
    options:
      annotations_path: brief
      show_source: false


## FAQ

**Do we copy the UDFs from the source table?**

No.  The UDF does not but any UDF calculated values in the original table come to the materialized table via refresh.
New columns defined by the UDFs in the materialized view creation are attached only to the materialized view.  They can be backfilled (since the UDF belongs to the view) or refreshed.

**On MV refresh, do we force materialization of UDFs cols on the source table?** 
No.  They are managed at the source table only.  If it is null the null values are propagated.   Future options may force materialization/backfill  “recursively”. 
