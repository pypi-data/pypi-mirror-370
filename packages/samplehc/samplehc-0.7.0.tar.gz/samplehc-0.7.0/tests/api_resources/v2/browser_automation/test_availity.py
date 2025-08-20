# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.browser_automation import AvailitySubmitAppealResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAvaility:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_submit_appeal(self, client: SampleHealthcare) -> None:
        availity = client.v2.browser_automation.availity.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        )
        assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_submit_appeal(self, client: SampleHealthcare) -> None:
        response = client.v2.browser_automation.availity.with_raw_response.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        availity = response.parse()
        assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_submit_appeal(self, client: SampleHealthcare) -> None:
        with client.v2.browser_automation.availity.with_streaming_response.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            availity = response.parse()
            assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAvaility:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_submit_appeal(self, async_client: AsyncSampleHealthcare) -> None:
        availity = await async_client.v2.browser_automation.availity.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        )
        assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_submit_appeal(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.browser_automation.availity.with_raw_response.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        availity = await response.parse()
        assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_submit_appeal(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.browser_automation.availity.with_streaming_response.submit_appeal(
            availity_payer="Anthem - CA",
            billed_amount="billedAmount",
            claim_number="claimNumber",
            contact_phone_number="contactPhoneNumber",
            document={
                "id": "id",
                "file_name": "fileName",
            },
            member_date_of_birth="memberDateOfBirth",
            member_first_name="memberFirstName",
            member_id="memberId",
            member_last_name="memberLastName",
            request_reason="Authorization Issue",
            service_start_date="serviceStartDate",
            state="state",
            supporting_rationale="supportingRationale",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            availity = await response.parse()
            assert_matches_type(AvailitySubmitAppealResponse, availity, path=["response"])

        assert cast(Any, response.is_closed) is True
