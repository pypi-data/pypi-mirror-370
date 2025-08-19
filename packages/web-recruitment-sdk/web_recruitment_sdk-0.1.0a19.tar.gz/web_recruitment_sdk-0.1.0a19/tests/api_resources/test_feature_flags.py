# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import FeatureFlagRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFeatureFlags:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        feature_flag = client.feature_flags.retrieve(
            "flag_key",
        )
        assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.feature_flags.with_raw_response.retrieve(
            "flag_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature_flag = response.parse()
        assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.feature_flags.with_streaming_response.retrieve(
            "flag_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature_flag = response.parse()
            assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flag_key` but received ''"):
            client.feature_flags.with_raw_response.retrieve(
                "",
            )


class TestAsyncFeatureFlags:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        feature_flag = await async_client.feature_flags.retrieve(
            "flag_key",
        )
        assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.feature_flags.with_raw_response.retrieve(
            "flag_key",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        feature_flag = await response.parse()
        assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.feature_flags.with_streaming_response.retrieve(
            "flag_key",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            feature_flag = await response.parse()
            assert_matches_type(FeatureFlagRetrieveResponse, feature_flag, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flag_key` but received ''"):
            await async_client.feature_flags.with_raw_response.retrieve(
                "",
            )
