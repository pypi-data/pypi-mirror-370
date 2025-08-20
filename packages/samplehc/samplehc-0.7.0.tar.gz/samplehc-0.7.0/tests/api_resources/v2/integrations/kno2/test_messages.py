# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.integrations.kno2 import MessageRetrieveResponse, MessageGetAttachmentResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMessages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: SampleHealthcare) -> None:
        message = client.v2.integrations.kno2.messages.retrieve(
            message_id="messageId",
            slug="slug",
        )
        assert_matches_type(MessageRetrieveResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.kno2.messages.with_raw_response.retrieve(
            message_id="messageId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageRetrieveResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.kno2.messages.with_streaming_response.retrieve(
            message_id="messageId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(MessageRetrieveResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.kno2.messages.with_raw_response.retrieve(
                message_id="messageId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.v2.integrations.kno2.messages.with_raw_response.retrieve(
                message_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_attachment(self, client: SampleHealthcare) -> None:
        message = client.v2.integrations.kno2.messages.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        )
        assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_attachment(self, client: SampleHealthcare) -> None:
        response = client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = response.parse()
        assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_attachment(self, client: SampleHealthcare) -> None:
        with client.v2.integrations.kno2.messages.with_streaming_response.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = response.parse()
            assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_attachment(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="attachmentId",
                slug="",
                message_id="messageId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="attachmentId",
                slug="slug",
                message_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `attachment_id` but received ''"):
            client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="",
                slug="slug",
                message_id="messageId",
            )


class TestAsyncMessages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        message = await async_client.v2.integrations.kno2.messages.retrieve(
            message_id="messageId",
            slug="slug",
        )
        assert_matches_type(MessageRetrieveResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.kno2.messages.with_raw_response.retrieve(
            message_id="messageId",
            slug="slug",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(MessageRetrieveResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.kno2.messages.with_streaming_response.retrieve(
            message_id="messageId",
            slug="slug",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(MessageRetrieveResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.kno2.messages.with_raw_response.retrieve(
                message_id="messageId",
                slug="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.v2.integrations.kno2.messages.with_raw_response.retrieve(
                message_id="",
                slug="slug",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_attachment(self, async_client: AsyncSampleHealthcare) -> None:
        message = await async_client.v2.integrations.kno2.messages.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        )
        assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_attachment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        message = await response.parse()
        assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_attachment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.integrations.kno2.messages.with_streaming_response.get_attachment(
            attachment_id="attachmentId",
            slug="slug",
            message_id="messageId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            message = await response.parse()
            assert_matches_type(MessageGetAttachmentResponse, message, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_attachment(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="attachmentId",
                slug="",
                message_id="messageId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `message_id` but received ''"):
            await async_client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="attachmentId",
                slug="slug",
                message_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `attachment_id` but received ''"):
            await async_client.v2.integrations.kno2.messages.with_raw_response.get_attachment(
                attachment_id="",
                slug="slug",
                message_id="messageId",
            )
