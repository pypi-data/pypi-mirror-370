# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk._utils import parse_date
from web_recruitment_sdk.types.outreach import (
    CampaignListResponse,
    CampaignPauseResponse,
    CampaignStartResponse,
    CampaignCreateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCampaigns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        campaign = client.outreach.campaigns.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        )
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        campaign = client.outreach.campaigns.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
            principal_investigator="principalInvestigator",
        )
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.with_raw_response.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = response.parse()
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.with_streaming_response.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = response.parse()
            assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        campaign = client.outreach.campaigns.list()
        assert_matches_type(CampaignListResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = response.parse()
        assert_matches_type(CampaignListResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = response.parse()
            assert_matches_type(CampaignListResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_pause(self, client: WebRecruitmentSDK) -> None:
        campaign = client.outreach.campaigns.pause(
            0,
        )
        assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_pause(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.with_raw_response.pause(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = response.parse()
        assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_pause(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.with_streaming_response.pause(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = response.parse()
            assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_start(self, client: WebRecruitmentSDK) -> None:
        campaign = client.outreach.campaigns.start(
            0,
        )
        assert_matches_type(CampaignStartResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_start(self, client: WebRecruitmentSDK) -> None:
        response = client.outreach.campaigns.with_raw_response.start(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = response.parse()
        assert_matches_type(CampaignStartResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_start(self, client: WebRecruitmentSDK) -> None:
        with client.outreach.campaigns.with_streaming_response.start(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = response.parse()
            assert_matches_type(CampaignStartResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCampaigns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        campaign = await async_client.outreach.campaigns.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        )
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        campaign = await async_client.outreach.campaigns.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
            principal_investigator="principalInvestigator",
        )
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.with_raw_response.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = await response.parse()
        assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.with_streaming_response.create(
            action_type="PHONE_CALL",
            booking_url="bookingUrl",
            end_date=parse_date("2019-12-27"),
            from_phone_number="fromPhoneNumber",
            hours_between_attempts=1,
            max_attempts_per_patient=1,
            name="name",
            outreach_hours_end=0,
            outreach_hours_start=0,
            patient_ids=["string"],
            start_date=parse_date("2019-12-27"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = await response.parse()
            assert_matches_type(CampaignCreateResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        campaign = await async_client.outreach.campaigns.list()
        assert_matches_type(CampaignListResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = await response.parse()
        assert_matches_type(CampaignListResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = await response.parse()
            assert_matches_type(CampaignListResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_pause(self, async_client: AsyncWebRecruitmentSDK) -> None:
        campaign = await async_client.outreach.campaigns.pause(
            0,
        )
        assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_pause(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.with_raw_response.pause(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = await response.parse()
        assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_pause(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.with_streaming_response.pause(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = await response.parse()
            assert_matches_type(CampaignPauseResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_start(self, async_client: AsyncWebRecruitmentSDK) -> None:
        campaign = await async_client.outreach.campaigns.start(
            0,
        )
        assert_matches_type(CampaignStartResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_start(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.outreach.campaigns.with_raw_response.start(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        campaign = await response.parse()
        assert_matches_type(CampaignStartResponse, campaign, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_start(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.outreach.campaigns.with_streaming_response.start(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            campaign = await response.parse()
            assert_matches_type(CampaignStartResponse, campaign, path=["response"])

        assert cast(Any, response.is_closed) is True
