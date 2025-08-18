# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ProjectSummary"]


class ProjectSummary(BaseModel):
    id: str

    description: Optional[str] = None

    label: Optional[str] = None

    location: Optional[str] = None

    metadata_version: Optional[str] = None

    status: Optional[str] = None
