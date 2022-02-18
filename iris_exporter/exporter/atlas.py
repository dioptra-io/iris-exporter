import json
from pathlib import Path
from tempfile import TemporaryDirectory

from diamond_miner.converters import to_ripe_atlas
from diamond_miner.queries import GetTraceroutes
from zstandard import ZstdCompressor

from iris_exporter.commons.database import measurement_id
from iris_exporter.exporter.base import Exporter


class AtlasExporter(Exporter):
    def export(self, measurement_uuid: str, agent_uuid: str):
        # TODO: Parallelize.
        with TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / self.key(measurement_uuid, agent_uuid)
            ctx = ZstdCompressor()
            with filename.open("wb") as f:
                with ctx.stream_writer(f) as s:
                    query = GetTraceroutes().statement(
                        measurement_id(measurement_uuid, agent_uuid)
                    )
                    rows = self.database.iter_json(query)
                    for row in rows:
                        obj = to_ripe_atlas(measurement_uuid, agent_uuid, **row)
                        line = json.dumps(obj) + "\n"
                        s.write(line.encode("utf-8"))
            self.object(measurement_uuid, agent_uuid).upload_file(str(filename))

    def key(self, measurement_uuid: str, agent_uuid: str) -> str:
        measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
        return f"{measurement_id_}__traceroutes_atlas.jsonl.zst"
