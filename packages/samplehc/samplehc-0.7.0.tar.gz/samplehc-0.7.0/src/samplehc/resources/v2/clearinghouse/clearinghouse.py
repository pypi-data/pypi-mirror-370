# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable

import httpx

from .claim import (
    ClaimResource,
    AsyncClaimResource,
    ClaimResourceWithRawResponse,
    AsyncClaimResourceWithRawResponse,
    ClaimResourceWithStreamingResponse,
    AsyncClaimResourceWithStreamingResponse,
)
from .payers import (
    PayersResource,
    AsyncPayersResource,
    PayersResourceWithRawResponse,
    AsyncPayersResourceWithRawResponse,
    PayersResourceWithStreamingResponse,
    AsyncPayersResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ....types.v2 import (
    clearinghouse_run_discovery_params,
    clearinghouse_check_eligibility_params,
    clearinghouse_calculate_patient_cost_params,
    clearinghouse_coordination_of_benefits_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.clearinghouse_run_discovery_response import ClearinghouseRunDiscoveryResponse
from ....types.v2.clearinghouse_check_eligibility_response import ClearinghouseCheckEligibilityResponse

__all__ = ["ClearinghouseResource", "AsyncClearinghouseResource"]


class ClearinghouseResource(SyncAPIResource):
    @cached_property
    def payers(self) -> PayersResource:
        return PayersResource(self._client)

    @cached_property
    def claim(self) -> ClaimResource:
        return ClaimResource(self._client)

    @cached_property
    def with_raw_response(self) -> ClearinghouseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return ClearinghouseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClearinghouseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return ClearinghouseResourceWithStreamingResponse(self)

    def calculate_patient_cost(
        self,
        *,
        eligibility_responses: Iterable[clearinghouse_calculate_patient_cost_params.EligibilityResponse],
        line_items: Iterable[clearinghouse_calculate_patient_cost_params.LineItem],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Calculates the cost of a patient's services based on the provided information.

        Args:
          eligibility_responses: The eligibility responses that the patient has in order of preference (primary,
              secondary, etc.).

          line_items: The line items you are estimating the patient cost for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/api/v2/clearinghouse/patient-cost",
            body=maybe_transform(
                {
                    "eligibility_responses": eligibility_responses,
                    "line_items": line_items,
                },
                clearinghouse_calculate_patient_cost_params.ClearinghouseCalculatePatientCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def check_eligibility(
        self,
        *,
        provider_identifier: str,
        provider_name: str,
        service_type_codes: List[str],
        subscriber_date_of_birth: str,
        subscriber_first_name: str,
        subscriber_last_name: str,
        subscriber_member_id: str,
        trading_partner_service_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClearinghouseCheckEligibilityResponse:
        """
        Verifies patient eligibility with a specific payer for given services based on
        the provided patient and provider information.

        Args:
          provider_identifier: The provider identifier. This is usually your NPI.

          provider_name: The provider name.

          service_type_codes: The service type codes.

          subscriber_date_of_birth: The date of birth of the subscriber.

          subscriber_first_name: The first name of the subscriber.

          subscriber_last_name: The last name of the subscriber.

          subscriber_member_id: The member ID of the subscriber.

          trading_partner_service_id: The trading partner service ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/clearinghouse/check-eligibility",
            body=maybe_transform(
                {
                    "provider_identifier": provider_identifier,
                    "provider_name": provider_name,
                    "service_type_codes": service_type_codes,
                    "subscriber_date_of_birth": subscriber_date_of_birth,
                    "subscriber_first_name": subscriber_first_name,
                    "subscriber_last_name": subscriber_last_name,
                    "subscriber_member_id": subscriber_member_id,
                    "trading_partner_service_id": trading_partner_service_id,
                },
                clearinghouse_check_eligibility_params.ClearinghouseCheckEligibilityParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClearinghouseCheckEligibilityResponse,
        )

    def coordination_of_benefits(
        self,
        *,
        dependent_date_of_birth: str,
        dependent_first_name: str,
        dependent_last_name: str,
        encounter_date_of_service: str,
        encounter_service_type_code: str,
        provider_name: str,
        provider_npi: str,
        subscriber_date_of_birth: str,
        subscriber_first_name: str,
        subscriber_last_name: str,
        subscriber_member_id: str,
        trading_partner_service_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Fetches coordination of benefits (COB) information for a patient from a
        specified payer, detailing other insurance coverages.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/clearinghouse/coordination-of-benefits",
            body=maybe_transform(
                {
                    "dependent_date_of_birth": dependent_date_of_birth,
                    "dependent_first_name": dependent_first_name,
                    "dependent_last_name": dependent_last_name,
                    "encounter_date_of_service": encounter_date_of_service,
                    "encounter_service_type_code": encounter_service_type_code,
                    "provider_name": provider_name,
                    "provider_npi": provider_npi,
                    "subscriber_date_of_birth": subscriber_date_of_birth,
                    "subscriber_first_name": subscriber_first_name,
                    "subscriber_last_name": subscriber_last_name,
                    "subscriber_member_id": subscriber_member_id,
                    "trading_partner_service_id": trading_partner_service_id,
                },
                clearinghouse_coordination_of_benefits_params.ClearinghouseCoordinationOfBenefitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def run_discovery(
        self,
        *,
        person: clearinghouse_run_discovery_params.Person,
        account_number: str | NotGiven = NOT_GIVEN,
        date_of_service: str | NotGiven = NOT_GIVEN,
        service_code: str | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClearinghouseRunDiscoveryResponse:
        """
        Initiates a discovery process to find insurance coverage for a patient using
        Front Runner integration.

        Args:
          person: Patient demographic information

          account_number: Account number

          date_of_service: Date of service (YYYY-MM-DD)

          service_code: Service code

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        return self._post(
            "/api/v2/clearinghouse/discovery",
            body=maybe_transform(
                {
                    "person": person,
                    "account_number": account_number,
                    "date_of_service": date_of_service,
                    "service_code": service_code,
                },
                clearinghouse_run_discovery_params.ClearinghouseRunDiscoveryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClearinghouseRunDiscoveryResponse,
        )


class AsyncClearinghouseResource(AsyncAPIResource):
    @cached_property
    def payers(self) -> AsyncPayersResource:
        return AsyncPayersResource(self._client)

    @cached_property
    def claim(self) -> AsyncClaimResource:
        return AsyncClaimResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncClearinghouseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClearinghouseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClearinghouseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncClearinghouseResourceWithStreamingResponse(self)

    async def calculate_patient_cost(
        self,
        *,
        eligibility_responses: Iterable[clearinghouse_calculate_patient_cost_params.EligibilityResponse],
        line_items: Iterable[clearinghouse_calculate_patient_cost_params.LineItem],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Calculates the cost of a patient's services based on the provided information.

        Args:
          eligibility_responses: The eligibility responses that the patient has in order of preference (primary,
              secondary, etc.).

          line_items: The line items you are estimating the patient cost for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/api/v2/clearinghouse/patient-cost",
            body=await async_maybe_transform(
                {
                    "eligibility_responses": eligibility_responses,
                    "line_items": line_items,
                },
                clearinghouse_calculate_patient_cost_params.ClearinghouseCalculatePatientCostParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def check_eligibility(
        self,
        *,
        provider_identifier: str,
        provider_name: str,
        service_type_codes: List[str],
        subscriber_date_of_birth: str,
        subscriber_first_name: str,
        subscriber_last_name: str,
        subscriber_member_id: str,
        trading_partner_service_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClearinghouseCheckEligibilityResponse:
        """
        Verifies patient eligibility with a specific payer for given services based on
        the provided patient and provider information.

        Args:
          provider_identifier: The provider identifier. This is usually your NPI.

          provider_name: The provider name.

          service_type_codes: The service type codes.

          subscriber_date_of_birth: The date of birth of the subscriber.

          subscriber_first_name: The first name of the subscriber.

          subscriber_last_name: The last name of the subscriber.

          subscriber_member_id: The member ID of the subscriber.

          trading_partner_service_id: The trading partner service ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/clearinghouse/check-eligibility",
            body=await async_maybe_transform(
                {
                    "provider_identifier": provider_identifier,
                    "provider_name": provider_name,
                    "service_type_codes": service_type_codes,
                    "subscriber_date_of_birth": subscriber_date_of_birth,
                    "subscriber_first_name": subscriber_first_name,
                    "subscriber_last_name": subscriber_last_name,
                    "subscriber_member_id": subscriber_member_id,
                    "trading_partner_service_id": trading_partner_service_id,
                },
                clearinghouse_check_eligibility_params.ClearinghouseCheckEligibilityParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClearinghouseCheckEligibilityResponse,
        )

    async def coordination_of_benefits(
        self,
        *,
        dependent_date_of_birth: str,
        dependent_first_name: str,
        dependent_last_name: str,
        encounter_date_of_service: str,
        encounter_service_type_code: str,
        provider_name: str,
        provider_npi: str,
        subscriber_date_of_birth: str,
        subscriber_first_name: str,
        subscriber_last_name: str,
        subscriber_member_id: str,
        trading_partner_service_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Fetches coordination of benefits (COB) information for a patient from a
        specified payer, detailing other insurance coverages.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/clearinghouse/coordination-of-benefits",
            body=await async_maybe_transform(
                {
                    "dependent_date_of_birth": dependent_date_of_birth,
                    "dependent_first_name": dependent_first_name,
                    "dependent_last_name": dependent_last_name,
                    "encounter_date_of_service": encounter_date_of_service,
                    "encounter_service_type_code": encounter_service_type_code,
                    "provider_name": provider_name,
                    "provider_npi": provider_npi,
                    "subscriber_date_of_birth": subscriber_date_of_birth,
                    "subscriber_first_name": subscriber_first_name,
                    "subscriber_last_name": subscriber_last_name,
                    "subscriber_member_id": subscriber_member_id,
                    "trading_partner_service_id": trading_partner_service_id,
                },
                clearinghouse_coordination_of_benefits_params.ClearinghouseCoordinationOfBenefitsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def run_discovery(
        self,
        *,
        person: clearinghouse_run_discovery_params.Person,
        account_number: str | NotGiven = NOT_GIVEN,
        date_of_service: str | NotGiven = NOT_GIVEN,
        service_code: str | NotGiven = NOT_GIVEN,
        idempotency_key: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClearinghouseRunDiscoveryResponse:
        """
        Initiates a discovery process to find insurance coverage for a patient using
        Front Runner integration.

        Args:
          person: Patient demographic information

          account_number: Account number

          date_of_service: Date of service (YYYY-MM-DD)

          service_code: Service code

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {**strip_not_given({"Idempotency-Key": idempotency_key}), **(extra_headers or {})}
        return await self._post(
            "/api/v2/clearinghouse/discovery",
            body=await async_maybe_transform(
                {
                    "person": person,
                    "account_number": account_number,
                    "date_of_service": date_of_service,
                    "service_code": service_code,
                },
                clearinghouse_run_discovery_params.ClearinghouseRunDiscoveryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClearinghouseRunDiscoveryResponse,
        )


class ClearinghouseResourceWithRawResponse:
    def __init__(self, clearinghouse: ClearinghouseResource) -> None:
        self._clearinghouse = clearinghouse

        self.calculate_patient_cost = to_raw_response_wrapper(
            clearinghouse.calculate_patient_cost,
        )
        self.check_eligibility = to_raw_response_wrapper(
            clearinghouse.check_eligibility,
        )
        self.coordination_of_benefits = to_raw_response_wrapper(
            clearinghouse.coordination_of_benefits,
        )
        self.run_discovery = to_raw_response_wrapper(
            clearinghouse.run_discovery,
        )

    @cached_property
    def payers(self) -> PayersResourceWithRawResponse:
        return PayersResourceWithRawResponse(self._clearinghouse.payers)

    @cached_property
    def claim(self) -> ClaimResourceWithRawResponse:
        return ClaimResourceWithRawResponse(self._clearinghouse.claim)


class AsyncClearinghouseResourceWithRawResponse:
    def __init__(self, clearinghouse: AsyncClearinghouseResource) -> None:
        self._clearinghouse = clearinghouse

        self.calculate_patient_cost = async_to_raw_response_wrapper(
            clearinghouse.calculate_patient_cost,
        )
        self.check_eligibility = async_to_raw_response_wrapper(
            clearinghouse.check_eligibility,
        )
        self.coordination_of_benefits = async_to_raw_response_wrapper(
            clearinghouse.coordination_of_benefits,
        )
        self.run_discovery = async_to_raw_response_wrapper(
            clearinghouse.run_discovery,
        )

    @cached_property
    def payers(self) -> AsyncPayersResourceWithRawResponse:
        return AsyncPayersResourceWithRawResponse(self._clearinghouse.payers)

    @cached_property
    def claim(self) -> AsyncClaimResourceWithRawResponse:
        return AsyncClaimResourceWithRawResponse(self._clearinghouse.claim)


class ClearinghouseResourceWithStreamingResponse:
    def __init__(self, clearinghouse: ClearinghouseResource) -> None:
        self._clearinghouse = clearinghouse

        self.calculate_patient_cost = to_streamed_response_wrapper(
            clearinghouse.calculate_patient_cost,
        )
        self.check_eligibility = to_streamed_response_wrapper(
            clearinghouse.check_eligibility,
        )
        self.coordination_of_benefits = to_streamed_response_wrapper(
            clearinghouse.coordination_of_benefits,
        )
        self.run_discovery = to_streamed_response_wrapper(
            clearinghouse.run_discovery,
        )

    @cached_property
    def payers(self) -> PayersResourceWithStreamingResponse:
        return PayersResourceWithStreamingResponse(self._clearinghouse.payers)

    @cached_property
    def claim(self) -> ClaimResourceWithStreamingResponse:
        return ClaimResourceWithStreamingResponse(self._clearinghouse.claim)


class AsyncClearinghouseResourceWithStreamingResponse:
    def __init__(self, clearinghouse: AsyncClearinghouseResource) -> None:
        self._clearinghouse = clearinghouse

        self.calculate_patient_cost = async_to_streamed_response_wrapper(
            clearinghouse.calculate_patient_cost,
        )
        self.check_eligibility = async_to_streamed_response_wrapper(
            clearinghouse.check_eligibility,
        )
        self.coordination_of_benefits = async_to_streamed_response_wrapper(
            clearinghouse.coordination_of_benefits,
        )
        self.run_discovery = async_to_streamed_response_wrapper(
            clearinghouse.run_discovery,
        )

    @cached_property
    def payers(self) -> AsyncPayersResourceWithStreamingResponse:
        return AsyncPayersResourceWithStreamingResponse(self._clearinghouse.payers)

    @cached_property
    def claim(self) -> AsyncClaimResourceWithStreamingResponse:
        return AsyncClaimResourceWithStreamingResponse(self._clearinghouse.claim)
