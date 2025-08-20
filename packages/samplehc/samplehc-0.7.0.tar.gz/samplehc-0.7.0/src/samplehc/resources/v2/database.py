# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import database_execute_sql_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.database_execute_sql_response import DatabaseExecuteSqlResponse

__all__ = ["DatabaseResource", "AsyncDatabaseResource"]


class DatabaseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatabaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return DatabaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatabaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return DatabaseResourceWithStreamingResponse(self)

    def execute_sql(
        self,
        *,
        query: str,
        params: List[Union[str, float, bool, Optional[Literal["null"]], Iterable[object], Dict[str, object]]]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseExecuteSqlResponse:
        """Allows execution of arbitrary SQL queries against the Sample database.

        Supports
        parameterized queries with complex data types including arrays, objects, and
        nested structures. Examples: arrays can be used with ANY/ALL operators, objects
        as structs for complex filtering.

        Args:
          query: The SQL query to execute.

          params: An array of parameters to be used in the SQL query. Supports primitive types
              (string, number, boolean, null), arrays, and objects. Use placeholders like $1,
              $2, etc. in the query string. Examples: ["hello", 123, [1,2,3], {"name": "John",
              "age": 30}]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/database/sql",
            body=maybe_transform(
                {
                    "query": query,
                    "params": params,
                },
                database_execute_sql_params.DatabaseExecuteSqlParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseExecuteSqlResponse,
        )


class AsyncDatabaseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatabaseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDatabaseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatabaseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncDatabaseResourceWithStreamingResponse(self)

    async def execute_sql(
        self,
        *,
        query: str,
        params: List[Union[str, float, bool, Optional[Literal["null"]], Iterable[object], Dict[str, object]]]
        | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatabaseExecuteSqlResponse:
        """Allows execution of arbitrary SQL queries against the Sample database.

        Supports
        parameterized queries with complex data types including arrays, objects, and
        nested structures. Examples: arrays can be used with ANY/ALL operators, objects
        as structs for complex filtering.

        Args:
          query: The SQL query to execute.

          params: An array of parameters to be used in the SQL query. Supports primitive types
              (string, number, boolean, null), arrays, and objects. Use placeholders like $1,
              $2, etc. in the query string. Examples: ["hello", 123, [1,2,3], {"name": "John",
              "age": 30}]

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/database/sql",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "params": params,
                },
                database_execute_sql_params.DatabaseExecuteSqlParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatabaseExecuteSqlResponse,
        )


class DatabaseResourceWithRawResponse:
    def __init__(self, database: DatabaseResource) -> None:
        self._database = database

        self.execute_sql = to_raw_response_wrapper(
            database.execute_sql,
        )


class AsyncDatabaseResourceWithRawResponse:
    def __init__(self, database: AsyncDatabaseResource) -> None:
        self._database = database

        self.execute_sql = async_to_raw_response_wrapper(
            database.execute_sql,
        )


class DatabaseResourceWithStreamingResponse:
    def __init__(self, database: DatabaseResource) -> None:
        self._database = database

        self.execute_sql = to_streamed_response_wrapper(
            database.execute_sql,
        )


class AsyncDatabaseResourceWithStreamingResponse:
    def __init__(self, database: AsyncDatabaseResource) -> None:
        self._database = database

        self.execute_sql = async_to_streamed_response_wrapper(
            database.execute_sql,
        )
