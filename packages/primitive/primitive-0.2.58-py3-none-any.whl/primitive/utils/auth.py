import sys

import backoff
from aiohttp.client_exceptions import ClientConnectorError
from gql.transport.exceptions import TransportServerError
from loguru import logger

from ..graphql.sdk import create_session

MAX_TIME_FOR_BACKOFF = 60 * 15  # 15 minutes


def connection_backoff_handler(details):
    logger.error(
        "Cannot connect to API. Waiting {wait:0.1f} seconds after {tries} tries.".format(
            **details
        )
    )


def create_new_session(primitive):
    token = primitive.host_config.get("token")
    transport = primitive.host_config.get("transport")
    fingerprint = primitive.host_config.get("fingerprint")

    if not token or not transport:
        logger.error(
            "CLI is not configured. Run `primitive config` to add an auth token."
        )
        sys.exit(1)

    return create_session(
        host=primitive.host,
        token=token,
        transport=transport,
        fingerprint=fingerprint,
    )


def guard(func):
    @backoff.on_exception(
        backoff.expo,
        (
            ConnectionRefusedError,
            ClientConnectorError,
            TransportServerError,
        ),
        on_backoff=connection_backoff_handler,
        max_time=MAX_TIME_FOR_BACKOFF,
    )
    def wrapper(self, *args, **kwargs):
        if self.primitive.session is None:
            self.primitive.session = create_new_session(self.primitive)

        return func(self, *args, **kwargs)

    return wrapper
