import logging
import os
import typing as t
from collections import OrderedDict
from pathlib import Path

import fsspec
import pandas as pd
import polars as pl
from influx_line import InfluxLine

logger = logging.getLogger(__name__)


BytesString = t.Union[bytes, str]
BytesStringList = t.List[BytesString]


def open(path: t.Union[Path, str]):  # noqa: A001
    """
    Access a plethora of resources using `fsspec`.
    """
    path = str(path)
    kwargs: t.Dict[str, t.Any] = {}

    # TODO: Also support authenticated S3.
    if path.startswith("s3"):
        kwargs["anon"] = True

    # TODO: Why isn't compression selected transparently?
    if path.endswith(".gz"):
        kwargs["compression"] = "gzip"
    fs = fsspec.open(path, mode="rb", **kwargs).open()
    return fs


def read_lineprotocol(data: t.IO[t.Any]):
    """
    Read stream of InfluxDB line protocol and decode raw data.

    https://docs.influxdata.com/influxdb/latest/reference/syntax/line-protocol/
    """
    from line_protocol_parser import LineFormatError, parse_line

    for line in data.readlines():
        try:
            yield parse_line(line)
        except LineFormatError as ex:
            logger.info(f"WARNING: Line protocol item {line} invalid. Reason: {ex}")


def records_from_lineprotocol(data: t.IO[t.Any]):
    """
    Read stream of InfluxDB line protocol and generate `OrderedDict` records.
    """
    for lp in read_lineprotocol(data=data):
        record = OrderedDict()
        record["measurement"] = lp["measurement"]
        record["time"] = lp["time"]
        for tag, value in lp["tags"].items():
            record[tag] = value
        for field, value in lp["fields"].items():
            record[field] = value
        yield record


def dataframes_from_lineprotocol(data: t.IO[t.Any]) -> t.Dict[str, pd.DataFrame]:
    """
    Read InfluxDB line protocol file, grouping individual measurement records into multiple Polars DataFrames.
    """
    records = records_from_lineprotocol(data)
    buffer = {}
    frame = pl.DataFrame(records)
    measurements = frame.unique("measurement")["measurement"]
    for measurement in measurements:
        buffer[measurement] = frame.filter(pl.col("measurement") == measurement)
    return buffer


def dataframe_to_lineprotocol(df: pd.DataFrame, progress: bool = False) -> t.Generator[str, None, None]:
    """
    Convert DataFrame to InfluxDB Line Protocol.

    TODO: Needs a test verifying dispatching of tags.
    TODO: Needs configurability to manually dispatch columns to either fields or tags.
    TODO: Needs heuristics if timestamp field is called differently than `time`.
    """
    for record in df.to_dict(orient="records"):
        line = InfluxLine(record["measurement"])
        line.set_timestamp(record["time"].to_datetime64().view("int64"))
        del record["measurement"]
        del record["time"]
        for key, value in record.items():
            if isinstance(value, (int, float)):
                line.add_field(key, value)
            else:
                line.add_tag(key, value)
        yield str(line)


def dataframe_to_sql(
    df: t.Union[pd.DataFrame, pl.DataFrame],
    dburi: str,
    tablename: str,
    index=False,
    chunksize=None,
    if_exists="fail",
    npartitions: int = None,
    progress: bool = False,
):
    """
    Load pandas dataframe into database using Dask.

    https://stackoverflow.com/questions/62404502/using-dasks-new-to-sql-for-improved-efficiency-memory-speed-or-alternative-to

    if_exists : {'fail', 'replace', 'append'}, default 'fail'
        How to behave if the table already exists.

        * fail: Raise a ValueError.
        * replace: Drop the table before inserting new values.
        * append: Insert new values to the existing table.
    """
    logger.info(f"Writing dataframe to SQL: uri={dburi}, table={tablename}")
    import dask.dataframe as dd

    # Set a few defaults.
    if_exists = if_exists or "fail"
    chunksize = chunksize or 5_000
    npartitions = npartitions or int(os.cpu_count() / 2)

    if progress:
        from dask.diagnostics import ProgressBar

        pbar = ProgressBar()
        pbar.register()

    if dburi.startswith("crate"):

        # Use performance INSERT method.
        try:
            from sqlalchemy_cratedb.support import insert_bulk
        except ImportError:  # pragma: nocover
            from crate.client.sqlalchemy.support import insert_bulk

        method = insert_bulk
    else:
        method = "multi"

    # Load data into database.
    if isinstance(df, pl.DataFrame):
        df = df.to_pandas()
    ddf = dd.from_pandas(df, npartitions=npartitions)
    ddf = ddf.drop(columns="measurement", errors="ignore")
    return ddf.to_sql(
        tablename,
        uri=dburi,
        index=index,
        chunksize=chunksize,
        if_exists=if_exists,
        method=method,
        parallel=True,
    )
