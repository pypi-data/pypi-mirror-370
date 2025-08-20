# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .default.default import (
    DefaultResource,
    AsyncDefaultResource,
    DefaultResourceWithRawResponse,
    AsyncDefaultResourceWithRawResponse,
    DefaultResourceWithStreamingResponse,
    AsyncDefaultResourceWithStreamingResponse,
)

__all__ = ["WebhooksResource", "AsyncWebhooksResource"]


class WebhooksResource(SyncAPIResource):
    @cached_property
    def default(self) -> DefaultResource:
        return DefaultResource(self._client)

    @cached_property
    def with_raw_response(self) -> WebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return WebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> WebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return WebhooksResourceWithStreamingResponse(self)


class AsyncWebhooksResource(AsyncAPIResource):
    @cached_property
    def default(self) -> AsyncDefaultResource:
        return AsyncDefaultResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncWebhooksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncWebhooksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncWebhooksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncWebhooksResourceWithStreamingResponse(self)


class WebhooksResourceWithRawResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

    @cached_property
    def default(self) -> DefaultResourceWithRawResponse:
        return DefaultResourceWithRawResponse(self._webhooks.default)


class AsyncWebhooksResourceWithRawResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

    @cached_property
    def default(self) -> AsyncDefaultResourceWithRawResponse:
        return AsyncDefaultResourceWithRawResponse(self._webhooks.default)


class WebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: WebhooksResource) -> None:
        self._webhooks = webhooks

    @cached_property
    def default(self) -> DefaultResourceWithStreamingResponse:
        return DefaultResourceWithStreamingResponse(self._webhooks.default)


class AsyncWebhooksResourceWithStreamingResponse:
    def __init__(self, webhooks: AsyncWebhooksResource) -> None:
        self._webhooks = webhooks

    @cached_property
    def default(self) -> AsyncDefaultResourceWithStreamingResponse:
        return AsyncDefaultResourceWithStreamingResponse(self._webhooks.default)
