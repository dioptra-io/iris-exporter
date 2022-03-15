import dramatiq
import redis
from dramatiq.brokers.redis import RedisBroker

from iris_exporter.commons.logger import configure_logging
from iris_exporter.commons.settings import Settings

settings = Settings()
redis_client = redis.from_url(settings.redis_url)

broker = RedisBroker(url=settings.redis_url, namespace=settings.redis_namespace)
dramatiq.set_broker(broker)

configure_logging()
