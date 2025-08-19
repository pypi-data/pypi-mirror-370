# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

from collections.abc import Callable, Iterator
from typing import Any

from lance.torch.data import LanceDataset, _buffer_arrow_batches, _to_tensor
from torch.utils.data import IterableDataset

from geneva.query import Query
from geneva.table import Table


class Dataset(IterableDataset):
    """PyTorch Dataset for Lance Datalake"""

    def __init__(
        self,
        table: Table,
        batch_size=1,
        to_tensor_fn: Callable | None = None,
    ) -> None:
        self.table = table
        self.batch_size = batch_size
        self._to_tensor_fn = to_tensor_fn or _to_tensor

    # TODO: This annotation sucks
    def __iter__(self) -> Iterator[Any]:
        if isinstance(self.table, Query) or self.table._is_view():
            stream = self.table.to_batches(self.batch_size)
            stream = _buffer_arrow_batches(stream, buffer_size=self.batch_size)
            for batch in stream:
                yield self._to_tensor_fn(batch)
        else:
            for batch in LanceDataset(
                self.table,
                batch_size=self.batch_size,
                to_tensor_fn=self._to_tensor_fn,
            ).__iter__():
                yield batch
