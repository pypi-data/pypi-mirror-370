# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["ListEnvironmentListResponse", "ListEnvironmentListResponseItem"]


class ListEnvironmentListResponseItem(BaseModel):
    id: str

    description: str

    gpu: bool

    languages: List[str]

    name: str

    version: str

    is_custom: Optional[bool] = None

    os: Optional[str] = None


ListEnvironmentListResponse: TypeAlias = List[ListEnvironmentListResponseItem]
