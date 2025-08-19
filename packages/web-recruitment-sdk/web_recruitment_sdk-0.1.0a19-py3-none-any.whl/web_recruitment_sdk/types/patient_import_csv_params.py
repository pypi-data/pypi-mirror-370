# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PatientImportCsvParams"]


class PatientImportCsvParams(TypedDict, total=False):
    fallback_zip_code: Required[Annotated[str, PropertyInfo(alias="fallbackZipCode")]]

    site_id: Required[Annotated[int, PropertyInfo(alias="siteId")]]

    storage_url: Required[Annotated[str, PropertyInfo(alias="storageUrl")]]
