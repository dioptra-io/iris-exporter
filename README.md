# iris-exporter

[![Docker](https://img.shields.io/github/workflow/status/dioptra-io/iris-exporter/Docker?logo=github)](https://github.com/dioptra-io/iris-exporter/actions/workflows/docker.yml)

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

The scripts require the following environment variables.
The default values are set to match the local development environment of Iris.
Note that the native interface of ClickHouse on port 9000 is used, and not the HTTP interface on port 8123.

| Name                          | Default                         |
|-------------------------------|---------------------------------|
| `CLICKHOUSE_HOST`             | `clickhouse.docker.localhost`   |
| `CLICKHOUSE_DATABASE`         | `iris`                          |
| `CLICKHOUSE_USERNAME`         | `iris`                          |
| `CLICKHOUSE_PASSWORD`         | `iris`                          |
| `CLICKHOUSE_MAX_MEMORY_USAGE` | `16Gi`                          |
| `IRIS_BASE_URL`               | `http://api.docker.localhost`   |
| `IRIS_USERNAME`               | `admin@example.org`             |
| `IRIS_PASSWORD`               | `admin`                         |
| `S3_ACCESS_KEY_ID`            | `minioadmin`                    |
| `S3_SECRET_ACCESS_KEY`        | `minioadmin`                    |
| `S3_BUCKET`                   | `public-exports`                |
| `S3_ENDPOINT_URL`             | `http://minio.docker.localhost` |

## Usage

### Exporting a single measurement

```bash
# scripts/iris-exporter-single.sh MEASUREMENT_UUID AGENT_UUID
scripts/iris-exporter-single.sh b1bd513f-1825-4d02-8807-a6c1f1ea0ddf 0d96a984-0839-41fd-ba76-e38b404a0aa6
```

### Exporting multiple measurements in parallel

```bash
# scripts/iris-exporter-multiple.sh LISTFILE
scripts/iris-exporter-multiple.sh measurements.txt
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

### Health check

```bash
scripts/iris-exporter-test.sh
```

## Tests

```bash
# In iris repo
docker compose up -d
```
