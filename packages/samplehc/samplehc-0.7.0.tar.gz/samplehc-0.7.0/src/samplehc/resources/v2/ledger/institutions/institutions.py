# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .orders import (
    OrdersResource,
    AsyncOrdersResource,
    OrdersResourceWithRawResponse,
    AsyncOrdersResourceWithRawResponse,
    OrdersResourceWithStreamingResponse,
    AsyncOrdersResourceWithStreamingResponse,
)
from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.ledger.institution_list_outstanding_accounts_response import (
    InstitutionListOutstandingAccountsResponse,
)
from .....types.v2.ledger.institution_retrieve_outstanding_orders_response import (
    InstitutionRetrieveOutstandingOrdersResponse,
)

__all__ = ["InstitutionsResource", "AsyncInstitutionsResource"]


class InstitutionsResource(SyncAPIResource):
    @cached_property
    def orders(self) -> OrdersResource:
        return OrdersResource(self._client)

    @cached_property
    def with_raw_response(self) -> InstitutionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return InstitutionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InstitutionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return InstitutionsResourceWithStreamingResponse(self)

    def list_outstanding_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstitutionListOutstandingAccountsResponse:
        """
        Retrieves all outstanding institutional accounts across all institutions
        (accounts with non-zero balances).
        """
        return self._get(
            "/api/v2/ledger/institutions/outstanding-accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstitutionListOutstandingAccountsResponse,
        )

    def retrieve_outstanding_orders(
        self,
        institution_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstitutionRetrieveOutstandingOrdersResponse:
        """
        Retrieves all outstanding orders for a specific institution (accounts with
        non-zero balances).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not institution_id:
            raise ValueError(f"Expected a non-empty value for `institution_id` but received {institution_id!r}")
        return self._get(
            f"/api/v2/ledger/institutions/{institution_id}/outstanding-orders",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstitutionRetrieveOutstandingOrdersResponse,
        )


class AsyncInstitutionsResource(AsyncAPIResource):
    @cached_property
    def orders(self) -> AsyncOrdersResource:
        return AsyncOrdersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncInstitutionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInstitutionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInstitutionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncInstitutionsResourceWithStreamingResponse(self)

    async def list_outstanding_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstitutionListOutstandingAccountsResponse:
        """
        Retrieves all outstanding institutional accounts across all institutions
        (accounts with non-zero balances).
        """
        return await self._get(
            "/api/v2/ledger/institutions/outstanding-accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstitutionListOutstandingAccountsResponse,
        )

    async def retrieve_outstanding_orders(
        self,
        institution_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InstitutionRetrieveOutstandingOrdersResponse:
        """
        Retrieves all outstanding orders for a specific institution (accounts with
        non-zero balances).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not institution_id:
            raise ValueError(f"Expected a non-empty value for `institution_id` but received {institution_id!r}")
        return await self._get(
            f"/api/v2/ledger/institutions/{institution_id}/outstanding-orders",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InstitutionRetrieveOutstandingOrdersResponse,
        )


class InstitutionsResourceWithRawResponse:
    def __init__(self, institutions: InstitutionsResource) -> None:
        self._institutions = institutions

        self.list_outstanding_accounts = to_raw_response_wrapper(
            institutions.list_outstanding_accounts,
        )
        self.retrieve_outstanding_orders = to_raw_response_wrapper(
            institutions.retrieve_outstanding_orders,
        )

    @cached_property
    def orders(self) -> OrdersResourceWithRawResponse:
        return OrdersResourceWithRawResponse(self._institutions.orders)


class AsyncInstitutionsResourceWithRawResponse:
    def __init__(self, institutions: AsyncInstitutionsResource) -> None:
        self._institutions = institutions

        self.list_outstanding_accounts = async_to_raw_response_wrapper(
            institutions.list_outstanding_accounts,
        )
        self.retrieve_outstanding_orders = async_to_raw_response_wrapper(
            institutions.retrieve_outstanding_orders,
        )

    @cached_property
    def orders(self) -> AsyncOrdersResourceWithRawResponse:
        return AsyncOrdersResourceWithRawResponse(self._institutions.orders)


class InstitutionsResourceWithStreamingResponse:
    def __init__(self, institutions: InstitutionsResource) -> None:
        self._institutions = institutions

        self.list_outstanding_accounts = to_streamed_response_wrapper(
            institutions.list_outstanding_accounts,
        )
        self.retrieve_outstanding_orders = to_streamed_response_wrapper(
            institutions.retrieve_outstanding_orders,
        )

    @cached_property
    def orders(self) -> OrdersResourceWithStreamingResponse:
        return OrdersResourceWithStreamingResponse(self._institutions.orders)


class AsyncInstitutionsResourceWithStreamingResponse:
    def __init__(self, institutions: AsyncInstitutionsResource) -> None:
        self._institutions = institutions

        self.list_outstanding_accounts = async_to_streamed_response_wrapper(
            institutions.list_outstanding_accounts,
        )
        self.retrieve_outstanding_orders = async_to_streamed_response_wrapper(
            institutions.retrieve_outstanding_orders,
        )

    @cached_property
    def orders(self) -> AsyncOrdersResourceWithStreamingResponse:
        return AsyncOrdersResourceWithStreamingResponse(self._institutions.orders)
