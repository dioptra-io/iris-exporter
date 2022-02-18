from diamond_miner.queries import results_table

from iris_exporter.exporter.exporters.base import Exporter
from iris_exporter.exporter.helpers import get_table_structure


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
