# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["UpsertSimulationCreateResponse"]


class UpsertSimulationCreateResponse(BaseModel):
    redirect_url: str

    status: Literal["success", "error"]
