import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3.service_resource import Object
from pych_client import ClickHouseClient


class Exporter:
    def __init__(
        self, database_credentials: dict, storage_credentials: dict, bucket_name: str
    ) -> None:
        self.database = ClickHouseClient(**database_credentials)
        self.database_credentials = database_credentials
        self.storage = boto3.resource("s3", **storage_credentials)
        self.storage_credentials = storage_credentials
        self.bucket_name = bucket_name

    def delete(self, measurement_uuid: str, agent_uuid: str) -> None:
        self.object(measurement_uuid, agent_uuid).delete()

    def exists(self, measurement_uuid: str, agent_uuid: str) -> bool:
        try:
            self.object(measurement_uuid, agent_uuid).load()
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise
        return False

    def export(self, measurement_uuid: str, agent_uuid: str) -> None:
        raise NotImplementedError

    def object(self, measurement_uuid: str, agent_uuid: str) -> Object:
        bucket = self.storage.Bucket(self.bucket_name)
        return bucket.Object(self.key(measurement_uuid, agent_uuid))

    def key(self, measurement_uuid: str, agent_uuid: str) -> str:
        raise NotImplementedError

    def path(self, measurement_uuid: str, agent_uuid: str) -> str:
        return "/".join(
            (
                self.storage_credentials["endpoint_url"],
                self.bucket_name,
                self.key(measurement_uuid, agent_uuid),
            )
        )
