# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SaveFileResponse"]


class SaveFileResponse(BaseModel):
    success: bool

    message: Optional[str] = None
