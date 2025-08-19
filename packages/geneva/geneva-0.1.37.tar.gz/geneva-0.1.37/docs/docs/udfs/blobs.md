# Blob types

Gevena supports UDFs that take [Lance Blobs](https://lancedb.github.io/lance/blob.html) (large binary objects) as input and has the ability to write out columns with binaries encoded as Lance Blobs.  Lance blobs are an optimization intended for large objects (1's MBs -> 100MB's) and provide a file-like object that lazily reads large binary objects.

## Reading Blobs

Defining functions that read blob columns is straight forward.  

For scalar UDFs, blob columns are expected to be of type `BlobFile`


```python
from lance.blob import BlobFile

@udf
def work_on_udf(blob: BlobFile) -> int:
    assert isinstance(blob, BlobFile)
    data = blob.read()
    # do something intresting.

    return len(data)
```

TODO: For batched  `pa.Array` UDFs and for `RecordBatch` UDFs, blob columns are dereferenced and are presented as bytes.

```python

```

## Writing Blobs


Defining UDFs that write out `Blob`s to a new column is straightforward.   Here we add the standard metadata annotation to the UDF so that Geneva knows to write out Blobs.

For scalar udfs, your udf will return `bytes`, explicitly set the `data_type` to `pa.large_binary()`, and add the `field_metadata` that specifies blob encoding.

```python
@udf(data_type=pa.large_binary(), field_metadata={"lance-encoding:blob": "true"})
def generate_blob(text: str, multiplier: int) -> bytes:
    """UDF that generates blob data by repeating text."""
    return (text * multiplier).encode("utf-8")

```

For `pa.RecordBatch` batched UDFs you the effort is similar:

```python
@udf(data_type=pa.large_binary(), field_metadata={"lance-encoding:blob": "true"})
def batch_to_blob(batch: pa.RecordBatch) -> pa.Array:
    """UDF that converts RecordBatch rows to blob data."""
    import json

    blobs = []
    for i in range(batch.num_rows):
        # do something that returns bytes
        blob_data = ... 
        blobs.append(blob_data)
    return pa.array(blobs, type=pa.large_binary())
```
