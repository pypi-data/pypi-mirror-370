# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system import (
    MatchingJobRead,
    MatchingTaskRead,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMatchingJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.retrieve(
                matching_job_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.cancel(
                matching_job_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_complete_task(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_complete_task(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_complete_task(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_complete_task(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.complete_task(
                path_tenant_db_name="",
                criteria_instances=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_error_task(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_error_task(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_error_task(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_error_task(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.error_task(
                path_tenant_db_name="",
                error_message="errorMessage",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_process(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_process(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_process(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_process(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.process(
                path_tenant_db_name="",
                job_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_all(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.matching_jobs.start_all(
            "tenant_db_name",
        )
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start_all(self, client: WebRecruitmentSDK) -> None:
        response = client.system.matching_jobs.with_raw_response.start_all(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start_all(self, client: WebRecruitmentSDK) -> None:
        with client.system.matching_jobs.with_streaming_response.start_all(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(object, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_start_all(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.matching_jobs.with_raw_response.start_all(
                "",
            )


class TestAsyncMatchingJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.retrieve(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.retrieve(
                matching_job_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.cancel(
            matching_job_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.cancel(
                matching_job_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_complete_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_complete_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_complete_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.complete_task(
            path_tenant_db_name="tenant_db_name",
            criteria_instances=[
                {
                    "answer": "yes",
                    "criteria_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_complete_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.complete_task(
                path_tenant_db_name="",
                criteria_instances=[
                    {
                        "answer": "yes",
                        "criteria_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_error_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_error_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_error_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.error_task(
            path_tenant_db_name="tenant_db_name",
            error_message="errorMessage",
            task_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(MatchingTaskRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_error_task(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.error_task(
                path_tenant_db_name="",
                error_message="errorMessage",
                task_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_process(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_process(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(MatchingJobRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_process(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.process(
            path_tenant_db_name="tenant_db_name",
            job_id=0,
            task_name="taskName",
            body_tenant_db_name="tenantDbName",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(MatchingJobRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_process(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.process(
                path_tenant_db_name="",
                job_id=0,
                task_name="taskName",
                body_tenant_db_name="tenantDbName",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_all(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.matching_jobs.start_all(
            "tenant_db_name",
        )
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start_all(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.matching_jobs.with_raw_response.start_all(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start_all(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.matching_jobs.with_streaming_response.start_all(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(object, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_start_all(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.matching_jobs.with_raw_response.start_all(
                "",
            )
