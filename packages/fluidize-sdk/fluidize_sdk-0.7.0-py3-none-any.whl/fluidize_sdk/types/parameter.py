# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["Parameter", "Option"]


class Option(BaseModel):
    label: str

    value: str


class Parameter(BaseModel):
    description: str

    label: str

    name: str

    type: str

    value: str

    latex: Optional[str] = None

    location: Optional[List[str]] = None

    options: Optional[List[Option]] = None

    scope: Optional[str] = None
