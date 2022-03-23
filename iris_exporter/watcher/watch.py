import time

from iris_client import IrisClient

from iris_exporter.commons.logger import logger
from iris_exporter.commons.settings import Settings
from iris_exporter.exporter.actors import export_results, export_traceroutes_atlas

settings = Settings()


def watch(interval: float) -> None:
    while True:
        watch_once()
        time.sleep(interval)


def watch_once() -> None:
    with IrisClient(
        base_url=settings.iris_base_url,
        username=settings.iris_username,
        password=settings.iris_password,
    ) as client:
        logger.info("state=fetch_measurements")
        # TODO: Use guesthouse to return proper credentials with write access.
        # TODO: ClickHouse doesn't seems to support session token for s3 table function.
        #       => PR?
        # services = client.get("/users/me/services").json()
        database_credentials = dict(
            base_url=settings.clickhouse_base_url,
            database=settings.clickhouse_database,
            username=settings.clickhouse_username,
            password=settings.clickhouse_password,
        )
        storage_credentials = dict(
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region_name,
        )
        measurements = client.all(
            "/measurements/",
            params=dict(only_mine=False, state="finished", tag=settings.tag),
        )
        for measurement in measurements:
            for agent in measurement["agents"]:
                measurement_uuid = measurement["uuid"]
                agent_uuid = agent["agent_uuid"]
                export_results.send(
                    database_credentials,
                    storage_credentials,
                    settings.s3_bucket,
                    measurement_uuid,
                    agent_uuid,
                )
                export_traceroutes_atlas.send(
                    database_credentials,
                    storage_credentials,
                    settings.s3_bucket,
                    measurement_uuid,
                    agent_uuid,
                )
                # export_traceroutes_warts.send(
                #     database_credentials,
                #     storage_credentials,
                #     settings.s3_bucket,
                #     measurement_uuid,
                #     agent_uuid,
                # )
                # export_graph.send(
                #     database_credentials,
                #     storage_credentials,
                #     settings.s3_bucket,
                #     measurement_uuid,
                #     agent_uuid,
                # )
        logger.info("state=done")
