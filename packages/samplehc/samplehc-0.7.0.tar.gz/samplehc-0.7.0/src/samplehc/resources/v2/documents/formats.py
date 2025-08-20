# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ....types.v2.documents import format_create_pdf_params
from ....types.v2.documents.format_create_pdf_response import FormatCreatePdfResponse

__all__ = ["FormatsResource", "AsyncFormatsResource"]


class FormatsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FormatsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return FormatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FormatsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return FormatsResourceWithStreamingResponse(self)

    def create_pdf(
        self,
        document_id: str,
        *,
        file_name: str,
        mime_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FormatCreatePdfResponse:
        """
        Converts an uploaded Word document (.doc, .docx) to a PDF file by creating a new
        PDF format representation. Returns the new PDF document's metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._post(
            f"/api/v2/documents/{document_id}/formats/pdf",
            body=maybe_transform(
                {
                    "file_name": file_name,
                    "mime_type": mime_type,
                },
                format_create_pdf_params.FormatCreatePdfParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FormatCreatePdfResponse,
        )


class AsyncFormatsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFormatsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFormatsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFormatsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncFormatsResourceWithStreamingResponse(self)

    async def create_pdf(
        self,
        document_id: str,
        *,
        file_name: str,
        mime_type: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FormatCreatePdfResponse:
        """
        Converts an uploaded Word document (.doc, .docx) to a PDF file by creating a new
        PDF format representation. Returns the new PDF document's metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._post(
            f"/api/v2/documents/{document_id}/formats/pdf",
            body=await async_maybe_transform(
                {
                    "file_name": file_name,
                    "mime_type": mime_type,
                },
                format_create_pdf_params.FormatCreatePdfParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FormatCreatePdfResponse,
        )


class FormatsResourceWithRawResponse:
    def __init__(self, formats: FormatsResource) -> None:
        self._formats = formats

        self.create_pdf = to_raw_response_wrapper(
            formats.create_pdf,
        )


class AsyncFormatsResourceWithRawResponse:
    def __init__(self, formats: AsyncFormatsResource) -> None:
        self._formats = formats

        self.create_pdf = async_to_raw_response_wrapper(
            formats.create_pdf,
        )


class FormatsResourceWithStreamingResponse:
    def __init__(self, formats: FormatsResource) -> None:
        self._formats = formats

        self.create_pdf = to_streamed_response_wrapper(
            formats.create_pdf,
        )


class AsyncFormatsResourceWithStreamingResponse:
    def __init__(self, formats: AsyncFormatsResource) -> None:
        self._formats = formats

        self.create_pdf = async_to_streamed_response_wrapper(
            formats.create_pdf,
        )
