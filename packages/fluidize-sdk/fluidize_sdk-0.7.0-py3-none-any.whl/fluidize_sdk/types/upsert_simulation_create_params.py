# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable
from typing_extensions import Required, TypedDict

__all__ = ["UpsertSimulationCreateParams", "EnvironmentVariable", "PackageManager"]


class UpsertSimulationCreateParams(TypedDict, total=False):
    container_image: Required[str]

    environment_variables: Required[Iterable[EnvironmentVariable]]

    name: Required[str]

    package_managers: Required[Iterable[PackageManager]]

    post_install_script: Required[str]


class EnvironmentVariable(TypedDict, total=False):
    key: Required[str]

    value: Required[str]


class PackageManager(TypedDict, total=False):
    name: Required[str]

    packages: Required[List[str]]

    version: Required[str]
