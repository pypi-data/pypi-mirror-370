# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProtocolParsing:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_error(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.system.protocol_parsing.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_error_with_all_params(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.system.protocol_parsing.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            status_message="status_message",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_error(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocol_parsing.with_raw_response.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = response.parse()
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_error(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocol_parsing.with_streaming_response.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = response.parse()
            assert_matches_type(object, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set_error(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocol_parsing.with_raw_response.set_error(
                job_id="job_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.system.protocol_parsing.with_raw_response.set_error(
                job_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_set_success(self, client: WebRecruitmentSDK) -> None:
        protocol_parsing = client.system.protocol_parsing.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_set_success(self, client: WebRecruitmentSDK) -> None:
        response = client.system.protocol_parsing.with_raw_response.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = response.parse()
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_set_success(self, client: WebRecruitmentSDK) -> None:
        with client.system.protocol_parsing.with_streaming_response.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = response.parse()
            assert_matches_type(object, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_set_success(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.protocol_parsing.with_raw_response.set_success(
                job_id="job_id",
                tenant_db_name="",
                criteria_create=[
                    {
                        "summary": "summary",
                        "type": "inclusion",
                    }
                ],
                external_protocol_id="external_protocol_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            client.system.protocol_parsing.with_raw_response.set_success(
                job_id="",
                tenant_db_name="tenant_db_name",
                criteria_create=[
                    {
                        "summary": "summary",
                        "type": "inclusion",
                    }
                ],
                external_protocol_id="external_protocol_id",
            )


class TestAsyncProtocolParsing:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_error(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.system.protocol_parsing.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_error_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.system.protocol_parsing.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            status_message="status_message",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_error(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocol_parsing.with_raw_response.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = await response.parse()
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_error(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocol_parsing.with_streaming_response.set_error(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = await response.parse()
            assert_matches_type(object, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set_error(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocol_parsing.with_raw_response.set_error(
                job_id="job_id",
                tenant_db_name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.system.protocol_parsing.with_raw_response.set_error(
                job_id="",
                tenant_db_name="tenant_db_name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_set_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol_parsing = await async_client.system.protocol_parsing.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        )
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_set_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.protocol_parsing.with_raw_response.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol_parsing = await response.parse()
        assert_matches_type(object, protocol_parsing, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_set_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.protocol_parsing.with_streaming_response.set_success(
            job_id="job_id",
            tenant_db_name="tenant_db_name",
            criteria_create=[
                {
                    "summary": "summary",
                    "type": "inclusion",
                }
            ],
            external_protocol_id="external_protocol_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol_parsing = await response.parse()
            assert_matches_type(object, protocol_parsing, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_set_success(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.protocol_parsing.with_raw_response.set_success(
                job_id="job_id",
                tenant_db_name="",
                criteria_create=[
                    {
                        "summary": "summary",
                        "type": "inclusion",
                    }
                ],
                external_protocol_id="external_protocol_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `job_id` but received ''"):
            await async_client.system.protocol_parsing.with_raw_response.set_success(
                job_id="",
                tenant_db_name="tenant_db_name",
                criteria_create=[
                    {
                        "summary": "summary",
                        "type": "inclusion",
                    }
                ],
                external_protocol_id="external_protocol_id",
            )
