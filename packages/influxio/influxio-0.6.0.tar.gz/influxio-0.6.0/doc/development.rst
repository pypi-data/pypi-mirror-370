.. _development:
.. _sandbox:

###########
Development
###########


*******
Sandbox
*******

Source Code
===========

Acquire sources, create Python virtualenv, install package and dependencies,
and run software tests::

    git clone https://github.com/daq-tools/influxio
    cd influxio
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --use-pep517 --prefer-binary --editable=.[test,develop,release]

Services
========

For properly running the test cases, you will need running instances of InfluxDB,
PostgreSQL, and CrateDB. The easiest way to spin up those instances is to use
Docker or Podman.

InfluxDB
--------
.. code-block:: shell

    docker run --rm -it --publish=8086:8086 \
        --env=DOCKER_INFLUXDB_INIT_MODE=setup \
        --env=DOCKER_INFLUXDB_INIT_USERNAME=admin \
        --env=DOCKER_INFLUXDB_INIT_PASSWORD=secret1234 \
        --env=DOCKER_INFLUXDB_INIT_ORG=example \
        --env=DOCKER_INFLUXDB_INIT_BUCKET=default \
        --env=DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=token \
        --volume="$PWD/var/lib/influxdb2:/var/lib/influxdb2" \
        influxdb:2.7

- https://github.com/docker-library/docs/blob/master/influxdb/README.md

CrateDB
-------
.. code-block:: shell

    docker run --rm -it --publish=4200:4200 \
        --volume="$PWD/var/lib/cratedb:/data" \
        crate:latest -Cdiscovery.type=single-node

- https://github.com/docker-library/docs/blob/master/crate/README.md

PostgreSQL
----------
.. code-block:: shell

    docker run --rm -it --publish=5432:5432 \
        --env "POSTGRES_HOST_AUTH_METHOD=trust" postgres:16 \
        postgres -c log_statement=all

Software Tests
==============
Invoke software tests::

    # Run linter and regular test suite.
    poe check


****************
Build OCI images
****************

OCI images will be automatically published to the GitHub Container Registry
(GHCR), see `influxio packages on GHCR`_. If you want to build images on your
machine, you can use those commands::

    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
    export BUILDKIT_PROGRESS=plain
    docker build --tag local/influxio --file release/oci/Dockerfile .

::

    docker run --rm -it local/influxio influxio --version
    docker run --rm -it local/influxio influxio info


.. _influxio packages on GHCR: https://github.com/orgs/daq-tools/packages?repo_name=influxio
