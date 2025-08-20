# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Optional, cast

import httpx

from .state import (
    StateResource,
    AsyncStateResource,
    StateResourceWithRawResponse,
    AsyncStateResourceWithRawResponse,
    StateResourceWithStreamingResponse,
    AsyncStateResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ....types.v2 import task_complete_params, task_update_screen_time_params
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.task_retry_response import TaskRetryResponse
from ....types.v2.task_cancel_response import TaskCancelResponse
from ....types.v2.task_complete_response import TaskCompleteResponse
from ....types.v2.task_retrieve_response import TaskRetrieveResponse
from ....types.v2.task_update_screen_time_response import TaskUpdateScreenTimeResponse
from ....types.v2.task_get_suspended_payload_response import TaskGetSuspendedPayloadResponse

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def state(self) -> StateResource:
        return StateResource(self._client)

    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def retrieve(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskRetrieveResponse:
        """
        Retrieves the details of a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/api/v2/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetrieveResponse,
        )

    def cancel(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskCancelResponse:
        """Marks a specified task as cancelled, preventing it from being executed.

        This
        also halts the execution of any subsequent tasks in the workflow.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/api/v2/tasks/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCancelResponse,
        )

    def complete(
        self,
        task_id: str,
        *,
        result: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskCompleteResponse:
        """Marks a specified task as complete, providing the result of its execution.

        This
        may trigger the next task in the workflow.

        Args:
          result: The result data from the task's execution.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/api/v2/tasks/{task_id}/complete",
            body=maybe_transform({"result": result}, task_complete_params.TaskCompleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCompleteResponse,
        )

    def get_suspended_payload(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskGetSuspendedPayloadResponse:
        """
        Retrieves the payload with which a task was suspended, typically for tasks
        awaiting external interaction or data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/api/v2/tasks/{task_id}/suspended-payload",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskGetSuspendedPayloadResponse,
        )

    def retry(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskRetryResponse:
        """Attempts to retry a failed task.

        This will re-queue the task for execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/api/v2/tasks/{task_id}/retry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetryResponse,
        )

    def update_screen_time(
        self,
        task_id: str,
        *,
        additional_screen_time: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Optional[TaskUpdateScreenTimeResponse]:
        """Adds a specified duration to the total screen time recorded for a task.

        This is
        typically used for tasks involving user interaction.

        Args:
          additional_screen_time: The additional screen time in milliseconds to add to the task's total.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._post(
            f"/api/v2/tasks/{task_id}/update-screen-time",
            body=maybe_transform(
                {"additional_screen_time": additional_screen_time},
                task_update_screen_time_params.TaskUpdateScreenTimeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(
                Any, TaskUpdateScreenTimeResponse
            ),  # Enum types cannot be passed in as arguments in the type system
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def state(self) -> AsyncStateResource:
        return AsyncStateResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskRetrieveResponse:
        """
        Retrieves the details of a task.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/api/v2/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetrieveResponse,
        )

    async def cancel(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskCancelResponse:
        """Marks a specified task as cancelled, preventing it from being executed.

        This
        also halts the execution of any subsequent tasks in the workflow.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/api/v2/tasks/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCancelResponse,
        )

    async def complete(
        self,
        task_id: str,
        *,
        result: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskCompleteResponse:
        """Marks a specified task as complete, providing the result of its execution.

        This
        may trigger the next task in the workflow.

        Args:
          result: The result data from the task's execution.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/api/v2/tasks/{task_id}/complete",
            body=await async_maybe_transform({"result": result}, task_complete_params.TaskCompleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskCompleteResponse,
        )

    async def get_suspended_payload(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskGetSuspendedPayloadResponse:
        """
        Retrieves the payload with which a task was suspended, typically for tasks
        awaiting external interaction or data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/api/v2/tasks/{task_id}/suspended-payload",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskGetSuspendedPayloadResponse,
        )

    async def retry(
        self,
        task_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TaskRetryResponse:
        """Attempts to retry a failed task.

        This will re-queue the task for execution.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/api/v2/tasks/{task_id}/retry",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskRetryResponse,
        )

    async def update_screen_time(
        self,
        task_id: str,
        *,
        additional_screen_time: float,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Optional[TaskUpdateScreenTimeResponse]:
        """Adds a specified duration to the total screen time recorded for a task.

        This is
        typically used for tasks involving user interaction.

        Args:
          additional_screen_time: The additional screen time in milliseconds to add to the task's total.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._post(
            f"/api/v2/tasks/{task_id}/update-screen-time",
            body=await async_maybe_transform(
                {"additional_screen_time": additional_screen_time},
                task_update_screen_time_params.TaskUpdateScreenTimeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(
                Any, TaskUpdateScreenTimeResponse
            ),  # Enum types cannot be passed in as arguments in the type system
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.retrieve = to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.cancel = to_raw_response_wrapper(
            tasks.cancel,
        )
        self.complete = to_raw_response_wrapper(
            tasks.complete,
        )
        self.get_suspended_payload = to_raw_response_wrapper(
            tasks.get_suspended_payload,
        )
        self.retry = to_raw_response_wrapper(
            tasks.retry,
        )
        self.update_screen_time = to_raw_response_wrapper(
            tasks.update_screen_time,
        )

    @cached_property
    def state(self) -> StateResourceWithRawResponse:
        return StateResourceWithRawResponse(self._tasks.state)


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.retrieve = async_to_raw_response_wrapper(
            tasks.retrieve,
        )
        self.cancel = async_to_raw_response_wrapper(
            tasks.cancel,
        )
        self.complete = async_to_raw_response_wrapper(
            tasks.complete,
        )
        self.get_suspended_payload = async_to_raw_response_wrapper(
            tasks.get_suspended_payload,
        )
        self.retry = async_to_raw_response_wrapper(
            tasks.retry,
        )
        self.update_screen_time = async_to_raw_response_wrapper(
            tasks.update_screen_time,
        )

    @cached_property
    def state(self) -> AsyncStateResourceWithRawResponse:
        return AsyncStateResourceWithRawResponse(self._tasks.state)


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.retrieve = to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.cancel = to_streamed_response_wrapper(
            tasks.cancel,
        )
        self.complete = to_streamed_response_wrapper(
            tasks.complete,
        )
        self.get_suspended_payload = to_streamed_response_wrapper(
            tasks.get_suspended_payload,
        )
        self.retry = to_streamed_response_wrapper(
            tasks.retry,
        )
        self.update_screen_time = to_streamed_response_wrapper(
            tasks.update_screen_time,
        )

    @cached_property
    def state(self) -> StateResourceWithStreamingResponse:
        return StateResourceWithStreamingResponse(self._tasks.state)


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.retrieve = async_to_streamed_response_wrapper(
            tasks.retrieve,
        )
        self.cancel = async_to_streamed_response_wrapper(
            tasks.cancel,
        )
        self.complete = async_to_streamed_response_wrapper(
            tasks.complete,
        )
        self.get_suspended_payload = async_to_streamed_response_wrapper(
            tasks.get_suspended_payload,
        )
        self.retry = async_to_streamed_response_wrapper(
            tasks.retry,
        )
        self.update_screen_time = async_to_streamed_response_wrapper(
            tasks.update_screen_time,
        )

    @cached_property
    def state(self) -> AsyncStateResourceWithStreamingResponse:
        return AsyncStateResourceWithStreamingResponse(self._tasks.state)
