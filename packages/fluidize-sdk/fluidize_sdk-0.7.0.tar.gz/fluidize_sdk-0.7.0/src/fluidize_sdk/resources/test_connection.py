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
from ..types.test_connection_check_response import TestConnectionCheckResponse

__all__ = ["TestConnectionResource", "AsyncTestConnectionResource"]


class TestConnectionResource(SyncAPIResource):
    __test__ = False

    @cached_property
    def with_raw_response(self) -> TestConnectionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return TestConnectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TestConnectionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return TestConnectionResourceWithStreamingResponse(self)

    def check(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestConnectionCheckResponse:
        """Read Root"""
        return self._get(
            "/test-connection",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestConnectionCheckResponse,
        )


class AsyncTestConnectionResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTestConnectionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTestConnectionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTestConnectionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncTestConnectionResourceWithStreamingResponse(self)

    async def check(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TestConnectionCheckResponse:
        """Read Root"""
        return await self._get(
            "/test-connection",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TestConnectionCheckResponse,
        )


class TestConnectionResourceWithRawResponse:
    __test__ = False

    def __init__(self, test_connection: TestConnectionResource) -> None:
        self._test_connection = test_connection

        self.check = to_raw_response_wrapper(
            test_connection.check,
        )


class AsyncTestConnectionResourceWithRawResponse:
    def __init__(self, test_connection: AsyncTestConnectionResource) -> None:
        self._test_connection = test_connection

        self.check = async_to_raw_response_wrapper(
            test_connection.check,
        )


class TestConnectionResourceWithStreamingResponse:
    __test__ = False

    def __init__(self, test_connection: TestConnectionResource) -> None:
        self._test_connection = test_connection

        self.check = to_streamed_response_wrapper(
            test_connection.check,
        )


class AsyncTestConnectionResourceWithStreamingResponse:
    def __init__(self, test_connection: AsyncTestConnectionResource) -> None:
        self._test_connection = test_connection

        self.check = async_to_streamed_response_wrapper(
            test_connection.check,
        )
