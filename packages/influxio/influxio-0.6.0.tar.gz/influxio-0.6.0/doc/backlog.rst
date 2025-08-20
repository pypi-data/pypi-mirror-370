#######
Backlog
#######


************
Iteration +1
************
- [o] README: Demonstrate "library use"
- [o] README: Caveat about overwrite protection
- [o] README: How to export from data directory using Docker?
- [o] README: Add examples using InfluxDB Cloud
- [o] README: Caveat when exporting unknown measurement from data directory:
  It can not be detected.
- [o] README: Inform about ``--verbose`` flag
- [o] Publish documentation on RTD
- [o] Add annotated CSV export/import
- [o] Address "TODO" items
- [o] Verify documentation. ``influxio.cli.help_copy``
- [o] More refinements
- [o] ``list-buckets`` subcommand, for both API and data directory
- [o] Progress bars for non-Dask tasks


************
Iteration +2
************
- [o] Fix ``crate.client.sqlalchemy.dialect.DateTime`` re. ``TimezoneUnawareException``
- [o] Support InfluxDB 1.x and 3.x
- [o] Add Docker Compose file for auxiliary services
- [o] Refactor general purpose code to ``pueblo`` package
- [o] Verify import and export of ILP and CSV files works well
- [o] Tests using ``assert_dataframe_equal``? Maybe in ``cratedb-toolkit``?
- [o] fluXpipe adapter
  https://github.com/crate/crate-clients-tools/issues/94


************
Iteration +3
************
- [o] Unlock more parameters in InfluxDbApiAdapter.write_df
- [o] Format: Compressed line protocol
- [o] Format: Annotated CSV
  - https://docs.influxdata.com/influxdb/v2.6/reference/syntax/annotated-csv/
  - https://docs.influxdata.com/influxdb/v2.6/reference/syntax/annotated-csv/extended/
- [o] Backends: python, cmdline, flux
- [o] InfluxDB 1.x subscriptions?
- [o] cloud-to-cloud copy
- [o] influxio list testdata://
- [o] "SQLAlchemy » Dialects built-in" is broken
- [o] ``DBURI = "crate+psycopg://localhost:4200"``
- [o] Use Podman instead of Docker

References
==========
- https://docs.influxdata.com/influxdb/v2.6/migrate-data/
- https://docs.influxdata.com/influxdb/v2.6/reference/cli/influx/write/
- https://docs.influxdata.com/influxdb/v2.6/reference/cli/influx/backup/
- https://docs.influxdata.com/influxdb/v2.6/reference/cli/influx/export/
- https://github.com/influxdata/flux/blob/e513f1483/stdlib/sql/sql_test.flux#L119-L173
- https://github.com/influxdata/flux/blob/e513f1483/stdlib/universe/universe.flux#L1159-L1176
- https://github.com/influxdata/flux/blob/e513f1483/stdlib/sql/to.go#L525


****
Done
****
- [x] Add project boilerplate
- [x] Make it work
- [x] Export to SQLite, PostgreSQL, and CrateDB
- [x] Fix documentation about crate:// target
- [x] Check if using a CrateDB schema works well
- [x] Release 0.1.0
- [x] Fix ``.from_lineprotocol``
- [x] Parameters bucket-id and measurement are obligatory on data
  directory export. Verify that.
- [x] Be ``--verbose`` by default
