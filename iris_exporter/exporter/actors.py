import dramatiq
import redis

from iris_exporter.commons.exclusive import exclusive
from iris_exporter.commons.logger import logger
from iris_exporter.commons.settings import Settings
from iris_exporter.exporter.atlas import AtlasExporter
from iris_exporter.exporter.csv import CSVExporter

settings = Settings()
redis_client = redis.from_url(settings.redis_url)

# NOTE: We do not retry failed actors as they will be re-scheduled by the watcher.


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_results(
    database_credentials: dict,
    storage_credentials: dict,
    bucket_name: str,
    measurement_uuid: str,
    agent_uuid: str,
) -> None:
    logger.info(
        "actor=export_results measurement_uuid=%s agent_uuid=%s",
        measurement_uuid,
        agent_uuid,
    )
    exporter = CSVExporter(database_credentials, storage_credentials, bucket_name)
    if exporter.exists(measurement_uuid, agent_uuid):
        logger.info(
            "actor=export_results measurement_uuid=%s agent_uuid=%s status=already-exists",
            measurement_uuid,
            agent_uuid,
        )
        return
    try:
        logger.info(
            "actor=export_results measurement_uuid=%s agent_uuid=%s status=export",
            measurement_uuid,
            agent_uuid,
        )
        exporter.export(measurement_uuid, agent_uuid)
    except Exception:
        logger.info(
            "actor=export_results measurement_uuid=%s agent_uuid=%s status=delete",
            measurement_uuid,
            agent_uuid,
        )
        exporter.delete(measurement_uuid, agent_uuid)
        raise


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_atlas(
    database_credentials: dict,
    storage_credentials: dict,
    bucket_name: str,
    measurement_uuid: str,
    agent_uuid: str,
) -> None:
    logger.info(
        "actor=export_traceroutes_atlas measurement_uuid=%s agent_uuid=%s",
        measurement_uuid,
        agent_uuid,
    )
    exporter = AtlasExporter(database_credentials, storage_credentials, bucket_name)
    if exporter.exists(measurement_uuid, agent_uuid):
        logger.info(
            "actor=export_traceroutes_atlas measurement_uuid=%s agent_uuid=%s status=already-exists",
            measurement_uuid,
            agent_uuid,
        )
        return
    try:
        logger.info(
            "actor=export_traceroutes_atlas measurement_uuid=%s agent_uuid=%s status=export",
            measurement_uuid,
            agent_uuid,
        )
        exporter.export(measurement_uuid, agent_uuid)
    except Exception:
        logger.info(
            "actor=export_traceroutes_atlas measurement_uuid=%s agent_uuid=%s status=delete",
            measurement_uuid,
            agent_uuid,
        )
        exporter.delete(measurement_uuid, agent_uuid)
        raise


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_warts(
    database_credentials: dict,
    storage_credentials: dict,
    bucket_name: str,
    measurement_uuid: str,
    agent_uuid: str,
) -> None:
    logger.info(
        "actor=export_results measurement_uuid=%s agent_uuid=%s",
        measurement_uuid,
        agent_uuid,
    )


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_graph(
    database_credentials: dict,
    storage_credentials: dict,
    bucket_name: str,
    measurement_uuid: str,
    agent_uuid: str,
) -> None:
    logger.info(
        "actor=export_results measurement_uuid=%s agent_uuid=%s",
        measurement_uuid,
        agent_uuid,
    )
