# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ....types.v2.clearinghouse import claim_submit_params
from ....types.v2.clearinghouse.claim_submit_response import ClaimSubmitResponse

__all__ = ["ClaimResource", "AsyncClaimResource"]


class ClaimResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClaimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return ClaimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClaimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return ClaimResourceWithStreamingResponse(self)

    def cancel(
        self,
        claim_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Voids a previously submitted claim by submitting a new claim with
        claimFrequencyCode set to 8.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not claim_id:
            raise ValueError(f"Expected a non-empty value for `claim_id` but received {claim_id!r}")
        return self._post(
            f"/api/v2/clearinghouse/claim/{claim_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def retrieve_status(
        self,
        claim_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Retrieves the status and details of a submitted claim by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not claim_id:
            raise ValueError(f"Expected a non-empty value for `claim_id` but received {claim_id!r}")
        return self._get(
            f"/api/v2/clearinghouse/claim/{claim_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def submit(
        self,
        *,
        billing: claim_submit_params.Billing,
        claim_information: claim_submit_params.ClaimInformation,
        is_testing: bool,
        receiver: claim_submit_params.Receiver,
        submitter: claim_submit_params.Submitter,
        subscriber: claim_submit_params.Subscriber,
        trading_partner_service_id: str,
        control_number: str | NotGiven = NOT_GIVEN,
        dependent: claim_submit_params.Dependent | NotGiven = NOT_GIVEN,
        ordering: claim_submit_params.Ordering | NotGiven = NOT_GIVEN,
        payer_address: claim_submit_params.PayerAddress | NotGiven = NOT_GIVEN,
        pay_to_address: claim_submit_params.PayToAddress | NotGiven = NOT_GIVEN,
        pay_to_plan: claim_submit_params.PayToPlan | NotGiven = NOT_GIVEN,
        providers: Iterable[claim_submit_params.Provider] | NotGiven = NOT_GIVEN,
        referring: claim_submit_params.Referring | NotGiven = NOT_GIVEN,
        rendering: claim_submit_params.Rendering | NotGiven = NOT_GIVEN,
        supervising: claim_submit_params.Supervising | NotGiven = NOT_GIVEN,
        trading_partner_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClaimSubmitResponse:
        """Submits an electronic claim for processing.

        The submission is handled
        asynchronously, and this endpoint returns an identifier to track the status of
        the claim submission.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/clearinghouse/claim",
            body=maybe_transform(
                {
                    "billing": billing,
                    "claim_information": claim_information,
                    "is_testing": is_testing,
                    "receiver": receiver,
                    "submitter": submitter,
                    "subscriber": subscriber,
                    "trading_partner_service_id": trading_partner_service_id,
                    "control_number": control_number,
                    "dependent": dependent,
                    "ordering": ordering,
                    "payer_address": payer_address,
                    "pay_to_address": pay_to_address,
                    "pay_to_plan": pay_to_plan,
                    "providers": providers,
                    "referring": referring,
                    "rendering": rendering,
                    "supervising": supervising,
                    "trading_partner_name": trading_partner_name,
                },
                claim_submit_params.ClaimSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClaimSubmitResponse,
        )


class AsyncClaimResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClaimResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClaimResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClaimResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncClaimResourceWithStreamingResponse(self)

    async def cancel(
        self,
        claim_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Voids a previously submitted claim by submitting a new claim with
        claimFrequencyCode set to 8.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not claim_id:
            raise ValueError(f"Expected a non-empty value for `claim_id` but received {claim_id!r}")
        return await self._post(
            f"/api/v2/clearinghouse/claim/{claim_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def retrieve_status(
        self,
        claim_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Retrieves the status and details of a submitted claim by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not claim_id:
            raise ValueError(f"Expected a non-empty value for `claim_id` but received {claim_id!r}")
        return await self._get(
            f"/api/v2/clearinghouse/claim/{claim_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def submit(
        self,
        *,
        billing: claim_submit_params.Billing,
        claim_information: claim_submit_params.ClaimInformation,
        is_testing: bool,
        receiver: claim_submit_params.Receiver,
        submitter: claim_submit_params.Submitter,
        subscriber: claim_submit_params.Subscriber,
        trading_partner_service_id: str,
        control_number: str | NotGiven = NOT_GIVEN,
        dependent: claim_submit_params.Dependent | NotGiven = NOT_GIVEN,
        ordering: claim_submit_params.Ordering | NotGiven = NOT_GIVEN,
        payer_address: claim_submit_params.PayerAddress | NotGiven = NOT_GIVEN,
        pay_to_address: claim_submit_params.PayToAddress | NotGiven = NOT_GIVEN,
        pay_to_plan: claim_submit_params.PayToPlan | NotGiven = NOT_GIVEN,
        providers: Iterable[claim_submit_params.Provider] | NotGiven = NOT_GIVEN,
        referring: claim_submit_params.Referring | NotGiven = NOT_GIVEN,
        rendering: claim_submit_params.Rendering | NotGiven = NOT_GIVEN,
        supervising: claim_submit_params.Supervising | NotGiven = NOT_GIVEN,
        trading_partner_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClaimSubmitResponse:
        """Submits an electronic claim for processing.

        The submission is handled
        asynchronously, and this endpoint returns an identifier to track the status of
        the claim submission.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/clearinghouse/claim",
            body=await async_maybe_transform(
                {
                    "billing": billing,
                    "claim_information": claim_information,
                    "is_testing": is_testing,
                    "receiver": receiver,
                    "submitter": submitter,
                    "subscriber": subscriber,
                    "trading_partner_service_id": trading_partner_service_id,
                    "control_number": control_number,
                    "dependent": dependent,
                    "ordering": ordering,
                    "payer_address": payer_address,
                    "pay_to_address": pay_to_address,
                    "pay_to_plan": pay_to_plan,
                    "providers": providers,
                    "referring": referring,
                    "rendering": rendering,
                    "supervising": supervising,
                    "trading_partner_name": trading_partner_name,
                },
                claim_submit_params.ClaimSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClaimSubmitResponse,
        )


class ClaimResourceWithRawResponse:
    def __init__(self, claim: ClaimResource) -> None:
        self._claim = claim

        self.cancel = to_raw_response_wrapper(
            claim.cancel,
        )
        self.retrieve_status = to_raw_response_wrapper(
            claim.retrieve_status,
        )
        self.submit = to_raw_response_wrapper(
            claim.submit,
        )


class AsyncClaimResourceWithRawResponse:
    def __init__(self, claim: AsyncClaimResource) -> None:
        self._claim = claim

        self.cancel = async_to_raw_response_wrapper(
            claim.cancel,
        )
        self.retrieve_status = async_to_raw_response_wrapper(
            claim.retrieve_status,
        )
        self.submit = async_to_raw_response_wrapper(
            claim.submit,
        )


class ClaimResourceWithStreamingResponse:
    def __init__(self, claim: ClaimResource) -> None:
        self._claim = claim

        self.cancel = to_streamed_response_wrapper(
            claim.cancel,
        )
        self.retrieve_status = to_streamed_response_wrapper(
            claim.retrieve_status,
        )
        self.submit = to_streamed_response_wrapper(
            claim.submit,
        )


class AsyncClaimResourceWithStreamingResponse:
    def __init__(self, claim: AsyncClaimResource) -> None:
        self._claim = claim

        self.cancel = async_to_streamed_response_wrapper(
            claim.cancel,
        )
        self.retrieve_status = async_to_streamed_response_wrapper(
            claim.retrieve_status,
        )
        self.submit = async_to_streamed_response_wrapper(
            claim.submit,
        )
