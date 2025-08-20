# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    CommunicationSendFaxResponse,
    CommunicationSendLetterResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCommunication:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_email(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_email(
            body="body",
            subject="subject",
            to="to",
        )
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_email_with_all_params(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_email(
            body="body",
            subject="subject",
            to="to",
            attach_as_files=True,
            attachments=[{"id": "id"}],
            enable_encryption=True,
            from_="from",
            zip_attachments=True,
        )
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send_email(self, client: SampleHealthcare) -> None:
        response = client.v2.communication.with_raw_response.send_email(
            body="body",
            subject="subject",
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = response.parse()
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send_email(self, client: SampleHealthcare) -> None:
        with client.v2.communication.with_streaming_response.send_email(
            body="body",
            subject="subject",
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = response.parse()
            assert_matches_type(object, communication, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_fax(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        )
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_fax_with_all_params(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
            batch_delay_seconds="batchDelaySeconds",
            enable_batch_collision_avoidance=True,
            enable_batch_delay=True,
        )
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send_fax(self, client: SampleHealthcare) -> None:
        response = client.v2.communication.with_raw_response.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = response.parse()
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send_fax(self, client: SampleHealthcare) -> None:
        with client.v2.communication.with_streaming_response.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = response.parse()
            assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_letter(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        )
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_letter_with_all_params(self, client: SampleHealthcare) -> None:
        communication = client.v2.communication.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
            from_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
            metadata={"foo": "string"},
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send_letter(self, client: SampleHealthcare) -> None:
        response = client.v2.communication.with_raw_response.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = response.parse()
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send_letter(self, client: SampleHealthcare) -> None:
        with client.v2.communication.with_streaming_response.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = response.parse()
            assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCommunication:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_email(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_email(
            body="body",
            subject="subject",
            to="to",
        )
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_email_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_email(
            body="body",
            subject="subject",
            to="to",
            attach_as_files=True,
            attachments=[{"id": "id"}],
            enable_encryption=True,
            from_="from",
            zip_attachments=True,
        )
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send_email(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.communication.with_raw_response.send_email(
            body="body",
            subject="subject",
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = await response.parse()
        assert_matches_type(object, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send_email(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.communication.with_streaming_response.send_email(
            body="body",
            subject="subject",
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = await response.parse()
            assert_matches_type(object, communication, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_fax(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        )
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_fax_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
            batch_delay_seconds="batchDelaySeconds",
            enable_batch_collision_avoidance=True,
            enable_batch_delay=True,
        )
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send_fax(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.communication.with_raw_response.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = await response.parse()
        assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send_fax(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.communication.with_streaming_response.send_fax(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = await response.parse()
            assert_matches_type(CommunicationSendFaxResponse, communication, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_letter(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        )
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_letter_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        communication = await async_client.v2.communication.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
            from_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
            metadata={"foo": "string"},
            idempotency_key="Idempotency-Key",
        )
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send_letter(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.communication.with_raw_response.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        communication = await response.parse()
        assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send_letter(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.communication.with_streaming_response.send_letter(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            to_address={
                "address": {
                    "city": "city",
                    "state": "state",
                    "street_lines": ["string"],
                    "zip_code": "zipCode",
                },
                "name": "name",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            communication = await response.parse()
            assert_matches_type(CommunicationSendLetterResponse, communication, path=["response"])

        assert cast(Any, response.is_closed) is True
