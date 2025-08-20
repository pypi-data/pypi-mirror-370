import io
import json
import logging
import sys
import typing as t
from pathlib import Path

import influxdb_client.rest
import pandas as pd
import polars as pl
import psycopg2
import sqlalchemy
import sqlalchemy as sa
from fsspec import filesystem
from influxdb_client import InfluxDBClient
from sqlalchemy_utils import create_database
from upath import UPath
from yarl import URL

from influxio.io import dataframe_to_lineprotocol, dataframe_to_sql, dataframes_from_lineprotocol
from influxio.model import CommandResult, DataFormat, OutputFile
from influxio.util.common import run_command, url_fullpath

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0


class InfluxDbApiAdapter:
    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        bucket: str,
        measurement: str,
        debug: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.measurement = measurement
        self.debug = debug
        self.timeout = timeout
        self.client = InfluxDBClient(
            url=self.url, org=self.org, token=self.token, debug=self.debug, timeout=int(self.timeout * 1000.0)
        )

    @classmethod
    def from_url(cls, url: t.Union[URL, str], **kwargs) -> "InfluxDbApiAdapter":
        if isinstance(url, str):
            url: URL = URL(url)
        token = url.password
        org = url.user
        try:
            bucket, measurement = url.path.strip("/").split("/")
        except ValueError:
            bucket = url.path.strip("/").split("/")[0]
            measurement = None
        bare_url = f"{url.scheme}://{url.host}:{url.port}"
        kwargs.setdefault("timeout", float(url.query.get("timeout", DEFAULT_TIMEOUT)))
        return cls(url=bare_url, token=token, org=org, bucket=bucket, measurement=measurement, **kwargs)

    def delete_measurement(self):
        """
        https://docs.influxdata.com/influxdb/cloud/write-data/delete-data/
        """
        try:
            return self.client.delete_api().delete(
                start="1677-09-21T00:12:43.145224194Z",
                stop="2262-04-11T23:47:16.854775806Z",
                predicate=f'_measurement="{self.measurement}"',
                bucket=self.bucket,
            )
        except influxdb_client.rest.ApiException as ex:
            if ex.status != 404:
                raise

    def read_df(self):
        """ """
        query = f"""
        from(bucket:"{self.bucket}")
            |> range(start: 0, stop: now())
            |> filter(fn: (r) => r._measurement == "{self.measurement}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
        #
        for df in self.client.query_api().query_data_frame_stream(query=query):
            df = df.drop(["result", "table", "_start", "_stop"], axis=1)
            df = df.rename(columns={"_time": "time", "_measurement": "measurement"})
            yield df

    def read_records(self, bucket: t.Optional[str] = None, measurement: t.Optional[str] = None) -> t.Dict[str, t.Any]:
        bucket = bucket or self.bucket
        measurement = measurement or self.measurement
        query = f"""
            from(bucket: "{bucket}")
                |> range(start: 0)
                |> filter(fn: (r) => r._measurement == "{measurement}")
            """
        result = self.client.query_api().query(query=query)
        return json.loads(result.to_json())

    def ensure_bucket(self):
        try:
            self.client.buckets_api().create_bucket(bucket_name=self.bucket)
        except influxdb_client.rest.ApiException as ex:
            if ex.status == 422:
                pass
            else:
                raise
        logger.info(f"Bucket id is {self.get_bucket_id()}")

    def delete_bucket(self, missing_ok: bool = True):
        """
        https://docs.influxdata.com/influxdb/v2/admin/buckets/delete-bucket/
        """
        try:
            bucket_id = self.get_bucket_id()
        except KeyError:
            if missing_ok:
                return
            else:
                raise
        try:
            self.client.buckets_api().delete_bucket(bucket_id)
        except influxdb_client.rest.ApiException as ex:
            if ex.status == 404 and missing_ok:
                pass
            else:
                raise

    def write_df(self, df: pd.DataFrame):
        """
        Use batching API to import data frame into InfluxDB.

        https://github.com/influxdata/influxdb-client-python/blob/master/examples/ingest_large_dataframe.py

        TODO: Add precision.
        """
        logger.info(f"Importing data frame to InfluxDB. bucket={self.bucket}, measurement={self.measurement}")
        self.ensure_bucket()
        with self.client.write_api() as write_api:
            write_api.write(
                bucket=self.bucket,
                record=df,
                data_frame_measurement_name=self.measurement,
                # TODO: Add more parameters.
                # write_precision=WritePrecision.MS,  # noqa: ERA001
                # data_frame_tag_columns=['tag'],  # noqa: ERA001
            )

    def from_lineprotocol(self, source: t.Union[Path, str], precision: str = "ns"):
        """
        Import data from file in lineprotocol format (ILP) by invoking `influx write`.

        Precision of the timestamps of the lines (default: ns) [$INFLUX_PRECISION]

        The default precision for timestamps is in nanoseconds. If the precision of
        the timestamps is anything other than nanoseconds (ns), you must specify the
        precision in your write request. InfluxDB accepts the following precisions:

            ns - Nanoseconds
            us - Microseconds
            ms - Milliseconds
            s - Seconds

        -- https://docs.influxdata.com/influxdb/cloud/write-data/developer-tools/line-protocol/
        """
        is_url = False
        try:
            URL(source)
            is_url = True
        except Exception:  # noqa: S110
            pass

        logger.info(f"Importing line protocol format to InfluxDB. bucket={self.bucket}")
        self.ensure_bucket()

        if is_url:
            source_option = f'--url="{str(source)}"'
        else:
            source_option = f'--file="{str(source)}"'
        command = f"""
        influx write \
            --host="{self.url}" \
            --token="{self.token}" \
            --org="{self.org}" \
            --bucket="{self.bucket}" \
            --precision={precision} \
            --format=lp \
            {source_option}
        """
        # print("command:", command)  # noqa: ERA001
        run_command(command)

    @property
    def bucket_id(self) -> str:
        return self.get_bucket_id()

    def get_bucket_id(self) -> str:
        """
        Resolve bucket name to bucket id.
        """
        bucket: influxdb_client.Bucket = self.client.buckets_api().find_bucket_by_name(bucket_name=self.bucket)
        if bucket is None:
            raise KeyError(f"Bucket not found: {self.bucket}")
        return bucket.id


class InfluxDbEngineAdapter:
    def __init__(self, path: t.Union[Path, str], bucket_id: str, measurement: str, debug: bool = False):

        if isinstance(path, str):
            path: Path = Path(path)

        self.path = path
        self.bucket_id = bucket_id
        self.measurement = measurement
        self.debug = debug

    @classmethod
    def from_url(cls, url: t.Union[URL, str], **kwargs) -> "InfluxDbEngineAdapter":
        if isinstance(url, str):
            url: URL = URL(url)
        return cls(
            path=url_fullpath(url),
            bucket_id=url.query.get("bucket-id"),
            measurement=url.query.get("measurement"),
            **kwargs,
        )

    def to_lineprotocol(self, url: t.Union[URL, str]) -> CommandResult:
        """
        Export data into lineprotocol format (ILP) by invoking `influxd inspect export-lp`.

        TODO: Unify with `FileAdapter` sink and expand with `InfluxDbApiAdapter`'s API connectivity.
        TODO: Using a hyphen `-` for `--output-path` works well now, so export can also go to stdout.
        TODO: By default, it will *append* to the .lp file.
              Make it configurable to "replace" data.
        TODO: Make it configurable to use compression, or not.
        TODO: Propagate `--start` and `--end` parameters.
        TODO: Capture stderr messages, and forward user admonition.
              »detected deletes in WAL file, some deleted data may be brought back by replaying this export«
              -- https://github.com/influxdata/influxdb/issues/24456

        https://docs.influxdata.com/influxdb/v2.6/migrate-data/migrate-oss/
        """
        if isinstance(url, str):
            url: URL = URL(url)
        format_ = DataFormat.from_url(url)
        logger.info(f"Exporting data to InfluxDB line protocol format (ILP): {format_}")
        command = f"""
        influxd inspect export-lp \
            --engine-path '{self.path}' \
            --bucket-id '{self.bucket_id}' \
            --measurement '{self.measurement}' \
            --output-path '{url_fullpath(url)}'
        """.rstrip()
        if format_ is DataFormat.LINE_PROTOCOL_COMPRESSED:
            command += " --compress"
        out = run_command(command)

        stderr = out.stderr.decode("utf-8")

        # Decode output of `influxd inspect export-lp`.
        """
        {"level":"info","ts":1712536769.359062,"caller":"export_lp/export_lp.go:219","msg":"exporting TSM files","tsm_dir":"var/lib/influxdb2/engine/data/372d1908eab801a6","file_count":3}
        {"level":"info","ts":1712536769.3782709,"caller":"export_lp/export_lp.go:315","msg":"exporting WAL files","wal_dir":"var/lib/influxdb2/engine/wal/372d1908eab801a6","file_count":3}
        {"level":"info","ts":1712536769.3783438,"caller":"export_lp/export_lp.go:204","msg":"export complete"}
        """  # noqa: E501
        if format_ in [DataFormat.LINE_PROTOCOL_UNCOMPRESSED, DataFormat.LINE_PROTOCOL_COMPRESSED]:
            report = pd.read_json(path_or_buf=io.StringIO(stderr), lines=True).to_dict(orient="records")
            tsm_file_count = report[0]["file_count"]
            wal_file_count = report[1]["file_count"]
            if tsm_file_count == 0 and wal_file_count == 0:
                raise FileNotFoundError(r"Export yielded zero records. Make sure to use a valid bucket-id.")
        else:
            raise NotImplementedError(f"Format is not supported: {format_}")
        if out.stdout:
            sys.stdout.buffer.write(out.stdout)
        return CommandResult(stderr=stderr, exitcode=out.returncode)


class SqlAlchemyAdapter:
    """
    Adapter to talk to SQLAlchemy-compatible databases.
    """

    def __init__(self, url: t.Union[URL, str], progress: bool = False, debug: bool = False):
        self.progress = progress

        if isinstance(url, str):
            url: URL = URL(url)

        self.database, self.table = self.decode_database_table(url)
        self.if_exists = url.query.get("if-exists")

        # Special handling for SQLite and CrateDB databases.
        self.dburi = str(url.with_query(None))
        if url.scheme == "crate":
            query_args_passthrough = ["ssl"]
            query = url.query
            url = url.with_path("")
            if self.database:
                url = url.update_query({"schema": self.database})
                for arg in query_args_passthrough:
                    if arg in query:
                        url = url.update_query({arg: query[arg]})
            self.dburi = str(url)
        elif url.scheme == "sqlite":
            self.dburi = self.dburi.replace("sqlite:/", "sqlite:///")
        else:
            url = url.with_path(self.database)
            self.dburi = str(url)

        logger.info(f"SQLAlchemy DB URI: {self.dburi}")

    @classmethod
    def from_url(cls, url: t.Union[URL, str], **kwargs) -> "SqlAlchemyAdapter":
        return cls(url=url, **kwargs)

    def write(self, source: t.Union[pd.DataFrame, InfluxDbApiAdapter], table: t.Optional[str] = None):
        table = table or self.table
        logger.info("Loading dataframes into RDBMS/SQL database using pandas/Dask")
        if isinstance(source, InfluxDbApiAdapter):
            for df in source.read_df():
                dataframe_to_sql(
                    df, dburi=self.dburi, tablename=table, if_exists=self.if_exists, progress=self.progress
                )
        elif isinstance(source, (pd.DataFrame, pl.DataFrame)):
            dataframe_to_sql(
                source, dburi=self.dburi, tablename=table, if_exists=self.if_exists, progress=self.progress
            )
        else:
            raise NotImplementedError(f"Failed handling source: {source}")

    def refresh_table(self):
        engine = sa.create_engine(self.dburi)
        with engine.connect() as connection:
            return connection.execute(sa.text(f"REFRESH TABLE {self.table};"))

    def read_records(self, table: t.Optional[str] = None) -> t.List[t.Dict]:
        table = table or self.table
        engine = sa.create_engine(self.dburi)
        with engine.connect() as connection:
            result = connection.execute(sa.text(f"SELECT * FROM {table};"))  # noqa: S608
            records = [dict(item) for item in result.mappings().fetchall()]
            return records

    def create_database(self):
        try:
            return create_database(self.dburi)
        except sqlalchemy.exc.ProgrammingError as ex:
            if "psycopg2.errors.DuplicateDatabase" not in str(ex):
                raise

    def run_sql(self, sql: str):
        engine = sa.create_engine(self.dburi)
        with engine.connect() as connection:
            if hasattr(connection.connection, "set_isolation_level"):
                connection.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            return connection.execute(sa.text(sql))

    def run_sql_raw(self, sql: str):
        engine = sa.create_engine(self.dburi)
        connection = engine.raw_connection()
        if hasattr(connection, "set_isolation_level"):
            connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    @staticmethod
    def decode_database_table(url: URL):
        """
        Decode database and table names from database URI path and/or query string.

        Variants:

            /<database>/<table>
            ?database=<database>&table=<table>
            ?schema=<database>&table=<table>
        """
        try:
            database, table = url.path.strip("/").split("/")
        except ValueError as ex:
            if "too many values to unpack" not in str(ex) and "not enough values to unpack" not in str(ex):
                raise
            database = url.query.get("database")
            table = url.query.get("table")
            if url.scheme == "crate" and not database:
                database = url.query.get("schema")
        return database, table

    def from_lineprotocol(self, source: t.Union[Path, str], precision: str = "ns"):
        """
        Load data from file or resource in lineprotocol format (ILP).
        """
        logger.info(f"Loading line protocol data. source={source}")
        p = UPath(source)
        fs = filesystem(p.protocol, **p.storage_options)  # equivalent to p.fs
        with fs.open(p.path) as fp:
            frames = dataframes_from_lineprotocol(fp)
            for table, df in frames.items():
                self.write(df, table=table)


class FileAdapter:
    """
    Adapter for pipelining data in and out of files.
    """

    def __init__(self, url: t.Union[URL, str], progress: bool = False, debug: bool = False):
        self.progress = progress

        if isinstance(url, str):
            url: URL = URL(url)

        self.output = OutputFile.from_url(url)

    @classmethod
    def from_url(cls, url: t.Union[URL, str], **kwargs) -> "FileAdapter":
        """
        Factory to create a `FileAdapter` instance from a URL.
        """
        return cls(url=url, **kwargs)

    def write(self, source: t.Union[pd.DataFrame, InfluxDbApiAdapter]):
        """
        Export data from a pandas DataFrame or from an API-connected InfluxDB database into lineprotocol format (ILP).
        """
        logger.info(f"Exporting dataframes in {self.output.format.value} format to {self.output.path}")
        generators = []
        if self.output.format is DataFormat.LINE_PROTOCOL_UNCOMPRESSED:
            if isinstance(source, InfluxDbApiAdapter):
                for df in source.read_df():
                    generators.append(dataframe_to_lineprotocol(df, progress=self.progress))
            elif isinstance(source, pd.DataFrame):
                generators.append(dataframe_to_lineprotocol(source, progress=self.progress))
            else:
                raise NotImplementedError(f"Unknown data source: {source}")
        else:
            raise NotImplementedError(f"File output format not implemented: {self.output.format}")
        for generator in generators:
            print("\n".join(generator), file=self.output.stream)
