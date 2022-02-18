import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker

from iris_exporter.commons.exclusive import exclusive
from iris_exporter.commons.logger import configure_logging
from iris_exporter.commons.settings import Settings
from iris_exporter.exporter.atlas import AtlasExporter
from iris_exporter.exporter.csv import CSVExporter

settings = Settings()
redis_client = redis.from_url(settings.redis_url)

broker = RedisBroker(url=settings.redis_url, namespace=settings.redis_namespace)
dramatiq.set_broker(broker)

configure_logging()

# NOTE: We do not retry failed actors as they will be re-scheduled by the watcher.


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_results(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_uuid: str,
    agent_uuid: str,
):
    exporter = CSVExporter(database_credentials, storage_credentials, "test-bucket")
    if exporter.exists(measurement_uuid, agent_uuid):
        return
    try:
        exporter.export(measurement_uuid, agent_uuid)
    except Exception:
        exporter.delete(measurement_uuid, agent_uuid)
        raise


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_atlas(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_uuid: str,
    agent_uuid: str,
):
    exporter = AtlasExporter(database_credentials, storage_credentials, "test-bucket")
    if exporter.exists(measurement_uuid, agent_uuid):
        return
    try:
        exporter.export(measurement_uuid, agent_uuid)
    except Exception:
        exporter.delete(measurement_uuid, agent_uuid)
        raise


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_warts(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_uuid: str,
    agent_uuid: str,
):
    pass


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_graph(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_uuid: str,
    agent_uuid: str,
):
    pass
