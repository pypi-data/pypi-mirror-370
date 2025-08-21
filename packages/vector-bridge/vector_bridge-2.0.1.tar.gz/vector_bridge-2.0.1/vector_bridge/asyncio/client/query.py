from typing import Any, Dict

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.queries import raise_for_query_detail
from vector_bridge.schema.queries import QueryResponse


class AsyncQueryClient:
    """Async user client for query endpoints that require an API key."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def run_search_query(
        self,
        vector_schema: str,
        query_args: Dict[str, Any],
        integration_name: str = None,
    ) -> QueryResponse:
        """
        Run a vector search query.

        Args:
            vector_schema: The schema to be queried
            query_args: Query parameters
            integration_name: The name of the Integration

        Returns:
            Search results
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/vector-query/search/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=query_args) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_query_detail)
            return QueryResponse.model_validate(result)

    async def run_find_similar_query(
        self,
        vector_schema: str,
        query_args: Dict[str, Any],
        integration_name: str = None,
    ) -> QueryResponse:
        """
        Run a vector similarity query.

        Args:
            vector_schema: The schema to be queried
            query_args: Query parameters
            integration_name: The name of the Integration

        Returns:
            Search results
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/vector-query/find-similar/run"
        params = {"vector_schema": vector_schema, "integration_name": integration_name}

        headers = self.client._get_auth_headers()

        async with self.client.session.post(url, headers=headers, params=params, json=query_args) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_query_detail)
            return QueryResponse.model_validate(result)
