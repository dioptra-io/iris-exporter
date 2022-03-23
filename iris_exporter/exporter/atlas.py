from pathlib import Path
from tempfile import TemporaryDirectory

import orjson as json
from diamond_miner.converters import to_ripe_atlas
from diamond_miner.queries import GetTraceroutes
from zstandard import ZstdCompressor

from iris_exporter.commons.database import measurement_id
from iris_exporter.exporter.base import Exporter


class AtlasExporter(Exporter):
    def export(self, measurement_uuid: str, agent_uuid: str) -> None:
        with TemporaryDirectory() as tmpdir:
            filename = Path(tmpdir) / "output.jsonl"
            ctx = ZstdCompressor()
            with filename.open("wb") as f, ctx.stream_writer(f) as c:
                rows = GetTraceroutes(round_eq=1).execute_iter(
                    self.database, measurement_id(measurement_uuid, agent_uuid)
                )
                for row in rows:
                    obj = to_ripe_atlas(measurement_uuid, agent_uuid, **row)
                    c.write(json.dumps(obj) + b"\n")
            self.object(measurement_uuid, agent_uuid).upload_file(str(filename))

    def key(self, measurement_uuid: str, agent_uuid: str) -> str:
        measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
        return f"{measurement_id_}__atlas.jsonl.zst"
