# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .run_status import RunStatus

__all__ = ["RunListResponse", "RunListResponseItem"]


class RunListResponseItem(BaseModel):
    id: str

    date_created: str

    date_modified: Optional[str] = None

    description: Optional[str] = None

    name: str

    run_folder: str

    run_number: int

    metadata_version: Optional[str] = None

    mlflow_experiment_id: Optional[str] = None

    mlflow_run_id: Optional[str] = None

    run_status: Optional[RunStatus] = None

    tags: Optional[List[str]] = None


RunListResponse: TypeAlias = List[RunListResponseItem]
