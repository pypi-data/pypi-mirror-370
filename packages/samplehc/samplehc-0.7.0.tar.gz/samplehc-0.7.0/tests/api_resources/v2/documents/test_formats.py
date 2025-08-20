# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.documents import FormatCreatePdfResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFormats:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_pdf(self, client: SampleHealthcare) -> None:
        format = client.v2.documents.formats.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        )
        assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_pdf(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.formats.with_raw_response.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        format = response.parse()
        assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_pdf(self, client: SampleHealthcare) -> None:
        with client.v2.documents.formats.with_streaming_response.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            format = response.parse()
            assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_pdf(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.v2.documents.formats.with_raw_response.create_pdf(
                document_id="",
                file_name="fileName",
                mime_type="mimeType",
            )


class TestAsyncFormats:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_pdf(self, async_client: AsyncSampleHealthcare) -> None:
        format = await async_client.v2.documents.formats.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        )
        assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_pdf(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.formats.with_raw_response.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        format = await response.parse()
        assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_pdf(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.formats.with_streaming_response.create_pdf(
            document_id="documentId",
            file_name="fileName",
            mime_type="mimeType",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            format = await response.parse()
            assert_matches_type(FormatCreatePdfResponse, format, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_pdf(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.v2.documents.formats.with_raw_response.create_pdf(
                document_id="",
                file_name="fileName",
                mime_type="mimeType",
            )
