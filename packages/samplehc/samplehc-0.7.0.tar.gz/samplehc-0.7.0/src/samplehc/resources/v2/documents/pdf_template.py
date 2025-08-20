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
from ....types.v2.documents.pdf_template_retrieve_metadata_response import PdfTemplateRetrieveMetadataResponse

__all__ = ["PdfTemplateResource", "AsyncPdfTemplateResource"]


class PdfTemplateResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PdfTemplateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PdfTemplateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PdfTemplateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PdfTemplateResourceWithStreamingResponse(self)

    def retrieve_metadata(
        self,
        slug: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PdfTemplateRetrieveMetadataResponse:
        """
        Retrieves document metadata for a PDF template by slug, including a presigned
        URL for direct access.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._get(
            f"/api/v2/documents/pdf-template/{slug}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfTemplateRetrieveMetadataResponse,
        )


class AsyncPdfTemplateResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPdfTemplateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPdfTemplateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPdfTemplateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPdfTemplateResourceWithStreamingResponse(self)

    async def retrieve_metadata(
        self,
        slug: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PdfTemplateRetrieveMetadataResponse:
        """
        Retrieves document metadata for a PDF template by slug, including a presigned
        URL for direct access.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._get(
            f"/api/v2/documents/pdf-template/{slug}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PdfTemplateRetrieveMetadataResponse,
        )


class PdfTemplateResourceWithRawResponse:
    def __init__(self, pdf_template: PdfTemplateResource) -> None:
        self._pdf_template = pdf_template

        self.retrieve_metadata = to_raw_response_wrapper(
            pdf_template.retrieve_metadata,
        )


class AsyncPdfTemplateResourceWithRawResponse:
    def __init__(self, pdf_template: AsyncPdfTemplateResource) -> None:
        self._pdf_template = pdf_template

        self.retrieve_metadata = async_to_raw_response_wrapper(
            pdf_template.retrieve_metadata,
        )


class PdfTemplateResourceWithStreamingResponse:
    def __init__(self, pdf_template: PdfTemplateResource) -> None:
        self._pdf_template = pdf_template

        self.retrieve_metadata = to_streamed_response_wrapper(
            pdf_template.retrieve_metadata,
        )


class AsyncPdfTemplateResourceWithStreamingResponse:
    def __init__(self, pdf_template: AsyncPdfTemplateResource) -> None:
        self._pdf_template = pdf_template

        self.retrieve_metadata = async_to_streamed_response_wrapper(
            pdf_template.retrieve_metadata,
        )
