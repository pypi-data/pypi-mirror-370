# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.documents import (
    LegacyReasonResponse,
    LegacyExtractResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLegacy:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract(self, client: SampleHealthcare) -> None:
        legacy = client.v2.documents.legacy.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )
        assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.legacy.with_raw_response.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        legacy = response.parse()
        assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract(self, client: SampleHealthcare) -> None:
        with client.v2.documents.legacy.with_streaming_response.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            legacy = response.parse()
            assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reason(self, client: SampleHealthcare) -> None:
        legacy = client.v2.documents.legacy.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        )
        assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reason(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.legacy.with_raw_response.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        legacy = response.parse()
        assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reason(self, client: SampleHealthcare) -> None:
        with client.v2.documents.legacy.with_streaming_response.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            legacy = response.parse()
            assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLegacy:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract(self, async_client: AsyncSampleHealthcare) -> None:
        legacy = await async_client.v2.documents.legacy.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )
        assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.legacy.with_raw_response.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        legacy = await response.parse()
        assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.legacy.with_streaming_response.extract(
            answer_schemas=[
                {
                    "label": "label",
                    "question": "question",
                    "type": "boolean",
                }
            ],
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            legacy = await response.parse()
            assert_matches_type(LegacyExtractResponse, legacy, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reason(self, async_client: AsyncSampleHealthcare) -> None:
        legacy = await async_client.v2.documents.legacy.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        )
        assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reason(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.legacy.with_raw_response.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        legacy = await response.parse()
        assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reason(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.legacy.with_streaming_response.reason(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            task={
                "id": "id",
                "description": "description",
                "label": "label",
                "type": "reasoning",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            legacy = await response.parse()
            assert_matches_type(LegacyReasonResponse, legacy, path=["response"])

        assert cast(Any, response.is_closed) is True
