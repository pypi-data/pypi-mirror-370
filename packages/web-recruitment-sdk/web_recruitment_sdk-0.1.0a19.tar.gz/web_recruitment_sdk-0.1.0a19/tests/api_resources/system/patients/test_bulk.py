# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk._utils import parse_date, parse_datetime
from web_recruitment_sdk.types.system.patients import (
    BulkInsertResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBulk:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_appointments(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_appointments(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_appointments(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_appointments(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.create_appointments(
                tenant_db_name="",
                body=[
                    {
                        "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "trially_appointment_id": "triallyAppointmentId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_allergies(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_allergies(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_allergies(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_allergies(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_allergies(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_allergy_id": "triallyAllergyId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_conditions(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_conditions(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_conditions(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_conditions(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_conditions(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_condition_id": "triallyConditionId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_demographics(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_demographics(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_demographics(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_demographics(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_demographics(
                tenant_db_name="",
                body=[{"trially_patient_id": "triallyPatientId"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_entity(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_entity(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_entity(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_entity(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_entity(
                tenant_db_name="",
                body=[
                    {
                        "entity_id": "entity_id",
                        "trially_patient_id": "trially_patient_id",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_entity_search(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_entity_search(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_entity_search(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_entity_search(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_entity_search(
                tenant_db_name="",
                body=[
                    {
                        "entity": "entity",
                        "entity_id": "entity_id",
                        "entity_type": "condition",
                        "search_text": "search_text",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_history(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_history(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_history(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_history(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_history(
                tenant_db_name="",
                body=[
                    {
                        "full_medical_history": "fullMedicalHistory",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_lab_results(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_lab_results(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_lab_results(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_lab_results(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_lab_results(
                tenant_db_name="",
                body=[
                    {
                        "entity_id": "entityId",
                        "name": "name",
                        "trially_lab_result_id": "triallyLabResultId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_medications(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_medications(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_medications(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_medications(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_medications(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_medication_id": "triallyMedicationId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_procedures(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_procedures(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_procedures(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_procedures(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_procedures(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_patient_id": "triallyPatientId",
                        "trially_procedure_id": "triallyProcedureId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_vitals(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_vitals(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_vitals(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_vitals(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.update_vitals(
                tenant_db_name="",
                body=[
                    {
                        "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.patients.bulk.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upsert(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.bulk.with_raw_response.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upsert(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.bulk.with_streaming_response.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upsert(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.bulk.with_raw_response.upsert(
                tenant_db_name="",
                body=[
                    {
                        "dob": parse_date("2019-12-27"),
                        "email": "email",
                        "family_name": "familyName",
                        "given_name": "givenName",
                        "site_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )


class TestAsyncBulk:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_appointments(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_appointments(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_appointments(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.create_appointments(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_appointment_id": "triallyAppointmentId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_appointments(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.create_appointments(
                tenant_db_name="",
                body=[
                    {
                        "date": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "trially_appointment_id": "triallyAppointmentId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_allergies(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_allergies(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_allergy_id": "triallyAllergyId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_conditions(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_conditions(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_condition_id": "triallyConditionId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_demographics(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_demographics(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_demographics(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_demographics(
            tenant_db_name="tenant_db_name",
            body=[{"trially_patient_id": "triallyPatientId"}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_demographics(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_demographics(
                tenant_db_name="",
                body=[{"trially_patient_id": "triallyPatientId"}],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_entity(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_entity(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_entity(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_entity(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entity_id",
                    "trially_patient_id": "trially_patient_id",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_entity(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_entity(
                tenant_db_name="",
                body=[
                    {
                        "entity_id": "entity_id",
                        "trially_patient_id": "trially_patient_id",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_entity_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_entity_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_entity_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_entity_search(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity": "entity",
                    "entity_id": "entity_id",
                    "entity_type": "condition",
                    "search_text": "search_text",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_entity_search(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_entity_search(
                tenant_db_name="",
                body=[
                    {
                        "entity": "entity",
                        "entity_id": "entity_id",
                        "entity_type": "condition",
                        "search_text": "search_text",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_history(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_history(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_history(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_history(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "full_medical_history": "fullMedicalHistory",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_history(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_history(
                tenant_db_name="",
                body=[
                    {
                        "full_medical_history": "fullMedicalHistory",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_lab_results(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_lab_results(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_lab_results(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_lab_results(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "entity_id": "entityId",
                    "name": "name",
                    "trially_lab_result_id": "triallyLabResultId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_lab_results(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_lab_results(
                tenant_db_name="",
                body=[
                    {
                        "entity_id": "entityId",
                        "name": "name",
                        "trially_lab_result_id": "triallyLabResultId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_medications(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_medications(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_medication_id": "triallyMedicationId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_procedures(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_procedures(
                tenant_db_name="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_patient_id": "triallyPatientId",
                        "trially_procedure_id": "triallyProcedureId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_vitals(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_vitals(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_vitals(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.update_vitals(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_vitals(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.update_vitals(
                tenant_db_name="",
                body=[
                    {
                        "effective_date": parse_datetime("2019-12-27T18:11:19.117Z"),
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.patients.bulk.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upsert(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.bulk.with_raw_response.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        bulk = await response.parse()
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upsert(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.bulk.with_streaming_response.upsert(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            bulk = await response.parse()
            assert_matches_type(BulkInsertResult, bulk, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upsert(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.bulk.with_raw_response.upsert(
                tenant_db_name="",
                body=[
                    {
                        "dob": parse_date("2019-12-27"),
                        "email": "email",
                        "family_name": "familyName",
                        "given_name": "givenName",
                        "site_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )
