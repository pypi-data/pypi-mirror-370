# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FileListDirectoryResponse", "Item"]


class Item(BaseModel):
    name: str

    path: str

    type: Literal["directory", "file"]

    last_modified: Optional[float] = None

    size: Optional[int] = None


class FileListDirectoryResponse(BaseModel):
    items: List[Item]

    total_count: int
