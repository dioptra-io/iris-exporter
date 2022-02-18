import boto3
from pych_client import ClickHouseClient

bucket = "test-bucket"

database_credentials = dict(
    base_url="http://clickhouse.docker.localhost",
    database="default",
    username="default",
)

# TODO: Remove
database = ClickHouseClient(**database_credentials)

storage_credentials = dict(
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    endpoint_url="http://minio.docker.localhost",
    region_name="local",
)

# TODO: Remove
storage = boto3.resource("s3", **storage_credentials)
