# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SystemCreateEntitySearchIndexResponse"]


class SystemCreateEntitySearchIndexResponse(BaseModel):
    created: bool

    index_name: str = FieldInfo(alias="indexName")

    num_leaves: Optional[int] = FieldInfo(alias="numLeaves", default=None)

    recreated: bool

    table_rows: int = FieldInfo(alias="tableRows")

    tenant_db_name: str = FieldInfo(alias="tenantDbName")
