# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["AuthSessionLoginResponse"]


class AuthSessionLoginResponse(BaseModel):
    email: str

    storage_bucket: str

    uid: str

    display_name: Optional[str] = None
