# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .logs import (
    LogsResource,
    AsyncLogsResource,
    LogsResourceWithRawResponse,
    AsyncLogsResourceWithRawResponse,
    LogsResourceWithStreamingResponse,
    AsyncLogsResourceWithStreamingResponse,
)
from ...types import (
    run_list_params,
    run_run_flow_params,
    run_get_properties_params,
    run_fetch_run_nodes_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.run_list_response import RunListResponse
from ...types.project_summary_param import ProjectSummaryParam
from ...types.run_run_flow_response import RunRunFlowResponse
from ...types.run_get_properties_response import RunGetPropertiesResponse
from ...types.run_fetch_run_nodes_response import RunFetchRunNodesResponse

__all__ = ["RunsResource", "AsyncRunsResource"]


class RunsResource(SyncAPIResource):
    @cached_property
    def logs(self) -> LogsResource:
        return LogsResource(self._client)

    @cached_property
    def with_raw_response(self) -> RunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return RunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return RunsResourceWithStreamingResponse(self)

    def list(
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
    ) -> RunListResponse:
        """
        List Runs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/runs/list_runs",
            body=maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "label": label,
                    "location": location,
                    "metadata_version": metadata_version,
                    "status": status,
                },
                run_list_params.RunListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunListResponse,
        )

    def fetch_run_nodes(
        self,
        run_folder: str,
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
    ) -> RunFetchRunNodesResponse:
        """
        Fetch Nodes for a Given Run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_folder:
            raise ValueError(f"Expected a non-empty value for `run_folder` but received {run_folder!r}")
        return self._get(
            f"/runs/fetch_run_nodes/{run_folder}",
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
                    run_fetch_run_nodes_params.RunFetchRunNodesParams,
                ),
            ),
            cast_to=RunFetchRunNodesResponse,
        )

    def get_file(
        self,
        path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retrieve and stream a file from the specified path.

        Args: path: Path to the file relative to the storage root

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path:
            raise ValueError(f"Expected a non-empty value for `path` but received {path!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/runs/file/{path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_properties(
        self,
        run_folder: str,
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
    ) -> RunGetPropertiesResponse:
        """
        Get properties for a specific run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_folder:
            raise ValueError(f"Expected a non-empty value for `run_folder` but received {run_folder!r}")
        return self._get(
            f"/runs/get_runs_properties/{run_folder}",
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
                    run_get_properties_params.RunGetPropertiesParams,
                ),
            ),
            cast_to=RunGetPropertiesResponse,
        )

    def run_flow(
        self,
        *,
        payload: run_run_flow_params.Payload,
        project: ProjectSummaryParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRunFlowResponse:
        """
        Run Flow

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/runs/run_flow",
            body=maybe_transform(
                {
                    "payload": payload,
                    "project": project,
                },
                run_run_flow_params.RunRunFlowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRunFlowResponse,
        )


class AsyncRunsResource(AsyncAPIResource):
    @cached_property
    def logs(self) -> AsyncLogsResource:
        return AsyncLogsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncRunsResourceWithStreamingResponse(self)

    async def list(
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
    ) -> RunListResponse:
        """
        List Runs

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/runs/list_runs",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "description": description,
                    "label": label,
                    "location": location,
                    "metadata_version": metadata_version,
                    "status": status,
                },
                run_list_params.RunListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunListResponse,
        )

    async def fetch_run_nodes(
        self,
        run_folder: str,
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
    ) -> RunFetchRunNodesResponse:
        """
        Fetch Nodes for a Given Run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_folder:
            raise ValueError(f"Expected a non-empty value for `run_folder` but received {run_folder!r}")
        return await self._get(
            f"/runs/fetch_run_nodes/{run_folder}",
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
                    run_fetch_run_nodes_params.RunFetchRunNodesParams,
                ),
            ),
            cast_to=RunFetchRunNodesResponse,
        )

    async def get_file(
        self,
        path: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Retrieve and stream a file from the specified path.

        Args: path: Path to the file relative to the storage root

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path:
            raise ValueError(f"Expected a non-empty value for `path` but received {path!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/runs/file/{path}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_properties(
        self,
        run_folder: str,
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
    ) -> RunGetPropertiesResponse:
        """
        Get properties for a specific run.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not run_folder:
            raise ValueError(f"Expected a non-empty value for `run_folder` but received {run_folder!r}")
        return await self._get(
            f"/runs/get_runs_properties/{run_folder}",
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
                    run_get_properties_params.RunGetPropertiesParams,
                ),
            ),
            cast_to=RunGetPropertiesResponse,
        )

    async def run_flow(
        self,
        *,
        payload: run_run_flow_params.Payload,
        project: ProjectSummaryParam,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRunFlowResponse:
        """
        Run Flow

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/runs/run_flow",
            body=await async_maybe_transform(
                {
                    "payload": payload,
                    "project": project,
                },
                run_run_flow_params.RunRunFlowParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRunFlowResponse,
        )


class RunsResourceWithRawResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.list = to_raw_response_wrapper(
            runs.list,
        )
        self.fetch_run_nodes = to_raw_response_wrapper(
            runs.fetch_run_nodes,
        )
        self.get_file = to_raw_response_wrapper(
            runs.get_file,
        )
        self.get_properties = to_raw_response_wrapper(
            runs.get_properties,
        )
        self.run_flow = to_raw_response_wrapper(
            runs.run_flow,
        )

    @cached_property
    def logs(self) -> LogsResourceWithRawResponse:
        return LogsResourceWithRawResponse(self._runs.logs)


class AsyncRunsResourceWithRawResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.list = async_to_raw_response_wrapper(
            runs.list,
        )
        self.fetch_run_nodes = async_to_raw_response_wrapper(
            runs.fetch_run_nodes,
        )
        self.get_file = async_to_raw_response_wrapper(
            runs.get_file,
        )
        self.get_properties = async_to_raw_response_wrapper(
            runs.get_properties,
        )
        self.run_flow = async_to_raw_response_wrapper(
            runs.run_flow,
        )

    @cached_property
    def logs(self) -> AsyncLogsResourceWithRawResponse:
        return AsyncLogsResourceWithRawResponse(self._runs.logs)


class RunsResourceWithStreamingResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.list = to_streamed_response_wrapper(
            runs.list,
        )
        self.fetch_run_nodes = to_streamed_response_wrapper(
            runs.fetch_run_nodes,
        )
        self.get_file = to_streamed_response_wrapper(
            runs.get_file,
        )
        self.get_properties = to_streamed_response_wrapper(
            runs.get_properties,
        )
        self.run_flow = to_streamed_response_wrapper(
            runs.run_flow,
        )

    @cached_property
    def logs(self) -> LogsResourceWithStreamingResponse:
        return LogsResourceWithStreamingResponse(self._runs.logs)


class AsyncRunsResourceWithStreamingResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.list = async_to_streamed_response_wrapper(
            runs.list,
        )
        self.fetch_run_nodes = async_to_streamed_response_wrapper(
            runs.fetch_run_nodes,
        )
        self.get_file = async_to_streamed_response_wrapper(
            runs.get_file,
        )
        self.get_properties = async_to_streamed_response_wrapper(
            runs.get_properties,
        )
        self.run_flow = async_to_streamed_response_wrapper(
            runs.run_flow,
        )

    @cached_property
    def logs(self) -> AsyncLogsResourceWithStreamingResponse:
        return AsyncLogsResourceWithStreamingResponse(self._runs.logs)
