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
from ...types.auth import ssh_connect_params
from ..._base_client import make_request_options
from ...types.auth.ssh_connect_response import SSHConnectResponse

__all__ = ["SSHResource", "AsyncSSHResource"]


class SSHResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SSHResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SSHResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SSHResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return SSHResourceWithStreamingResponse(self)

    def connect(
        self,
        *,
        password: str,
        username: str,
        verification_code: str,
        host: str | NotGiven = NOT_GIVEN,
        port: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSHConnectResponse:
        """
        Establish an SSH connection to the cluster using username, password, and 2FA.
        This connection will be stored for subsequent operations.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/auth/ssh/connect",
            body=maybe_transform(
                {
                    "password": password,
                    "username": username,
                    "verification_code": verification_code,
                    "host": host,
                    "port": port,
                },
                ssh_connect_params.SSHConnectParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSHConnectResponse,
        )

    def disconnect(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Disconnect all persistent SSH connections."""
        return self._post(
            "/auth/ssh/disconnect",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Check if we have any active SSH connections."""
        return self._get(
            "/auth/ssh/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncSSHResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSSHResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSSHResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSSHResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Fluidize-Inc/fluidize-python-sdk#with_streaming_response
        """
        return AsyncSSHResourceWithStreamingResponse(self)

    async def connect(
        self,
        *,
        password: str,
        username: str,
        verification_code: str,
        host: str | NotGiven = NOT_GIVEN,
        port: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSHConnectResponse:
        """
        Establish an SSH connection to the cluster using username, password, and 2FA.
        This connection will be stored for subsequent operations.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/auth/ssh/connect",
            body=await async_maybe_transform(
                {
                    "password": password,
                    "username": username,
                    "verification_code": verification_code,
                    "host": host,
                    "port": port,
                },
                ssh_connect_params.SSHConnectParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSHConnectResponse,
        )

    async def disconnect(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Disconnect all persistent SSH connections."""
        return await self._post(
            "/auth/ssh/disconnect",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Check if we have any active SSH connections."""
        return await self._get(
            "/auth/ssh/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class SSHResourceWithRawResponse:
    def __init__(self, ssh: SSHResource) -> None:
        self._ssh = ssh

        self.connect = to_raw_response_wrapper(
            ssh.connect,
        )
        self.disconnect = to_raw_response_wrapper(
            ssh.disconnect,
        )
        self.status = to_raw_response_wrapper(
            ssh.status,
        )


class AsyncSSHResourceWithRawResponse:
    def __init__(self, ssh: AsyncSSHResource) -> None:
        self._ssh = ssh

        self.connect = async_to_raw_response_wrapper(
            ssh.connect,
        )
        self.disconnect = async_to_raw_response_wrapper(
            ssh.disconnect,
        )
        self.status = async_to_raw_response_wrapper(
            ssh.status,
        )


class SSHResourceWithStreamingResponse:
    def __init__(self, ssh: SSHResource) -> None:
        self._ssh = ssh

        self.connect = to_streamed_response_wrapper(
            ssh.connect,
        )
        self.disconnect = to_streamed_response_wrapper(
            ssh.disconnect,
        )
        self.status = to_streamed_response_wrapper(
            ssh.status,
        )


class AsyncSSHResourceWithStreamingResponse:
    def __init__(self, ssh: AsyncSSHResource) -> None:
        self._ssh = ssh

        self.connect = async_to_streamed_response_wrapper(
            ssh.connect,
        )
        self.disconnect = async_to_streamed_response_wrapper(
            ssh.disconnect,
        )
        self.status = async_to_streamed_response_wrapper(
            ssh.status,
        )
