# import requests
# from requests import HTTPError
#
#
# class QueryError(Exception):
#     pass
#
#
# def execute(credentials: dict, query: str, params: dict, *, timeout=(1, 60)) -> str:
#     """
#     >>> from iris_exporter.test import settings
#     >>> execute(settings.database_url, "SELECT {val:String}", {"val": "abcd"})
#     'abcd'
#     >>> execute(settings.database_url, "SELECT val", {}) # doctest: +ELLIPSIS
#     Traceback (most recent call last):
#     database.QueryError: ...
#     """
#     query_params = {f"param_{k}": v for k, v in params.items()}
#     url = credentials
#     r = requests.post(
#         credentials["base_url"],
#         # TODO
#         # auth=(credentials["username"], credentials["password"]),
#         params={"database": credentials["database"], "query": query, **query_params},
#         timeout=timeout,
#     )
#     try:
#         r.raise_for_status()
#     except HTTPError as e:
#         raise QueryError(r.content) from e
#     return r.text.strip()
