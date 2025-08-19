# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.admin import (
    UserWithAccount,
    UserListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUsers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.retrieve(
            0,
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.list()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.list(
            limit=0,
            offset=0,
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.delete(
            0,
        )
        assert user is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert user is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert user is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_invite(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_invite_with_all_params(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
            site_ids=[0],
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_invite(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_invite(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_current(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.retrieve_current()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_current(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.retrieve_current()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_current(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.retrieve_current() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_tenant(self, client: WebRecruitmentSDK) -> None:
        user = client.admin.users.update_tenant(
            tenant_id="tenantId",
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_tenant(self, client: WebRecruitmentSDK) -> None:
        response = client.admin.users.with_raw_response.update_tenant(
            tenant_id="tenantId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_tenant(self, client: WebRecruitmentSDK) -> None:
        with client.admin.users.with_streaming_response.update_tenant(
            tenant_id="tenantId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUsers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.retrieve(
            0,
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.list()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.list(
            limit=0,
            offset=0,
        )
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserListResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserListResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.delete(
            0,
        )
        assert user is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert user is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert user is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_invite(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_invite_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
            site_ids=[0],
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_invite(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_invite(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.invite(
            email="dev@stainless.com",
            role_ids=["trially-system-admin"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_current(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.retrieve_current()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_current(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.retrieve_current()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_current(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.retrieve_current() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_tenant(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user = await async_client.admin.users.update_tenant(
            tenant_id="tenantId",
        )
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_tenant(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.admin.users.with_raw_response.update_tenant(
            tenant_id="tenantId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserWithAccount, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_tenant(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.admin.users.with_streaming_response.update_tenant(
            tenant_id="tenantId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserWithAccount, user, path=["response"])

        assert cast(Any, response.is_closed) is True
