from pych_client import ClickHouseClient


def get_table_structure(client: ClickHouseClient, table: str) -> str:
    """
    >>> from iris_exporter.test import database
    >>> get_table_structure(database, "results__test_nsdi_example") # doctest: +ELLIPSIS
    'capture_timestamp DateTime, probe_protocol UInt8, probe_src_addr IPv6, ...'
    """
    query = """
    SELECT name, type
    FROM system.columns
    WHERE table = {table:String} AND default_kind = ''
    ORDER BY position
    """
    columns = client.json(query, dict(table=table))
    return ", ".join(f"{x['name']} {x['type']}" for x in columns)


def measurement_id(measurement_uuid: str, agent_uuid: str) -> str:
    """
    Measurement IDs used by Iris
    >>> measurement_id("57a54767-8404-4070-8372-ac59337b6432", "e6f321bc-03f1-4abe-ab35-385fff1a923d")
    '57a54767-8404-4070-8372-ac59337b6432__e6f321bc-03f1-4abe-ab35-385fff1a923d'

    Measurement IDs used by Diamond-Miner test data
    >>> measurement_id("test_nsdi_example", "")
    'test_nsdi_example'
    """
    s = measurement_uuid
    if agent_uuid:
        s += f"__{agent_uuid}"
    return s
