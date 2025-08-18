# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional

import httpx

from ..types import (
    GraphNode,
    graph_sync_params,
    graph_retrieve_params,
    graph_delete_edge_params,
    graph_delete_node_params,
    graph_insert_node_params,
    graph_upsert_edge_params,
    graph_get_parameters_params,
    graph_set_parameters_params,
    graph_upsert_parameter_params,
    graph_update_node_position_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.parameter import Parameter
from ..types.graph_edge import GraphEdge
from ..types.graph_node import GraphNode
from ..types.parameter_param import ParameterParam
from ..types.graph_node_param import GraphNodeParam
from ..types.project_summary_param import ProjectSummaryParam
from ..types.graph_retrieve_response import GraphRetrieveResponse
from ..types.graph_get_parameters_response import GraphGetParametersResponse
from ..types.graph_set_parameters_response import GraphSetParametersResponse

__all__ = ["GraphResource", "AsyncGraphResource"]


class GraphResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GraphResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return GraphResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GraphResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return GraphResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphRetrieveResponse:
        """
        Instantiates a processor and gets the entire graph.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_retrieve_params.GraphRetrieveParams,
                ),
            ),
            cast_to=GraphRetrieveResponse,
        )

    def delete_edge(
        self,
        edge_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Instantiates a processor and deletes an edge.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not edge_id:
            raise ValueError(f"Expected a non-empty value for `edge_id` but received {edge_id!r}")
        return self._delete(
            f"/graph/delete_edge/{edge_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_delete_edge_params.GraphDeleteEdgeParams,
                ),
            ),
            cast_to=object,
        )

    def delete_node(
        self,
        node_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Instantiates a processor and deletes a node.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return self._delete(
            f"/graph/delete_node/{node_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_delete_node_params.GraphDeleteNodeParams,
                ),
            ),
            cast_to=object,
        )

    def get_parameters(
        self,
        node_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphGetParametersResponse:
        """
        Get Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return self._get(
            f"/graph/get_parameters/{node_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_get_parameters_params.GraphGetParametersParams,
                ),
            ),
            cast_to=GraphGetParametersResponse,
        )

    def insert_node(
        self,
        *,
        node: GraphNodeParam,
        project: ProjectSummaryParam,
        sim_global: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphNode:
        """
        Instantiates a processor and upserts a node.

        Args:
          node: A node in the graph.

              Attributes: id: Unique node ID. position: Node position. data: Extra metadata.
              type: Renderer/type key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/graph/insert_node",
            body=maybe_transform(
                {
                    "node": node,
                    "project": project,
                    "sim_global": sim_global,
                },
                graph_insert_node_params.GraphInsertNodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphNode,
        )

    def set_parameters(
        self,
        node_id: str,
        *,
        id: str,
        body: Iterable[ParameterParam],
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphSetParametersResponse:
        """
        Set Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return self._post(
            f"/graph/set_parameters/{node_id}",
            body=maybe_transform(body, Iterable[ParameterParam]),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_set_parameters_params.GraphSetParametersParams,
                ),
            ),
            cast_to=GraphSetParametersResponse,
        )

    def sync(
        self,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Sync all nodes from file system to Firestore.

        Treats file system as the source
        of truth and overwrites Firestore data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/graph/sync",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_sync_params.GraphSyncParams,
                ),
            ),
            cast_to=object,
        )

    def update_node_position(
        self,
        *,
        query_id: str,
        body_id: str,
        data: graph_update_node_position_params.Data,
        position: graph_update_node_position_params.Position,
        type: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphNode:
        """
        Instantiates a processor and updates a node's position.

        Args:
          data: Extra metadata for a node.

          position: Position of a node in layout space.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/graph/update_node_position",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "data": data,
                    "position": position,
                    "type": type,
                },
                graph_update_node_position_params.GraphUpdateNodePositionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "query_id": query_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_update_node_position_params.GraphUpdateNodePositionParams,
                ),
            ),
            cast_to=GraphNode,
        )

    def upsert_edge(
        self,
        *,
        query_id: str,
        body_id: str,
        source: str,
        target: str,
        type: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphEdge:
        """
        Instantiates a processor and upserts an edge.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/graph/upsert_edge",
            body=maybe_transform(
                {
                    "body_id": body_id,
                    "source": source,
                    "target": target,
                    "type": type,
                },
                graph_upsert_edge_params.GraphUpsertEdgeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "query_id": query_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_upsert_edge_params.GraphUpsertEdgeParams,
                ),
            ),
            cast_to=GraphEdge,
        )

    def upsert_parameter(
        self,
        path: str,
        *,
        description: str,
        label: str,
        name: str,
        type: str,
        value: str,
        latex: Optional[str] | NotGiven = NOT_GIVEN,
        location: Optional[List[str]] | NotGiven = NOT_GIVEN,
        options: Optional[Iterable[graph_upsert_parameter_params.Option]] | NotGiven = NOT_GIVEN,
        scope: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Parameter:
        """
        Upsert Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path:
            raise ValueError(f"Expected a non-empty value for `path` but received {path!r}")
        return self._post(
            f"/graph/upsert_parameter/{path}",
            body=maybe_transform(
                {
                    "description": description,
                    "label": label,
                    "name": name,
                    "type": type,
                    "value": value,
                    "latex": latex,
                    "location": location,
                    "options": options,
                    "scope": scope,
                },
                graph_upsert_parameter_params.GraphUpsertParameterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Parameter,
        )


class AsyncGraphResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGraphResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncGraphResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGraphResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncGraphResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphRetrieveResponse:
        """
        Instantiates a processor and gets the entire graph.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/graph",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_retrieve_params.GraphRetrieveParams,
                ),
            ),
            cast_to=GraphRetrieveResponse,
        )

    async def delete_edge(
        self,
        edge_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Instantiates a processor and deletes an edge.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not edge_id:
            raise ValueError(f"Expected a non-empty value for `edge_id` but received {edge_id!r}")
        return await self._delete(
            f"/graph/delete_edge/{edge_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_delete_edge_params.GraphDeleteEdgeParams,
                ),
            ),
            cast_to=object,
        )

    async def delete_node(
        self,
        node_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Instantiates a processor and deletes a node.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return await self._delete(
            f"/graph/delete_node/{node_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_delete_node_params.GraphDeleteNodeParams,
                ),
            ),
            cast_to=object,
        )

    async def get_parameters(
        self,
        node_id: str,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphGetParametersResponse:
        """
        Get Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return await self._get(
            f"/graph/get_parameters/{node_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_get_parameters_params.GraphGetParametersParams,
                ),
            ),
            cast_to=GraphGetParametersResponse,
        )

    async def insert_node(
        self,
        *,
        node: GraphNodeParam,
        project: ProjectSummaryParam,
        sim_global: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphNode:
        """
        Instantiates a processor and upserts a node.

        Args:
          node: A node in the graph.

              Attributes: id: Unique node ID. position: Node position. data: Extra metadata.
              type: Renderer/type key.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/graph/insert_node",
            body=await async_maybe_transform(
                {
                    "node": node,
                    "project": project,
                    "sim_global": sim_global,
                },
                graph_insert_node_params.GraphInsertNodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=GraphNode,
        )

    async def set_parameters(
        self,
        node_id: str,
        *,
        id: str,
        body: Iterable[ParameterParam],
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphSetParametersResponse:
        """
        Set Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not node_id:
            raise ValueError(f"Expected a non-empty value for `node_id` but received {node_id!r}")
        return await self._post(
            f"/graph/set_parameters/{node_id}",
            body=await async_maybe_transform(body, Iterable[ParameterParam]),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_set_parameters_params.GraphSetParametersParams,
                ),
            ),
            cast_to=GraphSetParametersResponse,
        )

    async def sync(
        self,
        *,
        id: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Sync all nodes from file system to Firestore.

        Treats file system as the source
        of truth and overwrites Firestore data.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/graph/sync",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "id": id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_sync_params.GraphSyncParams,
                ),
            ),
            cast_to=object,
        )

    async def update_node_position(
        self,
        *,
        query_id: str,
        body_id: str,
        data: graph_update_node_position_params.Data,
        position: graph_update_node_position_params.Position,
        type: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphNode:
        """
        Instantiates a processor and updates a node's position.

        Args:
          data: Extra metadata for a node.

          position: Position of a node in layout space.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/graph/update_node_position",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "data": data,
                    "position": position,
                    "type": type,
                },
                graph_update_node_position_params.GraphUpdateNodePositionParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "query_id": query_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_update_node_position_params.GraphUpdateNodePositionParams,
                ),
            ),
            cast_to=GraphNode,
        )

    async def upsert_edge(
        self,
        *,
        query_id: str,
        body_id: str,
        source: str,
        target: str,
        type: str,
        description: str | NotGiven = NOT_GIVEN,
        label: str | NotGiven = NOT_GIVEN,
        location: str | NotGiven = NOT_GIVEN,
        metadata_version: str | NotGiven = NOT_GIVEN,
        status: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GraphEdge:
        """
        Instantiates a processor and upserts an edge.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/graph/upsert_edge",
            body=await async_maybe_transform(
                {
                    "body_id": body_id,
                    "source": source,
                    "target": target,
                    "type": type,
                },
                graph_upsert_edge_params.GraphUpsertEdgeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "query_id": query_id,
                        "description": description,
                        "label": label,
                        "location": location,
                        "metadata_version": metadata_version,
                        "status": status,
                    },
                    graph_upsert_edge_params.GraphUpsertEdgeParams,
                ),
            ),
            cast_to=GraphEdge,
        )

    async def upsert_parameter(
        self,
        path: str,
        *,
        description: str,
        label: str,
        name: str,
        type: str,
        value: str,
        latex: Optional[str] | NotGiven = NOT_GIVEN,
        location: Optional[List[str]] | NotGiven = NOT_GIVEN,
        options: Optional[Iterable[graph_upsert_parameter_params.Option]] | NotGiven = NOT_GIVEN,
        scope: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Parameter:
        """
        Upsert Params

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path:
            raise ValueError(f"Expected a non-empty value for `path` but received {path!r}")
        return await self._post(
            f"/graph/upsert_parameter/{path}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "label": label,
                    "name": name,
                    "type": type,
                    "value": value,
                    "latex": latex,
                    "location": location,
                    "options": options,
                    "scope": scope,
                },
                graph_upsert_parameter_params.GraphUpsertParameterParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Parameter,
        )


class GraphResourceWithRawResponse:
    def __init__(self, graph: GraphResource) -> None:
        self._graph = graph

        self.retrieve = to_raw_response_wrapper(
            graph.retrieve,
        )
        self.delete_edge = to_raw_response_wrapper(
            graph.delete_edge,
        )
        self.delete_node = to_raw_response_wrapper(
            graph.delete_node,
        )
        self.get_parameters = to_raw_response_wrapper(
            graph.get_parameters,
        )
        self.insert_node = to_raw_response_wrapper(
            graph.insert_node,
        )
        self.set_parameters = to_raw_response_wrapper(
            graph.set_parameters,
        )
        self.sync = to_raw_response_wrapper(
            graph.sync,
        )
        self.update_node_position = to_raw_response_wrapper(
            graph.update_node_position,
        )
        self.upsert_edge = to_raw_response_wrapper(
            graph.upsert_edge,
        )
        self.upsert_parameter = to_raw_response_wrapper(
            graph.upsert_parameter,
        )


class AsyncGraphResourceWithRawResponse:
    def __init__(self, graph: AsyncGraphResource) -> None:
        self._graph = graph

        self.retrieve = async_to_raw_response_wrapper(
            graph.retrieve,
        )
        self.delete_edge = async_to_raw_response_wrapper(
            graph.delete_edge,
        )
        self.delete_node = async_to_raw_response_wrapper(
            graph.delete_node,
        )
        self.get_parameters = async_to_raw_response_wrapper(
            graph.get_parameters,
        )
        self.insert_node = async_to_raw_response_wrapper(
            graph.insert_node,
        )
        self.set_parameters = async_to_raw_response_wrapper(
            graph.set_parameters,
        )
        self.sync = async_to_raw_response_wrapper(
            graph.sync,
        )
        self.update_node_position = async_to_raw_response_wrapper(
            graph.update_node_position,
        )
        self.upsert_edge = async_to_raw_response_wrapper(
            graph.upsert_edge,
        )
        self.upsert_parameter = async_to_raw_response_wrapper(
            graph.upsert_parameter,
        )


class GraphResourceWithStreamingResponse:
    def __init__(self, graph: GraphResource) -> None:
        self._graph = graph

        self.retrieve = to_streamed_response_wrapper(
            graph.retrieve,
        )
        self.delete_edge = to_streamed_response_wrapper(
            graph.delete_edge,
        )
        self.delete_node = to_streamed_response_wrapper(
            graph.delete_node,
        )
        self.get_parameters = to_streamed_response_wrapper(
            graph.get_parameters,
        )
        self.insert_node = to_streamed_response_wrapper(
            graph.insert_node,
        )
        self.set_parameters = to_streamed_response_wrapper(
            graph.set_parameters,
        )
        self.sync = to_streamed_response_wrapper(
            graph.sync,
        )
        self.update_node_position = to_streamed_response_wrapper(
            graph.update_node_position,
        )
        self.upsert_edge = to_streamed_response_wrapper(
            graph.upsert_edge,
        )
        self.upsert_parameter = to_streamed_response_wrapper(
            graph.upsert_parameter,
        )


class AsyncGraphResourceWithStreamingResponse:
    def __init__(self, graph: AsyncGraphResource) -> None:
        self._graph = graph

        self.retrieve = async_to_streamed_response_wrapper(
            graph.retrieve,
        )
        self.delete_edge = async_to_streamed_response_wrapper(
            graph.delete_edge,
        )
        self.delete_node = async_to_streamed_response_wrapper(
            graph.delete_node,
        )
        self.get_parameters = async_to_streamed_response_wrapper(
            graph.get_parameters,
        )
        self.insert_node = async_to_streamed_response_wrapper(
            graph.insert_node,
        )
        self.set_parameters = async_to_streamed_response_wrapper(
            graph.set_parameters,
        )
        self.sync = async_to_streamed_response_wrapper(
            graph.sync,
        )
        self.update_node_position = async_to_streamed_response_wrapper(
            graph.update_node_position,
        )
        self.upsert_edge = async_to_streamed_response_wrapper(
            graph.upsert_edge,
        )
        self.upsert_parameter = async_to_streamed_response_wrapper(
            graph.upsert_parameter,
        )
