# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime
from typing import List, Optional

from .._models import BaseModel

__all__ = ["NodeMetadataSimulation", "Author", "Tag"]


class Author(BaseModel):
    institution: str

    name: str

    email: Optional[str] = None


class Tag(BaseModel):
    name: str

    color: Optional[str] = None

    description: Optional[str] = None

    icon: Optional[str] = None


class NodeMetadataSimulation(BaseModel):
    id: str

    authors: List[Author]

    date: Optional[datetime.date] = None

    description: str

    name: str

    tags: List[Tag]

    version: str

    code_url: Optional[str] = None

    metadata_version: Optional[str] = None

    mlflow_run_id: Optional[str] = None

    paper_url: Optional[str] = None
