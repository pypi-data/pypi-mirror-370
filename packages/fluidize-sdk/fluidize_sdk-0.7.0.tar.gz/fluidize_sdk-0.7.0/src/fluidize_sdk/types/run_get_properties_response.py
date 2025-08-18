# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .run_status import RunStatus

__all__ = ["RunGetPropertiesResponse", "RunGetPropertiesResponseItem"]


class RunGetPropertiesResponseItem(BaseModel):
    container_image: str

    node_id: str
    """Node ID is always the folder name where this node exists"""

    output_path: str

    simulation_mount_path: str

    last_run: Optional[str] = None

    properties_version: Optional[str] = None

    run_status: Optional[RunStatus] = None

    should_run: Optional[bool] = None

    source_output_folder: Optional[str] = None

    version: Union[str, float, None] = None


RunGetPropertiesResponse: TypeAlias = List[RunGetPropertiesResponseItem]
