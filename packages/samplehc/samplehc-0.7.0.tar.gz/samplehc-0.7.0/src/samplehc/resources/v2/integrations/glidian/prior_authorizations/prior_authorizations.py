# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable

import httpx

from ......_types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ......_utils import maybe_transform, async_maybe_transform
from ......_compat import cached_property
from ......_resource import SyncAPIResource, AsyncAPIResource
from ......_response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ......_base_client import make_request_options
from .clinical_questions import (
    ClinicalQuestionsResource,
    AsyncClinicalQuestionsResource,
    ClinicalQuestionsResourceWithRawResponse,
    AsyncClinicalQuestionsResourceWithRawResponse,
    ClinicalQuestionsResourceWithStreamingResponse,
    AsyncClinicalQuestionsResourceWithStreamingResponse,
)
from ......types.v2.integrations.glidian import (
    prior_authorization_create_draft_params,
    prior_authorization_update_record_params,
)
from ......types.v2.integrations.glidian.prior_authorization_submit_response import PriorAuthorizationSubmitResponse
from ......types.v2.integrations.glidian.prior_authorization_create_draft_response import (
    PriorAuthorizationCreateDraftResponse,
)
from ......types.v2.integrations.glidian.prior_authorization_update_record_response import (
    PriorAuthorizationUpdateRecordResponse,
)
from ......types.v2.integrations.glidian.prior_authorization_retrieve_record_response import (
    PriorAuthorizationRetrieveRecordResponse,
)

__all__ = ["PriorAuthorizationsResource", "AsyncPriorAuthorizationsResource"]


class PriorAuthorizationsResource(SyncAPIResource):
    @cached_property
    def clinical_questions(self) -> ClinicalQuestionsResource:
        return ClinicalQuestionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> PriorAuthorizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PriorAuthorizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PriorAuthorizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PriorAuthorizationsResourceWithStreamingResponse(self)

    def create_draft(
        self,
        slug: str,
        *,
        attachments: Iterable[prior_authorization_create_draft_params.Attachment],
        glidian_payer_id: float,
        glidian_service_id: str,
        reference_number: str,
        submission_requirements: Dict[str, str],
        reference_number_two: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationCreateDraftResponse:
        """
        Create a draft prior authorization request in Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations",
            body=maybe_transform(
                {
                    "attachments": attachments,
                    "glidian_payer_id": glidian_payer_id,
                    "glidian_service_id": glidian_service_id,
                    "reference_number": reference_number,
                    "submission_requirements": submission_requirements,
                    "reference_number_two": reference_number_two,
                    "state": state,
                },
                prior_authorization_create_draft_params.PriorAuthorizationCreateDraftParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationCreateDraftResponse,
        )

    def retrieve_record(
        self,
        record_id: str,
        *,
        slug: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationRetrieveRecordResponse:
        """
        Retrieve a specific prior authorization record from Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return self._get(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationRetrieveRecordResponse,
        )

    def submit(
        self,
        record_id: str,
        *,
        slug: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationSubmitResponse:
        """Submit a completed prior authorization to Glidian.

        All clinical questions must
        be answered first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return self._post(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/submit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationSubmitResponse,
        )

    def update_record(
        self,
        record_id: str,
        *,
        slug: str,
        reference_number: str | NotGiven = NOT_GIVEN,
        reference_number_two: str | NotGiven = NOT_GIVEN,
        submission_requirements: Dict[str, str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationUpdateRecordResponse:
        """
        Update an existing prior authorization record in Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return self._put(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}",
            body=maybe_transform(
                {
                    "reference_number": reference_number,
                    "reference_number_two": reference_number_two,
                    "submission_requirements": submission_requirements,
                },
                prior_authorization_update_record_params.PriorAuthorizationUpdateRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationUpdateRecordResponse,
        )


class AsyncPriorAuthorizationsResource(AsyncAPIResource):
    @cached_property
    def clinical_questions(self) -> AsyncClinicalQuestionsResource:
        return AsyncClinicalQuestionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPriorAuthorizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPriorAuthorizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPriorAuthorizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPriorAuthorizationsResourceWithStreamingResponse(self)

    async def create_draft(
        self,
        slug: str,
        *,
        attachments: Iterable[prior_authorization_create_draft_params.Attachment],
        glidian_payer_id: float,
        glidian_service_id: str,
        reference_number: str,
        submission_requirements: Dict[str, str],
        reference_number_two: str | NotGiven = NOT_GIVEN,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationCreateDraftResponse:
        """
        Create a draft prior authorization request in Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations",
            body=await async_maybe_transform(
                {
                    "attachments": attachments,
                    "glidian_payer_id": glidian_payer_id,
                    "glidian_service_id": glidian_service_id,
                    "reference_number": reference_number,
                    "submission_requirements": submission_requirements,
                    "reference_number_two": reference_number_two,
                    "state": state,
                },
                prior_authorization_create_draft_params.PriorAuthorizationCreateDraftParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationCreateDraftResponse,
        )

    async def retrieve_record(
        self,
        record_id: str,
        *,
        slug: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationRetrieveRecordResponse:
        """
        Retrieve a specific prior authorization record from Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return await self._get(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationRetrieveRecordResponse,
        )

    async def submit(
        self,
        record_id: str,
        *,
        slug: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationSubmitResponse:
        """Submit a completed prior authorization to Glidian.

        All clinical questions must
        be answered first.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return await self._post(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/submit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationSubmitResponse,
        )

    async def update_record(
        self,
        record_id: str,
        *,
        slug: str,
        reference_number: str | NotGiven = NOT_GIVEN,
        reference_number_two: str | NotGiven = NOT_GIVEN,
        submission_requirements: Dict[str, str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PriorAuthorizationUpdateRecordResponse:
        """
        Update an existing prior authorization record in Glidian.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        if not record_id:
            raise ValueError(f"Expected a non-empty value for `record_id` but received {record_id!r}")
        return await self._put(
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}",
            body=await async_maybe_transform(
                {
                    "reference_number": reference_number,
                    "reference_number_two": reference_number_two,
                    "submission_requirements": submission_requirements,
                },
                prior_authorization_update_record_params.PriorAuthorizationUpdateRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PriorAuthorizationUpdateRecordResponse,
        )


class PriorAuthorizationsResourceWithRawResponse:
    def __init__(self, prior_authorizations: PriorAuthorizationsResource) -> None:
        self._prior_authorizations = prior_authorizations

        self.create_draft = to_raw_response_wrapper(
            prior_authorizations.create_draft,
        )
        self.retrieve_record = to_raw_response_wrapper(
            prior_authorizations.retrieve_record,
        )
        self.submit = to_raw_response_wrapper(
            prior_authorizations.submit,
        )
        self.update_record = to_raw_response_wrapper(
            prior_authorizations.update_record,
        )

    @cached_property
    def clinical_questions(self) -> ClinicalQuestionsResourceWithRawResponse:
        return ClinicalQuestionsResourceWithRawResponse(self._prior_authorizations.clinical_questions)


class AsyncPriorAuthorizationsResourceWithRawResponse:
    def __init__(self, prior_authorizations: AsyncPriorAuthorizationsResource) -> None:
        self._prior_authorizations = prior_authorizations

        self.create_draft = async_to_raw_response_wrapper(
            prior_authorizations.create_draft,
        )
        self.retrieve_record = async_to_raw_response_wrapper(
            prior_authorizations.retrieve_record,
        )
        self.submit = async_to_raw_response_wrapper(
            prior_authorizations.submit,
        )
        self.update_record = async_to_raw_response_wrapper(
            prior_authorizations.update_record,
        )

    @cached_property
    def clinical_questions(self) -> AsyncClinicalQuestionsResourceWithRawResponse:
        return AsyncClinicalQuestionsResourceWithRawResponse(self._prior_authorizations.clinical_questions)


class PriorAuthorizationsResourceWithStreamingResponse:
    def __init__(self, prior_authorizations: PriorAuthorizationsResource) -> None:
        self._prior_authorizations = prior_authorizations

        self.create_draft = to_streamed_response_wrapper(
            prior_authorizations.create_draft,
        )
        self.retrieve_record = to_streamed_response_wrapper(
            prior_authorizations.retrieve_record,
        )
        self.submit = to_streamed_response_wrapper(
            prior_authorizations.submit,
        )
        self.update_record = to_streamed_response_wrapper(
            prior_authorizations.update_record,
        )

    @cached_property
    def clinical_questions(self) -> ClinicalQuestionsResourceWithStreamingResponse:
        return ClinicalQuestionsResourceWithStreamingResponse(self._prior_authorizations.clinical_questions)


class AsyncPriorAuthorizationsResourceWithStreamingResponse:
    def __init__(self, prior_authorizations: AsyncPriorAuthorizationsResource) -> None:
        self._prior_authorizations = prior_authorizations

        self.create_draft = async_to_streamed_response_wrapper(
            prior_authorizations.create_draft,
        )
        self.retrieve_record = async_to_streamed_response_wrapper(
            prior_authorizations.retrieve_record,
        )
        self.submit = async_to_streamed_response_wrapper(
            prior_authorizations.submit,
        )
        self.update_record = async_to_streamed_response_wrapper(
            prior_authorizations.update_record,
        )

    @cached_property
    def clinical_questions(self) -> AsyncClinicalQuestionsResourceWithStreamingResponse:
        return AsyncClinicalQuestionsResourceWithStreamingResponse(self._prior_authorizations.clinical_questions)
