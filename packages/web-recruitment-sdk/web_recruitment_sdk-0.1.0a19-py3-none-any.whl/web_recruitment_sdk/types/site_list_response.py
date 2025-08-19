# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .site_read import SiteRead

__all__ = ["SiteListResponse"]

SiteListResponse: TypeAlias = List[SiteRead]
