# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.ledger.insurance_list_outstanding_accounts_response import InsuranceListOutstandingAccountsResponse

__all__ = ["InsuranceResource", "AsyncInsuranceResource"]


class InsuranceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InsuranceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return InsuranceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InsuranceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return InsuranceResourceWithStreamingResponse(self)

    def list_outstanding_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InsuranceListOutstandingAccountsResponse:
        """
        Retrieves all outstanding insurance accounts across all insurance payors (claims
        with non-zero balances).
        """
        return self._get(
            "/api/v2/ledger/insurance/outstanding-accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InsuranceListOutstandingAccountsResponse,
        )


class AsyncInsuranceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInsuranceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInsuranceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInsuranceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncInsuranceResourceWithStreamingResponse(self)

    async def list_outstanding_accounts(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> InsuranceListOutstandingAccountsResponse:
        """
        Retrieves all outstanding insurance accounts across all insurance payors (claims
        with non-zero balances).
        """
        return await self._get(
            "/api/v2/ledger/insurance/outstanding-accounts",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=InsuranceListOutstandingAccountsResponse,
        )


class InsuranceResourceWithRawResponse:
    def __init__(self, insurance: InsuranceResource) -> None:
        self._insurance = insurance

        self.list_outstanding_accounts = to_raw_response_wrapper(
            insurance.list_outstanding_accounts,
        )


class AsyncInsuranceResourceWithRawResponse:
    def __init__(self, insurance: AsyncInsuranceResource) -> None:
        self._insurance = insurance

        self.list_outstanding_accounts = async_to_raw_response_wrapper(
            insurance.list_outstanding_accounts,
        )


class InsuranceResourceWithStreamingResponse:
    def __init__(self, insurance: InsuranceResource) -> None:
        self._insurance = insurance

        self.list_outstanding_accounts = to_streamed_response_wrapper(
            insurance.list_outstanding_accounts,
        )


class AsyncInsuranceResourceWithStreamingResponse:
    def __init__(self, insurance: AsyncInsuranceResource) -> None:
        self._insurance = insurance

        self.list_outstanding_accounts = async_to_streamed_response_wrapper(
            insurance.list_outstanding_accounts,
        )
