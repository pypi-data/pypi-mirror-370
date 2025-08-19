# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from ..site_read import SiteRead
from .matching_task_read import MatchingTaskRead
from .external_job_status import ExternalJobStatus
from ..custom_searches.criteria_read import CriteriaRead

__all__ = ["MatchingJobRead"]


class MatchingJobRead(BaseModel):
    id: int

    criteria_id: int = FieldInfo(alias="criteriaId")

    site_id: int = FieldInfo(alias="siteId")

    cancelled_at: Optional[datetime] = FieldInfo(alias="cancelledAt", default=None)

    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)

    criterion: Optional[CriteriaRead] = None

    job_trigger_task_name: Optional[str] = FieldInfo(alias="jobTriggerTaskName", default=None)

    site: Optional[SiteRead] = None

    status: Optional[ExternalJobStatus] = None
    """Enum for the status of an external job."""

    tasks: Optional[List[MatchingTaskRead]] = None

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
