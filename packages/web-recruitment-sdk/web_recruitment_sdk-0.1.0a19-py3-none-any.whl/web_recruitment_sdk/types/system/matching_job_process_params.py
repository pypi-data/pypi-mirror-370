# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["MatchingJobProcessParams"]


class MatchingJobProcessParams(TypedDict, total=False):
    job_id: Required[Annotated[int, PropertyInfo(alias="jobId")]]

    task_name: Required[Annotated[str, PropertyInfo(alias="taskName")]]
    """The name of the task"""

    body_tenant_db_name: Required[Annotated[str, PropertyInfo(alias="tenantDbName")]]
