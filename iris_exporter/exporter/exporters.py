import boto3
from diamond_miner.queries import results_table
from pych import ClickHouseClient


def get_table_structure(client: ClickHouseClient, table: str) -> str:
    """
    >>> from iris_exporter.test import settings
    >>> get_table_structure(settings.database_url, "test_nsdi_example") # doctest: +ELLIPSIS
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


def results_csv_s3_key(measurement_id: str):
    return f"{measurement_id}__results.csv.zst"


def find_results_csv_s3(storage_credentials: dict, measurement_id: str):
    s3 = boto3.resource("s3", **storage_credentials)
    for bucket in s3.buckets.all():
        print(bucket)


def export_results_csv_s3(
    client: ClickHouseClient, storage_credentials: dict, measurement_id: str
) -> str:
    """
    >>> from iris_exporter.test import settings
    >>> export_results_csv_s3(settings.database_url, settings.storage_url, "test_nsdi_example")
    'results__test_nsdi_example.csv.zst'
    """
    s3_key = results_csv_s3_key(measurement_id)
    structure = get_table_structure(client, results_table(measurement_id))
    query = """
    INSERT INTO FUNCTION s3(
        {s3_path:String},
        {s3_access_key_id:String},
        {s3_secret_access_key:String},
        'CSVWithNames',
        {structure:String},
        'zstd'
    )
    SELECT *
    FROM {table:Identifier}
    """
    params = dict(
        # TODO: Bucket param
        s3_path=f"{storage_credentials['endpoint_url']}/exporter/{s3_key}",
        s3_access_key_id=storage_credentials["aws_access_key_id"],
        s3_secret_access_key=storage_credentials["aws_secret_access_key"],
        structure=structure,
        table=results_table(measurement_id),
    )
    client.execute(query, params)
    return s3_key


# def fetch_results(directory: Path, url: str, measurement_id: str) -> Path:
#     """
#     Fetch the result table locally in CSV format.
#     >>> from diamond_miner.test import url
#     >>> from tempfile import TemporaryDirectory
#     >>> with TemporaryDirectory() as tmpdir:
#     ...     out = fetch_results(Path(tmpdir), url, "test_nsdi_example")
#     ...     len(out.read_text().split('\\n'))
#     87
#     """
#     query = GetResults()
#     params = {
#         "default_format": "CSVWithNames",
#         "query": query.statement(measurement_id),
#     }
#     # TODO: Replace _ with - in the UUIDs for consistency?
#     # TODO: Check that we have no errors from the db (or raise exception, and add doctest for it)
#     file = directory / f"results__{measurement_id}.csv"
#     r = requests.post(
#         url,
#         headers={"Accept-encoding": "gzip"},
#         params=params,
#         stream=True,
#         timeout=(1, 60),
#     )
#     with file.open("wb") as f:
#         shutil.copyfileobj(r.raw, f)
#     # TODO: Decompress?
#     return file
