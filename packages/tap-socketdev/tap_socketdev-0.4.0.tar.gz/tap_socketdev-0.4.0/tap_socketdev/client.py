"""REST client handling, including SocketDevStream base class."""

from __future__ import annotations

import sys
from http import HTTPStatus

from requests.auth import HTTPBasicAuth
from singer_sdk import RESTStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class SocketDevStream(RESTStream):
    """Socket stream class."""

    url_base = "https://api.socket.dev"

    extra_retry_statuses = (HTTPStatus.TOO_MANY_REQUESTS,)

    @property
    @override
    def authenticator(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(username=self.config["api_key"], password="")
