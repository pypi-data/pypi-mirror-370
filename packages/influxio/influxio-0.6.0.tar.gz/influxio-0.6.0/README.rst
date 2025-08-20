########
influxio
########

.. start-badges

|ci-tests| |ci-coverage| |license| |pypi-downloads|

|python-versions| |status| |pypi-version|

.. |ci-tests| image:: https://github.com/daq-tools/influxio/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/daq-tools/influxio/actions/workflows/tests.yml
    :alt: Build status

.. |ci-coverage| image:: https://codecov.io/gh/daq-tools/influxio/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/daq-tools/influxio
    :alt: Coverage

.. |pypi-version| image:: https://img.shields.io/pypi/v/influxio.svg
    :target: https://pypi.org/project/influxio/
    :alt: PyPI Version

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/influxio.svg
    :target: https://pypi.org/project/influxio/
    :alt: Python Version

.. |pypi-downloads| image:: https://static.pepy.tech/badge/influxio/month
    :target: https://www.pepy.tech/projects/influxio
    :alt: PyPI Downloads per month

.. |status| image:: https://img.shields.io/pypi/status/influxio.svg
    :target: https://pypi.org/project/influxio/
    :alt: Status

.. |license| image:: https://img.shields.io/pypi/l/influxio.svg
    :target: https://pypi.org/project/influxio/
    :alt: License

.. end-badges


.. start-links

» `Documentation <project-documentation_>`_
| `Changelog <project-changelog_>`_
| `PyPI <project-pypi_>`_
| `Issues <project-issues_>`_
| `Source code <project-source_>`_
| `License <project-license_>`_

.. end-links


.. _project-documentation: https://influxio.readthedocs.io
.. _project-changelog: https://github.com/daq-tools/influxio/blob/main/CHANGES.rst
.. _project-pypi: https://pypi.org/project/influxio/
.. _project-issues: https://github.com/daq-tools/influxio/issues
.. _project-source: https://github.com/daq-tools/influxio
.. _project-license: https://github.com/daq-tools/influxio/blob/main/LICENSE


*****
About
*****

You can use ``influxio`` to import and export data into/from InfluxDB.
It can be used both as a standalone program, and as a library.

``influxio`` is, amongst others, based on the excellent `dask`_, `fsspec`_,
`influxdb-client`_, `influx-line`_, `line-protocol-parser`_, `pandas`_,
`Polars`_, and `SQLAlchemy`_ packages.


********
Synopsis
********

.. code-block:: shell

    # Export from API to database.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "sqlite://export.sqlite?table=demo"

    # Export from data directory to line protocol format.
    influxio copy \
        "file:///path/to/influxdb/engine?bucket-id=372d1908eab801a6&measurement=demo" \
        "file://export.lp"


**********
Quickstart
**********

If you are in a hurry, and want to run ``influxio`` without any installation,
just use the OCI image on Podman or Docker.

.. code-block:: shell

    docker run --rm --network=host ghcr.io/daq-tools/influxio \
        influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "crate://crate@localhost:4200/testdrive/demo"


*****
Setup
*****

Install ``influxio`` from PyPI.

.. code-block:: shell

    pip install influxio


*****
Usage
*****

This section outlines some example invocations of ``influxio``, both on the
command line, and per library use. Other than the resources available from
the web, testing data can be acquired from the repository's `testdata`_ folder.

Prerequisites
=============

For properly running some of the example invocations outlined below, you will
need an InfluxDB and a CrateDB server. The easiest way to spin up those
instances is to use Podman or Docker.

Please visit the ``docs/development.rst`` documentation to learn about how to
spin up corresponding sandbox instances on your workstation.

Command line use
================

Help
----

.. code-block:: shell

    influxio --help
    influxio info
    influxio copy --help

Import
------

Import data from different sources into InfluxDB Server.

.. code-block:: shell

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


Export from API
---------------

Export data from InfluxDB Server into different sinks.

.. code-block:: shell

    # From API to database file.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "sqlite:///export.sqlite?table=demo"

    # From API to database server.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "crate://crate@localhost:4200/testdrive/demo"

    # From API to line protocol file.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "file://export.lp"

    # From API to line protocol on stdout.
    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "file://-?format=lp"

Load from File
--------------

Load data from InfluxDB files into any SQL database supported by SQLAlchemy.

.. code-block:: shell

    # From local line protocol file to SQLite.
    influxio copy \
        "file://export.lp" \
        "sqlite:///export.sqlite?table=export"

    # From local line protocol file to CrateDB.
    influxio copy \
        "file://export.lp" \
        "crate://crate@localhost:4200/testdrive/demo"

    # From remote line protocol file to SQLite.
    influxio copy \
        "https://github.com/influxdata/influxdb2-sample-data/raw/master/air-sensor-data/air-sensor-data.lp" \
        "sqlite:///export.sqlite?table=air-sensor-data"

    # From remote line protocol file to CrateDB.
    influxio copy \
        "https://github.com/influxdata/influxdb2-sample-data/raw/master/air-sensor-data/air-sensor-data.lp" \
        "crate://crate@localhost:4200/testdrive/demo"


Export from Cloud to Cloud
--------------------------

.. code-block:: shell

    # From InfluxDB Cloud to CrateDB Cloud.
    influxio copy \
        "https://8e9ec869a91a3517:T268DVLDHD8AJsjzOEluu...Pic4A==@eu-central-1-1.aws.cloud2.influxdata.com/testdrive/demo" \
        "crate://admin:dZ,Y18*Z...7)6LqB@green-shaak-ti.eks1.eu-west-1.aws.cratedb.net:4200/testdrive/demo?ssl=true"

    crash \
        --hosts 'https://admin:dZ,Y18*Z...7)6LqB@green-shaak-ti.eks1.eu-west-1.aws.cratedb.net:4200' \
        --command 'SELECT * FROM testdrive.demo;'

Export from data directory
--------------------------

.. code-block:: shell

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
        "file://-?format=lp"


OCI
---

OCI images are available on the GitHub Container Registry (GHCR). In order to
run them on Podman or Docker, invoke:

.. code-block:: shell

    docker run --rm --network=host ghcr.io/daq-tools/influxio \
        influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "stdout://export.lp"

If you want to work with files on your filesystem, you will need to either
mount the working directory into the container using the ``--volume`` option,
or use the ``--interactive`` option to consume STDIN, like:

.. code-block:: shell

    docker run --rm --volume=$(pwd):/data ghcr.io/daq-tools/influxio \
        influxio copy "file:///data/export.lp" "sqlite:///data/export.sqlite?table=export"

    cat export.lp | \
    docker run --rm --interactive --network=host ghcr.io/daq-tools/influxio \
        influxio copy "stdin://?format=lp" "crate://crate@localhost:4200/testdrive/export"

In order to always run the latest ``nightly`` development version, and to use a
shortcut for that, this section outlines how to use an alias for ``influxio``,
and a variable for storing the input URL. It may be useful to save a few
keystrokes on subsequent invocations.

.. code-block:: shell

    docker pull ghcr.io/daq-tools/influxio:nightly
    alias influxio="docker run --rm --interactive ghcr.io/daq-tools/influxio:nightly influxio"
    SOURCE=https://github.com/daq-tools/influxio/raw/main/tests/testdata/basic.lp
    TARGET=crate://crate@localhost:4200/testdrive/basic

    influxio copy "${SOURCE}" "${TARGET}"


InfluxDB parameters
===================

``timeout``
-----------
The network timeout value is specified in seconds, the default value
is 60 seconds. Both details deviate from the standard default setting
of the underlying `InfluxDB client library <influxdb-client>`_, which
uses milliseconds, and a default value of 10_000 milliseconds.

If you need to adjust this setting, add the parameter ``timeout`` to
the InfluxDB URL like this:

.. code-block:: shell

    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo?timeout=300" \
        "crate://crate@localhost:4200/testdrive/demo"


CrateDB parameters
==================

``if-exists``
-------------
When targeting the SQLAlchemy database interface, the target table will be
created automatically, if it does not exist. The ``if-exists`` URL query
parameter can be used to configure this behavior. The default value is
``fail``.

* fail: Raise a ValueError.
* replace: Drop the table before inserting new values.
* append: Insert new values to the existing table.

Example usage:

.. code-block:: shell

    influxio copy \
        "http://example:token@localhost:8086/testdrive/demo" \
        "crate://crate@localhost:4200/testdrive/demo?if-exists=replace"


*******************
Project information
*******************

Contribute
==========
Contributions of all kinds are much very welcome, in order to make the
software more solid.

For installing the project from source, please follow the `development`_
documentation.

Status
======

Breaking changes should be expected until a 1.0 release, so version pinning
is recommended, especially when you use it as a library.

Prior art
=========
There are a few other projects which are aiming at similar goals.

- `InfluxDB Fetcher`_
- `influxdb-write-to-postgresql`_ (IW2PG)
- `Outflux`_


.. _dask: https://www.dask.org/
.. _development: doc/development.rst
.. _fsspec: https://pypi.org/project/fsspec/
.. _influx: https://docs.influxdata.com/influxdb/latest/reference/cli/influx/
.. _influx-line: https://github.com/functionoffunction/influx-line
.. _influxd: https://docs.influxdata.com/influxdb/latest/reference/cli/influxd/
.. _InfluxDB Fetcher: https://github.com/hgomez/influxdb
.. _InfluxDB line protocol: https://docs.influxdata.com/influxdb/latest/reference/syntax/line-protocol/
.. _influxdb-client: https://github.com/influxdata/influxdb-client-python
.. _influxdb-write-to-postgresql: https://github.com/eras/influxdb-write-to-postgresql
.. _line-protocol-parser: https://github.com/Penlect/line-protocol-parser
.. _list of other projects: doc/prior-art.rst
.. _Outflux: https://github.com/timescale/outflux
.. _pandas: https://pandas.pydata.org/
.. _Polars: https://pola.rs/
.. _SQLAlchemy: https://pypi.org/project/SQLAlchemy/
.. _testdata: https://github.com/daq-tools/influxio/tree/main/tests/testdata
