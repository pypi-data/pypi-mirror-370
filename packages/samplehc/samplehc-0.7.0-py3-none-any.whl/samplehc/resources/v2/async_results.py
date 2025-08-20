# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import overload

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import required_args, maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import async_result_sleep_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.async_result_sleep_response import AsyncResultSleepResponse
from ...types.v2.async_result_retrieve_response import AsyncResultRetrieveResponse

__all__ = ["AsyncResultsResource", "AsyncAsyncResultsResource"]


class AsyncResultsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncResultsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        async_result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultRetrieveResponse:
        """
        Retrieves the status and result of an asynchronous operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not async_result_id:
            raise ValueError(f"Expected a non-empty value for `async_result_id` but received {async_result_id!r}")
        return self._get(
            f"/api/v2/async-results/{async_result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncResultRetrieveResponse,
        )

    @overload
    def sleep(
        self,
        *,
        delay: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        """
        Creates an async result that will automatically resolve after a specified delay
        or at a future time.

        Args:
          delay: The number of milliseconds to wait before completing the async result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def sleep(
        self,
        *,
        resume_at: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        """
        Creates an async result that will automatically resolve after a specified delay
        or at a future time.

        Args:
          resume_at: An ISO-8601 string specifying when the async result should be completed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["delay"], ["resume_at"])
    def sleep(
        self,
        *,
        delay: float | NotGiven = NOT_GIVEN,
        resume_at: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        return self._post(
            "/api/v2/async-results/sleep",
            body=maybe_transform(
                {
                    "delay": delay,
                    "resume_at": resume_at,
                },
                async_result_sleep_params.AsyncResultSleepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncResultSleepResponse,
        )


class AsyncAsyncResultsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAsyncResultsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAsyncResultsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAsyncResultsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncAsyncResultsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        async_result_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultRetrieveResponse:
        """
        Retrieves the status and result of an asynchronous operation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not async_result_id:
            raise ValueError(f"Expected a non-empty value for `async_result_id` but received {async_result_id!r}")
        return await self._get(
            f"/api/v2/async-results/{async_result_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncResultRetrieveResponse,
        )

    @overload
    async def sleep(
        self,
        *,
        delay: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        """
        Creates an async result that will automatically resolve after a specified delay
        or at a future time.

        Args:
          delay: The number of milliseconds to wait before completing the async result.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def sleep(
        self,
        *,
        resume_at: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        """
        Creates an async result that will automatically resolve after a specified delay
        or at a future time.

        Args:
          resume_at: An ISO-8601 string specifying when the async result should be completed.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["delay"], ["resume_at"])
    async def sleep(
        self,
        *,
        delay: float | NotGiven = NOT_GIVEN,
        resume_at: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResultSleepResponse:
        return await self._post(
            "/api/v2/async-results/sleep",
            body=await async_maybe_transform(
                {
                    "delay": delay,
                    "resume_at": resume_at,
                },
                async_result_sleep_params.AsyncResultSleepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncResultSleepResponse,
        )


class AsyncResultsResourceWithRawResponse:
    def __init__(self, async_results: AsyncResultsResource) -> None:
        self._async_results = async_results

        self.retrieve = to_raw_response_wrapper(
            async_results.retrieve,
        )
        self.sleep = to_raw_response_wrapper(
            async_results.sleep,
        )


class AsyncAsyncResultsResourceWithRawResponse:
    def __init__(self, async_results: AsyncAsyncResultsResource) -> None:
        self._async_results = async_results

        self.retrieve = async_to_raw_response_wrapper(
            async_results.retrieve,
        )
        self.sleep = async_to_raw_response_wrapper(
            async_results.sleep,
        )


class AsyncResultsResourceWithStreamingResponse:
    def __init__(self, async_results: AsyncResultsResource) -> None:
        self._async_results = async_results

        self.retrieve = to_streamed_response_wrapper(
            async_results.retrieve,
        )
        self.sleep = to_streamed_response_wrapper(
            async_results.sleep,
        )


class AsyncAsyncResultsResourceWithStreamingResponse:
    def __init__(self, async_results: AsyncAsyncResultsResource) -> None:
        self._async_results = async_results

        self.retrieve = async_to_streamed_response_wrapper(
            async_results.retrieve,
        )
        self.sleep = async_to_streamed_response_wrapper(
            async_results.sleep,
        )
