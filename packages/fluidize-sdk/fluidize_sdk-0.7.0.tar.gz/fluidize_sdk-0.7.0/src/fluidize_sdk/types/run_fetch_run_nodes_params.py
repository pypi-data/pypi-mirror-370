# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RunFetchRunNodesParams"]


class RunFetchRunNodesParams(TypedDict, total=False):
    id: Required[str]

    description: str

    label: str

    location: str

    metadata_version: str

    status: str
