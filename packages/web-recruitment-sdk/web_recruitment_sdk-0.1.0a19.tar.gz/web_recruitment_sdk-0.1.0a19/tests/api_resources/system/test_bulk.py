# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system.patients import BulkInsertResult

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBulk:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        bulk = client.system.bulk.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        response = client.system.bulk.with_raw_response.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
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
    def test_streaming_response_update_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        with client.system.bulk.with_streaming_response.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
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
    def test_path_params_update_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.bulk.with_raw_response.update_criteria_instances(
                tenant_db_name="",
                body=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
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
    async def test_method_update_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        bulk = await async_client.system.bulk.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, bulk, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.bulk.with_raw_response.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
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
    async def test_streaming_response_update_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.bulk.with_streaming_response.update_criteria_instances(
            tenant_db_name="tenant_db_name",
            body=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
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
    async def test_path_params_update_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.bulk.with_raw_response.update_criteria_instances(
                tenant_db_name="",
                body=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )
