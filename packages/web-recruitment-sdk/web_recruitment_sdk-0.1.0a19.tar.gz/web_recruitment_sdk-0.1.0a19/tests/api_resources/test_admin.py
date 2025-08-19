# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import AdminListAccountsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAdmin:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_accounts(self, client: WebRecruitmentSDK) -> None:
        admin = client.admin.list_accounts()
        assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_accounts(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.with_raw_response.list_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin = response.parse()
        assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_accounts(self, client: WebRecruitmentSDK) -> None:
        with client.admin.with_streaming_response.list_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin = response.parse()
            assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAdmin:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_accounts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        admin = await async_client.admin.list_accounts()
        assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_accounts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.with_raw_response.list_accounts()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        admin = await response.parse()
        assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_accounts(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.with_streaming_response.list_accounts() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            admin = await response.parse()
            assert_matches_type(AdminListAccountsResponse, admin, path=["response"])

        assert cast(Any, response.is_closed) is True
