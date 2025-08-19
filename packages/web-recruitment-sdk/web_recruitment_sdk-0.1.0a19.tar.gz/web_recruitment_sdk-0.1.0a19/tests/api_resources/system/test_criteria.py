# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system import (
    CriterionListResponse,
    CriterionGetPatientsToMatchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCriteria:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        criterion = client.system.criteria.list(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.system.criteria.list(
            tenant_db_name="tenant_db_name",
            criteria_ids=[0],
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.system.criteria.with_raw_response.list(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.system.criteria.with_streaming_response.list(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriterionListResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.criteria.with_raw_response.list(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_patients_to_match(self, client: WebRecruitmentSDK) -> None:
        criterion = client.system.criteria.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_patients_to_match(self, client: WebRecruitmentSDK) -> None:
        response = client.system.criteria.with_raw_response.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_patients_to_match(self, client: WebRecruitmentSDK) -> None:
        with client.system.criteria.with_streaming_response.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_patients_to_match(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.criteria.with_raw_response.get_patients_to_match(
                criteria_id="criteria_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `criteria_id` but received ''"):
            client.system.criteria.with_raw_response.get_patients_to_match(
                criteria_id="",
                tenant_db_name="tenant_db_name",
            )


class TestAsyncCriteria:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.system.criteria.list(
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.system.criteria.list(
            tenant_db_name="tenant_db_name",
            criteria_ids=[0],
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.criteria.with_raw_response.list(
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.criteria.with_streaming_response.list(
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionListResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.criteria.with_raw_response.list(
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_patients_to_match(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.system.criteria.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_patients_to_match(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.criteria.with_raw_response.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_patients_to_match(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.criteria.with_streaming_response.get_patients_to_match(
            criteria_id="criteria_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionGetPatientsToMatchResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_patients_to_match(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.criteria.with_raw_response.get_patients_to_match(
                criteria_id="criteria_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `criteria_id` but received ''"):
            await async_client.system.criteria.with_raw_response.get_patients_to_match(
                criteria_id="",
                tenant_db_name="tenant_db_name",
            )
