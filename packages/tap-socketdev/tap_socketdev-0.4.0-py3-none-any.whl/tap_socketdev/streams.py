"""Stream type classes for tap-socketdev."""

from __future__ import annotations

import sys
import typing as t

from singer_sdk import typing as th

from tap_socketdev.client import SocketDevStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from requests import Response


class Reports(SocketDevStream):
    """Reports stream."""

    name = "reports"
    path = "/v0/report/list"
    records_jsonpath = "$[*]"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The report's unique identifier",
        ),
        th.Property(
            "url",
            th.StringType,
            description="The URL to the report",
        ),
    ).to_dict()


class Organizations(SocketDevStream):
    """Organizations stream."""

    name = "organizations"
    path = "/v0/organizations"
    primary_keys = ("id",)
    replication_key = None

    schema = th.PropertiesList(
        th.Property(
            "id",
            th.StringType,
            description="The organization's unique identifier",
        ),
        th.Property(
            "name",
            th.StringType,
            description="The organization's name",
        ),
        th.Property(
            "image",
            th.StringType,
            description="The organization's image",
        ),
        th.Property(
            "plan",
            th.StringType,
            description="The organization's plan",
        ),
    ).to_dict()

    @override
    def parse_response(self, response: Response) -> t.Generator[dict, None, None]:
        yield from response.json()["organizations"].values()
