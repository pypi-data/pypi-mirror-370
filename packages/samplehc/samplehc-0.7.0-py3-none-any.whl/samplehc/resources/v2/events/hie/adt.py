# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.events.hie import adt_subscribe_params

__all__ = ["AdtResource", "AsyncAdtResource"]


class AdtResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AdtResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AdtResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AdtResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AdtResourceWithStreamingResponse(self)

    def subscribe(
        self,
        *,
        address: Iterable[adt_subscribe_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[adt_subscribe_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[adt_subscribe_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Creates or updates a patient and subscribes to their ADT (Admission, Discharge,
        Transfer) feed.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/hie/adt/subscribe",
            body=maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                adt_subscribe_params.AdtSubscribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncAdtResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAdtResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAdtResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAdtResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncAdtResourceWithStreamingResponse(self)

    async def subscribe(
        self,
        *,
        address: Iterable[adt_subscribe_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[adt_subscribe_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[adt_subscribe_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Creates or updates a patient and subscribes to their ADT (Admission, Discharge,
        Transfer) feed.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/hie/adt/subscribe",
            body=await async_maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                adt_subscribe_params.AdtSubscribeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AdtResourceWithRawResponse:
    def __init__(self, adt: AdtResource) -> None:
        self._adt = adt

        self.subscribe = to_raw_response_wrapper(
            adt.subscribe,
        )


class AsyncAdtResourceWithRawResponse:
    def __init__(self, adt: AsyncAdtResource) -> None:
        self._adt = adt

        self.subscribe = async_to_raw_response_wrapper(
            adt.subscribe,
        )


class AdtResourceWithStreamingResponse:
    def __init__(self, adt: AdtResource) -> None:
        self._adt = adt

        self.subscribe = to_streamed_response_wrapper(
            adt.subscribe,
        )


class AsyncAdtResourceWithStreamingResponse:
    def __init__(self, adt: AsyncAdtResource) -> None:
        self._adt = adt

        self.subscribe = async_to_streamed_response_wrapper(
            adt.subscribe,
        )
