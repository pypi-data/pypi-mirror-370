# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .project_summary import ProjectSummary

__all__ = ["ProjectListResponse"]

ProjectListResponse: TypeAlias = List[ProjectSummary]
