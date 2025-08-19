# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types import PatientRead
from web_recruitment_sdk._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
            cell_phone="cellPhone",
            do_not_call=True,
            home_phone="homePhone",
            is_interested_in_research=True,
            last_encounter_date=parse_date("2019-12-27"),
            last_patient_activity=parse_date("2019-12-27"),
            middle_name="middleName",
            phone="phone",
            preferred_language="ENGLISH",
            primary_provider="primaryProvider",
            provider_first_name="providerFirstName",
            provider_last_name="providerLastName",
            source="EHR",
            zip_code="zipCode",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.with_raw_response.create(
                tenant_db_name="",
                dob=parse_date("2019-12-27"),
                email="email",
                family_name="familyName",
                given_name="givenName",
                site_id=0,
                trially_patient_id="triallyPatientId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            client.system.patients.with_raw_response.update(
                patient_id=0,
                tenant_db_name="",
                do_not_call=True,
            )


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
            cell_phone="cellPhone",
            do_not_call=True,
            home_phone="homePhone",
            is_interested_in_research=True,
            last_encounter_date=parse_date("2019-12-27"),
            last_patient_activity=parse_date("2019-12-27"),
            middle_name="middleName",
            phone="phone",
            preferred_language="ENGLISH",
            primary_provider="primaryProvider",
            provider_first_name="providerFirstName",
            provider_last_name="providerLastName",
            source="EHR",
            zip_code="zipCode",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.create(
            tenant_db_name="tenant_db_name",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.with_raw_response.create(
                tenant_db_name="",
                dob=parse_date("2019-12-27"),
                email="email",
                family_name="familyName",
                given_name="givenName",
                site_id=0,
                trially_patient_id="triallyPatientId",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.update(
            patient_id=0,
            tenant_db_name="tenant_db_name",
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_db_name` but received ''"):
            await async_client.system.patients.with_raw_response.update(
                patient_id=0,
                tenant_db_name="",
                do_not_call=True,
            )
