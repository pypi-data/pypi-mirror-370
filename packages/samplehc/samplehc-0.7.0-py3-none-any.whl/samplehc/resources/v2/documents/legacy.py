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
from ....types.v2.documents import legacy_reason_params, legacy_extract_params
from ....types.v2.documents.legacy_reason_response import LegacyReasonResponse
from ....types.v2.documents.legacy_extract_response import LegacyExtractResponse

__all__ = ["LegacyResource", "AsyncLegacyResource"]


class LegacyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LegacyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return LegacyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LegacyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return LegacyResourceWithStreamingResponse(self)

    def extract(
        self,
        *,
        answer_schemas: Iterable[legacy_extract_params.AnswerSchema],
        documents: Iterable[legacy_extract_params.Document],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LegacyExtractResponse:
        """Initiates an asynchronous legacy data extraction process.

        Returns an ID to track
        the async result.

        Args:
          answer_schemas: An array of answer schemas defining data to extract.

          documents: An array of documents to process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/legacy/extract",
            body=maybe_transform(
                {
                    "answer_schemas": answer_schemas,
                    "documents": documents,
                },
                legacy_extract_params.LegacyExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LegacyExtractResponse,
        )

    def reason(
        self,
        *,
        documents: Iterable[legacy_reason_params.Document],
        task: legacy_reason_params.Task,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LegacyReasonResponse:
        """Initiates an asynchronous document reasoning process based on a task.

        Returns an
        ID for tracking.

        Args:
          documents: An array of documents to apply reasoning to.

          task: The task schema defining the reasoning process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/legacy/reason",
            body=maybe_transform(
                {
                    "documents": documents,
                    "task": task,
                },
                legacy_reason_params.LegacyReasonParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LegacyReasonResponse,
        )


class AsyncLegacyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLegacyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLegacyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLegacyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncLegacyResourceWithStreamingResponse(self)

    async def extract(
        self,
        *,
        answer_schemas: Iterable[legacy_extract_params.AnswerSchema],
        documents: Iterable[legacy_extract_params.Document],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LegacyExtractResponse:
        """Initiates an asynchronous legacy data extraction process.

        Returns an ID to track
        the async result.

        Args:
          answer_schemas: An array of answer schemas defining data to extract.

          documents: An array of documents to process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/legacy/extract",
            body=await async_maybe_transform(
                {
                    "answer_schemas": answer_schemas,
                    "documents": documents,
                },
                legacy_extract_params.LegacyExtractParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LegacyExtractResponse,
        )

    async def reason(
        self,
        *,
        documents: Iterable[legacy_reason_params.Document],
        task: legacy_reason_params.Task,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LegacyReasonResponse:
        """Initiates an asynchronous document reasoning process based on a task.

        Returns an
        ID for tracking.

        Args:
          documents: An array of documents to apply reasoning to.

          task: The task schema defining the reasoning process.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/legacy/reason",
            body=await async_maybe_transform(
                {
                    "documents": documents,
                    "task": task,
                },
                legacy_reason_params.LegacyReasonParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LegacyReasonResponse,
        )


class LegacyResourceWithRawResponse:
    def __init__(self, legacy: LegacyResource) -> None:
        self._legacy = legacy

        self.extract = to_raw_response_wrapper(
            legacy.extract,
        )
        self.reason = to_raw_response_wrapper(
            legacy.reason,
        )


class AsyncLegacyResourceWithRawResponse:
    def __init__(self, legacy: AsyncLegacyResource) -> None:
        self._legacy = legacy

        self.extract = async_to_raw_response_wrapper(
            legacy.extract,
        )
        self.reason = async_to_raw_response_wrapper(
            legacy.reason,
        )


class LegacyResourceWithStreamingResponse:
    def __init__(self, legacy: LegacyResource) -> None:
        self._legacy = legacy

        self.extract = to_streamed_response_wrapper(
            legacy.extract,
        )
        self.reason = to_streamed_response_wrapper(
            legacy.reason,
        )


class AsyncLegacyResourceWithStreamingResponse:
    def __init__(self, legacy: AsyncLegacyResource) -> None:
        self._legacy = legacy

        self.extract = async_to_streamed_response_wrapper(
            legacy.extract,
        )
        self.reason = async_to_streamed_response_wrapper(
            legacy.reason,
        )
