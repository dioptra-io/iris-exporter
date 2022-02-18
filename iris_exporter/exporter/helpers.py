from pych_client import ClickHouseClient

import iris_exporter
from iris_exporter.test import database


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
