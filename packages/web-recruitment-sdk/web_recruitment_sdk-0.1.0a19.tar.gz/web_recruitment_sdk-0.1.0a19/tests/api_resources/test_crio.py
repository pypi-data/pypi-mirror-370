# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import CrioListSitesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCrio:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_sites(self, client: WebRecruitmentSDK) -> None:
        crio = client.crio.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(CrioListSitesResponse, crio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_sites(self, client: WebRecruitmentSDK) -> None:
        response = client.crio.with_raw_response.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crio = response.parse()
        assert_matches_type(CrioListSitesResponse, crio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_sites(self, client: WebRecruitmentSDK) -> None:
        with client.crio.with_streaming_response.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crio = response.parse()
            assert_matches_type(CrioListSitesResponse, crio, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCrio:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        crio = await async_client.crio.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(CrioListSitesResponse, crio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.crio.with_raw_response.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        crio = await response.parse()
        assert_matches_type(CrioListSitesResponse, crio, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.crio.with_streaming_response.list_sites(
            client_id="client_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            crio = await response.parse()
            assert_matches_type(CrioListSitesResponse, crio, path=["response"])

        assert cast(Any, response.is_closed) is True
