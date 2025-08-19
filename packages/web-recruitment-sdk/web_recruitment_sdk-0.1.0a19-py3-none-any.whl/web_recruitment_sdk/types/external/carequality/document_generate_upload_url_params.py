# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentGenerateUploadURLParams"]


class DocumentGenerateUploadURLParams(TypedDict, total=False):
    carequality_patient_id: Required[Annotated[str, PropertyInfo(alias="carequalityPatientId")]]
    """The encrypted CareQuality patient ID (format: encrypted(tenant:patient_id))"""

    content_type: Required[Annotated[str, PropertyInfo(alias="contentType")]]
    """The content type of the file (e.g., application/xml, application/pdf)"""

    file_md5_hash: Required[Annotated[str, PropertyInfo(alias="fileMd5Hash")]]
    """Base64-encoded MD5 hash of the file for integrity validation"""

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]
    """The name of the file to upload"""

    file_size_bytes: Required[Annotated[int, PropertyInfo(alias="fileSizeBytes")]]
    """The size of the file in bytes"""

    x_api_key: Required[Annotated[str, PropertyInfo(alias="X-API-Key")]]
