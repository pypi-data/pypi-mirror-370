# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["ReadmeResource", "AsyncReadmeResource"]


class ReadmeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReadmeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return ReadmeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReadmeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return ReadmeResourceWithStreamingResponse(self)

    def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the README content for a model.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/readme
        ```

        The response will be the README content as plain text in Markdown format:

        ```
        # Hello World Model

        This is an example model that...
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._get(
            f"/models/{model_owner}/{model_name}/readme",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class AsyncReadmeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReadmeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncReadmeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReadmeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncReadmeResourceWithStreamingResponse(self)

    async def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the README content for a model.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/readme
        ```

        The response will be the README content as plain text in Markdown format:

        ```
        # Hello World Model

        This is an example model that...
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not model_owner:
            raise ValueError(f"Expected a non-empty value for `model_owner` but received {model_owner!r}")
        if not model_name:
            raise ValueError(f"Expected a non-empty value for `model_name` but received {model_name!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._get(
            f"/models/{model_owner}/{model_name}/readme",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class ReadmeResourceWithRawResponse:
    def __init__(self, readme: ReadmeResource) -> None:
        self._readme = readme

        self.get = to_raw_response_wrapper(
            readme.get,
        )


class AsyncReadmeResourceWithRawResponse:
    def __init__(self, readme: AsyncReadmeResource) -> None:
        self._readme = readme

        self.get = async_to_raw_response_wrapper(
            readme.get,
        )


class ReadmeResourceWithStreamingResponse:
    def __init__(self, readme: ReadmeResource) -> None:
        self._readme = readme

        self.get = to_streamed_response_wrapper(
            readme.get,
        )


class AsyncReadmeResourceWithStreamingResponse:
    def __init__(self, readme: AsyncReadmeResource) -> None:
        self._readme = readme

        self.get = async_to_streamed_response_wrapper(
            readme.get,
        )
