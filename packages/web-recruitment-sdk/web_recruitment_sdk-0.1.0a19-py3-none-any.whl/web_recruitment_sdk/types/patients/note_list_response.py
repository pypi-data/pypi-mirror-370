# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .note_read import NoteRead

__all__ = ["NoteListResponse"]

NoteListResponse: TypeAlias = List[NoteRead]
