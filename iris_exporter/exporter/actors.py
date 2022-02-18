import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker
from pych import ClickHouseClient

from iris_exporter.commons.exclusive import exclusive
from iris_exporter.commons.logger import configure_logging
from iris_exporter.commons.settings import Settings
from iris_exporter.exporter.exporters import export_results_csv_s3

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
    measurement_id: str,
):
    with ClickHouseClient(**database_credentials) as client:
        # find_results_csv_s3(storage_credentials, measurement_id)
        # TODO: Cleanup on failure.
        export_results_csv_s3(client, storage_credentials, measurement_id)


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_atlas(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_id: str,
):
    pass


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_traceroutes_warts(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_id: str,
):
    pass


@dramatiq.actor(max_retries=0)
@exclusive(redis_client)
def export_graph(
    database_credentials: dict,
    storage_credentials: dict,
    measurement_id: str,
):
    pass
