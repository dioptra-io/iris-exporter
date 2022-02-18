from iris_exporter.commons.logger import configure_logging
from iris_exporter.commons.settings import Settings
from iris_exporter.watcher.watch import watch


def main(settings=Settings()):
    configure_logging()
    watch(interval=settings.watch_interval)
