from typing import Dict

import requests
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from primitive.__about__ import __version__


def create_session(
    token: str,
    host: str = "api.primitive.tech",
    transport: str = "https",
    fingerprint: str = None,
    fetch_schema_from_transport: bool = False,
):
    url = f"{transport}://{host}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-primitive-agent": f"primitive@{__version__}",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    if fingerprint:
        headers["x-primitive-fingerprint"] = fingerprint

    transport = AIOHTTPTransport(url=url, headers=headers)
    session = Client(
        transport=transport,
        fetch_schema_from_transport=fetch_schema_from_transport,
        execute_timeout=None,  # Prevents timeout errors on async transports
    )
    return session


def create_requests_session(
    host_config: Dict,
):
    token = host_config.get("token")

    headers = {
        # "Content-Type": "multipart/form-data", # DO NOT ADD THIS MIME TYPE IT BREAKS
        "Accept": "application/json",
        "x-primitive-agent": f"primitive@{__version__}",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    if fingerprint := host_config.get("fingerprint", None):
        headers["x-primitive-fingerprint"] = fingerprint

    session = requests.Session()
    session.headers.update(headers)
    return session
