# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.documents import (
    TemplateRenderDocumentResponse,
    TemplateGenerateDocumentAsyncResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTemplates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_document_async_overload_1(self, client: SampleHealthcare) -> None:
        template = client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="document",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_document_async_with_all_params_overload_1(self, client: SampleHealthcare) -> None:
        template = client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="document",
            document_body={},
            file_name="fileName",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_document_async_overload_1(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.templates.with_raw_response.generate_document_async(
            slug="slug",
            type="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_document_async_overload_1(self, client: SampleHealthcare) -> None:
        with client.v2.documents.templates.with_streaming_response.generate_document_async(
            slug="slug",
            type="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_document_async_overload_2(self, client: SampleHealthcare) -> None:
        template = client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_document_async_with_all_params_overload_2(self, client: SampleHealthcare) -> None:
        template = client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
            file_name="fileName",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_document_async_overload_2(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.templates.with_raw_response.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_document_async_overload_2(self, client: SampleHealthcare) -> None:
        with client.v2.documents.templates.with_streaming_response.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_render_document(self, client: SampleHealthcare) -> None:
        template = client.v2.documents.templates.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        )
        assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_render_document(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.templates.with_raw_response.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_render_document(self, client: SampleHealthcare) -> None:
        with client.v2.documents.templates.with_streaming_response.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTemplates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_document_async_overload_1(self, async_client: AsyncSampleHealthcare) -> None:
        template = await async_client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="document",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_document_async_with_all_params_overload_1(
        self, async_client: AsyncSampleHealthcare
    ) -> None:
        template = await async_client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="document",
            document_body={},
            file_name="fileName",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_document_async_overload_1(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.templates.with_raw_response.generate_document_async(
            slug="slug",
            type="document",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = await response.parse()
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_document_async_overload_1(
        self, async_client: AsyncSampleHealthcare
    ) -> None:
        async with async_client.v2.documents.templates.with_streaming_response.generate_document_async(
            slug="slug",
            type="document",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_document_async_overload_2(self, async_client: AsyncSampleHealthcare) -> None:
        template = await async_client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_document_async_with_all_params_overload_2(
        self, async_client: AsyncSampleHealthcare
    ) -> None:
        template = await async_client.v2.documents.templates.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
            file_name="fileName",
        )
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_document_async_overload_2(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.templates.with_raw_response.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = await response.parse()
        assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_document_async_overload_2(
        self, async_client: AsyncSampleHealthcare
    ) -> None:
        async with async_client.v2.documents.templates.with_streaming_response.generate_document_async(
            slug="slug",
            type="pdf",
            variables={"foo": "string"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(TemplateGenerateDocumentAsyncResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_render_document(self, async_client: AsyncSampleHealthcare) -> None:
        template = await async_client.v2.documents.templates.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        )
        assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_render_document(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.templates.with_raw_response.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = await response.parse()
        assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_render_document(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.templates.with_streaming_response.render_document(
            slug="slug",
            variables={"foo": [{"foo": "string"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(TemplateRenderDocumentResponse, template, path=["response"])

        assert cast(Any, response.is_closed) is True
