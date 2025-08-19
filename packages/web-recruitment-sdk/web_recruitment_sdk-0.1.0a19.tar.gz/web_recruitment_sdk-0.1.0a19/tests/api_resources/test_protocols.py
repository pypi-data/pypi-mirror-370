# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import (
    FunnelStats,
    ProtocolRead,
    ProtocolParsingRead,
    ProtocolListResponse,
    ProtocolGetMatchesResponse,
    ProtocolGetCriteriaInstancesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProtocols:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.retrieve(
            0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.update(
            protocol_id=0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.update(
            protocol_id=0,
            external_protocol_id="externalProtocolId",
            sites=[
                {
                    "id": 0,
                    "recruiting": True,
                }
            ],
            status="parsing",
            title="title",
            version=0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.update(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.update(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.list()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.delete(
            0,
        )
        assert protocol is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert protocol is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert protocol is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_criteria_instances(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_funnel(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_funnel(
            protocol_id=0,
        )
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_funnel_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_funnel(
            protocol_id=0,
            matching_criteria_ids=[0],
            site_ids=[0],
        )
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_funnel(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.get_funnel(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_funnel(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.get_funnel(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(FunnelStats, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matches(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_matches(
            protocol_id=0,
        )
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_matches_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_matches(
            protocol_id=0,
            matching_criteria_ids=[0],
        )
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_matches(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.get_matches(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_matches(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.get_matches(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_parsing_status(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.get_parsing_status(
            0,
        )
        assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_parsing_status(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.get_parsing_status(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_parsing_status(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.get_parsing_status(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_ready(self, client: WebRecruitmentSDK) -> None:
        protocol = client.protocols.set_ready(
            0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_ready(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.with_raw_response.set_ready(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_ready(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.with_streaming_response.set_ready(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProtocols:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.retrieve(
            0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.update(
            protocol_id=0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.update(
            protocol_id=0,
            external_protocol_id="externalProtocolId",
            sites=[
                {
                    "id": 0,
                    "recruiting": True,
                }
            ],
            status="parsing",
            title="title",
            version=0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.update(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.update(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.list()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.delete(
            0,
        )
        assert protocol is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert protocol is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert protocol is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_criteria_instances(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.get_criteria_instances(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolGetCriteriaInstancesResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_funnel(
            protocol_id=0,
        )
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_funnel_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_funnel(
            protocol_id=0,
            matching_criteria_ids=[0],
            site_ids=[0],
        )
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.get_funnel(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(FunnelStats, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_funnel(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.get_funnel(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(FunnelStats, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_matches(
            protocol_id=0,
        )
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_matches_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_matches(
            protocol_id=0,
            matching_criteria_ids=[0],
        )
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.get_matches(
            protocol_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.get_matches(
            protocol_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolGetMatchesResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_parsing_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.get_parsing_status(
            0,
        )
        assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_parsing_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.get_parsing_status(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_parsing_status(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.get_parsing_status(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolParsingRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_ready(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.protocols.set_ready(
            0,
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_ready(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.with_raw_response.set_ready(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_ready(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.with_streaming_response.set_ready(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True
