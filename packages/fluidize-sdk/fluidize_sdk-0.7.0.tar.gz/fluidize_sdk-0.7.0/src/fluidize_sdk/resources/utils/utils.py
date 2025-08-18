# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .retrieval_mode import (
    RetrievalModeResource,
    AsyncRetrievalModeResource,
    RetrievalModeResourceWithRawResponse,
    AsyncRetrievalModeResourceWithRawResponse,
    RetrievalModeResourceWithStreamingResponse,
    AsyncRetrievalModeResourceWithStreamingResponse,
)

__all__ = ["UtilsResource", "AsyncUtilsResource"]


class UtilsResource(SyncAPIResource):
    @cached_property
    def retrieval_mode(self) -> RetrievalModeResource:
        return RetrievalModeResource(self._client)

    @cached_property
    def with_raw_response(self) -> UtilsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return UtilsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UtilsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return UtilsResourceWithStreamingResponse(self)


class AsyncUtilsResource(AsyncAPIResource):
    @cached_property
    def retrieval_mode(self) -> AsyncRetrievalModeResource:
        return AsyncRetrievalModeResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncUtilsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncUtilsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUtilsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncUtilsResourceWithStreamingResponse(self)


class UtilsResourceWithRawResponse:
    def __init__(self, utils: UtilsResource) -> None:
        self._utils = utils

    @cached_property
    def retrieval_mode(self) -> RetrievalModeResourceWithRawResponse:
        return RetrievalModeResourceWithRawResponse(self._utils.retrieval_mode)


class AsyncUtilsResourceWithRawResponse:
    def __init__(self, utils: AsyncUtilsResource) -> None:
        self._utils = utils

    @cached_property
    def retrieval_mode(self) -> AsyncRetrievalModeResourceWithRawResponse:
        return AsyncRetrievalModeResourceWithRawResponse(self._utils.retrieval_mode)


class UtilsResourceWithStreamingResponse:
    def __init__(self, utils: UtilsResource) -> None:
        self._utils = utils

    @cached_property
    def retrieval_mode(self) -> RetrievalModeResourceWithStreamingResponse:
        return RetrievalModeResourceWithStreamingResponse(self._utils.retrieval_mode)


class AsyncUtilsResourceWithStreamingResponse:
    def __init__(self, utils: AsyncUtilsResource) -> None:
        self._utils = utils

    @cached_property
    def retrieval_mode(self) -> AsyncRetrievalModeResourceWithStreamingResponse:
        return AsyncRetrievalModeResourceWithStreamingResponse(self._utils.retrieval_mode)
