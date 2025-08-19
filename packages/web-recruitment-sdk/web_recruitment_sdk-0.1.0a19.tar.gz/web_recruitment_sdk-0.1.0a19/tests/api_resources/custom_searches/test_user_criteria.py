# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.custom_searches import (
    UserCriterionUpdateResponse,
    UserCriterionRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserCriteria:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        user_criterion = client.custom_searches.user_criteria.retrieve(
            custom_search_id=0,
        )
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: WebRecruitmentSDK) -> None:
        user_criterion = client.custom_searches.user_criteria.retrieve(
            custom_search_id=0,
            limit=0,
            skip=0,
        )
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.user_criteria.with_raw_response.retrieve(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_criterion = response.parse()
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.user_criteria.with_streaming_response.retrieve(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_criterion = response.parse()
            assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        user_criterion = client.custom_searches.user_criteria.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        )
        assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.user_criteria.with_raw_response.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_criterion = response.parse()
        assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.user_criteria.with_streaming_response.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_criterion = response.parse()
            assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUserCriteria:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user_criterion = await async_client.custom_searches.user_criteria.retrieve(
            custom_search_id=0,
        )
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user_criterion = await async_client.custom_searches.user_criteria.retrieve(
            custom_search_id=0,
            limit=0,
            skip=0,
        )
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.user_criteria.with_raw_response.retrieve(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_criterion = await response.parse()
        assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.user_criteria.with_streaming_response.retrieve(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_criterion = await response.parse()
            assert_matches_type(UserCriterionRetrieveResponse, user_criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        user_criterion = await async_client.custom_searches.user_criteria.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        )
        assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.user_criteria.with_raw_response.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user_criterion = await response.parse()
        assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.user_criteria.with_streaming_response.update(
            custom_search_id=0,
            active_criteria_ids=[0],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user_criterion = await response.parse()
            assert_matches_type(UserCriterionUpdateResponse, user_criterion, path=["response"])

        assert cast(Any, response.is_closed) is True
