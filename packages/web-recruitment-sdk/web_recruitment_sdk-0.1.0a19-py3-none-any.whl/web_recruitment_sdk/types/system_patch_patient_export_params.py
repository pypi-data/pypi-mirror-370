# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .export_status import ExportStatus

__all__ = ["SystemPatchPatientExportParams"]


class SystemPatchPatientExportParams(TypedDict, total=False):
    tenant_db_name: Required[str]

    status: Required[ExportStatus]
