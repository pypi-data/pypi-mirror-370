# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

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
from ....types.v2.browser_automation import availity_submit_appeal_params
from ....types.v2.browser_automation.availity_submit_appeal_response import AvailitySubmitAppealResponse

__all__ = ["AvailityResource", "AsyncAvailityResource"]


class AvailityResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AvailityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AvailityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AvailityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AvailityResourceWithStreamingResponse(self)

    def submit_appeal(
        self,
        *,
        availity_payer: Literal["Anthem - CA"],
        billed_amount: str,
        claim_number: str,
        contact_phone_number: str,
        document: availity_submit_appeal_params.Document,
        member_date_of_birth: str,
        member_first_name: str,
        member_id: str,
        member_last_name: str,
        request_reason: Literal[
            "Authorization Issue",
            "Balance Bill (Not Medicaid)",
            "Benefit Issue",
            "Claim Coding Issue",
            "Claim Payment Issue",
            "Contract Dispute",
            "DRG Outlier Review",
            "Federal Surprise Bill (Not Medicaid)",
            "State Surprise Bill (Not Medicaid)",
            "Timely Filing",
        ],
        service_start_date: str,
        state: str,
        supporting_rationale: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AvailitySubmitAppealResponse:
        """Initiates an asynchronous process to submit an appeal to Availity.

        Returns an ID
        for tracking.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/browser-automation/availity/submit-appeal",
            body=maybe_transform(
                {
                    "availity_payer": availity_payer,
                    "billed_amount": billed_amount,
                    "claim_number": claim_number,
                    "contact_phone_number": contact_phone_number,
                    "document": document,
                    "member_date_of_birth": member_date_of_birth,
                    "member_first_name": member_first_name,
                    "member_id": member_id,
                    "member_last_name": member_last_name,
                    "request_reason": request_reason,
                    "service_start_date": service_start_date,
                    "state": state,
                    "supporting_rationale": supporting_rationale,
                },
                availity_submit_appeal_params.AvailitySubmitAppealParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AvailitySubmitAppealResponse,
        )


class AsyncAvailityResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAvailityResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAvailityResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAvailityResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncAvailityResourceWithStreamingResponse(self)

    async def submit_appeal(
        self,
        *,
        availity_payer: Literal["Anthem - CA"],
        billed_amount: str,
        claim_number: str,
        contact_phone_number: str,
        document: availity_submit_appeal_params.Document,
        member_date_of_birth: str,
        member_first_name: str,
        member_id: str,
        member_last_name: str,
        request_reason: Literal[
            "Authorization Issue",
            "Balance Bill (Not Medicaid)",
            "Benefit Issue",
            "Claim Coding Issue",
            "Claim Payment Issue",
            "Contract Dispute",
            "DRG Outlier Review",
            "Federal Surprise Bill (Not Medicaid)",
            "State Surprise Bill (Not Medicaid)",
            "Timely Filing",
        ],
        service_start_date: str,
        state: str,
        supporting_rationale: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AvailitySubmitAppealResponse:
        """Initiates an asynchronous process to submit an appeal to Availity.

        Returns an ID
        for tracking.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/browser-automation/availity/submit-appeal",
            body=await async_maybe_transform(
                {
                    "availity_payer": availity_payer,
                    "billed_amount": billed_amount,
                    "claim_number": claim_number,
                    "contact_phone_number": contact_phone_number,
                    "document": document,
                    "member_date_of_birth": member_date_of_birth,
                    "member_first_name": member_first_name,
                    "member_id": member_id,
                    "member_last_name": member_last_name,
                    "request_reason": request_reason,
                    "service_start_date": service_start_date,
                    "state": state,
                    "supporting_rationale": supporting_rationale,
                },
                availity_submit_appeal_params.AvailitySubmitAppealParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AvailitySubmitAppealResponse,
        )


class AvailityResourceWithRawResponse:
    def __init__(self, availity: AvailityResource) -> None:
        self._availity = availity

        self.submit_appeal = to_raw_response_wrapper(
            availity.submit_appeal,
        )


class AsyncAvailityResourceWithRawResponse:
    def __init__(self, availity: AsyncAvailityResource) -> None:
        self._availity = availity

        self.submit_appeal = async_to_raw_response_wrapper(
            availity.submit_appeal,
        )


class AvailityResourceWithStreamingResponse:
    def __init__(self, availity: AvailityResource) -> None:
        self._availity = availity

        self.submit_appeal = to_streamed_response_wrapper(
            availity.submit_appeal,
        )


class AsyncAvailityResourceWithStreamingResponse:
    def __init__(self, availity: AsyncAvailityResource) -> None:
        self._availity = availity

        self.submit_appeal = async_to_streamed_response_wrapper(
            availity.submit_appeal,
        )
