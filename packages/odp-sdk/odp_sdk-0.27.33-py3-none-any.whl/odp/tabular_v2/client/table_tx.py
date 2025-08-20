import io
import logging
from typing import Dict, Iterator, List, Union

import pandas as pd
import pyarrow as pa
from pyarrow.lib import ArrowInvalid

from odp.tabular_v2.client import Table
from odp.tabular_v2.client.validation import validate_data_against_schema


class Transaction:
    """
    a transaction is created implicitly when a table is used as a context manager:

        with table as tx:
            ...

    transaction should be used to modify the data, and make the modifications atomic (which means users won't see
    the changes while they are being made, but only all at once when the transaction is committed at the end).

    they transaction won't commit (and instead rollback) if an exception is raised inside the block.

    when a transaction is created, it might buffer some data locally to improve the performance of the system.
    """

    _buffer: pa.Table

    def __init__(self, table: Table, tx_id: str):
        if not tx_id:
            raise ValueError("tx_id must not be empty")
        self._table = table
        self._id = tx_id
        self._buffer = pa.Table.from_pylist([], schema=table.schema())

    # FIXME(oha) this is broken, since we have data buffered locally,
    # we could just flush the data first and make this work
    # or instead put the effort to use the local buffer as false positives
    # since there is no strong use case, this can be done later when the rest is sorted
    # def select(self, query: Union[exp.Op, str, None] = None) -> Iterator[Dict]:
    #    for row in self._table.select(query).rows():
    #        yield row

    def replace(self, filter: str = "", vars: Union[Dict, List, None] = None, **kwargs) -> Iterator[Dict]:
        """perform a two-step replace:
        rows that don't match the query are kept.
        rows that match are removed and sent to the caller.
        the caller might insert them again or do something else.

        NOTE: internally, the server might have to send false positives (because of bigcol), which means
        the SDK will have to check for them and insert them back into the table.
        This happens internally and is not exposed to the user.
        """
        filter = filter or kwargs.get("query", "")
        if not filter:
            raise ValueError("For your own safety, a filter is required, use 1==1 to match all rows")
        assert self._buffer.num_rows == 0  # FIXME: handle buffered data in replace/select
        for row in self._table._query_cursor(type="replace", filter=filter, vars=vars, tx_id=self._id).rows():
            yield row

    def delete(self, query: str = "") -> int:
        """
        delete rows that match the query

        Note: similarly to the replace, some rows might be false positive and should be added back, but this
        happens internally and is not exposed to the user.
        Returns how many rows were changed
        """
        ct = 0
        for _ in self.replace(query):  # Note(oha) we must iterate over the generator to make it work
            ct += 1
        return ct

    def flush(self):
        """
        flush the data to the server, in case some data is buffered locally
        """
        logging.debug("flushing to stage %s", self._id)

        if self._buffer.num_rows == 0:
            return

        schema = self._buffer.schema
        buf = io.BytesIO()
        w = pa.ipc.RecordBatchStreamWriter(buf, schema, options=pa.ipc.IpcWriteOptions(compression="lz4"))

        # recursively split the batch in smaller ones if it's too big
        def write_batch(b: pa.RecordBatch):
            # small enough to be sent in one go
            if b.nbytes < 30_000_000 and b.num_rows < 5_000:
                w.write_batch(b)
            elif b.num_rows > 1:
                mid = b.num_rows // 2
                write_batch(b.slice(0, mid))
                write_batch(b.slice(mid))
            else:
                # we can't split it further
                w.write_batch(b)

        for b in self._buffer.to_batches():
            try:
                write_batch(b)
            except ArrowInvalid as e:
                raise ValueError("Invalid arrow format") from e
        w.close()

        self._table._impl(
            path="/api/table/v2/sdk/insert",
            params={
                "table_id": self._table._id,
                "tx_id": self._id,
            },
            data=buf.getvalue(),
        ).json()
        self._buffer = pa.Table.from_pylist([], schema=schema)

    def insert(self, data: Union[Dict, List[Dict], pa.RecordBatch, pd.DataFrame, pa.Table]):
        """
        add data to the internal buffer to be inserted into the table
        if the buffered data is enough, it will be automatically flushed

        accept a single dictionary, a list of dictionaries, a pandas DataFrame, or a pyarrow RecordBatch
        """

        schema = self._buffer.schema

        if isinstance(data, dict):
            validate_data_against_schema([data], schema)
            data = pa.Table.from_pylist([data], schema=schema)
        elif isinstance(data, list):
            validate_data_against_schema(data, schema)
            data = pa.Table.from_pylist(data, schema=schema)
        elif isinstance(data, pd.DataFrame):
            validate_data_against_schema(data, schema)
            data = pa.Table.from_pandas(data, schema=schema)
        elif isinstance(data, pa.RecordBatch):
            data = pa.Table.from_batches([data], schema=schema)
        elif isinstance(data, pa.Table):
            pass
        else:
            raise ValueError(f"unexpected type {type(data)}")

        self._buffer = pa.concat_tables([self._buffer, data]).combine_chunks()

        if self._buffer.num_rows >= 10_000 or self._buffer.nbytes >= 10_000_000:
            self.flush()
