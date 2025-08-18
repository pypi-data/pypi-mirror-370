# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["ParameterParam", "Option"]


class Option(TypedDict, total=False):
    label: Required[str]

    value: Required[str]


class ParameterParam(TypedDict, total=False):
    description: Required[str]

    label: Required[str]

    name: Required[str]

    type: Required[str]

    value: Required[str]

    latex: Optional[str]

    location: Optional[List[str]]

    options: Optional[Iterable[Option]]

    scope: Optional[str]
