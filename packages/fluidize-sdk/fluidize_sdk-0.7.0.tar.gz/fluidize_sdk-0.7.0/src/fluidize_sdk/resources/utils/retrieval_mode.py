# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.utils import retrieval_mode_update_params
from ..._base_client import make_request_options
from ...types.utils.retrieval_mode import RetrievalMode

__all__ = ["RetrievalModeResource", "AsyncRetrievalModeResource"]


class RetrievalModeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RetrievalModeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return RetrievalModeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RetrievalModeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return RetrievalModeResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalMode:
        """Get Retrieval Mode Endpoint"""
        return self._get(
            "/utils/retrieval_mode",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalMode,
        )

    def update(
        self,
        *,
        mode: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalMode:
        """
        Update the retrieval mode (local or cloud or cluster) Writes to a local file:
        app/retrieval_mode.json

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/utils/retrieval_mode",
            body=maybe_transform({"mode": mode}, retrieval_mode_update_params.RetrievalModeUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalMode,
        )


class AsyncRetrievalModeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRetrievalModeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncRetrievalModeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRetrievalModeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncRetrievalModeResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalMode:
        """Get Retrieval Mode Endpoint"""
        return await self._get(
            "/utils/retrieval_mode",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalMode,
        )

    async def update(
        self,
        *,
        mode: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RetrievalMode:
        """
        Update the retrieval mode (local or cloud or cluster) Writes to a local file:
        app/retrieval_mode.json

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/utils/retrieval_mode",
            body=await async_maybe_transform({"mode": mode}, retrieval_mode_update_params.RetrievalModeUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RetrievalMode,
        )


class RetrievalModeResourceWithRawResponse:
    def __init__(self, retrieval_mode: RetrievalModeResource) -> None:
        self._retrieval_mode = retrieval_mode

        self.retrieve = to_raw_response_wrapper(
            retrieval_mode.retrieve,
        )
        self.update = to_raw_response_wrapper(
            retrieval_mode.update,
        )


class AsyncRetrievalModeResourceWithRawResponse:
    def __init__(self, retrieval_mode: AsyncRetrievalModeResource) -> None:
        self._retrieval_mode = retrieval_mode

        self.retrieve = async_to_raw_response_wrapper(
            retrieval_mode.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            retrieval_mode.update,
        )


class RetrievalModeResourceWithStreamingResponse:
    def __init__(self, retrieval_mode: RetrievalModeResource) -> None:
        self._retrieval_mode = retrieval_mode

        self.retrieve = to_streamed_response_wrapper(
            retrieval_mode.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            retrieval_mode.update,
        )


class AsyncRetrievalModeResourceWithStreamingResponse:
    def __init__(self, retrieval_mode: AsyncRetrievalModeResource) -> None:
        self._retrieval_mode = retrieval_mode

        self.retrieve = async_to_streamed_response_wrapper(
            retrieval_mode.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            retrieval_mode.update,
        )
