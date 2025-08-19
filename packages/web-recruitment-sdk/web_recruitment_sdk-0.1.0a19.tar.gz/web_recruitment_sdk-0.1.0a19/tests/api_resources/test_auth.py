# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import Authorization, AuthListRolesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAuth:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_roles(self, client: WebRecruitmentSDK) -> None:
        auth = client.auth.list_roles()
        assert_matches_type(AuthListRolesResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_roles(self, client: WebRecruitmentSDK) -> None:
        response = client.auth.with_raw_response.list_roles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(AuthListRolesResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_roles(self, client: WebRecruitmentSDK) -> None:
        with client.auth.with_streaming_response.list_roles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(AuthListRolesResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_user_authorization(self, client: WebRecruitmentSDK) -> None:
        auth = client.auth.update_user_authorization(
            user_id=0,
        )
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_user_authorization_with_all_params(self, client: WebRecruitmentSDK) -> None:
        auth = client.auth.update_user_authorization(
            user_id=0,
            role_ids=["string"],
            site_ids=[0],
        )
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_user_authorization(self, client: WebRecruitmentSDK) -> None:
        response = client.auth.with_raw_response.update_user_authorization(
            user_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = response.parse()
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_user_authorization(self, client: WebRecruitmentSDK) -> None:
        with client.auth.with_streaming_response.update_user_authorization(
            user_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = response.parse()
            assert_matches_type(Authorization, auth, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAuth:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_roles(self, async_client: AsyncWebRecruitmentSDK) -> None:
        auth = await async_client.auth.list_roles()
        assert_matches_type(AuthListRolesResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_roles(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.auth.with_raw_response.list_roles()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(AuthListRolesResponse, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_roles(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.auth.with_streaming_response.list_roles() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(AuthListRolesResponse, auth, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_user_authorization(self, async_client: AsyncWebRecruitmentSDK) -> None:
        auth = await async_client.auth.update_user_authorization(
            user_id=0,
        )
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_user_authorization_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        auth = await async_client.auth.update_user_authorization(
            user_id=0,
            role_ids=["string"],
            site_ids=[0],
        )
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_user_authorization(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.auth.with_raw_response.update_user_authorization(
            user_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        auth = await response.parse()
        assert_matches_type(Authorization, auth, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_user_authorization(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.auth.with_streaming_response.update_user_authorization(
            user_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            auth = await response.parse()
            assert_matches_type(Authorization, auth, path=["response"])

        assert cast(Any, response.is_closed) is True
