import json
from pathlib import Path
from tempfile import TemporaryDirectory

import boto3
from botocore.exceptions import ClientError
from diamond_miner.converters import to_ripe_atlas
from diamond_miner.queries import GetTraceroutes, results_table
from mypy_boto3_s3.service_resource import Object
from pych_client import ClickHouseClient
from zstandard import ZstdCompressor

from iris_exporter.exporter.helpers import get_table_structure


class Exporter:
    def __init__(
        self, database_credentials: dict, storage_credentials: dict, bucket_name: str
    ):
        self.database = ClickHouseClient(**database_credentials)
        self.storage = boto3.resource("s3", **storage_credentials)
        self.storage_credentials = storage_credentials
        self.bucket_name = bucket_name

    def delete(self, measurement_id: str):
        self.object(measurement_id).delete()

    def exists(self, measurement_id: str) -> bool:
        try:
            self.object(measurement_id).load()
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                raise
        return False

    def export(self, measurement_id: str):
        raise NotImplementedError

    def object(self, measurement_id: str) -> Object:
        bucket = self.storage.Bucket(self.bucket_name)
        return bucket.Object(self.key(measurement_id))

    def key(self, measurement_id: str) -> str:
        raise NotImplementedError

    def path(self, measurement_id: str) -> str:
        return "/".join(
            (
                self.storage_credentials["endpoint_url"],
                self.bucket_name,
                self.key(measurement_id),
            )
        )


class AtlasExporter(Exporter):
    """
    >>> from iris_exporter.test import bucket, database_credentials, storage_credentials
    >>> exporter = AtlasExporter(database_credentials, storage_credentials, bucket)
    >>> exporter.delete("test_nsdi_example")
    >>> exporter.exists("test_nsdi_example")
    False
    >>> exporter.export("test_nsdi_example")
    >>> exporter.exists("test_nsdi_example")
    True
    """

    def export(self, measurement_id: str):
        # TODO: Parallelize.
        with TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / self.key(measurement_id)
            ctx = ZstdCompressor()
            with filename.open("wb") as f:
                with ctx.stream_writer(f) as s:
                    query = GetTraceroutes().statement(measurement_id)
                    rows = self.database.iter_json(query)
                    for row in rows:
                        # TODO: Use measurement_uuid, agent_uuid in exporter.
                        obj = to_ripe_atlas("TODO", "TODO", **row)
                        line = json.dumps(obj) + "\n"
                        s.write(line.encode("utf-8"))
            self.object(measurement_id).upload_file(str(filename))

    def key(self, measurement_id: str) -> str:
        return f"{measurement_id}__traceroutes_atlas.jsonl.zst"


class CSVExporter(Exporter):
    """
    >>> from iris_exporter.test import bucket, database_credentials, storage_credentials
    >>> exporter = CSVExporter(database_credentials, storage_credentials, bucket)
    >>> exporter.delete("test_nsdi_example")
    >>> exporter.exists("test_nsdi_example")
    False
    >>> exporter.export("test_nsdi_example")
    >>> exporter.exists("test_nsdi_example")
    True
    """

    def export(self, measurement_id: str):
        table = results_table(measurement_id)
        structure = get_table_structure(self.database, table)
        query = """
        INSERT INTO FUNCTION s3(
            {path:String},
            {aws_access_key_id:String},
            {aws_secret_access_key:String},
            'CSVWithNames',
            {structure:String},
            'zstd'
        )
        SELECT * FROM {table:Identifier}
        """
        params = dict(
            **self.storage_credentials,
            path=self.path(measurement_id),
            table=results_table(measurement_id),
            structure=structure,
        )
        self.database.execute(query, params)

    def key(self, measurement_id: str) -> str:
        return f"{measurement_id}__results.csv.zst"
