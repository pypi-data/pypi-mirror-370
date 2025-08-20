# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc._utils import parse_datetime
from samplehc.types.v2 import (
    LedgerNewOrderResponse,
    LedgerClaimPaymentResponse,
    LedgerReverseEntryResponse,
    LedgerAssignInvoiceResponse,
    LedgerOrderWriteoffResponse,
    LedgerPatientPaymentResponse,
    LedgerClaimAdjustmentResponse,
    LedgerPatientAdjustmentResponse,
    LedgerInstitutionPaymentResponse,
    LedgerInstitutionAdjustmentResponse,
    LedgerPostRemittanceAcceptedResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLedger:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_assign_invoice(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_assign_invoice_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_assign_invoice(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_assign_invoice(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_claim_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_claim_adjustment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_claim_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_claim_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_claim_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_claim_payment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_claim_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_claim_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_institution_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_institution_adjustment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_institution_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_institution_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_institution_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_institution_payment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_institution_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_institution_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_new_order(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_new_order_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.new_order(
            amount_usd_cents=0,
            order_id="orderId",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_new_order(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_new_order(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_order_writeoff(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_order_writeoff_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_order_writeoff(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_order_writeoff(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patient_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patient_adjustment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patient_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patient_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patient_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patient_payment_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patient_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patient_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_post_remittance_accepted(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        )
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_post_remittance_accepted_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_post_remittance_accepted(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_post_remittance_accepted(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reverse_entry(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.reverse_entry(
            ik="ik",
        )
        assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reverse_entry(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.reverse_entry(
            ik="ik",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reverse_entry(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.reverse_entry(
            ik="ik",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLedger:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_assign_invoice(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_assign_invoice_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_assign_invoice(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_assign_invoice(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.assign_invoice(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerAssignInvoiceResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_claim_adjustment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_claim_payment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_institution_adjustment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.institution_adjustment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_institution_payment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.institution_payment(
            amount_usd_cents=0,
            ik="ik",
            institution_id="institutionId",
            invoice_id="invoiceId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_new_order_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.new_order(
            amount_usd_cents=0,
            order_id="orderId",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.new_order(
            amount_usd_cents=0,
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_order_writeoff_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patient_adjustment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patient_payment_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_post_remittance_accepted(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        )
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_post_remittance_accepted_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
            posted_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_post_remittance_accepted(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_post_remittance_accepted(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.post_remittance_accepted(
            adjustment_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            patient_id="patientId",
            patient_responsibility_usd_cents=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerPostRemittanceAcceptedResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reverse_entry(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.reverse_entry(
            ik="ik",
        )
        assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reverse_entry(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.reverse_entry(
            ik="ik",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reverse_entry(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.reverse_entry(
            ik="ik",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerReverseEntryResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True
