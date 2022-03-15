bucket = "iris-exporter"

database_credentials = dict(
    base_url="http://clickhouse.docker.localhost",
    database="default",
    username="default",
)

storage_credentials = dict(
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    endpoint_url="http://minio.docker.localhost",
    region_name="local",
)
