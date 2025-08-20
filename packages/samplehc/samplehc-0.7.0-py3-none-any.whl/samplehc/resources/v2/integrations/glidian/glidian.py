# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.integrations import (
    glidian_list_payers_params,
    glidian_list_services_params,
    glidian_get_submission_requirements_params,
)
from .prior_authorizations.prior_authorizations import (
    PriorAuthorizationsResource,
    AsyncPriorAuthorizationsResource,
    PriorAuthorizationsResourceWithRawResponse,
    AsyncPriorAuthorizationsResourceWithRawResponse,
    PriorAuthorizationsResourceWithStreamingResponse,
    AsyncPriorAuthorizationsResourceWithStreamingResponse,
)
from .....types.v2.integrations.glidian_list_payers_response import GlidianListPayersResponse
from .....types.v2.integrations.glidian_list_services_response import GlidianListServicesResponse
from .....types.v2.integrations.glidian_get_submission_requirements_response import (
    GlidianGetSubmissionRequirementsResponse,
)

__all__ = ["GlidianResource", "AsyncGlidianResource"]


class GlidianResource(SyncAPIResource):
    @cached_property
    def prior_authorizations(self) -> PriorAuthorizationsResource:
        return PriorAuthorizationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> GlidianResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return GlidianResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GlidianResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return GlidianResourceWithStreamingResponse(self)

    def get_submission_requirements(
        self,
        slug: str,
        *,
        insurance_id: float,
        service_id: float,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianGetSubmissionRequirementsResponse:
        """
        Get submission requirements for a specific insurance and service combination.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return cast(
            GlidianGetSubmissionRequirementsResponse,
            self._get(
                f"/api/v2/integrations/glidian/{slug}/submission-requirements",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=maybe_transform(
                        {
                            "insurance_id": insurance_id,
                            "service_id": service_id,
                            "state": state,
                        },
                        glidian_get_submission_requirements_params.GlidianGetSubmissionRequirementsParams,
                    ),
                ),
                cast_to=cast(
                    Any, GlidianGetSubmissionRequirementsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    def list_payers(
        self,
        slug: str,
        *,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianListPayersResponse:
        """
        Get a list of available Glidian payers/insurances for a specific connection.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._get(
            f"/api/v2/integrations/glidian/{slug}/payers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"state": state}, glidian_list_payers_params.GlidianListPayersParams),
            ),
            cast_to=GlidianListPayersResponse,
        )

    def list_services(
        self,
        slug: str,
        *,
        insurance_id: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianListServicesResponse:
        """
        Get a list of available Glidian services for a specific connection.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._get(
            f"/api/v2/integrations/glidian/{slug}/services",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"insurance_id": insurance_id}, glidian_list_services_params.GlidianListServicesParams
                ),
            ),
            cast_to=GlidianListServicesResponse,
        )


class AsyncGlidianResource(AsyncAPIResource):
    @cached_property
    def prior_authorizations(self) -> AsyncPriorAuthorizationsResource:
        return AsyncPriorAuthorizationsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncGlidianResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncGlidianResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGlidianResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncGlidianResourceWithStreamingResponse(self)

    async def get_submission_requirements(
        self,
        slug: str,
        *,
        insurance_id: float,
        service_id: float,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianGetSubmissionRequirementsResponse:
        """
        Get submission requirements for a specific insurance and service combination.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return cast(
            GlidianGetSubmissionRequirementsResponse,
            await self._get(
                f"/api/v2/integrations/glidian/{slug}/submission-requirements",
                options=make_request_options(
                    extra_headers=extra_headers,
                    extra_query=extra_query,
                    extra_body=extra_body,
                    timeout=timeout,
                    query=await async_maybe_transform(
                        {
                            "insurance_id": insurance_id,
                            "service_id": service_id,
                            "state": state,
                        },
                        glidian_get_submission_requirements_params.GlidianGetSubmissionRequirementsParams,
                    ),
                ),
                cast_to=cast(
                    Any, GlidianGetSubmissionRequirementsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )

    async def list_payers(
        self,
        slug: str,
        *,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianListPayersResponse:
        """
        Get a list of available Glidian payers/insurances for a specific connection.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._get(
            f"/api/v2/integrations/glidian/{slug}/payers",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"state": state}, glidian_list_payers_params.GlidianListPayersParams),
            ),
            cast_to=GlidianListPayersResponse,
        )

    async def list_services(
        self,
        slug: str,
        *,
        insurance_id: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GlidianListServicesResponse:
        """
        Get a list of available Glidian services for a specific connection.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._get(
            f"/api/v2/integrations/glidian/{slug}/services",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"insurance_id": insurance_id}, glidian_list_services_params.GlidianListServicesParams
                ),
            ),
            cast_to=GlidianListServicesResponse,
        )


class GlidianResourceWithRawResponse:
    def __init__(self, glidian: GlidianResource) -> None:
        self._glidian = glidian

        self.get_submission_requirements = to_raw_response_wrapper(
            glidian.get_submission_requirements,
        )
        self.list_payers = to_raw_response_wrapper(
            glidian.list_payers,
        )
        self.list_services = to_raw_response_wrapper(
            glidian.list_services,
        )

    @cached_property
    def prior_authorizations(self) -> PriorAuthorizationsResourceWithRawResponse:
        return PriorAuthorizationsResourceWithRawResponse(self._glidian.prior_authorizations)


class AsyncGlidianResourceWithRawResponse:
    def __init__(self, glidian: AsyncGlidianResource) -> None:
        self._glidian = glidian

        self.get_submission_requirements = async_to_raw_response_wrapper(
            glidian.get_submission_requirements,
        )
        self.list_payers = async_to_raw_response_wrapper(
            glidian.list_payers,
        )
        self.list_services = async_to_raw_response_wrapper(
            glidian.list_services,
        )

    @cached_property
    def prior_authorizations(self) -> AsyncPriorAuthorizationsResourceWithRawResponse:
        return AsyncPriorAuthorizationsResourceWithRawResponse(self._glidian.prior_authorizations)


class GlidianResourceWithStreamingResponse:
    def __init__(self, glidian: GlidianResource) -> None:
        self._glidian = glidian

        self.get_submission_requirements = to_streamed_response_wrapper(
            glidian.get_submission_requirements,
        )
        self.list_payers = to_streamed_response_wrapper(
            glidian.list_payers,
        )
        self.list_services = to_streamed_response_wrapper(
            glidian.list_services,
        )

    @cached_property
    def prior_authorizations(self) -> PriorAuthorizationsResourceWithStreamingResponse:
        return PriorAuthorizationsResourceWithStreamingResponse(self._glidian.prior_authorizations)


class AsyncGlidianResourceWithStreamingResponse:
    def __init__(self, glidian: AsyncGlidianResource) -> None:
        self._glidian = glidian

        self.get_submission_requirements = async_to_streamed_response_wrapper(
            glidian.get_submission_requirements,
        )
        self.list_payers = async_to_streamed_response_wrapper(
            glidian.list_payers,
        )
        self.list_services = async_to_streamed_response_wrapper(
            glidian.list_services,
        )

    @cached_property
    def prior_authorizations(self) -> AsyncPriorAuthorizationsResourceWithStreamingResponse:
        return AsyncPriorAuthorizationsResourceWithStreamingResponse(self._glidian.prior_authorizations)
