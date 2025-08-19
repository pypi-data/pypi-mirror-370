# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.custom_searches import (
    CriteriaRead,
    CriterionRetrieveResponse,
    CriterionGetMatchingProgressResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCriteria:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
            body_custom_search_id=0,
            description="description",
            protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.criteria.with_raw_response.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.criteria.with_streaming_response.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.retrieve(
            0,
        )
        assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.criteria.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.criteria.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
            body_custom_search_id=0,
            description="description",
            protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.criteria.with_raw_response.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.criteria.with_streaming_response.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.delete(
            criterion_id=0,
            custom_search_id=0,
        )
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.criteria.with_raw_response.delete(
            criterion_id=0,
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.criteria.with_streaming_response.delete(
            criterion_id=0,
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert criterion is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.get_matching_progress(
            custom_search_id=0,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matching_progress_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.custom_searches.criteria.get_matching_progress(
            custom_search_id=0,
            enable_sites_breakdown=True,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.criteria.with_raw_response.get_matching_progress(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.criteria.with_streaming_response.get_matching_progress(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCriteria:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
            body_custom_search_id=0,
            description="description",
            protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.criteria.with_raw_response.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.criteria.with_streaming_response.create(
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.retrieve(
            0,
        )
        assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.criteria.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.criteria.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionRetrieveResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
            body_custom_search_id=0,
            description="description",
            protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.criteria.with_raw_response.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.criteria.with_streaming_response.update(
            criterion_id=0,
            path_custom_search_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.delete(
            criterion_id=0,
            custom_search_id=0,
        )
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.criteria.with_raw_response.delete(
            criterion_id=0,
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.criteria.with_streaming_response.delete(
            criterion_id=0,
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert criterion is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.get_matching_progress(
            custom_search_id=0,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matching_progress_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.custom_searches.criteria.get_matching_progress(
            custom_search_id=0,
            enable_sites_breakdown=True,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.criteria.with_raw_response.get_matching_progress(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.criteria.with_streaming_response.get_matching_progress(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True
