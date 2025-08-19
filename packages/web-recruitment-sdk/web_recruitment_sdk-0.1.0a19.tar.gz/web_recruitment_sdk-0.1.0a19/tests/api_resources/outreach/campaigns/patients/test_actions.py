# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.outreach.campaigns.patients import (
    ActionListResponse,
    ActionCreateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestActions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_1(self, client: WebRecruitmentSDK) -> None:
        action = client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: WebRecruitmentSDK) -> None:
        action = client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
            previous_action_id=0,
            transcript_url="transcriptUrl",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_1(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.patients.actions.with_raw_response.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_1(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.patients.actions.with_streaming_response.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionCreateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_overload_1(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            client.outreach.campaigns.patients.actions.with_raw_response.create(
                patient_id="",
                campaign_id=0,
                caller_phone_number="callerPhoneNumber",
                duration_seconds=0,
                recipient_phone_number="recipientPhoneNumber",
                status="NO_ANSWER",
                task_id=0,
                type="PHONE_CALL",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_overload_2(self, client: WebRecruitmentSDK) -> None:
        action = client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: WebRecruitmentSDK) -> None:
        action = client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
            previous_action_id=0,
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_overload_2(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.patients.actions.with_raw_response.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_overload_2(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.patients.actions.with_streaming_response.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionCreateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_overload_2(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            client.outreach.campaigns.patients.actions.with_raw_response.create(
                patient_id="",
                campaign_id=0,
                message="message",
                recipient_phone_number="recipientPhoneNumber",
                sender_phone_number="senderPhoneNumber",
                status="SENT",
                task_id=0,
                type="SMS",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        action = client.outreach.campaigns.patients.actions.list(
            patient_id="patient_id",
            campaign_id=0,
        )
        assert_matches_type(ActionListResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.patients.actions.with_raw_response.list(
            patient_id="patient_id",
            campaign_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionListResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.patients.actions.with_streaming_response.list(
            patient_id="patient_id",
            campaign_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionListResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            client.outreach.campaigns.patients.actions.with_raw_response.list(
                patient_id="",
                campaign_id=0,
            )


class TestAsyncActions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        action = await async_client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        action = await async_client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
            previous_action_id=0,
            transcript_url="transcriptUrl",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.patients.actions.with_raw_response.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.patients.actions.with_streaming_response.create(
            patient_id="patient_id",
            campaign_id=0,
            caller_phone_number="callerPhoneNumber",
            duration_seconds=0,
            recipient_phone_number="recipientPhoneNumber",
            status="NO_ANSWER",
            task_id=0,
            type="PHONE_CALL",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionCreateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            await async_client.outreach.campaigns.patients.actions.with_raw_response.create(
                patient_id="",
                campaign_id=0,
                caller_phone_number="callerPhoneNumber",
                duration_seconds=0,
                recipient_phone_number="recipientPhoneNumber",
                status="NO_ANSWER",
                task_id=0,
                type="PHONE_CALL",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        action = await async_client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        action = await async_client.outreach.campaigns.patients.actions.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
            previous_action_id=0,
        )
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.patients.actions.with_raw_response.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionCreateResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.patients.actions.with_streaming_response.create(
            patient_id="patient_id",
            campaign_id=0,
            message="message",
            recipient_phone_number="recipientPhoneNumber",
            sender_phone_number="senderPhoneNumber",
            status="SENT",
            task_id=0,
            type="SMS",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionCreateResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            await async_client.outreach.campaigns.patients.actions.with_raw_response.create(
                patient_id="",
                campaign_id=0,
                message="message",
                recipient_phone_number="recipientPhoneNumber",
                sender_phone_number="senderPhoneNumber",
                status="SENT",
                task_id=0,
                type="SMS",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        action = await async_client.outreach.campaigns.patients.actions.list(
            patient_id="patient_id",
            campaign_id=0,
        )
        assert_matches_type(ActionListResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.patients.actions.with_raw_response.list(
            patient_id="patient_id",
            campaign_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionListResponse, action, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.patients.actions.with_streaming_response.list(
            patient_id="patient_id",
            campaign_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionListResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `patient_id` but received ''"):
            await async_client.outreach.campaigns.patients.actions.with_raw_response.list(
                patient_id="",
                campaign_id=0,
            )
