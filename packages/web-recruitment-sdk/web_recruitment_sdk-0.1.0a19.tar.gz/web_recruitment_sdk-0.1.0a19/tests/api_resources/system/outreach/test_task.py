# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk._utils import parse_datetime
from web_recruitment_sdk.types.system.outreach import TaskStartHandlerResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTask:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start_handler(self, client: WebRecruitmentSDK) -> None:
        task = client.system.outreach.task.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start_handler(self, client: WebRecruitmentSDK) -> None:
        response = client.system.outreach.task.with_raw_response.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start_handler(self, client: WebRecruitmentSDK) -> None:
        with client.system.outreach.task.with_streaming_response.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_start_handler(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.outreach.task.with_raw_response.start_handler(
                tenant_db_name="",
                action_type="PHONE_CALL",
                booking_url="bookingUrl",
                outreach_task_id=0,
                patient_campaign_id=0,
                scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )


class TestAsyncTask:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start_handler(self, async_client: AsyncWebRecruitmentSDK) -> None:
        task = await async_client.system.outreach.task.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start_handler(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.outreach.task.with_raw_response.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start_handler(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.outreach.task.with_streaming_response.start_handler(
            tenant_db_name="tenant_db_name",
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            outreach_task_id=0,
            patient_campaign_id=0,
            scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(TaskStartHandlerResponse, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_start_handler(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.outreach.task.with_raw_response.start_handler(
                tenant_db_name="",
                action_type="PHONE_CALL",
                booking_url="bookingUrl",
                outreach_task_id=0,
                patient_campaign_id=0,
                scheduled_date=parse_datetime("2019-12-27T18:11:19.117Z"),
            )
