# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .secret import (
    SecretResource,
    AsyncSecretResource,
    SecretResourceWithRawResponse,
    AsyncSecretResourceWithRawResponse,
    SecretResourceWithStreamingResponse,
    AsyncSecretResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["DefaultResource", "AsyncDefaultResource"]


class DefaultResource(SyncAPIResource):
    @cached_property
    def secret(self) -> SecretResource:
        return SecretResource(self._client)

    @cached_property
    def with_raw_response(self) -> DefaultResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return DefaultResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DefaultResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return DefaultResourceWithStreamingResponse(self)


class AsyncDefaultResource(AsyncAPIResource):
    @cached_property
    def secret(self) -> AsyncSecretResource:
        return AsyncSecretResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDefaultResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncDefaultResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDefaultResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncDefaultResourceWithStreamingResponse(self)


class DefaultResourceWithRawResponse:
    def __init__(self, default: DefaultResource) -> None:
        self._default = default

    @cached_property
    def secret(self) -> SecretResourceWithRawResponse:
        return SecretResourceWithRawResponse(self._default.secret)


class AsyncDefaultResourceWithRawResponse:
    def __init__(self, default: AsyncDefaultResource) -> None:
        self._default = default

    @cached_property
    def secret(self) -> AsyncSecretResourceWithRawResponse:
        return AsyncSecretResourceWithRawResponse(self._default.secret)


class DefaultResourceWithStreamingResponse:
    def __init__(self, default: DefaultResource) -> None:
        self._default = default

    @cached_property
    def secret(self) -> SecretResourceWithStreamingResponse:
        return SecretResourceWithStreamingResponse(self._default.secret)


class AsyncDefaultResourceWithStreamingResponse:
    def __init__(self, default: AsyncDefaultResource) -> None:
        self._default = default

    @cached_property
    def secret(self) -> AsyncSecretResourceWithStreamingResponse:
        return AsyncSecretResourceWithStreamingResponse(self._default.secret)
