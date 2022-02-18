from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://default:iris@redis.docker.localhost:6379"
    redis_namespace: str = "iris-exporter"
    watch_interval: int = 15  # seconds
    working_directory: Path = Path()
