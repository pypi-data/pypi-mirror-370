# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import OutreachTriggerCallResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOutreach:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_trigger_call(self, client: WebRecruitmentSDK) -> None:
        outreach = client.outreach.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        )
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_trigger_call_with_all_params(self, client: WebRecruitmentSDK) -> None:
        outreach = client.outreach.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {
                    "name": "name",
                    "summary": "summary",
                },
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
                "booking_url": "booking_url",
                "patient_campaign_id": 0,
                "task_id": 0,
            },
            conversation_flow="study_qualification",
        )
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_trigger_call(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.with_raw_response.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = response.parse()
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_trigger_call(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.with_streaming_response.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = response.parse()
            assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOutreach:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_trigger_call(self, async_client: AsyncWebRecruitmentSDK) -> None:
        outreach = await async_client.outreach.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        )
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_trigger_call_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        outreach = await async_client.outreach.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {
                    "name": "name",
                    "summary": "summary",
                },
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
                "booking_url": "booking_url",
                "patient_campaign_id": 0,
                "task_id": 0,
            },
            conversation_flow="study_qualification",
        )
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_trigger_call(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.with_raw_response.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outreach = await response.parse()
        assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_trigger_call(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.with_streaming_response.trigger_call(
            call_data={
                "from_phone_number": "from_phone_number",
                "site": {
                    "name": "name",
                    "provider_name": "provider_name",
                },
                "study": {"name": "name"},
                "to_person": {
                    "first_name": "first_name",
                    "last_name": "last_name",
                    "phone_number": "phone_number",
                },
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outreach = await response.parse()
            assert_matches_type(OutreachTriggerCallResponse, outreach, path=["response"])

        assert cast(Any, response.is_closed) is True
