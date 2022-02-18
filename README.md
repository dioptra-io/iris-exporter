# iris-exporter

🚧 Work in progress.

```bash
# TODO: Create sample measurement + create bucket
mc alias set docker http://minio.docker.localhost minioadmin minioadmin
mc mb docker/exporter
mc ls docker/exporter
export IRIS_BASE_URL=http://api.docker.localhost IRIS_USERNAME=admin@example.org IRIS_PASSWORD=admin
docker compose --project-name=iris up
docker compose up -d clickhouse minio redis
poetry run python -m iris_exporter.watcher
```

```sql
GRANT SELECT on iris.* TO 'iris-exporter';
GRANT S3 ON *.* TO 'iris-exporter';
```

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::public-exports/*"
            ]
        }
    ]
}
```

## Installation

### Docker 🐳

```bash
docker build -t iris-exporter .
docker run iris-exporter --help
```

### Poetry 🐍

```bash
poetry install
poetry run iris-exporter --help
```
