# iris-exporter

TODO: Queue with GNU parallel (+maxmem option).

## Usage

TODO: Docker compose with example env.

## Design

Exporting Iris data to various formats is a data-intensive task that requires to fetch and transform 100GB+ of data per
measurement. The majority of the work is done by the [iris-converters](https://github.com/dioptra-io/iris-converters).
This repository contains scripts for orchestrating data extraction, transformation and load into S3.
