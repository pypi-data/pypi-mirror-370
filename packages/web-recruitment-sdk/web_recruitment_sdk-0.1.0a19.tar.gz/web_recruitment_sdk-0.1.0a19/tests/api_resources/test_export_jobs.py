# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    ExportJobListResponse,
    ExportJobCreateResponse,
    ExportJobRetrievePatientsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExportJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        export_job = client.export_jobs.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        )
        assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.export_jobs.with_raw_response.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = response.parse()
        assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.export_jobs.with_streaming_response.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = response.parse()
            assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        export_job = client.export_jobs.list()
        assert_matches_type(ExportJobListResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.export_jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = response.parse()
        assert_matches_type(ExportJobListResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.export_jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = response.parse()
            assert_matches_type(ExportJobListResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_patients(self, client: WebRecruitmentSDK) -> None:
        export_job = client.export_jobs.retrieve_patients(
            0,
        )
        assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_patients(self, client: WebRecruitmentSDK) -> None:
        response = client.export_jobs.with_raw_response.retrieve_patients(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = response.parse()
        assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_patients(self, client: WebRecruitmentSDK) -> None:
        with client.export_jobs.with_streaming_response.retrieve_patients(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = response.parse()
            assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExportJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        export_job = await async_client.export_jobs.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        )
        assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.export_jobs.with_raw_response.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = await response.parse()
        assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.export_jobs.with_streaming_response.create(
            site_id=0,
            client_id="clientId",
            ctms="ctms",
            ctms_site_id="ctmsSiteId",
            patients=[
                {
                    "match_percentage": 0,
                    "patient_id": "patientId",
                }
            ],
            referral_source_category_key=0,
            referral_source_key=0,
            study_id="studyId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = await response.parse()
            assert_matches_type(ExportJobCreateResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        export_job = await async_client.export_jobs.list()
        assert_matches_type(ExportJobListResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.export_jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = await response.parse()
        assert_matches_type(ExportJobListResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.export_jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = await response.parse()
            assert_matches_type(ExportJobListResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_patients(self, async_client: AsyncWebRecruitmentSDK) -> None:
        export_job = await async_client.export_jobs.retrieve_patients(
            0,
        )
        assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_patients(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.export_jobs.with_raw_response.retrieve_patients(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        export_job = await response.parse()
        assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_patients(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.export_jobs.with_streaming_response.retrieve_patients(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            export_job = await response.parse()
            assert_matches_type(ExportJobRetrievePatientsResponse, export_job, path=["response"])

        assert cast(Any, response.is_closed) is True
