from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    # TODO: Requests credentials/URLs from the Iris API.
    redis_url: str = "redis://default:iris@redis.docker.localhost:6379"
    redis_namespace: str = "iris-exporter"
    watch_interval: int = 15  # seconds # TODO: Set again to 15 seconds.
    working_directory: Path = Path()
