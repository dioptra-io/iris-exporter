# iris-exporter

## Design

Exporting Iris data to various formats is a data-intensive task that requires to fetch and transform 100GB+ of data per measurement.
The bulk of the work is done by [pantrace](https://github.com/dioptra-io/pantrace).
This repository contains scripts for orchestrating data extraction, transformation and load into S3.

## Installation

### Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Docker

```bash
docker run ghcr.io/dioptra-io/iris-exporter:main scripts/...
```

## Configuration

The scripts require the following environment variables:

Name                          | Default
------------------------------|--------
`AWS_S3_ENDPOINT_URL`         | -
`AWS_S3_BUCKET`               | -
`CLICKHOUSE_MAX_MEMORY_USAGE` | `16Gi`
`CLICKHOUSE_DATABASE`         | `default`
`CLICKHOUSE_HOST`             | `localhost`
`CLICKHOUSE_USERNAME`         | `default`
`CLICKHOUSE_PASSWORD`         | -
`IRIS_BASE_URL`               | -
`IRIS_USERNAME`               | -
`IRIS_PASSWORD`               | -

Note that the scripts use the native interface of ClickHouse on port 9000, and not the HTTP interface on port 8123.

## Usage

### Exporting a single measurement

```bash
# scripts/iris-exporter-single.sh MEASUREMENT_UUID AGENT_UUID
scripts/iris-exporter-single.sh b1bd513f-1825-4d02-8807-a6c1f1ea0ddf 0d96a984-0839-41fd-ba76-e38b404a0aa6
```

### Exporting multiple measurements in parallel

```bash
# scripts/iris-exporter-all.sh LISTFILE
scripts/iris-exporter-all.sh measurements.txt
```

where `measurements.txt` is a list of measurement and agent UUIDs:
```
b1bd513f-1825-4d02-8807-a6c1f1ea0ddf 0d96a984-0839-41fd-ba76-e38b404a0aa6
b1bd513f-1825-4d02-8807-a6c1f1ea0ddf 23eef902-d1bf-49e3-bd45-d4b8148d539f
b1bd513f-1825-4d02-8807-a6c1f1ea0ddf fda938ce-bed2-4fbf-979a-d5d5cf609034
```

### Generating a list of measurements

```bash
# scripts/iris-exporter-list.py --tag TAG
scripts/iris-exporter-list.py --tag visibility:public > measurements.txt
```
