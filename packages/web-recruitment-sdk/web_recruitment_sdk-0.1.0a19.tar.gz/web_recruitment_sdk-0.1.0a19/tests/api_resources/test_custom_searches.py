# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    FunnelStats,
    CustomSearchRead,
    CustomSearchListResponse,
    CustomSearchRetrieveSitesResponse,
    CustomSearchRetrieveMatchesResponse,
    CustomSearchGetCriteriaInstancesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCustomSearches:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.create(
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.create(
            title="title",
            site_ids=[0],
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.create(
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.create(
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve(
            0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.update(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.update(
            custom_search_id=0,
            sites=[{"id": 0}],
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.update(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.update(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.list()
        assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.delete(
            0,
        )
        assert custom_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert custom_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert custom_search is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.patch(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_patch_with_all_params(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.patch(
            custom_search_id=0,
            sites=[{"id": 0}],
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_patch(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.patch(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_patch(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.patch(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_funnel(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve_funnel(
            custom_search_id=0,
        )
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_funnel_with_all_params(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve_funnel(
            custom_search_id=0,
            matching_criteria_ids=[0],
            site_ids=[0],
        )
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_funnel(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.retrieve_funnel(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_funnel(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.retrieve_funnel(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(FunnelStats, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_matches(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve_matches(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_matches_with_all_params(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve_matches(
            custom_search_id=0,
            matching_criteria_ids=[0],
        )
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_matches(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.retrieve_matches(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_matches(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.retrieve_matches(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_sites(self, client: WebRecruitmentSDK) -> None:
        custom_search = client.custom_searches.retrieve_sites(
            0,
        )
        assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_sites(self, client: WebRecruitmentSDK) -> None:
        response = client.custom_searches.with_raw_response.retrieve_sites(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = response.parse()
        assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_sites(self, client: WebRecruitmentSDK) -> None:
        with client.custom_searches.with_streaming_response.retrieve_sites(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = response.parse()
            assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCustomSearches:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.create(
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.create(
            title="title",
            site_ids=[0],
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.create(
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.create(
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve(
            0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.update(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.update(
            custom_search_id=0,
            sites=[{"id": 0}],
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.update(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.update(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.list()
        assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchListResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.delete(
            0,
        )
        assert custom_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert custom_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert custom_search is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.get_criteria_instances(
            custom_search_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchGetCriteriaInstancesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.patch(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_patch_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.patch(
            custom_search_id=0,
            sites=[{"id": 0}],
            title="title",
        )
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_patch(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.patch(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRead, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_patch(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.patch(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRead, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve_funnel(
            custom_search_id=0,
        )
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_funnel_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve_funnel(
            custom_search_id=0,
            matching_criteria_ids=[0],
            site_ids=[0],
        )
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.retrieve_funnel(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(FunnelStats, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.retrieve_funnel(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(FunnelStats, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve_matches(
            custom_search_id=0,
        )
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_matches_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve_matches(
            custom_search_id=0,
            matching_criteria_ids=[0],
        )
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.retrieve_matches(
            custom_search_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.retrieve_matches(
            custom_search_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRetrieveMatchesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        custom_search = await async_client.custom_searches.retrieve_sites(
            0,
        )
        assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.custom_searches.with_raw_response.retrieve_sites(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        custom_search = await response.parse()
        assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_sites(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.custom_searches.with_streaming_response.retrieve_sites(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            custom_search = await response.parse()
            assert_matches_type(CustomSearchRetrieveSitesResponse, custom_search, path=["response"])

        assert cast(Any, response.is_closed) is True
