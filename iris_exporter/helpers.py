from botocore.exceptions import ClientError
from pych_client import AsyncClickHouseClient
from types_aiobotocore_s3.service_resource import Bucket


def measurement_id(measurement_uuid: str, agent_uuid: str) -> str:
    return f"{measurement_uuid}__{agent_uuid}"


async def delete_object(bucket: Bucket, measurement_uuid: str, agent_uuid: str) -> None:
    try:
        obj = await bucket.Object(object_key(measurement_uuid, agent_uuid))
        await obj.delete()
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise


async def object_exists(bucket: Bucket, measurement_uuid: str, agent_uuid: str) -> bool:
    try:
        obj = await bucket.Object(object_key(measurement_uuid, agent_uuid))
        await obj.load()
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            raise
        return False
    return True


def object_key(measurement_uuid: str, agent_uuid: str) -> str:
    measurement_id_ = measurement_id(measurement_uuid, agent_uuid)
    return f"{measurement_id_}__jsonl.jsonl.zst"


def query_id(measurement_uuid: str, agent_uuid: str) -> str:
    return object_key(measurement_uuid, agent_uuid)


async def query_is_running(
    clickhouse: AsyncClickHouseClient, measurement_uuid: str, agent_uuid: str
) -> bool:
    query = """
    SELECT groupArray(type) AS types
    FROM system.query_log
    WHERE query_id = {query_id:String}
    GROUP BY query_id
    """
    rows = await clickhouse.json(
        query, {"query_id": query_id(measurement_uuid, agent_uuid)}
    )
    # A query is currently running if its only entry in the query log is "QueryStart".
    return len(rows) > 0 and rows[0]["types"] == ["QueryStart"]


async def has_column(
    clickhouse: AsyncClickHouseClient,
    table: str,
    column: str,
) -> bool:
    query = """
    SELECT name
    FROM system.columns
    WHERE name = {column:String} AND table = {table:String}
    """
    rows = await clickhouse.json(query, {"column": column, "table": table})
    return len(rows) > 0
