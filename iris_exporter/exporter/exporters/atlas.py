import json
from pathlib import Path
from tempfile import TemporaryDirectory

from diamond_miner.converters import to_ripe_atlas
from diamond_miner.queries import GetTraceroutes
from zstandard import ZstdCompressor

from iris_exporter.exporter.exporters.base import Exporter


class AtlasExporter(Exporter):
    """
    # TODO: Generic test for all exporters in tests/.
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
