# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime

import httpx

from .orders import (
    OrdersResource,
    AsyncOrdersResource,
    OrdersResourceWithRawResponse,
    AsyncOrdersResourceWithRawResponse,
    OrdersResourceWithStreamingResponse,
    AsyncOrdersResourceWithStreamingResponse,
)
from .patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from .insurance import (
    InsuranceResource,
    AsyncInsuranceResource,
    InsuranceResourceWithRawResponse,
    AsyncInsuranceResourceWithRawResponse,
    InsuranceResourceWithStreamingResponse,
    AsyncInsuranceResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ....types.v2 import (
    ledger_new_order_params,
    ledger_claim_payment_params,
    ledger_reverse_entry_params,
    ledger_assign_invoice_params,
    ledger_order_writeoff_params,
    ledger_patient_payment_params,
    ledger_claim_adjustment_params,
    ledger_patient_adjustment_params,
    ledger_institution_payment_params,
    ledger_institution_adjustment_params,
    ledger_post_remittance_accepted_params,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from .institutions.institutions import (
    InstitutionsResource,
    AsyncInstitutionsResource,
    InstitutionsResourceWithRawResponse,
    AsyncInstitutionsResourceWithRawResponse,
    InstitutionsResourceWithStreamingResponse,
    AsyncInstitutionsResourceWithStreamingResponse,
)
from ....types.v2.ledger_new_order_response import LedgerNewOrderResponse
from ....types.v2.ledger_claim_payment_response import LedgerClaimPaymentResponse
from ....types.v2.ledger_reverse_entry_response import LedgerReverseEntryResponse
from ....types.v2.ledger_assign_invoice_response import LedgerAssignInvoiceResponse
from ....types.v2.ledger_order_writeoff_response import LedgerOrderWriteoffResponse
from ....types.v2.ledger_patient_payment_response import LedgerPatientPaymentResponse
from ....types.v2.ledger_claim_adjustment_response import LedgerClaimAdjustmentResponse
from ....types.v2.ledger_patient_adjustment_response import LedgerPatientAdjustmentResponse
from ....types.v2.ledger_institution_payment_response import LedgerInstitutionPaymentResponse
from ....types.v2.ledger_institution_adjustment_response import LedgerInstitutionAdjustmentResponse
from ....types.v2.ledger_post_remittance_accepted_response import LedgerPostRemittanceAcceptedResponse

__all__ = ["LedgerResource", "AsyncLedgerResource"]


class LedgerResource(SyncAPIResource):
    @cached_property
    def institutions(self) -> InstitutionsResource:
        return InstitutionsResource(self._client)

    @cached_property
    def insurance(self) -> InsuranceResource:
        return InsuranceResource(self._client)

    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

    @cached_property
    def orders(self) -> OrdersResource:
        return OrdersResource(self._client)

    @cached_property
    def with_raw_response(self) -> LedgerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return LedgerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LedgerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return LedgerResourceWithStreamingResponse(self)

    def assign_invoice(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        invoice_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerAssignInvoiceResponse:
        """
        Assigns an invoice to an institution for a given order.

        Args:
          amount_usd_cents: Assignment amount in cents (positive or negative).

          ik: Idempotency key for the assignment.

          institution_id: Identifier of the institution for the assignment.

          invoice_id: Invoice ID being assigned.

          order_id: Order ID associated with the assignment.

          reason: Reason for the assignment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/invoice-assignment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "invoice_id": invoice_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_assign_invoice_params.LedgerAssignInvoiceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerAssignInvoiceResponse,
        )

    def claim_adjustment(
        self,
        *,
        amount_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerClaimAdjustmentResponse:
        """Posts a claim adjustment to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          claim_id: Identifier of the claim associated with this adjustment.

          ik: Idempotency key for the adjustment.

          insurance_id: Identifier of the insurance for the adjustment.

          order_id: Order ID associated with the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/claim-adjustment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_claim_adjustment_params.LedgerClaimAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerClaimAdjustmentResponse,
        )

    def claim_payment(
        self,
        *,
        amount_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerClaimPaymentResponse:
        """Posts a claim payment to the ledger.

        All monetary amounts should be provided in
        cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          claim_id: Identifier of the claim associated with this payment.

          ik: Idempotency key for the payment.

          insurance_id: Identifier of the insurance for the payment.

          order_id: Order ID associated with the payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/claim-payment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_claim_payment_params.LedgerClaimPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerClaimPaymentResponse,
        )

    def institution_adjustment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerInstitutionAdjustmentResponse:
        """Posts an institution adjustment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          ik: Idempotency key for the adjustment.

          institution_id: Identifier of the institution for the adjustment.

          order_id: Order ID associated with the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/institution-adjustment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_institution_adjustment_params.LedgerInstitutionAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerInstitutionAdjustmentResponse,
        )

    def institution_payment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        invoice_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerInstitutionPaymentResponse:
        """Posts an institution payment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          ik: Idempotency key for the payment.

          institution_id: Identifier of the institution for the payment.

          invoice_id: Identifier of the invoice associated with this payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/institution-payment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "invoice_id": invoice_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_institution_payment_params.LedgerInstitutionPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerInstitutionPaymentResponse,
        )

    def new_order(
        self,
        *,
        amount_usd_cents: float,
        order_id: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerNewOrderResponse:
        """
        Creates a new ledger entry for an order, linking claim, institution, patient,
        and insurance financial details. All monetary amounts should be provided in
        cents.

        Args:
          amount_usd_cents: Total amount for the order, in cents.

          order_id: Unique identifier for the order being processed.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/new-order",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "order_id": order_id,
                    "posted_at": posted_at,
                },
                ledger_new_order_params.LedgerNewOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerNewOrderResponse,
        )

    def order_writeoff(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerOrderWriteoffResponse:
        """Posts an order write-off to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Write-off amount in cents.

          ik: Idempotency key for the write-off.

          order_id: Order ID associated with the write-off.

          reason: Reason for the write-off.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/order-writeoff",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_order_writeoff_params.LedgerOrderWriteoffParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerOrderWriteoffResponse,
        )

    def patient_adjustment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        order_id: str,
        patient_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPatientAdjustmentResponse:
        """Posts a patient adjustment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          ik: Idempotency key for the adjustment.

          order_id: Order ID associated with the adjustment.

          patient_id: Identifier of the patient for the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/patient-adjustment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "order_id": order_id,
                    "patient_id": patient_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_patient_adjustment_params.LedgerPatientAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPatientAdjustmentResponse,
        )

    def patient_payment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        patient_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPatientPaymentResponse:
        """Posts a patient payment to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          ik: Idempotency key for the payment.

          patient_id: Identifier of the patient for the payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/patient-payment",
            body=maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "patient_id": patient_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_patient_payment_params.LedgerPatientPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPatientPaymentResponse,
        )

    def post_remittance_accepted(
        self,
        *,
        adjustment_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        patient_id: str,
        patient_responsibility_usd_cents: float,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPostRemittanceAcceptedResponse:
        """Posts a remittance accepted entry to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          adjustment_usd_cents: Adjustment amount in cents (positive or negative).

          claim_id: Identifier of the claim associated with this remittance.

          ik: Idempotency key for the remittance.

          insurance_id: Identifier of the insurance for the remittance.

          order_id: Order ID associated with the remittance.

          patient_id: Identifier of the patient for the remittance.

          patient_responsibility_usd_cents: Patient responsibility amount in cents.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/remittance-accepted",
            body=maybe_transform(
                {
                    "adjustment_usd_cents": adjustment_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "patient_id": patient_id,
                    "patient_responsibility_usd_cents": patient_responsibility_usd_cents,
                    "posted_at": posted_at,
                },
                ledger_post_remittance_accepted_params.LedgerPostRemittanceAcceptedParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPostRemittanceAcceptedResponse,
        )

    def reverse_entry(
        self,
        *,
        ik: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerReverseEntryResponse:
        """
        Given a ledger entry ID, posts its reversal entry.

        Args:
          ik: Idempotency key for the reversal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/ledger/reverse-entry",
            body=maybe_transform({"ik": ik}, ledger_reverse_entry_params.LedgerReverseEntryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerReverseEntryResponse,
        )


class AsyncLedgerResource(AsyncAPIResource):
    @cached_property
    def institutions(self) -> AsyncInstitutionsResource:
        return AsyncInstitutionsResource(self._client)

    @cached_property
    def insurance(self) -> AsyncInsuranceResource:
        return AsyncInsuranceResource(self._client)

    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

    @cached_property
    def orders(self) -> AsyncOrdersResource:
        return AsyncOrdersResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncLedgerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLedgerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLedgerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncLedgerResourceWithStreamingResponse(self)

    async def assign_invoice(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        invoice_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerAssignInvoiceResponse:
        """
        Assigns an invoice to an institution for a given order.

        Args:
          amount_usd_cents: Assignment amount in cents (positive or negative).

          ik: Idempotency key for the assignment.

          institution_id: Identifier of the institution for the assignment.

          invoice_id: Invoice ID being assigned.

          order_id: Order ID associated with the assignment.

          reason: Reason for the assignment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/invoice-assignment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "invoice_id": invoice_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_assign_invoice_params.LedgerAssignInvoiceParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerAssignInvoiceResponse,
        )

    async def claim_adjustment(
        self,
        *,
        amount_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerClaimAdjustmentResponse:
        """Posts a claim adjustment to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          claim_id: Identifier of the claim associated with this adjustment.

          ik: Idempotency key for the adjustment.

          insurance_id: Identifier of the insurance for the adjustment.

          order_id: Order ID associated with the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/claim-adjustment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_claim_adjustment_params.LedgerClaimAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerClaimAdjustmentResponse,
        )

    async def claim_payment(
        self,
        *,
        amount_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerClaimPaymentResponse:
        """Posts a claim payment to the ledger.

        All monetary amounts should be provided in
        cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          claim_id: Identifier of the claim associated with this payment.

          ik: Idempotency key for the payment.

          insurance_id: Identifier of the insurance for the payment.

          order_id: Order ID associated with the payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/claim-payment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_claim_payment_params.LedgerClaimPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerClaimPaymentResponse,
        )

    async def institution_adjustment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerInstitutionAdjustmentResponse:
        """Posts an institution adjustment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          ik: Idempotency key for the adjustment.

          institution_id: Identifier of the institution for the adjustment.

          order_id: Order ID associated with the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/institution-adjustment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_institution_adjustment_params.LedgerInstitutionAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerInstitutionAdjustmentResponse,
        )

    async def institution_payment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        institution_id: str,
        invoice_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerInstitutionPaymentResponse:
        """Posts an institution payment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          ik: Idempotency key for the payment.

          institution_id: Identifier of the institution for the payment.

          invoice_id: Identifier of the invoice associated with this payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/institution-payment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "institution_id": institution_id,
                    "invoice_id": invoice_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_institution_payment_params.LedgerInstitutionPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerInstitutionPaymentResponse,
        )

    async def new_order(
        self,
        *,
        amount_usd_cents: float,
        order_id: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerNewOrderResponse:
        """
        Creates a new ledger entry for an order, linking claim, institution, patient,
        and insurance financial details. All monetary amounts should be provided in
        cents.

        Args:
          amount_usd_cents: Total amount for the order, in cents.

          order_id: Unique identifier for the order being processed.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/new-order",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "order_id": order_id,
                    "posted_at": posted_at,
                },
                ledger_new_order_params.LedgerNewOrderParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerNewOrderResponse,
        )

    async def order_writeoff(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        order_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerOrderWriteoffResponse:
        """Posts an order write-off to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Write-off amount in cents.

          ik: Idempotency key for the write-off.

          order_id: Order ID associated with the write-off.

          reason: Reason for the write-off.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/order-writeoff",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "order_id": order_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_order_writeoff_params.LedgerOrderWriteoffParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerOrderWriteoffResponse,
        )

    async def patient_adjustment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        order_id: str,
        patient_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPatientAdjustmentResponse:
        """Posts a patient adjustment to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          amount_usd_cents: Adjustment amount in cents (positive or negative).

          ik: Idempotency key for the adjustment.

          order_id: Order ID associated with the adjustment.

          patient_id: Identifier of the patient for the adjustment.

          reason: Reason for the adjustment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/patient-adjustment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "order_id": order_id,
                    "patient_id": patient_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_patient_adjustment_params.LedgerPatientAdjustmentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPatientAdjustmentResponse,
        )

    async def patient_payment(
        self,
        *,
        amount_usd_cents: float,
        ik: str,
        patient_id: str,
        reason: str,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPatientPaymentResponse:
        """Posts a patient payment to the ledger.

        All monetary amounts should be provided
        in cents.

        Args:
          amount_usd_cents: Payment amount in cents.

          ik: Idempotency key for the payment.

          patient_id: Identifier of the patient for the payment.

          reason: Reason for the payment.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/patient-payment",
            body=await async_maybe_transform(
                {
                    "amount_usd_cents": amount_usd_cents,
                    "ik": ik,
                    "patient_id": patient_id,
                    "reason": reason,
                    "posted_at": posted_at,
                },
                ledger_patient_payment_params.LedgerPatientPaymentParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPatientPaymentResponse,
        )

    async def post_remittance_accepted(
        self,
        *,
        adjustment_usd_cents: float,
        claim_id: str,
        ik: str,
        insurance_id: str,
        order_id: str,
        patient_id: str,
        patient_responsibility_usd_cents: float,
        posted_at: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerPostRemittanceAcceptedResponse:
        """Posts a remittance accepted entry to the ledger.

        All monetary amounts should be
        provided in cents.

        Args:
          adjustment_usd_cents: Adjustment amount in cents (positive or negative).

          claim_id: Identifier of the claim associated with this remittance.

          ik: Idempotency key for the remittance.

          insurance_id: Identifier of the insurance for the remittance.

          order_id: Order ID associated with the remittance.

          patient_id: Identifier of the patient for the remittance.

          patient_responsibility_usd_cents: Patient responsibility amount in cents.

          posted_at: Optional ISO 8601 date-time to post the entry.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/remittance-accepted",
            body=await async_maybe_transform(
                {
                    "adjustment_usd_cents": adjustment_usd_cents,
                    "claim_id": claim_id,
                    "ik": ik,
                    "insurance_id": insurance_id,
                    "order_id": order_id,
                    "patient_id": patient_id,
                    "patient_responsibility_usd_cents": patient_responsibility_usd_cents,
                    "posted_at": posted_at,
                },
                ledger_post_remittance_accepted_params.LedgerPostRemittanceAcceptedParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerPostRemittanceAcceptedResponse,
        )

    async def reverse_entry(
        self,
        *,
        ik: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LedgerReverseEntryResponse:
        """
        Given a ledger entry ID, posts its reversal entry.

        Args:
          ik: Idempotency key for the reversal.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/ledger/reverse-entry",
            body=await async_maybe_transform({"ik": ik}, ledger_reverse_entry_params.LedgerReverseEntryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LedgerReverseEntryResponse,
        )


class LedgerResourceWithRawResponse:
    def __init__(self, ledger: LedgerResource) -> None:
        self._ledger = ledger

        self.assign_invoice = to_raw_response_wrapper(
            ledger.assign_invoice,
        )
        self.claim_adjustment = to_raw_response_wrapper(
            ledger.claim_adjustment,
        )
        self.claim_payment = to_raw_response_wrapper(
            ledger.claim_payment,
        )
        self.institution_adjustment = to_raw_response_wrapper(
            ledger.institution_adjustment,
        )
        self.institution_payment = to_raw_response_wrapper(
            ledger.institution_payment,
        )
        self.new_order = to_raw_response_wrapper(
            ledger.new_order,
        )
        self.order_writeoff = to_raw_response_wrapper(
            ledger.order_writeoff,
        )
        self.patient_adjustment = to_raw_response_wrapper(
            ledger.patient_adjustment,
        )
        self.patient_payment = to_raw_response_wrapper(
            ledger.patient_payment,
        )
        self.post_remittance_accepted = to_raw_response_wrapper(
            ledger.post_remittance_accepted,
        )
        self.reverse_entry = to_raw_response_wrapper(
            ledger.reverse_entry,
        )

    @cached_property
    def institutions(self) -> InstitutionsResourceWithRawResponse:
        return InstitutionsResourceWithRawResponse(self._ledger.institutions)

    @cached_property
    def insurance(self) -> InsuranceResourceWithRawResponse:
        return InsuranceResourceWithRawResponse(self._ledger.insurance)

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._ledger.patients)

    @cached_property
    def orders(self) -> OrdersResourceWithRawResponse:
        return OrdersResourceWithRawResponse(self._ledger.orders)


class AsyncLedgerResourceWithRawResponse:
    def __init__(self, ledger: AsyncLedgerResource) -> None:
        self._ledger = ledger

        self.assign_invoice = async_to_raw_response_wrapper(
            ledger.assign_invoice,
        )
        self.claim_adjustment = async_to_raw_response_wrapper(
            ledger.claim_adjustment,
        )
        self.claim_payment = async_to_raw_response_wrapper(
            ledger.claim_payment,
        )
        self.institution_adjustment = async_to_raw_response_wrapper(
            ledger.institution_adjustment,
        )
        self.institution_payment = async_to_raw_response_wrapper(
            ledger.institution_payment,
        )
        self.new_order = async_to_raw_response_wrapper(
            ledger.new_order,
        )
        self.order_writeoff = async_to_raw_response_wrapper(
            ledger.order_writeoff,
        )
        self.patient_adjustment = async_to_raw_response_wrapper(
            ledger.patient_adjustment,
        )
        self.patient_payment = async_to_raw_response_wrapper(
            ledger.patient_payment,
        )
        self.post_remittance_accepted = async_to_raw_response_wrapper(
            ledger.post_remittance_accepted,
        )
        self.reverse_entry = async_to_raw_response_wrapper(
            ledger.reverse_entry,
        )

    @cached_property
    def institutions(self) -> AsyncInstitutionsResourceWithRawResponse:
        return AsyncInstitutionsResourceWithRawResponse(self._ledger.institutions)

    @cached_property
    def insurance(self) -> AsyncInsuranceResourceWithRawResponse:
        return AsyncInsuranceResourceWithRawResponse(self._ledger.insurance)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._ledger.patients)

    @cached_property
    def orders(self) -> AsyncOrdersResourceWithRawResponse:
        return AsyncOrdersResourceWithRawResponse(self._ledger.orders)


class LedgerResourceWithStreamingResponse:
    def __init__(self, ledger: LedgerResource) -> None:
        self._ledger = ledger

        self.assign_invoice = to_streamed_response_wrapper(
            ledger.assign_invoice,
        )
        self.claim_adjustment = to_streamed_response_wrapper(
            ledger.claim_adjustment,
        )
        self.claim_payment = to_streamed_response_wrapper(
            ledger.claim_payment,
        )
        self.institution_adjustment = to_streamed_response_wrapper(
            ledger.institution_adjustment,
        )
        self.institution_payment = to_streamed_response_wrapper(
            ledger.institution_payment,
        )
        self.new_order = to_streamed_response_wrapper(
            ledger.new_order,
        )
        self.order_writeoff = to_streamed_response_wrapper(
            ledger.order_writeoff,
        )
        self.patient_adjustment = to_streamed_response_wrapper(
            ledger.patient_adjustment,
        )
        self.patient_payment = to_streamed_response_wrapper(
            ledger.patient_payment,
        )
        self.post_remittance_accepted = to_streamed_response_wrapper(
            ledger.post_remittance_accepted,
        )
        self.reverse_entry = to_streamed_response_wrapper(
            ledger.reverse_entry,
        )

    @cached_property
    def institutions(self) -> InstitutionsResourceWithStreamingResponse:
        return InstitutionsResourceWithStreamingResponse(self._ledger.institutions)

    @cached_property
    def insurance(self) -> InsuranceResourceWithStreamingResponse:
        return InsuranceResourceWithStreamingResponse(self._ledger.insurance)

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._ledger.patients)

    @cached_property
    def orders(self) -> OrdersResourceWithStreamingResponse:
        return OrdersResourceWithStreamingResponse(self._ledger.orders)


class AsyncLedgerResourceWithStreamingResponse:
    def __init__(self, ledger: AsyncLedgerResource) -> None:
        self._ledger = ledger

        self.assign_invoice = async_to_streamed_response_wrapper(
            ledger.assign_invoice,
        )
        self.claim_adjustment = async_to_streamed_response_wrapper(
            ledger.claim_adjustment,
        )
        self.claim_payment = async_to_streamed_response_wrapper(
            ledger.claim_payment,
        )
        self.institution_adjustment = async_to_streamed_response_wrapper(
            ledger.institution_adjustment,
        )
        self.institution_payment = async_to_streamed_response_wrapper(
            ledger.institution_payment,
        )
        self.new_order = async_to_streamed_response_wrapper(
            ledger.new_order,
        )
        self.order_writeoff = async_to_streamed_response_wrapper(
            ledger.order_writeoff,
        )
        self.patient_adjustment = async_to_streamed_response_wrapper(
            ledger.patient_adjustment,
        )
        self.patient_payment = async_to_streamed_response_wrapper(
            ledger.patient_payment,
        )
        self.post_remittance_accepted = async_to_streamed_response_wrapper(
            ledger.post_remittance_accepted,
        )
        self.reverse_entry = async_to_streamed_response_wrapper(
            ledger.reverse_entry,
        )

    @cached_property
    def institutions(self) -> AsyncInstitutionsResourceWithStreamingResponse:
        return AsyncInstitutionsResourceWithStreamingResponse(self._ledger.institutions)

    @cached_property
    def insurance(self) -> AsyncInsuranceResourceWithStreamingResponse:
        return AsyncInsuranceResourceWithStreamingResponse(self._ledger.insurance)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._ledger.patients)

    @cached_property
    def orders(self) -> AsyncOrdersResourceWithStreamingResponse:
        return AsyncOrdersResourceWithStreamingResponse(self._ledger.orders)
