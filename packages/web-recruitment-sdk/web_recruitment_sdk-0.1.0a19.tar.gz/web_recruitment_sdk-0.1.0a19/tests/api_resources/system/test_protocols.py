# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import ProtocolRead
from web_recruitment_sdk.types.system import ProtocolListResponse, ProtocolGetCriteriaResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProtocols:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        protocol = client.system.protocols.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.with_raw_response.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.with_streaming_response.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.with_raw_response.retrieve(
                protocol_id="protocol_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `protocol_id` but received ''"):
            client.system.protocols.with_raw_response.retrieve(
                protocol_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        protocol = client.system.protocols.list(
            "tenant_db_name",
        )
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.with_raw_response.list(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.with_streaming_response.list(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_criteria(self, client: WebRecruitmentSDK) -> None:
        protocol = client.system.protocols.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_criteria(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.with_raw_response.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_criteria(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.with_streaming_response.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_criteria(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.with_raw_response.get_criteria(
                protocol_id="protocol_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `protocol_id` but received ''"):
            client.system.protocols.with_raw_response.get_criteria(
                protocol_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_refresh_patient_matches(self, client: WebRecruitmentSDK) -> None:
        protocol = client.system.protocols.refresh_patient_matches(
            "tenant_db_name",
        )
        assert_matches_type(object, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_refresh_patient_matches(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.with_raw_response.refresh_patient_matches(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(object, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_refresh_patient_matches(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.with_streaming_response.refresh_patient_matches(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(object, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_refresh_patient_matches(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.with_raw_response.refresh_patient_matches(
                "",
            )


class TestAsyncProtocols:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.system.protocols.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.with_raw_response.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolRead, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.with_streaming_response.retrieve(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolRead, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.with_raw_response.retrieve(
                protocol_id="protocol_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `protocol_id` but received ''"):
            await async_client.system.protocols.with_raw_response.retrieve(
                protocol_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.system.protocols.list(
            "tenant_db_name",
        )
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.with_raw_response.list(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.with_streaming_response.list(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_criteria(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.system.protocols.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_criteria(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.with_raw_response.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_criteria(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.with_streaming_response.get_criteria(
            protocol_id="protocol_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolGetCriteriaResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_criteria(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.with_raw_response.get_criteria(
                protocol_id="protocol_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `protocol_id` but received ''"):
            await async_client.system.protocols.with_raw_response.get_criteria(
                protocol_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_refresh_patient_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.system.protocols.refresh_patient_matches(
            "tenant_db_name",
        )
        assert_matches_type(object, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_refresh_patient_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.with_raw_response.refresh_patient_matches(
            "tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(object, protocol, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_refresh_patient_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.with_streaming_response.refresh_patient_matches(
            "tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(object, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_refresh_patient_matches(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.with_raw_response.refresh_patient_matches(
                "",
            )
