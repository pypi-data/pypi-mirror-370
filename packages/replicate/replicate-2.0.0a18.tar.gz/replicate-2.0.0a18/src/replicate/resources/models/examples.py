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
from ...pagination import SyncCursorURLPage, AsyncCursorURLPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.prediction import Prediction

__all__ = ["ExamplesResource", "AsyncExamplesResource"]


class ExamplesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExamplesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return ExamplesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExamplesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return ExamplesResourceWithStreamingResponse(self)

    def list(
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
    ) -> SyncCursorURLPage[Prediction]:
        """
        List
        [example predictions](https://replicate.com/docs/topics/models/publish-a-model#what-are-examples)
        made using the model. These are predictions that were saved by the model author
        as illustrative examples of the model's capabilities.

        If you want all the examples for a model, use this operation.

        If you just want the model's default example, you can use the
        [`models.get`](#models.get) operation instead, which includes a
        `default_example` object.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/examples
        ```

        The response will be a pagination object containing a list of example
        predictions:

        ```json
        {
          "next": "https://api.replicate.com/v1/models/replicate/hello-world/examples?cursor=...",
          "previous": "https://api.replicate.com/v1/models/replicate/hello-world/examples?cursor=...",
          "results": [...]
        }
        ```

        Each item in the `results` list is a [prediction object](#predictions.get).

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
        return self._get_api_list(
            f"/models/{model_owner}/{model_name}/examples",
            page=SyncCursorURLPage[Prediction],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=Prediction,
        )


class AsyncExamplesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExamplesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncExamplesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExamplesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncExamplesResourceWithStreamingResponse(self)

    def list(
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
    ) -> AsyncPaginator[Prediction, AsyncCursorURLPage[Prediction]]:
        """
        List
        [example predictions](https://replicate.com/docs/topics/models/publish-a-model#what-are-examples)
        made using the model. These are predictions that were saved by the model author
        as illustrative examples of the model's capabilities.

        If you want all the examples for a model, use this operation.

        If you just want the model's default example, you can use the
        [`models.get`](#models.get) operation instead, which includes a
        `default_example` object.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/examples
        ```

        The response will be a pagination object containing a list of example
        predictions:

        ```json
        {
          "next": "https://api.replicate.com/v1/models/replicate/hello-world/examples?cursor=...",
          "previous": "https://api.replicate.com/v1/models/replicate/hello-world/examples?cursor=...",
          "results": [...]
        }
        ```

        Each item in the `results` list is a [prediction object](#predictions.get).

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
        return self._get_api_list(
            f"/models/{model_owner}/{model_name}/examples",
            page=AsyncCursorURLPage[Prediction],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=Prediction,
        )


class ExamplesResourceWithRawResponse:
    def __init__(self, examples: ExamplesResource) -> None:
        self._examples = examples

        self.list = to_raw_response_wrapper(
            examples.list,
        )


class AsyncExamplesResourceWithRawResponse:
    def __init__(self, examples: AsyncExamplesResource) -> None:
        self._examples = examples

        self.list = async_to_raw_response_wrapper(
            examples.list,
        )


class ExamplesResourceWithStreamingResponse:
    def __init__(self, examples: ExamplesResource) -> None:
        self._examples = examples

        self.list = to_streamed_response_wrapper(
            examples.list,
        )


class AsyncExamplesResourceWithStreamingResponse:
    def __init__(self, examples: AsyncExamplesResource) -> None:
        self._examples = examples

        self.list = async_to_streamed_response_wrapper(
            examples.list,
        )
