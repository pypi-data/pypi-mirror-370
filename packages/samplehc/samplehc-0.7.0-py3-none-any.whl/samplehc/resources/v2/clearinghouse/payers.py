# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.clearinghouse import payer_retrieve_search_params
from ....types.v2.clearinghouse.payer_list_response import PayerListResponse
from ....types.v2.clearinghouse.payer_retrieve_search_response import PayerRetrieveSearchResponse

__all__ = ["PayersResource", "AsyncPayersResource"]


class PayersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PayersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PayersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PayersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PayersResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PayerListResponse:
        """Lists all payers available for eligibility checks."""
        return self._get(
            "/api/v2/clearinghouse/payers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PayerListResponse,
        )

    def retrieve_search(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PayerRetrieveSearchResponse:
        """
        Searches for payers based on the provided search criteria.

        Args:
          query: The search query (e.g. name, ID, etc.) for the payer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/clearinghouse/payers/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"query": query}, payer_retrieve_search_params.PayerRetrieveSearchParams),
            ),
            cast_to=PayerRetrieveSearchResponse,
        )


class AsyncPayersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPayersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPayersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPayersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPayersResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PayerListResponse:
        """Lists all payers available for eligibility checks."""
        return await self._get(
            "/api/v2/clearinghouse/payers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PayerListResponse,
        )

    async def retrieve_search(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PayerRetrieveSearchResponse:
        """
        Searches for payers based on the provided search criteria.

        Args:
          query: The search query (e.g. name, ID, etc.) for the payer.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/clearinghouse/payers/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"query": query}, payer_retrieve_search_params.PayerRetrieveSearchParams
                ),
            ),
            cast_to=PayerRetrieveSearchResponse,
        )


class PayersResourceWithRawResponse:
    def __init__(self, payers: PayersResource) -> None:
        self._payers = payers

        self.list = to_raw_response_wrapper(
            payers.list,
        )
        self.retrieve_search = to_raw_response_wrapper(
            payers.retrieve_search,
        )


class AsyncPayersResourceWithRawResponse:
    def __init__(self, payers: AsyncPayersResource) -> None:
        self._payers = payers

        self.list = async_to_raw_response_wrapper(
            payers.list,
        )
        self.retrieve_search = async_to_raw_response_wrapper(
            payers.retrieve_search,
        )


class PayersResourceWithStreamingResponse:
    def __init__(self, payers: PayersResource) -> None:
        self._payers = payers

        self.list = to_streamed_response_wrapper(
            payers.list,
        )
        self.retrieve_search = to_streamed_response_wrapper(
            payers.retrieve_search,
        )


class AsyncPayersResourceWithStreamingResponse:
    def __init__(self, payers: AsyncPayersResource) -> None:
        self._payers = payers

        self.list = async_to_streamed_response_wrapper(
            payers.list,
        )
        self.retrieve_search = async_to_streamed_response_wrapper(
            payers.retrieve_search,
        )
