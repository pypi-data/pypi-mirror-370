# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Required, TypedDict

from .project_summary_param import ProjectSummaryParam

__all__ = ["RunRunFlowParams", "Payload"]


class RunRunFlowParams(TypedDict, total=False):
    payload: Required[Payload]

    project: Required[ProjectSummaryParam]


class Payload(TypedDict, total=False):
    description: Optional[str]

    name: Optional[str]

    tags: Optional[List[str]]
