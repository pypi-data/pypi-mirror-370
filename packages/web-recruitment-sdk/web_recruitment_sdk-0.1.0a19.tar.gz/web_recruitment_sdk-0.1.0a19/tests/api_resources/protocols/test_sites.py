# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.protocols import SiteListResponse, SiteCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSites:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        site = client.protocols.sites.create(
            site_id=0,
            protocol_id=0,
        )
        assert_matches_type(SiteCreateResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.sites.with_raw_response.create(
            site_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteCreateResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.sites.with_streaming_response.create(
            site_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteCreateResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        site = client.protocols.sites.list(
            0,
        )
        assert_matches_type(SiteListResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.sites.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteListResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.sites.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteListResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        site = client.protocols.sites.delete(
            site_id=0,
            protocol_id=0,
        )
        assert site is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.sites.with_raw_response.delete(
            site_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert site is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.sites.with_streaming_response.delete(
            site_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert site is None

        assert cast(Any, response.is_closed) is True


class TestAsyncSites:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.protocols.sites.create(
            site_id=0,
            protocol_id=0,
        )
        assert_matches_type(SiteCreateResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.sites.with_raw_response.create(
            site_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteCreateResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.sites.with_streaming_response.create(
            site_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteCreateResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.protocols.sites.list(
            0,
        )
        assert_matches_type(SiteListResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.sites.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteListResponse, site, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.sites.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteListResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.protocols.sites.delete(
            site_id=0,
            protocol_id=0,
        )
        assert site is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.sites.with_raw_response.delete(
            site_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert site is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.sites.with_streaming_response.delete(
            site_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert site is None

        assert cast(Any, response.is_closed) is True
