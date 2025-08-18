# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .graph_edge import GraphEdge
from .graph_node import GraphNode

__all__ = ["GraphRetrieveResponse"]


class GraphRetrieveResponse(BaseModel):
    edges: List[GraphEdge]

    nodes: List[GraphNode]
