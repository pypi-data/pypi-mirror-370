# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdt:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_subscribe(self, client: SampleHealthcare) -> None:
        adt = client.v2.events.hie.adt.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_subscribe_with_all_params(self, client: SampleHealthcare) -> None:
        adt = client.v2.events.hie.adt.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_subscribe(self, client: SampleHealthcare) -> None:
        response = client.v2.events.hie.adt.with_raw_response.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adt = response.parse()
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_subscribe(self, client: SampleHealthcare) -> None:
        with client.v2.events.hie.adt.with_streaming_response.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adt = response.parse()
            assert_matches_type(object, adt, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAdt:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_subscribe(self, async_client: AsyncSampleHealthcare) -> None:
        adt = await async_client.v2.events.hie.adt.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_subscribe_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        adt = await async_client.v2.events.hie.adt.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                    "address_line2": "addressLine2",
                    "country": "country",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
            contact=[
                {
                    "email": "email",
                    "phone": "phone",
                }
            ],
            personal_identifiers=[
                {
                    "type": "driversLicense",
                    "value": "value",
                    "state": "state",
                }
            ],
        )
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_subscribe(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.events.hie.adt.with_raw_response.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        adt = await response.parse()
        assert_matches_type(object, adt, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_subscribe(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.events.hie.adt.with_streaming_response.subscribe(
            address=[
                {
                    "address_line1": "addressLine1",
                    "city": "city",
                    "state": "state",
                    "zip": "zip",
                }
            ],
            dob="dob",
            external_id="externalId",
            first_name="firstName",
            gender_at_birth="M",
            last_name="lastName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            adt = await response.parse()
            assert_matches_type(object, adt, path=["response"])

        assert cast(Any, response.is_closed) is True
