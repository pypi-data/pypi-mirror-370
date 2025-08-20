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
from ....types.v2.workflow_runs.step_get_output_response import StepGetOutputResponse

__all__ = ["StepResource", "AsyncStepResource"]


class StepResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StepResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return StepResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StepResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return StepResourceWithStreamingResponse(self)

    def get_output(
        self,
        step_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepGetOutputResponse:
        """Retrieves the output data of a specific step within a workflow run.

        This
        endpoint requires an ExecuteStepRequestContext with `workflowRunId` and
        `stepAddr`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return self._get(
            f"/api/v2/workflow-runs/step/{step_id}/output",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StepGetOutputResponse,
        )


class AsyncStepResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStepResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStepResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStepResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncStepResourceWithStreamingResponse(self)

    async def get_output(
        self,
        step_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StepGetOutputResponse:
        """Retrieves the output data of a specific step within a workflow run.

        This
        endpoint requires an ExecuteStepRequestContext with `workflowRunId` and
        `stepAddr`.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not step_id:
            raise ValueError(f"Expected a non-empty value for `step_id` but received {step_id!r}")
        return await self._get(
            f"/api/v2/workflow-runs/step/{step_id}/output",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StepGetOutputResponse,
        )


class StepResourceWithRawResponse:
    def __init__(self, step: StepResource) -> None:
        self._step = step

        self.get_output = to_raw_response_wrapper(
            step.get_output,
        )


class AsyncStepResourceWithRawResponse:
    def __init__(self, step: AsyncStepResource) -> None:
        self._step = step

        self.get_output = async_to_raw_response_wrapper(
            step.get_output,
        )


class StepResourceWithStreamingResponse:
    def __init__(self, step: StepResource) -> None:
        self._step = step

        self.get_output = to_streamed_response_wrapper(
            step.get_output,
        )


class AsyncStepResourceWithStreamingResponse:
    def __init__(self, step: AsyncStepResource) -> None:
        self._step = step

        self.get_output = async_to_streamed_response_wrapper(
            step.get_output,
        )
