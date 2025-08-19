# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["DocumentConfirmUploadParams"]


class DocumentConfirmUploadParams(TypedDict, total=False):
    webhook_data: Required[Annotated[object, PropertyInfo(alias="webhookData")]]

    webhook_type: Required[Annotated[Literal["carequality_document_uploaded"], PropertyInfo(alias="webhookType")]]
    """Types of webhooks."""
