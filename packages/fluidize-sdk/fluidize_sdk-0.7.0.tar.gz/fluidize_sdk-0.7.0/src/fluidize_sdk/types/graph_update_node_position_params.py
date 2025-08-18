# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GraphUpdateNodePositionParams", "Data", "Position"]


class GraphUpdateNodePositionParams(TypedDict, total=False):
    query_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    body_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    data: Required[Data]
    """Extra metadata for a node."""

    position: Required[Position]
    """Position of a node in layout space."""

    type: Required[str]

    description: str

    label: str

    location: str

    metadata_version: str

    status: str


class Data(TypedDict, total=False):
    label: Required[str]

    simulation_id: Optional[str]


class Position(TypedDict, total=False):
    x: Required[float]

    y: Required[float]
