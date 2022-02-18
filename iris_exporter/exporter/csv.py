from diamond_miner.queries import results_table

from iris_exporter.commons.database import get_table_structure, measurement_id
from iris_exporter.exporter.base import Exporter


class CSVExporter(Exporter):
    def export(self, measurement_uuid: str, agent_uuid: str):
        table = results_table(measurement_id(measurement_uuid, agent_uuid))
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
            path=self.path(measurement_uuid, agent_uuid),
            table=table,
            structure=structure,
        )
        self.database.execute(query, params)

    def key(self, measurement_uuid: str, agent_uuid: str) -> str:
        measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
        return f"{measurement_id_}__results.csv.zst"
