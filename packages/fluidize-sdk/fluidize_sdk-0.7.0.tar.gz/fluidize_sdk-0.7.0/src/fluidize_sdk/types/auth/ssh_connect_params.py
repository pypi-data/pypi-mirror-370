# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SSHConnectParams"]


class SSHConnectParams(TypedDict, total=False):
    password: Required[str]

    username: Required[str]

    verification_code: Required[str]

    host: str

    port: int
