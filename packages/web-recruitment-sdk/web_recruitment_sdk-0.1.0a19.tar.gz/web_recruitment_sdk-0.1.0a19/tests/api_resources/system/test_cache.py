# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCache:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear(self, client: WebRecruitmentSDK) -> None:
        cache = client.system.cache.clear(
            "tenant_db_name",
        )
        assert_matches_type(object, cache, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear(self, client: WebRecruitmentSDK) -> None:
        response = client.system.cache.with_raw_response.clear(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cache = response.parse()
        assert_matches_type(object, cache, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear(self, client: WebRecruitmentSDK) -> None:
        with client.system.cache.with_streaming_response.clear(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cache = response.parse()
            assert_matches_type(object, cache, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.cache.with_raw_response.clear(
                "",
            )


class TestAsyncCache:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear(self, async_client: AsyncWebRecruitmentSDK) -> None:
        cache = await async_client.system.cache.clear(
            "tenant_db_name",
        )
        assert_matches_type(object, cache, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.cache.with_raw_response.clear(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        cache = await response.parse()
        assert_matches_type(object, cache, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.cache.with_streaming_response.clear(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            cache = await response.parse()
            assert_matches_type(object, cache, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.cache.with_raw_response.clear(
                "",
            )
