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
from ..types.hardware_list_response import HardwareListResponse

__all__ = ["HardwareResource", "AsyncHardwareResource"]


class HardwareResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> HardwareResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return HardwareResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> HardwareResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return HardwareResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HardwareListResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/hardware
        ```

        The response will be a JSON array of hardware objects:

        ```json
        [
          { "name": "CPU", "sku": "cpu" },
          { "name": "Nvidia T4 GPU", "sku": "gpu-t4" },
          { "name": "Nvidia A40 GPU", "sku": "gpu-a40-small" },
          { "name": "Nvidia A40 (Large) GPU", "sku": "gpu-a40-large" }
        ]
        ```
        """
        return self._get(
            "/hardware",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HardwareListResponse,
        )


class AsyncHardwareResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncHardwareResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncHardwareResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncHardwareResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncHardwareResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> HardwareListResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/hardware
        ```

        The response will be a JSON array of hardware objects:

        ```json
        [
          { "name": "CPU", "sku": "cpu" },
          { "name": "Nvidia T4 GPU", "sku": "gpu-t4" },
          { "name": "Nvidia A40 GPU", "sku": "gpu-a40-small" },
          { "name": "Nvidia A40 (Large) GPU", "sku": "gpu-a40-large" }
        ]
        ```
        """
        return await self._get(
            "/hardware",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=HardwareListResponse,
        )


class HardwareResourceWithRawResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.list = to_raw_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithRawResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.list = async_to_raw_response_wrapper(
            hardware.list,
        )


class HardwareResourceWithStreamingResponse:
    def __init__(self, hardware: HardwareResource) -> None:
        self._hardware = hardware

        self.list = to_streamed_response_wrapper(
            hardware.list,
        )


class AsyncHardwareResourceWithStreamingResponse:
    def __init__(self, hardware: AsyncHardwareResource) -> None:
        self._hardware = hardware

        self.list = async_to_streamed_response_wrapper(
            hardware.list,
        )
