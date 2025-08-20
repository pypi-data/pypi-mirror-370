# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import policy_list_params, policy_list_plans_params, policy_list_companies_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.policy_list_response import PolicyListResponse
from ...types.v2.policy_list_plans_response import PolicyListPlansResponse
from ...types.v2.policy_retrieve_text_response import PolicyRetrieveTextResponse
from ...types.v2.policy_list_companies_response import PolicyListCompaniesResponse
from ...types.v2.policy_retrieve_presigned_url_response import PolicyRetrievePresignedURLResponse

__all__ = ["PoliciesResource", "AsyncPoliciesResource"]


class PoliciesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PoliciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return PoliciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PoliciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return PoliciesResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        active_at: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        hcpcs_codes: str | NotGiven = NOT_GIVEN,
        icd10_cm_codes: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        plan_id: str | NotGiven = NOT_GIVEN,
        policy_topic: str | NotGiven = NOT_GIVEN,
        policy_topic_for_keyword_extraction: str | NotGiven = NOT_GIVEN,
        policy_type: str | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        updated_at_max: str | NotGiven = NOT_GIVEN,
        updated_at_min: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListResponse:
        """
        Retrieve a list of policies based on specified filters.

        Args:
          active_at: Filter policies active at this date (YYYY-MM-DD)

          company_id: ID of the company to which the policy belongs

          hcpcs_codes: Comma-separated HCPCS codes to filter by

          icd10_cm_codes: Comma-separated ICD-10-CM codes to filter by

          limit: Maximum number of results to return

          plan_id: ID of the plan to which the policy belongs

          policy_topic: Keywords describing the policy content

          policy_topic_for_keyword_extraction: String for keyword extraction (beta)

          policy_type: Type of policy (MEDICAL_POLICY, PAYMENT_POLICY, etc.)

          skip: Number of results to skip

          updated_at_max: Filter policies updated on or before this date (YYYY-MM-DD)

          updated_at_min: Filter policies updated on or after this date (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/policies/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "active_at": active_at,
                        "company_id": company_id,
                        "hcpcs_codes": hcpcs_codes,
                        "icd10_cm_codes": icd10_cm_codes,
                        "limit": limit,
                        "plan_id": plan_id,
                        "policy_topic": policy_topic,
                        "policy_topic_for_keyword_extraction": policy_topic_for_keyword_extraction,
                        "policy_type": policy_type,
                        "skip": skip,
                        "updated_at_max": updated_at_max,
                        "updated_at_min": updated_at_min,
                    },
                    policy_list_params.PolicyListParams,
                ),
            ),
            cast_to=PolicyListResponse,
        )

    def list_companies(
        self,
        *,
        company_name: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListCompaniesResponse:
        """
        Retrieve a list of companies.

        Args:
          company_name: Company name to filter by

          limit: Maximum number of results to return

          skip: Number of results to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/policies/companies",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "company_name": company_name,
                        "limit": limit,
                        "skip": skip,
                    },
                    policy_list_companies_params.PolicyListCompaniesParams,
                ),
            ),
            cast_to=PolicyListCompaniesResponse,
        )

    def list_plans(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        plan_name: str | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListPlansResponse:
        """
        Retrieve a list of plans.

        Args:
          limit: Maximum number of results to return

          plan_name: Plan name to filter by

          skip: Number of results to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/v2/policies/plans",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "plan_name": plan_name,
                        "skip": skip,
                    },
                    policy_list_plans_params.PolicyListPlansParams,
                ),
            ),
            cast_to=PolicyListPlansResponse,
        )

    def retrieve_presigned_url(
        self,
        policy_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyRetrievePresignedURLResponse:
        """
        Retrieve a presigned URL for accessing a policy document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")
        return self._get(
            f"/api/v2/policies/{policy_id}/url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PolicyRetrievePresignedURLResponse,
        )

    def retrieve_text(
        self,
        policy_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyRetrieveTextResponse:
        """
        Retrieve the raw text content of a policy document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")
        return self._get(
            f"/api/v2/policies/{policy_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PolicyRetrieveTextResponse,
        )


class AsyncPoliciesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPoliciesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPoliciesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPoliciesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncPoliciesResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        active_at: str | NotGiven = NOT_GIVEN,
        company_id: str | NotGiven = NOT_GIVEN,
        hcpcs_codes: str | NotGiven = NOT_GIVEN,
        icd10_cm_codes: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        plan_id: str | NotGiven = NOT_GIVEN,
        policy_topic: str | NotGiven = NOT_GIVEN,
        policy_topic_for_keyword_extraction: str | NotGiven = NOT_GIVEN,
        policy_type: str | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        updated_at_max: str | NotGiven = NOT_GIVEN,
        updated_at_min: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListResponse:
        """
        Retrieve a list of policies based on specified filters.

        Args:
          active_at: Filter policies active at this date (YYYY-MM-DD)

          company_id: ID of the company to which the policy belongs

          hcpcs_codes: Comma-separated HCPCS codes to filter by

          icd10_cm_codes: Comma-separated ICD-10-CM codes to filter by

          limit: Maximum number of results to return

          plan_id: ID of the plan to which the policy belongs

          policy_topic: Keywords describing the policy content

          policy_topic_for_keyword_extraction: String for keyword extraction (beta)

          policy_type: Type of policy (MEDICAL_POLICY, PAYMENT_POLICY, etc.)

          skip: Number of results to skip

          updated_at_max: Filter policies updated on or before this date (YYYY-MM-DD)

          updated_at_min: Filter policies updated on or after this date (YYYY-MM-DD)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/policies/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "active_at": active_at,
                        "company_id": company_id,
                        "hcpcs_codes": hcpcs_codes,
                        "icd10_cm_codes": icd10_cm_codes,
                        "limit": limit,
                        "plan_id": plan_id,
                        "policy_topic": policy_topic,
                        "policy_topic_for_keyword_extraction": policy_topic_for_keyword_extraction,
                        "policy_type": policy_type,
                        "skip": skip,
                        "updated_at_max": updated_at_max,
                        "updated_at_min": updated_at_min,
                    },
                    policy_list_params.PolicyListParams,
                ),
            ),
            cast_to=PolicyListResponse,
        )

    async def list_companies(
        self,
        *,
        company_name: str | NotGiven = NOT_GIVEN,
        limit: float | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListCompaniesResponse:
        """
        Retrieve a list of companies.

        Args:
          company_name: Company name to filter by

          limit: Maximum number of results to return

          skip: Number of results to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/policies/companies",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "company_name": company_name,
                        "limit": limit,
                        "skip": skip,
                    },
                    policy_list_companies_params.PolicyListCompaniesParams,
                ),
            ),
            cast_to=PolicyListCompaniesResponse,
        )

    async def list_plans(
        self,
        *,
        limit: float | NotGiven = NOT_GIVEN,
        plan_name: str | NotGiven = NOT_GIVEN,
        skip: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyListPlansResponse:
        """
        Retrieve a list of plans.

        Args:
          limit: Maximum number of results to return

          plan_name: Plan name to filter by

          skip: Number of results to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/v2/policies/plans",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "plan_name": plan_name,
                        "skip": skip,
                    },
                    policy_list_plans_params.PolicyListPlansParams,
                ),
            ),
            cast_to=PolicyListPlansResponse,
        )

    async def retrieve_presigned_url(
        self,
        policy_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyRetrievePresignedURLResponse:
        """
        Retrieve a presigned URL for accessing a policy document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")
        return await self._get(
            f"/api/v2/policies/{policy_id}/url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PolicyRetrievePresignedURLResponse,
        )

    async def retrieve_text(
        self,
        policy_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PolicyRetrieveTextResponse:
        """
        Retrieve the raw text content of a policy document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")
        return await self._get(
            f"/api/v2/policies/{policy_id}/text",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=PolicyRetrieveTextResponse,
        )


class PoliciesResourceWithRawResponse:
    def __init__(self, policies: PoliciesResource) -> None:
        self._policies = policies

        self.list = to_raw_response_wrapper(
            policies.list,
        )
        self.list_companies = to_raw_response_wrapper(
            policies.list_companies,
        )
        self.list_plans = to_raw_response_wrapper(
            policies.list_plans,
        )
        self.retrieve_presigned_url = to_raw_response_wrapper(
            policies.retrieve_presigned_url,
        )
        self.retrieve_text = to_raw_response_wrapper(
            policies.retrieve_text,
        )


class AsyncPoliciesResourceWithRawResponse:
    def __init__(self, policies: AsyncPoliciesResource) -> None:
        self._policies = policies

        self.list = async_to_raw_response_wrapper(
            policies.list,
        )
        self.list_companies = async_to_raw_response_wrapper(
            policies.list_companies,
        )
        self.list_plans = async_to_raw_response_wrapper(
            policies.list_plans,
        )
        self.retrieve_presigned_url = async_to_raw_response_wrapper(
            policies.retrieve_presigned_url,
        )
        self.retrieve_text = async_to_raw_response_wrapper(
            policies.retrieve_text,
        )


class PoliciesResourceWithStreamingResponse:
    def __init__(self, policies: PoliciesResource) -> None:
        self._policies = policies

        self.list = to_streamed_response_wrapper(
            policies.list,
        )
        self.list_companies = to_streamed_response_wrapper(
            policies.list_companies,
        )
        self.list_plans = to_streamed_response_wrapper(
            policies.list_plans,
        )
        self.retrieve_presigned_url = to_streamed_response_wrapper(
            policies.retrieve_presigned_url,
        )
        self.retrieve_text = to_streamed_response_wrapper(
            policies.retrieve_text,
        )


class AsyncPoliciesResourceWithStreamingResponse:
    def __init__(self, policies: AsyncPoliciesResource) -> None:
        self._policies = policies

        self.list = async_to_streamed_response_wrapper(
            policies.list,
        )
        self.list_companies = async_to_streamed_response_wrapper(
            policies.list_companies,
        )
        self.list_plans = async_to_streamed_response_wrapper(
            policies.list_plans,
        )
        self.retrieve_presigned_url = async_to_streamed_response_wrapper(
            policies.retrieve_presigned_url,
        )
        self.retrieve_text = async_to_streamed_response_wrapper(
            policies.retrieve_text,
        )
