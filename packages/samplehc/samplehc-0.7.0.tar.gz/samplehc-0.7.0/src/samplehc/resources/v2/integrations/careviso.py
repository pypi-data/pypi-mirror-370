# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
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
from ....types.v2.integrations import careviso_submit_prior_authorization_params
from ....types.v2.integrations.careviso_get_payers_response import CarevisoGetPayersResponse

__all__ = ["CarevisoResource", "AsyncCarevisoResource"]


class CarevisoResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CarevisoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return CarevisoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CarevisoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return CarevisoResourceWithStreamingResponse(self)

    def get_payers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CarevisoGetPayersResponse:
        """Get a list of Careviso payers."""
        return self._get(
            "/api/v2/integrations/careviso/payers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CarevisoGetPayersResponse,
        )

    def submit_prior_authorization(
        self,
        slug: str,
        *,
        attachments: Iterable[careviso_submit_prior_authorization_params.Attachment],
        case_type: Literal["prior_auth_request", "benefits_investigation"],
        cpt_codes: List[str],
        group_id: str,
        icd10_codes: List[str],
        insurance_name: str,
        lab_order_id: str,
        member_id: str,
        patient_dob: str,
        patient_first_name: str,
        patient_id: str,
        patient_last_name: str,
        patient_phone: str,
        provider_fax: str,
        provider_first_name: str,
        provider_id: str,
        provider_last_name: str,
        provider_npi: str,
        provider_phone: str,
        service_date: str,
        test_names: List[str],
        accession_date: str | NotGiven = NOT_GIVEN,
        collection_date: str | NotGiven = NOT_GIVEN,
        collection_type: str | NotGiven = NOT_GIVEN,
        insurance_id: str | NotGiven = NOT_GIVEN,
        patient_city: str | NotGiven = NOT_GIVEN,
        patient_gender: Literal["M", "F", "Non-binary", "Non-specified"] | NotGiven = NOT_GIVEN,
        patient_state: str | NotGiven = NOT_GIVEN,
        patient_street: str | NotGiven = NOT_GIVEN,
        patient_street2: str | NotGiven = NOT_GIVEN,
        patient_zip: str | NotGiven = NOT_GIVEN,
        test_identifiers: List[str] | NotGiven = NOT_GIVEN,
        test_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Submit a prior authorization request to Careviso.

        Args:
          service_date: The date of service for the test. Should be in the format YYYY-MM-DD.

          collection_date: The date of collection for the test. Should be in the format YYYY-MM-DD.

          collection_type: The type of collection for the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/careviso/{slug}/prior-authorizations",
            body=maybe_transform(
                {
                    "attachments": attachments,
                    "case_type": case_type,
                    "cpt_codes": cpt_codes,
                    "group_id": group_id,
                    "icd10_codes": icd10_codes,
                    "insurance_name": insurance_name,
                    "lab_order_id": lab_order_id,
                    "member_id": member_id,
                    "patient_dob": patient_dob,
                    "patient_first_name": patient_first_name,
                    "patient_id": patient_id,
                    "patient_last_name": patient_last_name,
                    "patient_phone": patient_phone,
                    "provider_fax": provider_fax,
                    "provider_first_name": provider_first_name,
                    "provider_id": provider_id,
                    "provider_last_name": provider_last_name,
                    "provider_npi": provider_npi,
                    "provider_phone": provider_phone,
                    "service_date": service_date,
                    "test_names": test_names,
                    "accession_date": accession_date,
                    "collection_date": collection_date,
                    "collection_type": collection_type,
                    "insurance_id": insurance_id,
                    "patient_city": patient_city,
                    "patient_gender": patient_gender,
                    "patient_state": patient_state,
                    "patient_street": patient_street,
                    "patient_street2": patient_street2,
                    "patient_zip": patient_zip,
                    "test_identifiers": test_identifiers,
                    "test_type": test_type,
                },
                careviso_submit_prior_authorization_params.CarevisoSubmitPriorAuthorizationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncCarevisoResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCarevisoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCarevisoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCarevisoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncCarevisoResourceWithStreamingResponse(self)

    async def get_payers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CarevisoGetPayersResponse:
        """Get a list of Careviso payers."""
        return await self._get(
            "/api/v2/integrations/careviso/payers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CarevisoGetPayersResponse,
        )

    async def submit_prior_authorization(
        self,
        slug: str,
        *,
        attachments: Iterable[careviso_submit_prior_authorization_params.Attachment],
        case_type: Literal["prior_auth_request", "benefits_investigation"],
        cpt_codes: List[str],
        group_id: str,
        icd10_codes: List[str],
        insurance_name: str,
        lab_order_id: str,
        member_id: str,
        patient_dob: str,
        patient_first_name: str,
        patient_id: str,
        patient_last_name: str,
        patient_phone: str,
        provider_fax: str,
        provider_first_name: str,
        provider_id: str,
        provider_last_name: str,
        provider_npi: str,
        provider_phone: str,
        service_date: str,
        test_names: List[str],
        accession_date: str | NotGiven = NOT_GIVEN,
        collection_date: str | NotGiven = NOT_GIVEN,
        collection_type: str | NotGiven = NOT_GIVEN,
        insurance_id: str | NotGiven = NOT_GIVEN,
        patient_city: str | NotGiven = NOT_GIVEN,
        patient_gender: Literal["M", "F", "Non-binary", "Non-specified"] | NotGiven = NOT_GIVEN,
        patient_state: str | NotGiven = NOT_GIVEN,
        patient_street: str | NotGiven = NOT_GIVEN,
        patient_street2: str | NotGiven = NOT_GIVEN,
        patient_zip: str | NotGiven = NOT_GIVEN,
        test_identifiers: List[str] | NotGiven = NOT_GIVEN,
        test_type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Submit a prior authorization request to Careviso.

        Args:
          service_date: The date of service for the test. Should be in the format YYYY-MM-DD.

          collection_date: The date of collection for the test. Should be in the format YYYY-MM-DD.

          collection_type: The type of collection for the test

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/careviso/{slug}/prior-authorizations",
            body=await async_maybe_transform(
                {
                    "attachments": attachments,
                    "case_type": case_type,
                    "cpt_codes": cpt_codes,
                    "group_id": group_id,
                    "icd10_codes": icd10_codes,
                    "insurance_name": insurance_name,
                    "lab_order_id": lab_order_id,
                    "member_id": member_id,
                    "patient_dob": patient_dob,
                    "patient_first_name": patient_first_name,
                    "patient_id": patient_id,
                    "patient_last_name": patient_last_name,
                    "patient_phone": patient_phone,
                    "provider_fax": provider_fax,
                    "provider_first_name": provider_first_name,
                    "provider_id": provider_id,
                    "provider_last_name": provider_last_name,
                    "provider_npi": provider_npi,
                    "provider_phone": provider_phone,
                    "service_date": service_date,
                    "test_names": test_names,
                    "accession_date": accession_date,
                    "collection_date": collection_date,
                    "collection_type": collection_type,
                    "insurance_id": insurance_id,
                    "patient_city": patient_city,
                    "patient_gender": patient_gender,
                    "patient_state": patient_state,
                    "patient_street": patient_street,
                    "patient_street2": patient_street2,
                    "patient_zip": patient_zip,
                    "test_identifiers": test_identifiers,
                    "test_type": test_type,
                },
                careviso_submit_prior_authorization_params.CarevisoSubmitPriorAuthorizationParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class CarevisoResourceWithRawResponse:
    def __init__(self, careviso: CarevisoResource) -> None:
        self._careviso = careviso

        self.get_payers = to_raw_response_wrapper(
            careviso.get_payers,
        )
        self.submit_prior_authorization = to_raw_response_wrapper(
            careviso.submit_prior_authorization,
        )


class AsyncCarevisoResourceWithRawResponse:
    def __init__(self, careviso: AsyncCarevisoResource) -> None:
        self._careviso = careviso

        self.get_payers = async_to_raw_response_wrapper(
            careviso.get_payers,
        )
        self.submit_prior_authorization = async_to_raw_response_wrapper(
            careviso.submit_prior_authorization,
        )


class CarevisoResourceWithStreamingResponse:
    def __init__(self, careviso: CarevisoResource) -> None:
        self._careviso = careviso

        self.get_payers = to_streamed_response_wrapper(
            careviso.get_payers,
        )
        self.submit_prior_authorization = to_streamed_response_wrapper(
            careviso.submit_prior_authorization,
        )


class AsyncCarevisoResourceWithStreamingResponse:
    def __init__(self, careviso: AsyncCarevisoResource) -> None:
        self._careviso = careviso

        self.get_payers = async_to_streamed_response_wrapper(
            careviso.get_payers,
        )
        self.submit_prior_authorization = async_to_streamed_response_wrapper(
            careviso.submit_prior_authorization,
        )
