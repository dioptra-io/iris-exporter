from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

import orjson as json
from diamond_miner.converters import to_ripe_atlas
from diamond_miner.queries import GetTraceroutes
from diamond_miner.subsets import subsets_for
from diamond_miner.typing import IPNetwork
from pych_client import ClickHouseClient
from zstandard import ZstdCompressor

from iris_exporter.commons.database import measurement_id
from iris_exporter.commons.io import concatenate
from iris_exporter.exporter.base import Exporter


class AtlasExporter(Exporter):
    def export(self, measurement_uuid: str, agent_uuid: str) -> None:
        measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
        subsets = subsets_for(GetTraceroutes(), self.database, measurement_id_)

        with TemporaryDirectory() as tmpdir:
            files = [Path(tmpdir) / f"subset_{i}" for i in range(len(subsets))]
            with ProcessPoolExecutor() as executor:
                for subset, file in zip(subsets, files):
                    executor.submit(
                        self.export_subset,
                        self.database_credentials,
                        measurement_uuid,
                        agent_uuid,
                        subset,
                        file,
                    )

            destination = Path(tmpdir) / "merged"
            concatenate(files, destination)
            self.object(measurement_uuid, agent_uuid).upload_file(str(destination))

    @staticmethod
    def export_subset(
        database_credentials: dict,
        measurement_uuid: str,
        agent_uuid: str,
        subset: IPNetwork,
        destination: Path,
    ) -> None:
        # NOTE: We cannot pickle httpx client instances, so we pass the credentials
        # instead, and instantiate the database client inside the function.
        database = ClickHouseClient(**database_credentials)
        ctx = ZstdCompressor()
        with destination.open("wb") as f, ctx.stream_writer(f) as c:
            rows = GetTraceroutes().execute_iter(
                database,
                measurement_id(measurement_uuid, agent_uuid),
                subsets=(subset,),
            )
            for row in rows:
                obj = to_ripe_atlas(measurement_uuid, agent_uuid, **row)
                c.write(json.dumps(obj) + b"\n")

    def key(self, measurement_uuid: str, agent_uuid: str) -> str:
        measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
        return f"{measurement_id_}__atlas.jsonl.zst"
