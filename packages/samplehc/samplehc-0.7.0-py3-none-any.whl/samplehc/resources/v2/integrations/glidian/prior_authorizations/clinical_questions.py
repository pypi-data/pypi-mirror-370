# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

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
from ......types.v2.integrations.glidian.prior_authorizations import clinical_question_update_params
from ......types.v2.integrations.glidian.prior_authorizations.clinical_question_list_response import (
    ClinicalQuestionListResponse,
)
from ......types.v2.integrations.glidian.prior_authorizations.clinical_question_update_response import (
    ClinicalQuestionUpdateResponse,
)

__all__ = ["ClinicalQuestionsResource", "AsyncClinicalQuestionsResource"]


class ClinicalQuestionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClinicalQuestionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return ClinicalQuestionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClinicalQuestionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return ClinicalQuestionsResourceWithStreamingResponse(self)

    def update(
        self,
        record_id: str,
        *,
        slug: str,
        responses: Dict[str, clinical_question_update_params.Responses],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClinicalQuestionUpdateResponse:
        """Update clinical question responses for a Glidian prior authorization.

        May
        trigger additional questions.

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
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/clinical-questions",
            body=maybe_transform(
                {"responses": responses}, clinical_question_update_params.ClinicalQuestionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClinicalQuestionUpdateResponse,
        )

    def list(
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
    ) -> ClinicalQuestionListResponse:
        """
        Retrieve clinical questions for a specific prior authorization record from
        Glidian.

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
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/clinical-questions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClinicalQuestionListResponse,
        )


class AsyncClinicalQuestionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClinicalQuestionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncClinicalQuestionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClinicalQuestionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncClinicalQuestionsResourceWithStreamingResponse(self)

    async def update(
        self,
        record_id: str,
        *,
        slug: str,
        responses: Dict[str, clinical_question_update_params.Responses],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClinicalQuestionUpdateResponse:
        """Update clinical question responses for a Glidian prior authorization.

        May
        trigger additional questions.

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
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/clinical-questions",
            body=await async_maybe_transform(
                {"responses": responses}, clinical_question_update_params.ClinicalQuestionUpdateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClinicalQuestionUpdateResponse,
        )

    async def list(
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
    ) -> ClinicalQuestionListResponse:
        """
        Retrieve clinical questions for a specific prior authorization record from
        Glidian.

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
            f"/api/v2/integrations/glidian/{slug}/prior-authorizations/{record_id}/clinical-questions",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ClinicalQuestionListResponse,
        )


class ClinicalQuestionsResourceWithRawResponse:
    def __init__(self, clinical_questions: ClinicalQuestionsResource) -> None:
        self._clinical_questions = clinical_questions

        self.update = to_raw_response_wrapper(
            clinical_questions.update,
        )
        self.list = to_raw_response_wrapper(
            clinical_questions.list,
        )


class AsyncClinicalQuestionsResourceWithRawResponse:
    def __init__(self, clinical_questions: AsyncClinicalQuestionsResource) -> None:
        self._clinical_questions = clinical_questions

        self.update = async_to_raw_response_wrapper(
            clinical_questions.update,
        )
        self.list = async_to_raw_response_wrapper(
            clinical_questions.list,
        )


class ClinicalQuestionsResourceWithStreamingResponse:
    def __init__(self, clinical_questions: ClinicalQuestionsResource) -> None:
        self._clinical_questions = clinical_questions

        self.update = to_streamed_response_wrapper(
            clinical_questions.update,
        )
        self.list = to_streamed_response_wrapper(
            clinical_questions.list,
        )


class AsyncClinicalQuestionsResourceWithStreamingResponse:
    def __init__(self, clinical_questions: AsyncClinicalQuestionsResource) -> None:
        self._clinical_questions = clinical_questions

        self.update = async_to_streamed_response_wrapper(
            clinical_questions.update,
        )
        self.list = async_to_streamed_response_wrapper(
            clinical_questions.list,
        )
