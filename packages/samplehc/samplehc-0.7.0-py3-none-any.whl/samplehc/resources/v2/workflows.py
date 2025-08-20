# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import is_given, maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import workflow_query_params, workflow_start_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.workflow_query_response import WorkflowQueryResponse
from ...types.v2.workflow_start_response import WorkflowStartResponse
from ...types.v2.workflow_deploy_response import WorkflowDeployResponse

__all__ = ["WorkflowsResource", "AsyncWorkflowsResource"]


class WorkflowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> WorkflowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return WorkflowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WorkflowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return WorkflowsResourceWithStreamingResponse(self)

    def deploy(
        self,
        workflow_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowDeployResponse:
        """
        Creates a new deployment for the specified workflow ID, making the current
        version of the workflow live.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return self._post(
            f"/api/v2/workflows/{workflow_id}/deploy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowDeployResponse,
        )

    def query(
        self,
        workflow_slug: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowQueryResponse:
        """
        Query workflow outputs

        Args:
          query: The query to run on the workflow outputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_slug:
            raise ValueError(f"Expected a non-empty value for `workflow_slug` but received {workflow_slug!r}")
        return self._post(
            f"/api/v2/workflows/{workflow_slug}/query",
            body=maybe_transform({"query": query}, workflow_query_params.WorkflowQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowQueryResponse,
        )

    def start(
        self,
        workflow_slug: str,
        *,
        body: object | NotGiven = NOT_GIVEN,
        x_sample_start_data_parse_method: Literal["standard", "top-level"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStartResponse:
        """Initiates a workflow run based on its slug.

        Accepts JSON or multipart/form-data
        for input.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_slug:
            raise ValueError(f"Expected a non-empty value for `workflow_slug` but received {workflow_slug!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "X-Sample-Start-Data-Parse-Method": str(x_sample_start_data_parse_method)
                    if is_given(x_sample_start_data_parse_method)
                    else NOT_GIVEN
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            f"/api/v2/workflows/{workflow_slug}/start",
            body=maybe_transform(body, workflow_start_params.WorkflowStartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStartResponse,
        )


class AsyncWorkflowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncWorkflowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncWorkflowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWorkflowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncWorkflowsResourceWithStreamingResponse(self)

    async def deploy(
        self,
        workflow_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowDeployResponse:
        """
        Creates a new deployment for the specified workflow ID, making the current
        version of the workflow live.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_id:
            raise ValueError(f"Expected a non-empty value for `workflow_id` but received {workflow_id!r}")
        return await self._post(
            f"/api/v2/workflows/{workflow_id}/deploy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowDeployResponse,
        )

    async def query(
        self,
        workflow_slug: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowQueryResponse:
        """
        Query workflow outputs

        Args:
          query: The query to run on the workflow outputs.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_slug:
            raise ValueError(f"Expected a non-empty value for `workflow_slug` but received {workflow_slug!r}")
        return await self._post(
            f"/api/v2/workflows/{workflow_slug}/query",
            body=await async_maybe_transform({"query": query}, workflow_query_params.WorkflowQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowQueryResponse,
        )

    async def start(
        self,
        workflow_slug: str,
        *,
        body: object | NotGiven = NOT_GIVEN,
        x_sample_start_data_parse_method: Literal["standard", "top-level"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> WorkflowStartResponse:
        """Initiates a workflow run based on its slug.

        Accepts JSON or multipart/form-data
        for input.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not workflow_slug:
            raise ValueError(f"Expected a non-empty value for `workflow_slug` but received {workflow_slug!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "X-Sample-Start-Data-Parse-Method": str(x_sample_start_data_parse_method)
                    if is_given(x_sample_start_data_parse_method)
                    else NOT_GIVEN
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            f"/api/v2/workflows/{workflow_slug}/start",
            body=await async_maybe_transform(body, workflow_start_params.WorkflowStartParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=WorkflowStartResponse,
        )


class WorkflowsResourceWithRawResponse:
    def __init__(self, workflows: WorkflowsResource) -> None:
        self._workflows = workflows

        self.deploy = to_raw_response_wrapper(
            workflows.deploy,
        )
        self.query = to_raw_response_wrapper(
            workflows.query,
        )
        self.start = to_raw_response_wrapper(
            workflows.start,
        )


class AsyncWorkflowsResourceWithRawResponse:
    def __init__(self, workflows: AsyncWorkflowsResource) -> None:
        self._workflows = workflows

        self.deploy = async_to_raw_response_wrapper(
            workflows.deploy,
        )
        self.query = async_to_raw_response_wrapper(
            workflows.query,
        )
        self.start = async_to_raw_response_wrapper(
            workflows.start,
        )


class WorkflowsResourceWithStreamingResponse:
    def __init__(self, workflows: WorkflowsResource) -> None:
        self._workflows = workflows

        self.deploy = to_streamed_response_wrapper(
            workflows.deploy,
        )
        self.query = to_streamed_response_wrapper(
            workflows.query,
        )
        self.start = to_streamed_response_wrapper(
            workflows.start,
        )


class AsyncWorkflowsResourceWithStreamingResponse:
    def __init__(self, workflows: AsyncWorkflowsResource) -> None:
        self._workflows = workflows

        self.deploy = async_to_streamed_response_wrapper(
            workflows.deploy,
        )
        self.query = async_to_streamed_response_wrapper(
            workflows.query,
        )
        self.start = async_to_streamed_response_wrapper(
            workflows.start,
        )
