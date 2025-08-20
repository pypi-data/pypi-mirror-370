# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Iterable, cast

import httpx

from ...types import v1_sql_execute_params, v1_query_audit_logs_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v1_sql_execute_response import V1SqlExecuteResponse
from ...types.v1_query_audit_logs_response import V1QueryAuditLogsResponse

__all__ = ["V1Resource", "AsyncV1Resource"]


class V1Resource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> V1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return V1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> V1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return V1ResourceWithStreamingResponse(self)

    def query_audit_logs(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1QueryAuditLogsResponse:
        """Retrieves audit logs.

        Allows for filtering and searching through historical
        audit data.

        Args:
          query: The query string to filter audit logs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/audit-logs",
            body=maybe_transform({"query": query}, v1_query_audit_logs_params.V1QueryAuditLogsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1QueryAuditLogsResponse,
        )

    def sql_execute(
        self,
        *,
        query: str,
        array_mode: bool | NotGiven = NOT_GIVEN,
        params: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1SqlExecuteResponse:
        """Allows execution of arbitrary SQL queries against the Sample database.

        Supports
        parameterized queries.

        Args:
          query: The SQL query to execute.

          array_mode: If true, rows will be returned as arrays of values instead of objects. Defaults
              to false.

          params: An array of parameters to be used in the SQL query. Use placeholders like $1,
              $2, etc. in the query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            V1SqlExecuteResponse,
            self._post(
                "/api/v1/sql",
                body=maybe_transform(
                    {
                        "query": query,
                        "array_mode": array_mode,
                        "params": params,
                    },
                    v1_sql_execute_params.V1SqlExecuteParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, V1SqlExecuteResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncV1Resource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncV1ResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncV1ResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncV1ResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncV1ResourceWithStreamingResponse(self)

    async def query_audit_logs(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1QueryAuditLogsResponse:
        """Retrieves audit logs.

        Allows for filtering and searching through historical
        audit data.

        Args:
          query: The query string to filter audit logs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/audit-logs",
            body=await async_maybe_transform({"query": query}, v1_query_audit_logs_params.V1QueryAuditLogsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=V1QueryAuditLogsResponse,
        )

    async def sql_execute(
        self,
        *,
        query: str,
        array_mode: bool | NotGiven = NOT_GIVEN,
        params: Iterable[object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> V1SqlExecuteResponse:
        """Allows execution of arbitrary SQL queries against the Sample database.

        Supports
        parameterized queries.

        Args:
          query: The SQL query to execute.

          array_mode: If true, rows will be returned as arrays of values instead of objects. Defaults
              to false.

          params: An array of parameters to be used in the SQL query. Use placeholders like $1,
              $2, etc. in the query string.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            V1SqlExecuteResponse,
            await self._post(
                "/api/v1/sql",
                body=await async_maybe_transform(
                    {
                        "query": query,
                        "array_mode": array_mode,
                        "params": params,
                    },
                    v1_sql_execute_params.V1SqlExecuteParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, V1SqlExecuteResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class V1ResourceWithRawResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.query_audit_logs = to_raw_response_wrapper(
            v1.query_audit_logs,
        )
        self.sql_execute = to_raw_response_wrapper(
            v1.sql_execute,
        )


class AsyncV1ResourceWithRawResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.query_audit_logs = async_to_raw_response_wrapper(
            v1.query_audit_logs,
        )
        self.sql_execute = async_to_raw_response_wrapper(
            v1.sql_execute,
        )


class V1ResourceWithStreamingResponse:
    def __init__(self, v1: V1Resource) -> None:
        self._v1 = v1

        self.query_audit_logs = to_streamed_response_wrapper(
            v1.query_audit_logs,
        )
        self.sql_execute = to_streamed_response_wrapper(
            v1.sql_execute,
        )


class AsyncV1ResourceWithStreamingResponse:
    def __init__(self, v1: AsyncV1Resource) -> None:
        self._v1 = v1

        self.query_audit_logs = async_to_streamed_response_wrapper(
            v1.query_audit_logs,
        )
        self.sql_execute = async_to_streamed_response_wrapper(
            v1.sql_execute,
        )
