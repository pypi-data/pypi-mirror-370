# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["GraphNodeParam", "Data", "Position"]


class Data(TypedDict, total=False):
    label: Required[str]

    simulation_id: Optional[str]


class Position(TypedDict, total=False):
    x: Required[float]

    y: Required[float]


class GraphNodeParam(TypedDict, total=False):
    id: Required[str]

    data: Required[Data]
    """Extra metadata for a node."""

    position: Required[Position]
    """Position of a node in layout space."""

    type: Required[str]
