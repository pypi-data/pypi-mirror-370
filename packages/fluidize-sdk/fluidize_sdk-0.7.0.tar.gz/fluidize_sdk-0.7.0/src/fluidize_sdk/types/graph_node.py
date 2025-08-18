# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["GraphNode", "Data", "Position"]


class Data(BaseModel):
    label: str

    simulation_id: Optional[str] = None


class Position(BaseModel):
    x: float

    y: float


class GraphNode(BaseModel):
    id: str

    data: Data
    """Extra metadata for a node."""

    position: Position
    """Position of a node in layout space."""

    type: str
