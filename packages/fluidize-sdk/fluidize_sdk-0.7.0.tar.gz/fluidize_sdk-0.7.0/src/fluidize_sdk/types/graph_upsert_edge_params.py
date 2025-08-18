# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["GraphUpsertEdgeParams"]


class GraphUpsertEdgeParams(TypedDict, total=False):
    query_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    body_id: Required[Annotated[str, PropertyInfo(alias="id")]]

    source: Required[str]

    target: Required[str]

    type: Required[str]

    description: str

    label: str

    location: str

    metadata_version: str

    status: str
