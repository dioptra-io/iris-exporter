import time

from iris_client import IrisClient

from iris_exporter.commons.logger import logger
from iris_exporter.exporter.actors import (
    export_graph,
    export_results,
    export_traceroutes_atlas,
    export_traceroutes_warts,
)


def watch(interval: float):
    while True:
        watch_once()
        time.sleep(interval)


def watch_once():
    with IrisClient() as client:
        logger.info("state=fetch_measurements")
        services = client.get("/users/me/services").json()
        # TODO: Use guesthouse to return proper credentials with write access.
        database_credentials = dict(
            base_url=services["chproxy_base_url"],
            database=services["chproxy_database"],
            username="default",
            password=""
            # username=services["chproxy_username"],
            # password=services["chproxy_password"],
        )
        # TODO: ClickHouse doesn't seems to support session token for s3 table function.
        # => PR?
        storage_credentials = dict(
            endpoint_url=services["s3_host"],
            aws_session_token=None,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin"
            # aws_session_token=services["s3_session_token"],
            # aws_access_key_id=services["s3_access_key_id"],
            # aws_secret_access_key=services["s3_secret_access_key"],
        )
        measurements = client.all("/measurements/public", params=dict(state="finished"))
        for measurement in measurements:
            for agent in measurement["agents"]:
                measurement_id = f"{measurement['uuid']}__{agent['agent_uuid']}"
                export_results.send(
                    database_credentials, storage_credentials, measurement_id
                )
                export_traceroutes_atlas.send(
                    database_credentials, storage_credentials, measurement_id
                )
                export_traceroutes_warts.send(
                    database_credentials, storage_credentials, measurement_id
                )
                export_graph.send(
                    database_credentials, storage_credentials, measurement_id
                )
        logger.info("state=done")
