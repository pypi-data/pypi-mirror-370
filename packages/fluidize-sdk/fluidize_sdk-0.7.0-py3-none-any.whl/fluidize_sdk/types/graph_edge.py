# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["GraphEdge"]


class GraphEdge(BaseModel):
    id: str

    source: str

    target: str

    type: str
