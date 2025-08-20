# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.hie import document_query_params, document_upload_params
from ....types.v2.hie.document_query_response import DocumentQueryResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def query(
        self,
        *,
        address: Iterable[document_query_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[document_query_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[document_query_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentQueryResponse:
        """Queries patient documents from the HIE network.

        Will reuse previously fetched
        data if a patient with the same external ID already exists in our records.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/hie/documents/query",
            body=maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                document_query_params.DocumentQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentQueryResponse,
        )

    def upload(
        self,
        *,
        description: str,
        document_type: document_upload_params.DocumentType,
        file_metadata_id: str,
        patient_id: str,
        date_end: str | NotGiven = NOT_GIVEN,
        date_start: str | NotGiven = NOT_GIVEN,
        facility_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Contributes a document to the HIE network for a specific patient.

        Args:
          description: A brief description of the document.

          document_type: The type of document being uploaded.

          file_metadata_id: The ID of the file metadata to upload.

          patient_id: The external Patient ID that you store and can use to reference this Patient.

          date_end: ISO 8601 timestamp for when the document period ends.

          date_start: ISO 8601 timestamp for when the document period starts.

          facility_name: The name and type of facility (e.g., 'John Snow Clinic - Acute Care Centre').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/hie/documents/upload",
            body=maybe_transform(
                {
                    "description": description,
                    "document_type": document_type,
                    "file_metadata_id": file_metadata_id,
                    "patient_id": patient_id,
                    "date_end": date_end,
                    "date_start": date_start,
                    "facility_name": facility_name,
                },
                document_upload_params.DocumentUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    async def query(
        self,
        *,
        address: Iterable[document_query_params.Address],
        dob: str,
        external_id: str,
        first_name: str,
        gender_at_birth: Literal["M", "F", "O", "U"],
        last_name: str,
        contact: Iterable[document_query_params.Contact] | NotGiven = NOT_GIVEN,
        personal_identifiers: Iterable[document_query_params.PersonalIdentifier] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentQueryResponse:
        """Queries patient documents from the HIE network.

        Will reuse previously fetched
        data if a patient with the same external ID already exists in our records.

        Args:
          address: An array of Address objects, representing the Patient's current and/or previous
              addresses. May be empty.

          dob: The Patient's date of birth (DOB), formatted `YYYY-MM-DD` as per ISO 8601.

          external_id: An external Patient ID that you store and can use to reference this Patient.

          first_name: The Patient's first name(s).

          gender_at_birth: The Patient's gender at birth, can be one of `M` or `F` or `O` or `U`. Use `O`
              (other) when the patient's gender is known but it is not `M` or `F`, i.e
              intersex or hermaphroditic. Use `U` (unknown) when the patient's gender is not
              known.

          last_name: The Patient's last name(s).

          contact: An array of Contact objects, representing the Patient's current and/or previous
              contact information. May be empty.

          personal_identifiers: An array of the Patient's personal IDs, such as a driver's license or SSN. May
              be empty.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/hie/documents/query",
            body=await async_maybe_transform(
                {
                    "address": address,
                    "dob": dob,
                    "external_id": external_id,
                    "first_name": first_name,
                    "gender_at_birth": gender_at_birth,
                    "last_name": last_name,
                    "contact": contact,
                    "personal_identifiers": personal_identifiers,
                },
                document_query_params.DocumentQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentQueryResponse,
        )

    async def upload(
        self,
        *,
        description: str,
        document_type: document_upload_params.DocumentType,
        file_metadata_id: str,
        patient_id: str,
        date_end: str | NotGiven = NOT_GIVEN,
        date_start: str | NotGiven = NOT_GIVEN,
        facility_name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Contributes a document to the HIE network for a specific patient.

        Args:
          description: A brief description of the document.

          document_type: The type of document being uploaded.

          file_metadata_id: The ID of the file metadata to upload.

          patient_id: The external Patient ID that you store and can use to reference this Patient.

          date_end: ISO 8601 timestamp for when the document period ends.

          date_start: ISO 8601 timestamp for when the document period starts.

          facility_name: The name and type of facility (e.g., 'John Snow Clinic - Acute Care Centre').

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/hie/documents/upload",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "document_type": document_type,
                    "file_metadata_id": file_metadata_id,
                    "patient_id": patient_id,
                    "date_end": date_end,
                    "date_start": date_start,
                    "facility_name": facility_name,
                },
                document_upload_params.DocumentUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.query = to_raw_response_wrapper(
            documents.query,
        )
        self.upload = to_raw_response_wrapper(
            documents.upload,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.query = async_to_raw_response_wrapper(
            documents.query,
        )
        self.upload = async_to_raw_response_wrapper(
            documents.upload,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.query = to_streamed_response_wrapper(
            documents.query,
        )
        self.upload = to_streamed_response_wrapper(
            documents.upload,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.query = async_to_streamed_response_wrapper(
            documents.query,
        )
        self.upload = async_to_streamed_response_wrapper(
            documents.upload,
        )
