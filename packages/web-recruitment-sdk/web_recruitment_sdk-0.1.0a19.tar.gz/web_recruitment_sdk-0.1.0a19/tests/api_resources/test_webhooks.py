# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import WebhookLogPayloadResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestWebhooks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_log_payload(self, client: WebRecruitmentSDK) -> None:
        webhook = client.webhooks.log_payload()
        assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_log_payload(self, client: WebRecruitmentSDK) -> None:
        response = client.webhooks.with_raw_response.log_payload()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = response.parse()
        assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_log_payload(self, client: WebRecruitmentSDK) -> None:
        with client.webhooks.with_streaming_response.log_payload() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = response.parse()
            assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncWebhooks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_log_payload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        webhook = await async_client.webhooks.log_payload()
        assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_log_payload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.webhooks.with_raw_response.log_payload()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        webhook = await response.parse()
        assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_log_payload(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.webhooks.with_streaming_response.log_payload() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            webhook = await response.parse()
            assert_matches_type(WebhookLogPayloadResponse, webhook, path=["response"])

        assert cast(Any, response.is_closed) is True
