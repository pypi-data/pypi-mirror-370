# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.protocols import (
    CriterionListResponse,
    CriterionGetMatchingProgressResponse,
)
from web_recruitment_sdk.types.custom_searches import CriteriaRead

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCriteria:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.create(
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.create(
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
            custom_search_id=0,
            description="description",
            body_protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria.with_raw_response.create(
            path_protocol_id=0,
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
        with client.protocols.criteria.with_streaming_response.create(
            path_protocol_id=0,
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
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.update(
            criterion_id=0,
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.update(
            criterion_id=0,
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
            custom_search_id=0,
            description="description",
            body_protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria.with_raw_response.update(
            criterion_id=0,
            path_protocol_id=0,
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
        with client.protocols.criteria.with_streaming_response.update(
            criterion_id=0,
            path_protocol_id=0,
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
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.list(
            0,
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.criteria.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriterionListResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.delete(
            criterion_id=0,
            protocol_id=0,
        )
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria.with_raw_response.delete(
            criterion_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.criteria.with_streaming_response.delete(
            criterion_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert criterion is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.get_matching_progress(
            protocol_id=0,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matching_progress_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.protocols.criteria.get_matching_progress(
            protocol_id=0,
            enable_sites_breakdown=True,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria.with_raw_response.get_matching_progress(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_matching_progress(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.criteria.with_streaming_response.get_matching_progress(
            protocol_id=0,
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
        criterion = await async_client.protocols.criteria.create(
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.create(
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
            custom_search_id=0,
            description="description",
            body_protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria.with_raw_response.create(
            path_protocol_id=0,
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
        async with async_client.protocols.criteria.with_streaming_response.create(
            path_protocol_id=0,
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
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.update(
            criterion_id=0,
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.update(
            criterion_id=0,
            path_protocol_id=0,
            summary="summary",
            type="inclusion",
            custom_search_id=0,
            description="description",
            body_protocol_id=0,
            status="active",
            user_raw_input="userRawInput",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria.with_raw_response.update(
            criterion_id=0,
            path_protocol_id=0,
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
        async with async_client.protocols.criteria.with_streaming_response.update(
            criterion_id=0,
            path_protocol_id=0,
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
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.list(
            0,
        )
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria.with_raw_response.list(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionListResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.criteria.with_streaming_response.list(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionListResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.delete(
            criterion_id=0,
            protocol_id=0,
        )
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria.with_raw_response.delete(
            criterion_id=0,
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert criterion is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.criteria.with_streaming_response.delete(
            criterion_id=0,
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert criterion is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.get_matching_progress(
            protocol_id=0,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matching_progress_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.protocols.criteria.get_matching_progress(
            protocol_id=0,
            enable_sites_breakdown=True,
        )
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria.with_raw_response.get_matching_progress(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_matching_progress(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.criteria.with_streaming_response.get_matching_progress(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriterionGetMatchingProgressResponse, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True
