from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    clickhouse_base_url: str = "http://clickhouse.docker.localhost"
    clickhouse_database: str = "iris"
    clickhouse_username: str = "default"
    clickhouse_password: str = ""
    iris_base_url: str = "http://api.docker.localhost"
    iris_username: str = "admin@example.org"
    iris_password: str = "admin"
    redis_url: str = "redis://default:iris@redis.docker.localhost:6379"
    redis_namespace: str = "iris-exporter"
    s3_bucket: str = "iris-exporter"
    s3_endpoint_url: str = "http://minio.docker.localhost"
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_region_name: str = "local"
    tag: str = "!public"
    watch_interval: int = 5  # seconds
    working_directory: Path = Path()
