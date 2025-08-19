# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["BulkInsertResult"]


class BulkInsertResult(BaseModel):
    requested_count: int

    updated_count: int
