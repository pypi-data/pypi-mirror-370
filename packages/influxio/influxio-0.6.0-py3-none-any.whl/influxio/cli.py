import logging

import click

import influxio.core
from influxio.util.cli import boot_click, docstring_format_verbatim
from influxio.util.report import AboutReport

logger = logging.getLogger(__name__)


def help_copy():
    """
    Import and export data into/from InfluxDB

    SOURCE can be a file or a URL.
    TARGET can be a file or a URL.

    Synopsis
    ========

    # Export from API to database.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "sqlite://export.sqlite?table=demo"

    # Export from data directory to line protocol format.
    influxio copy \
        "file:///path/to/influxdb/engine?bucket-id=372d1908eab801a6&measurement=demo" \
        "file://export.lp"

    Examples
    ========

    Export from API
    ---------------

    # From API to database file.
    influxio copy \
        http://example:token@localhost:8086/testdrive/demo \
        sqlite:///export.sqlite

    # From API to database server.
    influxio copy \
        http://example:token@localhost:8086/testdrive/demo \
        crate://crate@localhost:4200/testdrive

    # From API to line protocol file.
    influxio copy \
        http://example:token@localhost:8086/testdrive/demo \
        file://export.lp

    # From API to line protocol on stdout.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "file://-?format=lp"

    Export from data directory
    --------------------------

    # From InfluxDB data directory to line protocol file.
    influxio copy \
        "file:///path/to/influxdb/engine?bucket-id=372d1908eab801a6&measurement=demo" \
        "file://export.lp"

    # From InfluxDB data directory to line protocol file, compressed with gzip.
    influxio copy \
        "file:///path/to/influxdb/engine?bucket-id=372d1908eab801a6&measurement=demo" \
        "file://export.lp.gz"

    # From InfluxDB data directory to line protocol on stdout.
    influxio copy \
        "file:///path/to/influxdb/engine?bucket-id=372d1908eab801a6&measurement=demo" \
        ""file://-?format=lp"

    Convert from file
    -----------------

    # From line protocol file to database.
    influxio copy \
        "file://export.lp" \
        "sqlite://export.sqlite?table=export"


    Import
    ------

    # From test data to API.
    # Choose one of dummy, mixed, dateindex, wide.
    influxio copy \
        "testdata://dateindex/" \
        "http://example:token@localhost:8086/testdrive/demo"

    # With selected amount of rows.
    influxio copy \
        "testdata://dateindex/?rows=42" \
        "http://example:token@localhost:8086/testdrive/demo"

    # With selected amount of rows and columns (only supported by certain test data sources).
    influxio copy \
        "testdata://wide/?rows=42&columns=42" \
        "http://example:token@localhost:8086/testdrive/demo"

    # From line protocol file to InfluxDB API.
    influxio copy \
        "file://tests/testdata/basic.lp" \
        "http://example:token@localhost:8086/testdrive/demo"

    # From line protocol file to InfluxDB API.
    influxio copy \
        "https://github.com/influxdata/influxdb2-sample-data/raw/master/air-sensor-data/air-sensor-data.lp" \
        "http://example:token@localhost:8086/testdrive/demo"

    # From line protocol file to any database supported by SQLAlchemy.
    influxio copy \
        "file://export.lp" \
        "sqlite://export.sqlite?table=export"

    Documentation
    =============

    More options and examples can be discovered on the influxio README [1].

    [1] https://github.com/daq-tools/influxio/blob/main/README.rst
    """  # noqa: E501


@click.group()
@click.version_option(package_name="influxio")
@click.option("--verbose", is_flag=True, required=False, default=True, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot_click(ctx, verbose, debug)


@cli.command("info", help="Report about platform information")
def info():
    AboutReport.platform()


@cli.command(
    "copy",
    help=docstring_format_verbatim(help_copy.__doc__),
    context_settings={"max_content_width": 120},
)
@click.argument("source", type=str, required=True)
@click.argument("target", type=str, required=True)
@click.pass_context
def copy(ctx: click.Context, source: str, target: str):
    influxio.core.copy(source, target)
    logger.info("Ready.")
