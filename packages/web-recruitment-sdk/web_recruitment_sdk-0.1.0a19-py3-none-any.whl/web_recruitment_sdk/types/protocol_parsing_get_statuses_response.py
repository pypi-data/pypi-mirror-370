# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .protocol_parsing_read import ProtocolParsingRead

__all__ = ["ProtocolParsingGetStatusesResponse"]

ProtocolParsingGetStatusesResponse: TypeAlias = List[ProtocolParsingRead]
