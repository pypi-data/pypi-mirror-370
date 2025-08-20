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
from ....types.v2.tasks import state_update_params
from ....types.v2.tasks.state_get_response import StateGetResponse
from ....types.v2.tasks.state_update_response import StateUpdateResponse

__all__ = ["StateResource", "AsyncStateResource"]


class StateResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return StateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return StateResourceWithStreamingResponse(self)

    def update(
        self,
        task_id: str,
        *,
        key: str,
        value: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StateUpdateResponse:
        """
        Updates the state of a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/api/v2/tasks/{task_id}/state",
            body=maybe_transform(
                {
                    "key": key,
                    "value": value,
                },
                state_update_params.StateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StateUpdateResponse,
        )

    def get(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StateGetResponse:
        """Retrieves the state of a task.

        This is typically used for tasks that need to
        persist state across multiple requests.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/api/v2/tasks/{task_id}/state",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StateGetResponse,
        )


class AsyncStateResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncStateResourceWithStreamingResponse(self)

    async def update(
        self,
        task_id: str,
        *,
        key: str,
        value: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StateUpdateResponse:
        """
        Updates the state of a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/api/v2/tasks/{task_id}/state",
            body=await async_maybe_transform(
                {
                    "key": key,
                    "value": value,
                },
                state_update_params.StateUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StateUpdateResponse,
        )

    async def get(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> StateGetResponse:
        """Retrieves the state of a task.

        This is typically used for tasks that need to
        persist state across multiple requests.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/api/v2/tasks/{task_id}/state",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StateGetResponse,
        )


class StateResourceWithRawResponse:
    def __init__(self, state: StateResource) -> None:
        self._state = state

        self.update = to_raw_response_wrapper(
            state.update,
        )
        self.get = to_raw_response_wrapper(
            state.get,
        )


class AsyncStateResourceWithRawResponse:
    def __init__(self, state: AsyncStateResource) -> None:
        self._state = state

        self.update = async_to_raw_response_wrapper(
            state.update,
        )
        self.get = async_to_raw_response_wrapper(
            state.get,
        )


class StateResourceWithStreamingResponse:
    def __init__(self, state: StateResource) -> None:
        self._state = state

        self.update = to_streamed_response_wrapper(
            state.update,
        )
        self.get = to_streamed_response_wrapper(
            state.get,
        )


class AsyncStateResourceWithStreamingResponse:
    def __init__(self, state: AsyncStateResource) -> None:
        self._state = state

        self.update = async_to_streamed_response_wrapper(
            state.update,
        )
        self.get = async_to_streamed_response_wrapper(
            state.get,
        )
