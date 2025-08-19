# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["FeatureFlagRetrieveResponse"]


class FeatureFlagRetrieveResponse(BaseModel):
    enabled: Optional[bool] = None

    value: Optional[str] = None
