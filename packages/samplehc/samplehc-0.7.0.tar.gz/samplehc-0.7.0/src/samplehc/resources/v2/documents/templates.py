# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, overload

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import required_args, maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.documents import template_render_document_params, template_generate_document_async_params
from ....types.v2.documents.template_render_document_response import TemplateRenderDocumentResponse
from ....types.v2.documents.template_generate_document_async_response import TemplateGenerateDocumentAsyncResponse

__all__ = ["TemplatesResource", "AsyncTemplatesResource"]


class TemplatesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return TemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return TemplatesResourceWithStreamingResponse(self)

    @overload
    def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["document"],
        document_body: object | NotGiven = NOT_GIVEN,
        file_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        """
        Initiates an asynchronous process to generate a document from a template slug
        and relevant data (documentBody for document, variables for PDF). Returns an ID
        for tracking.

        Args:
          slug: The slug of the template to use.

          document_body: The body of the document.

          file_name: The name of the file to save.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["pdf"],
        variables: Dict[str, Union[str, float, bool, Iterable[Dict[str, Union[str, float]]]]],
        file_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        """
        Initiates an asynchronous process to generate a document from a template slug
        and relevant data (documentBody for document, variables for PDF). Returns an ID
        for tracking.

        Args:
          slug: The slug of the template to use.

          variables: The variables to use in the template. Arrays will be converted to text
              representation for PDF form fields.

          file_name: The name of the file to save.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["slug", "type"], ["slug", "type", "variables"])
    def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["document"] | Literal["pdf"],
        document_body: object | NotGiven = NOT_GIVEN,
        file_name: str | NotGiven = NOT_GIVEN,
        variables: Dict[str, Union[str, float, bool, Iterable[Dict[str, Union[str, float]]]]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        return self._post(
            "/api/v2/documents/templates/generate-document",
            body=maybe_transform(
                {
                    "slug": slug,
                    "type": type,
                    "document_body": document_body,
                    "file_name": file_name,
                    "variables": variables,
                },
                template_generate_document_async_params.TemplateGenerateDocumentAsyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplateGenerateDocumentAsyncResponse,
        )

    def render_document(
        self,
        *,
        slug: str,
        variables: Dict[str, Union[Iterable[Dict[str, str]], str]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateRenderDocumentResponse:
        """
        Renders a document body from a template slug and variables and returns the JSON
        content. Variables can be strings or arrays of objects for table data.

        Args:
          slug: The slug of the template to use.

          variables: The variables to use in the template. Can be strings or arrays of objects for
              table data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/documents/templates/render",
            body=maybe_transform(
                {
                    "slug": slug,
                    "variables": variables,
                },
                template_render_document_params.TemplateRenderDocumentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplateRenderDocumentResponse,
        )


class AsyncTemplatesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTemplatesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTemplatesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTemplatesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncTemplatesResourceWithStreamingResponse(self)

    @overload
    async def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["document"],
        document_body: object | NotGiven = NOT_GIVEN,
        file_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        """
        Initiates an asynchronous process to generate a document from a template slug
        and relevant data (documentBody for document, variables for PDF). Returns an ID
        for tracking.

        Args:
          slug: The slug of the template to use.

          document_body: The body of the document.

          file_name: The name of the file to save.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["pdf"],
        variables: Dict[str, Union[str, float, bool, Iterable[Dict[str, Union[str, float]]]]],
        file_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        """
        Initiates an asynchronous process to generate a document from a template slug
        and relevant data (documentBody for document, variables for PDF). Returns an ID
        for tracking.

        Args:
          slug: The slug of the template to use.

          variables: The variables to use in the template. Arrays will be converted to text
              representation for PDF form fields.

          file_name: The name of the file to save.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["slug", "type"], ["slug", "type", "variables"])
    async def generate_document_async(
        self,
        *,
        slug: str,
        type: Literal["document"] | Literal["pdf"],
        document_body: object | NotGiven = NOT_GIVEN,
        file_name: str | NotGiven = NOT_GIVEN,
        variables: Dict[str, Union[str, float, bool, Iterable[Dict[str, Union[str, float]]]]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateGenerateDocumentAsyncResponse:
        return await self._post(
            "/api/v2/documents/templates/generate-document",
            body=await async_maybe_transform(
                {
                    "slug": slug,
                    "type": type,
                    "document_body": document_body,
                    "file_name": file_name,
                    "variables": variables,
                },
                template_generate_document_async_params.TemplateGenerateDocumentAsyncParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplateGenerateDocumentAsyncResponse,
        )

    async def render_document(
        self,
        *,
        slug: str,
        variables: Dict[str, Union[Iterable[Dict[str, str]], str]],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TemplateRenderDocumentResponse:
        """
        Renders a document body from a template slug and variables and returns the JSON
        content. Variables can be strings or arrays of objects for table data.

        Args:
          slug: The slug of the template to use.

          variables: The variables to use in the template. Can be strings or arrays of objects for
              table data.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/documents/templates/render",
            body=await async_maybe_transform(
                {
                    "slug": slug,
                    "variables": variables,
                },
                template_render_document_params.TemplateRenderDocumentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplateRenderDocumentResponse,
        )


class TemplatesResourceWithRawResponse:
    def __init__(self, templates: TemplatesResource) -> None:
        self._templates = templates

        self.generate_document_async = to_raw_response_wrapper(
            templates.generate_document_async,
        )
        self.render_document = to_raw_response_wrapper(
            templates.render_document,
        )


class AsyncTemplatesResourceWithRawResponse:
    def __init__(self, templates: AsyncTemplatesResource) -> None:
        self._templates = templates

        self.generate_document_async = async_to_raw_response_wrapper(
            templates.generate_document_async,
        )
        self.render_document = async_to_raw_response_wrapper(
            templates.render_document,
        )


class TemplatesResourceWithStreamingResponse:
    def __init__(self, templates: TemplatesResource) -> None:
        self._templates = templates

        self.generate_document_async = to_streamed_response_wrapper(
            templates.generate_document_async,
        )
        self.render_document = to_streamed_response_wrapper(
            templates.render_document,
        )


class AsyncTemplatesResourceWithStreamingResponse:
    def __init__(self, templates: AsyncTemplatesResource) -> None:
        self._templates = templates

        self.generate_document_async = async_to_streamed_response_wrapper(
            templates.generate_document_async,
        )
        self.render_document = async_to_streamed_response_wrapper(
            templates.render_document,
        )
