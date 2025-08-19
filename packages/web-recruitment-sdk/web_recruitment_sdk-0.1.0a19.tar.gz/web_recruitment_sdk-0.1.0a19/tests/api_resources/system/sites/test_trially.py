# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system.sites import (
    TriallyGetActiveProtocolsResponse,
    TriallyGetActiveCustomSearchesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrially:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_active_custom_searches(self, client: WebRecruitmentSDK) -> None:
        trially = client.system.sites.trially.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_active_custom_searches(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.trially.with_raw_response.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trially = response.parse()
        assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_active_custom_searches(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.trially.with_streaming_response.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trially = response.parse()
            assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_active_custom_searches(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.sites.trially.with_raw_response.get_active_custom_searches(
                trially_site_id="trially_site_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            client.system.sites.trially.with_raw_response.get_active_custom_searches(
                trially_site_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_active_protocols(self, client: WebRecruitmentSDK) -> None:
        trially = client.system.sites.trially.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_active_protocols(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.trially.with_raw_response.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trially = response.parse()
        assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_active_protocols(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.trially.with_streaming_response.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trially = response.parse()
            assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_active_protocols(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.sites.trially.with_raw_response.get_active_protocols(
                trially_site_id="trially_site_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            client.system.sites.trially.with_raw_response.get_active_protocols(
                trially_site_id="",
                tenant_db_name="tenant_db_name",
            )


class TestAsyncTrially:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_active_custom_searches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        trially = await async_client.system.sites.trially.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_active_custom_searches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.trially.with_raw_response.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trially = await response.parse()
        assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_active_custom_searches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.trially.with_streaming_response.get_active_custom_searches(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trially = await response.parse()
            assert_matches_type(TriallyGetActiveCustomSearchesResponse, trially, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_active_custom_searches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.sites.trially.with_raw_response.get_active_custom_searches(
                trially_site_id="trially_site_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            await async_client.system.sites.trially.with_raw_response.get_active_custom_searches(
                trially_site_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_active_protocols(self, async_client: AsyncWebRecruitmentSDK) -> None:
        trially = await async_client.system.sites.trially.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_active_protocols(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.trially.with_raw_response.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trially = await response.parse()
        assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_active_protocols(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.trially.with_streaming_response.get_active_protocols(
            trially_site_id="trially_site_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trially = await response.parse()
            assert_matches_type(TriallyGetActiveProtocolsResponse, trially, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_active_protocols(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.sites.trially.with_raw_response.get_active_protocols(
                trially_site_id="trially_site_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            await async_client.system.sites.trially.with_raw_response.get_active_protocols(
                trially_site_id="",
                tenant_db_name="tenant_db_name",
            )
