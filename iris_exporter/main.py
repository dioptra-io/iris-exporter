import asyncio
import logging

import aioboto3
import typer
from iris_client import AsyncIrisClient
from pych_client import AsyncClickHouseClient
from types_aiobotocore_s3 import S3ServiceResource

from iris_exporter.exceptions import ExportException
from iris_exporter.export import export
from iris_exporter.helpers import delete_object, object_exists, query_running
from iris_exporter.logging import logger

app = typer.Typer()


@app.command()
def main(
    tag: str = typer.Argument(
        ...,
        help="Tag to export",
    ),
    dry_run: bool = typer.Option(
        False,
        help="Do not actually export measurements.",
    ),
    overwrite: bool = typer.Option(
        False,
        help="Overwrite existing objects.",
    ),
    clickhouse_base_url: str = typer.Option(
        "http://clickhouse.docker.localhost",
        help="ClickHouse HTTP interface URL",
        metavar="URL",
    ),
    clickhouse_database: str = typer.Option(
        "iris", help="ClickHouse database", metavar="DATABASE"
    ),
    clickhouse_username: str = typer.Option(
        "iris",
        help="ClickHouse username",
        metavar="USERNAME",
    ),
    clickhouse_password: str = typer.Option(
        "iris",
        help="ClickHouse password",
        metavar="PASSWORD",
    ),
    iris_base_url: str = typer.Option(
        "http://api.docker.localhost",
        help="Iris API URL",
        metavar="URL",
    ),
    iris_username: str = typer.Option(
        "admin@example.org",
        help="Iris API username",
        metavar="USERNAME",
    ),
    iris_password: str = typer.Option(
        "admin",
        help="Iris API password",
        metavar="PASSWORD",
    ),
    s3_base_url: str = typer.Option(
        "http://minio.docker.localhost",
        help="S3 URL",
        metavar="URL",
    ),
    s3_bucket: str = typer.Option(
        "public-exports",
        help="S3 bucket",
        metavar="BUCKET",
    ),
    s3_access_key_id: str = typer.Option(
        "minioadmin",
        help="S3 Access Key ID",
        metavar="ID",
    ),
    s3_secret_access_key: str = typer.Option(
        "minioadmin",
        help="S3 Secret Access Key",
        metavar="SECRET",
    ),
) -> None:
    async def main_() -> None:
        logging.basicConfig(level=logging.INFO)
        session = aioboto3.Session()
        async with (
            AsyncClickHouseClient(
                base_url=clickhouse_base_url,
                database=clickhouse_database,
                username=clickhouse_username,
                password=clickhouse_password,
            ) as clickhouse,
            AsyncIrisClient(
                base_url=iris_base_url,
                username=iris_username,
                password=iris_password,
            ) as iris,
            session.resource(
                service_name="s3",
                aws_access_key_id=s3_access_key_id,
                aws_secret_access_key=s3_secret_access_key,
                endpoint_url=s3_base_url,
            ) as s3,
        ):
            await run_exporter(
                clickhouse=clickhouse,
                iris=iris,
                s3=s3,
                s3_base_url=s3_base_url,
                s3_bucket=s3_bucket,
                s3_access_key_id=s3_access_key_id,
                s3_secret_access_key=s3_secret_access_key,
                dry_run=dry_run,
                overwrite=overwrite,
                tag=tag,
            )

    asyncio.run(main_())


async def run_exporter(
    *,
    clickhouse: AsyncClickHouseClient,
    iris: AsyncIrisClient,
    s3: S3ServiceResource,
    s3_base_url: str,
    s3_bucket: str,
    s3_access_key_id: str,
    s3_secret_access_key: str,
    dry_run: bool,
    overwrite: bool,
    tag: str,
) -> None:
    bucket = await s3.Bucket(s3_bucket)
    measurements = await iris.all(
        "/measurements/",
        params={
            "limit": 200,
            "only_mine": False,
            "state": "finished",
            "tag": tag,
        },
    )
    futures = []
    for measurement in measurements:
        for agent in measurement["agents"]:
            measurement_uuid = measurement["uuid"]
            agent_uuid = agent["agent_uuid"]
            if not overwrite and await object_exists(
                bucket, measurement_uuid, agent_uuid
            ):
                logger.info(
                    "measurement_uuid=%s agent_uuid=%s action=skip-existing-object",
                    measurement_uuid,
                    agent_uuid,
                )
                continue
            if await query_running(clickhouse, measurement_uuid, agent_uuid):
                logger.info(
                    "measurement_uuid=%s agent_uuid=%s action=skip-running-query",
                    measurement_uuid,
                    agent_uuid,
                )
                continue
            logger.info(
                "measurement_uuid=%s agent_uuid=%s action=export",
                measurement_uuid,
                agent_uuid,
            )
            if not dry_run:
                futures.append(
                    asyncio.create_task(
                        export(
                            clickhouse,
                            s3_base_url,
                            s3_bucket,
                            s3_access_key_id,
                            s3_secret_access_key,
                            measurement_uuid,
                            agent_uuid,
                        )
                    )
                )
    for future in asyncio.as_completed(futures):
        try:
            await future
        except ExportException as e:
            logger.exception(
                "measurement_uuid=%s agent_uuid=%s",
                e.measurement_uuid,
                e.agent_uuid,
            )
            logger.info(
                "measurement_uuid=%s agent_uuid=%s action=cleanup",
                e.measurement_uuid,
                e.agent_uuid,
            )
            if await object_exists(bucket, e.measurement_uuid, e.agent_uuid):
                await delete_object(bucket, e.measurement_uuid, e.agent_uuid)
