# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.external import CarequalityHealthCheckResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCarequality:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_health_check(self, client: WebRecruitmentSDK) -> None:
        carequality = client.external.carequality.health_check(
            x_api_key="X-API-Key",
        )
        assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_health_check(self, client: WebRecruitmentSDK) -> None:
        response = client.external.carequality.with_raw_response.health_check(
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        carequality = response.parse()
        assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_health_check(self, client: WebRecruitmentSDK) -> None:
        with client.external.carequality.with_streaming_response.health_check(
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            carequality = response.parse()
            assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCarequality:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_health_check(self, async_client: AsyncWebRecruitmentSDK) -> None:
        carequality = await async_client.external.carequality.health_check(
            x_api_key="X-API-Key",
        )
        assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_health_check(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.external.carequality.with_raw_response.health_check(
            x_api_key="X-API-Key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        carequality = await response.parse()
        assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_health_check(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.external.carequality.with_streaming_response.health_check(
            x_api_key="X-API-Key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            carequality = await response.parse()
            assert_matches_type(CarequalityHealthCheckResponse, carequality, path=["response"])

        assert cast(Any, response.is_closed) is True
