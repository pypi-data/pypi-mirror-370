# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .parameter_param import ParameterParam

__all__ = ["GraphSetParametersParams"]


class GraphSetParametersParams(TypedDict, total=False):
    id: Required[str]

    body: Required[Iterable[ParameterParam]]

    description: str

    label: str

    location: str

    metadata_version: str

    status: str
