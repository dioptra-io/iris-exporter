# iris-exporter

[![Docker](https://img.shields.io/github/workflow/status/dioptra-io/iris-exporter/Docker?logo=github)](https://github.com/dioptra-io/iris-exporter/actions/workflows/docker.yml)

Exporting Iris data to various formats is a data-intensive task that requires to fetch and transform 100GB+ of data per
measurement.
The original approach was to generate all the formats server-side and upload them on S3,
however this was very expensive in terms of compute power and storage.
The current approach is to export a single format, and to let the user convert it to its desired format with
[pantrace](https://github.com/dioptra-io/pantrace).

## Quickstart

```bash
docker run ghcr.io/dioptra-io/iris-exporter:main --help
```

## Development

The default settings of the exporter match the default settings of Iris.
As such, no particular configuration is required to run the exporter against a local instance of Iris.

```bash
# In the iris repository:
docker compose up -d
docker compose exec api .venv/bin/alembic upgrade head
# Ensure that the `public-exports` bucket exists:
# https://docs.min.io/docs/minio-client-quickstart-guide.html
mc alias set docker http://minio.docker.localhost minioadmin minioadmin
mc mb docker/public-exports
# In the iris-exporter repository:
python -m iris_exporter TAG
```
