# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .graph_node_param import GraphNodeParam
from .project_summary_param import ProjectSummaryParam

__all__ = ["GraphInsertNodeParams"]


class GraphInsertNodeParams(TypedDict, total=False):
    node: Required[GraphNodeParam]
    """A node in the graph.

    Attributes: id: Unique node ID. position: Node position. data: Extra metadata.
    type: Renderer/type key.
    """

    project: Required[ProjectSummaryParam]

    sim_global: bool
