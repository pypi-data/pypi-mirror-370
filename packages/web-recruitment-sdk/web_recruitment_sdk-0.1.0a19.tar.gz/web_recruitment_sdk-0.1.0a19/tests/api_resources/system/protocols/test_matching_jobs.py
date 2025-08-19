# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import ProtocolRead

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMatchingJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.protocols.matching_jobs.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.matching_jobs.with_raw_response.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(ProtocolRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.matching_jobs.with_streaming_response.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(ProtocolRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.matching_jobs.with_raw_response.create(
                protocol_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        matching_job = client.system.protocols.matching_jobs.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocols.matching_jobs.with_raw_response.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = response.parse()
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocols.matching_jobs.with_streaming_response.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = response.parse()
            assert_matches_type(object, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocols.matching_jobs.with_raw_response.delete(
                protocol_id=0,
                tenant_db_name="",
            )


class TestAsyncMatchingJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.protocols.matching_jobs.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(ProtocolRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.matching_jobs.with_raw_response.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(ProtocolRead, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.matching_jobs.with_streaming_response.create(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(ProtocolRead, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.matching_jobs.with_raw_response.create(
                protocol_id=0,
                tenant_db_name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        matching_job = await async_client.system.protocols.matching_jobs.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocols.matching_jobs.with_raw_response.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        matching_job = await response.parse()
        assert_matches_type(object, matching_job, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocols.matching_jobs.with_streaming_response.delete(
            protocol_id=0,
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            matching_job = await response.parse()
            assert_matches_type(object, matching_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocols.matching_jobs.with_raw_response.delete(
                protocol_id=0,
                tenant_db_name="",
            )
