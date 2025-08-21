from collections.abc import AsyncGenerator
from typing import Any

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport
from gql.transport.websockets import WebsocketsTransport


class GraphQLClient:
    def __init__(self, api_key: str, base_api_url: str, base_ws_url: str):
        self.graphql_url = f"{base_api_url}/graphql"
        self.websocket_url = f"{base_ws_url}/graphql_ws".replace(
            "https", "wss"
        ).replace("http", "ws")

        self.api_key = api_key

    def get_transport(self, timeout: float | None = None) -> HTTPXAsyncTransport:
        return HTTPXAsyncTransport(
            url=self.graphql_url,
            headers={"API-KEY": self.api_key},
            timeout=timeout,
        )

    def get_ws_transport(self) -> WebsocketsTransport:
        return WebsocketsTransport(
            url=self.websocket_url,
            init_payload={"apiKey": self.api_key},
        )

    async def execute(
        self,
        query_str: str,
        vars: dict[str, Any] | None = None,
        op_name: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        async with Client(
            transport=self.get_transport(timeout),
            fetch_schema_from_transport=False,
            execute_timeout=timeout,
        ) as session:
            # Execute single query
            query = gql(query_str)
            result = await session.execute(query, vars, op_name)
            return result

    async def subscribe(
        self,
        subscription_str: str,
        vars: dict[str, Any] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        async with Client(
            transport=self.get_ws_transport(),
        ) as session:
            # Execute subscription
            subscription = gql(subscription_str)
            async for result in session.subscribe(subscription, vars):
                yield result
