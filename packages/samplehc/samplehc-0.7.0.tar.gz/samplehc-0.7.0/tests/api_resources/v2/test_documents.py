# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    DocumentSplitResponse,
    DocumentUnzipResponse,
    DocumentSearchResponse,
    DocumentCombineResponse,
    DocumentExtractResponse,
    DocumentClassifyResponse,
    DocumentRetrieveResponse,
    DocumentGenerateCsvResponse,
    DocumentCreateFromSplitsResponse,
    DocumentRetrieveMetadataResponse,
    DocumentPresignedUploadURLResponse,
    DocumentRetrieveCsvContentResponse,
    DocumentTransformJsonToHTMLResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.retrieve(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.retrieve(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.retrieve(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.v2.documents.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_classify(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        )
        assert_matches_type(DocumentClassifyResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_classify(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentClassifyResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_classify(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentClassifyResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_combine(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )
        assert_matches_type(DocumentCombineResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_combine(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCombineResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_combine(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCombineResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_from_splits(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        )
        assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_from_splits(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_from_splits(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        )
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_extract_with_all_params(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
            model="reasoning-3-mini",
            reasoning_effort="low",
        )
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_extract(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_extract(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentExtractResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_csv(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        )
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_generate_csv_with_all_params(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
            options={
                "column_order": ["string"],
                "export_as_excel": True,
            },
        )
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_generate_csv(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_generate_csv(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_presigned_upload_url(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        )
        assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_presigned_upload_url(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_presigned_upload_url(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_csv_content(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.retrieve_csv_content(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_csv_content(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.retrieve_csv_content(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_csv_content(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.retrieve_csv_content(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_csv_content(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.v2.documents.with_raw_response.retrieve_csv_content(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_metadata(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.retrieve_metadata(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_metadata(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.retrieve_metadata(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_metadata(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.retrieve_metadata(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_metadata(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.v2.documents.with_raw_response.retrieve_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        )
        assert_matches_type(DocumentSearchResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentSearchResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentSearchResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_split(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        )
        assert_matches_type(DocumentSplitResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_split(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentSplitResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_split(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentSplitResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_transform_json_to_html(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.transform_json_to_html()
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_transform_json_to_html_with_all_params(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.transform_json_to_html(
            json={},
        )
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_transform_json_to_html(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.transform_json_to_html()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_transform_json_to_html(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.transform_json_to_html() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unzip(self, client: SampleHealthcare) -> None:
        document = client.v2.documents.unzip(
            "documentId",
        )
        assert_matches_type(DocumentUnzipResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unzip(self, client: SampleHealthcare) -> None:
        response = client.v2.documents.with_raw_response.unzip(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUnzipResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unzip(self, client: SampleHealthcare) -> None:
        with client.v2.documents.with_streaming_response.unzip(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUnzipResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_unzip(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            client.v2.documents.with_raw_response.unzip(
                "",
            )


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.retrieve(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.retrieve(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.retrieve(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.v2.documents.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_classify(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        )
        assert_matches_type(DocumentClassifyResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_classify(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentClassifyResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_classify(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.classify(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            label_schemas=[{"label": "label"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentClassifyResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_combine(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )
        assert_matches_type(DocumentCombineResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_combine(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCombineResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_combine(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.combine(
            combined_file_name="combinedFileName",
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCombineResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_from_splits(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        )
        assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_from_splits(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_from_splits(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.create_from_splits(
            document={
                "id": "id",
                "file_name": "fileName",
            },
            splits=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCreateFromSplitsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        )
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_extract_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
            model="reasoning-3-mini",
            reasoning_effort="low",
        )
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentExtractResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.extract(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            prompt="prompt",
            response_json_schema={"foo": "bar"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentExtractResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_csv(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        )
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_generate_csv_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
            options={
                "column_order": ["string"],
                "export_as_excel": True,
            },
        )
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_generate_csv(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_generate_csv(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.generate_csv(
            file_name="fileName",
            rows=[{"foo": "string"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGenerateCsvResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_presigned_upload_url(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        )
        assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_presigned_upload_url(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_presigned_upload_url(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.presigned_upload_url(
            file_name="fileName",
            mime_type="application/zip",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentPresignedUploadURLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_csv_content(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.retrieve_csv_content(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_csv_content(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.retrieve_csv_content(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_csv_content(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.retrieve_csv_content(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRetrieveCsvContentResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_csv_content(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.v2.documents.with_raw_response.retrieve_csv_content(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_metadata(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.retrieve_metadata(
            "documentId",
        )
        assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_metadata(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.retrieve_metadata(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_metadata(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.retrieve_metadata(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRetrieveMetadataResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_metadata(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.v2.documents.with_raw_response.retrieve_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        )
        assert_matches_type(DocumentSearchResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentSearchResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.search(
            documents=[
                {
                    "id": "id",
                    "file_name": "fileName",
                }
            ],
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentSearchResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_split(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        )
        assert_matches_type(DocumentSplitResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_split(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentSplitResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_split(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.split(
            document={
                "id": "id",
                "file_name": "fileName",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentSplitResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_transform_json_to_html(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.transform_json_to_html()
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_transform_json_to_html_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.transform_json_to_html(
            json={},
        )
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_transform_json_to_html(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.transform_json_to_html()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_transform_json_to_html(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.transform_json_to_html() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentTransformJsonToHTMLResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unzip(self, async_client: AsyncSampleHealthcare) -> None:
        document = await async_client.v2.documents.unzip(
            "documentId",
        )
        assert_matches_type(DocumentUnzipResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unzip(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.documents.with_raw_response.unzip(
            "documentId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUnzipResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unzip(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.documents.with_streaming_response.unzip(
            "documentId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUnzipResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_unzip(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_id` but received ''"):
            await async_client.v2.documents.with_raw_response.unzip(
                "",
            )
