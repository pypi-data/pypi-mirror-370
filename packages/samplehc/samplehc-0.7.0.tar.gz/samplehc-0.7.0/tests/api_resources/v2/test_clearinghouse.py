# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    ClearinghouseRunDiscoveryResponse,
    ClearinghouseCheckEligibilityResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClearinghouse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_calculate_patient_cost(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        )
        assert clearinghouse is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_calculate_patient_cost(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert clearinghouse is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_calculate_patient_cost(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert clearinghouse is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check_eligibility(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check_eligibility(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check_eligibility(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert_matches_type(object, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_discovery(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.run_discovery(
            person={},
        )
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_run_discovery_with_all_params(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.run_discovery(
            person={
                "address_line1": "addressLine1",
                "address_line2": "addressLine2",
                "city": "city",
                "date_of_birth": "dateOfBirth",
                "first_name": "firstName",
                "last_name": "lastName",
                "state": "state",
                "zip": "zip",
            },
            account_number="accountNumber",
            date_of_service="dateOfService",
            service_code="serviceCode",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_run_discovery(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.run_discovery(
            person={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_run_discovery(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.run_discovery(
            person={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClearinghouse:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_calculate_patient_cost(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        )
        assert clearinghouse is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_calculate_patient_cost(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert clearinghouse is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_calculate_patient_cost(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.calculate_patient_cost(
            eligibility_responses=[{"in_network": True}],
            line_items=[
                {
                    "id": "id",
                    "cpt_code": "cptCode",
                    "service_amount": 0,
                    "service_date": "serviceDate",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert clearinghouse is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert_matches_type(object, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_discovery(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.run_discovery(
            person={},
        )
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_run_discovery_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.run_discovery(
            person={
                "address_line1": "addressLine1",
                "address_line2": "addressLine2",
                "city": "city",
                "date_of_birth": "dateOfBirth",
                "first_name": "firstName",
                "last_name": "lastName",
                "state": "state",
                "zip": "zip",
            },
            account_number="accountNumber",
            date_of_service="dateOfService",
            service_code="serviceCode",
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_run_discovery(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.run_discovery(
            person={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_run_discovery(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.run_discovery(
            person={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert_matches_type(ClearinghouseRunDiscoveryResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True
