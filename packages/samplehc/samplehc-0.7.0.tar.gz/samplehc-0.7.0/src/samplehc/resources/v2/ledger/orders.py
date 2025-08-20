# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

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
from ....types.v2.ledger import order_retrieve_batch_balances_params
from ....types.v2.ledger.order_retrieve_balances_response import OrderRetrieveBalancesResponse
from ....types.v2.ledger.order_retrieve_batch_balances_response import OrderRetrieveBatchBalancesResponse

__all__ = ["OrdersResource", "AsyncOrdersResource"]


class OrdersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return OrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return OrdersResourceWithStreamingResponse(self)

    def retrieve_balances(
        self,
        order_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRetrieveBalancesResponse:
        """
        Retrieves outstanding balances for a single order ID across all balance
        categories (order-writeoff, unallocated, institution invoices, institution
        uninvoiced, patient responsibility).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return self._get(
            f"/api/v2/ledger/orders/{order_id}/balances",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRetrieveBalancesResponse,
        )

    def retrieve_batch_balances(
        self,
        *,
        order_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRetrieveBatchBalancesResponse:
        """
        Retrieves outstanding balances for an array of order IDs across all balance
        categories (order-writeoff, unallocated, institution invoices, institution
        uninvoiced, patient responsibility).

        Args:
          order_ids: Array of order IDs to retrieve balances for (max 100)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/orders/batch-balances",
            body=maybe_transform(
                {"order_ids": order_ids}, order_retrieve_batch_balances_params.OrderRetrieveBatchBalancesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRetrieveBatchBalancesResponse,
        )


class AsyncOrdersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrdersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrdersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrdersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncOrdersResourceWithStreamingResponse(self)

    async def retrieve_balances(
        self,
        order_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRetrieveBalancesResponse:
        """
        Retrieves outstanding balances for a single order ID across all balance
        categories (order-writeoff, unallocated, institution invoices, institution
        uninvoiced, patient responsibility).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not order_id:
            raise ValueError(f"Expected a non-empty value for `order_id` but received {order_id!r}")
        return await self._get(
            f"/api/v2/ledger/orders/{order_id}/balances",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRetrieveBalancesResponse,
        )

    async def retrieve_batch_balances(
        self,
        *,
        order_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderRetrieveBatchBalancesResponse:
        """
        Retrieves outstanding balances for an array of order IDs across all balance
        categories (order-writeoff, unallocated, institution invoices, institution
        uninvoiced, patient responsibility).

        Args:
          order_ids: Array of order IDs to retrieve balances for (max 100)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/orders/batch-balances",
            body=await async_maybe_transform(
                {"order_ids": order_ids}, order_retrieve_batch_balances_params.OrderRetrieveBatchBalancesParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderRetrieveBatchBalancesResponse,
        )


class OrdersResourceWithRawResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve_balances = to_raw_response_wrapper(
            orders.retrieve_balances,
        )
        self.retrieve_batch_balances = to_raw_response_wrapper(
            orders.retrieve_batch_balances,
        )


class AsyncOrdersResourceWithRawResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve_balances = async_to_raw_response_wrapper(
            orders.retrieve_balances,
        )
        self.retrieve_batch_balances = async_to_raw_response_wrapper(
            orders.retrieve_batch_balances,
        )


class OrdersResourceWithStreamingResponse:
    def __init__(self, orders: OrdersResource) -> None:
        self._orders = orders

        self.retrieve_balances = to_streamed_response_wrapper(
            orders.retrieve_balances,
        )
        self.retrieve_batch_balances = to_streamed_response_wrapper(
            orders.retrieve_batch_balances,
        )


class AsyncOrdersResourceWithStreamingResponse:
    def __init__(self, orders: AsyncOrdersResource) -> None:
        self._orders = orders

        self.retrieve_balances = async_to_streamed_response_wrapper(
            orders.retrieve_balances,
        )
        self.retrieve_batch_balances = async_to_streamed_response_wrapper(
            orders.retrieve_batch_balances,
        )
