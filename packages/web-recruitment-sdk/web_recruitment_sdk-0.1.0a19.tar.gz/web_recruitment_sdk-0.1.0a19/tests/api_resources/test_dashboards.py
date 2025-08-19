# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    ChartResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDashboards:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_age_distribution(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_age_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_age_distribution_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_age_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
            step=2,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_age_distribution(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_age_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_age_distribution(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_age_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_ethnic_distribution(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_ethnic_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_ethnic_distribution_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_ethnic_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_ethnic_distribution(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_ethnic_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_ethnic_distribution(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_ethnic_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_gender_distribution(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_gender_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_gender_distribution_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_gender_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_gender_distribution(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_gender_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_gender_distribution(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_gender_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_race_distribution(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_race_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_race_distribution_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_race_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_race_distribution(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_race_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_race_distribution(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_race_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_conditions(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_conditions()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_conditions_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_conditions(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_top_conditions(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_top_conditions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_top_conditions(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_top_conditions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_medications(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_medications()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_medications_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_medications(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_top_medications(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_top_medications()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_top_medications(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_top_medications() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_procedures(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_procedures()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_top_procedures_with_all_params(self, client: WebRecruitmentSDK) -> None:
        dashboard = client.dashboards.get_top_procedures(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_top_procedures(self, client: WebRecruitmentSDK) -> None:
        response = client.dashboards.with_raw_response.get_top_procedures()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_top_procedures(self, client: WebRecruitmentSDK) -> None:
        with client.dashboards.with_streaming_response.get_top_procedures() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDashboards:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_age_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_age_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_age_distribution_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_age_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
            step=2,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_age_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_age_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_age_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_age_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_ethnic_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_ethnic_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_ethnic_distribution_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_ethnic_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_ethnic_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_ethnic_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_ethnic_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_ethnic_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_gender_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_gender_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_gender_distribution_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_gender_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_gender_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_gender_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_gender_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_gender_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_race_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_race_distribution()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_race_distribution_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_race_distribution(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_race_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_race_distribution()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_race_distribution(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_race_distribution() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_conditions()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_conditions_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_conditions(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_top_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_top_conditions()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_top_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_top_conditions() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_medications()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_medications_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_medications(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_top_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_top_medications()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_top_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_top_medications() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_procedures()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_top_procedures_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        dashboard = await async_client.dashboards.get_top_procedures(
            custom_search_id=0,
            limit=1,
            matching_criteria_ids=[0],
            protocol_id=0,
        )
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_top_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.dashboards.with_raw_response.get_top_procedures()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dashboard = await response.parse()
        assert_matches_type(ChartResponse, dashboard, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_top_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.dashboards.with_streaming_response.get_top_procedures() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dashboard = await response.parse()
            assert_matches_type(ChartResponse, dashboard, path=["response"])

        assert cast(Any, response.is_closed) is True
