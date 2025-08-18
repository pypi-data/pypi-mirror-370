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

__all__ = ["CandyResource", "AsyncCandyResource"]


class CandyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CandyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return CandyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CandyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return CandyResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Read Candy"""
        return self._get(
            "/candy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncCandyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCandyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCandyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCandyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncCandyResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Read Candy"""
        return await self._get(
            "/candy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class CandyResourceWithRawResponse:
    def __init__(self, candy: CandyResource) -> None:
        self._candy = candy

        self.list = to_raw_response_wrapper(
            candy.list,
        )


class AsyncCandyResourceWithRawResponse:
    def __init__(self, candy: AsyncCandyResource) -> None:
        self._candy = candy

        self.list = async_to_raw_response_wrapper(
            candy.list,
        )


class CandyResourceWithStreamingResponse:
    def __init__(self, candy: CandyResource) -> None:
        self._candy = candy

        self.list = to_streamed_response_wrapper(
            candy.list,
        )


class AsyncCandyResourceWithStreamingResponse:
    def __init__(self, candy: AsyncCandyResource) -> None:
        self._candy = candy

        self.list = async_to_streamed_response_wrapper(
            candy.list,
        )
