# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.list_environment_list_response import ListEnvironmentListResponse

__all__ = ["ListEnvironmentsResource", "AsyncListEnvironmentsResource"]


class ListEnvironmentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ListEnvironmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ListEnvironmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ListEnvironmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return ListEnvironmentsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListEnvironmentListResponse:
        """List Environments"""
        return self._get(
            "/list_environments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListEnvironmentListResponse,
        )


class AsyncListEnvironmentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncListEnvironmentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncListEnvironmentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncListEnvironmentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncListEnvironmentsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ListEnvironmentListResponse:
        """List Environments"""
        return await self._get(
            "/list_environments",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ListEnvironmentListResponse,
        )


class ListEnvironmentsResourceWithRawResponse:
    def __init__(self, list_environments: ListEnvironmentsResource) -> None:
        self._list_environments = list_environments

        self.list = to_raw_response_wrapper(
            list_environments.list,
        )


class AsyncListEnvironmentsResourceWithRawResponse:
    def __init__(self, list_environments: AsyncListEnvironmentsResource) -> None:
        self._list_environments = list_environments

        self.list = async_to_raw_response_wrapper(
            list_environments.list,
        )


class ListEnvironmentsResourceWithStreamingResponse:
    def __init__(self, list_environments: ListEnvironmentsResource) -> None:
        self._list_environments = list_environments

        self.list = to_streamed_response_wrapper(
            list_environments.list,
        )


class AsyncListEnvironmentsResourceWithStreamingResponse:
    def __init__(self, list_environments: AsyncListEnvironmentsResource) -> None:
        self._list_environments = list_environments

        self.list = async_to_streamed_response_wrapper(
            list_environments.list,
        )
