from diamond_miner.queries import results_table
from pych_client import AsyncClickHouseClient

from iris_exporter.exceptions import ExportException
from iris_exporter.helpers import measurement_id, object_key, query_id


async def export(
    *,
    clickhouse: AsyncClickHouseClient,
    s3_base_url: str,
    s3_bucket: str,
    s3_access_key_id: str,
    s3_secret_access_key: str,
    measurement_uuid: str,
    agent_uuid: str,
) -> None:
    query = """
    INSERT INTO FUNCTION s3(
        {s3_path:String},
        {s3_access_key_id:String},
        {s3_secret_access_key:String},
        'JSONEachRow'
    )
    SELECT
        {measurement_uuid:String} AS measurement_uuid,
        {agent_uuid:String} AS agent_uuid,
        formatDateTime(min(capture_timestamp), '%Y-%m-%dT%H:%M:%SZ') AS traceroute_start,
        probe_protocol,
        probe_src_addr,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port,
        groupArray((
            formatDateTime(capture_timestamp, '%Y-%m-%dT%H:%M:%SZ'),
            probe_ttl,
            quoted_ttl,
            reply_icmp_type,
            reply_icmp_code,
            reply_ttl,
            reply_size,
            reply_mpls_labels,
            reply_src_addr,
            rtt
        )) AS replies
    FROM {table:Identifier}
    WHERE NOT destination_host_reply
          AND NOT destination_prefix_reply
          AND NOT private_probe_dst_prefix
          AND NOT private_reply_src_addr
          AND time_exceeded_reply
          AND valid_probe_protocol
    GROUP BY (
        probe_protocol,
        probe_src_addr,
        probe_dst_prefix,
        probe_dst_addr,
        probe_src_port,
        probe_dst_port
    )
    """
    try:
        await clickhouse.execute(
            query,
            params={
                "measurement_uuid": measurement_uuid,
                "agent_uuid": agent_uuid,
                "table": results_table(measurement_id(measurement_uuid, agent_uuid)),
                "s3_path": f"{s3_base_url}/{s3_bucket}/{object_key(measurement_uuid, agent_uuid)}",
                "s3_access_key_id": s3_access_key_id,
                "s3_secret_access_key": s3_secret_access_key,
            },
            settings={
                "optimize_aggregation_in_order": 1,
                "query_id": query_id(measurement_uuid, agent_uuid),
                "s3_truncate_on_insert": 1,
            },
        )
    except Exception as e:
        raise ExportException(measurement_uuid, agent_uuid) from e
