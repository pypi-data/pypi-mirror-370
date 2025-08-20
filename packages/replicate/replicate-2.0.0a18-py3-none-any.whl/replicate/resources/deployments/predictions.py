# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, strip_not_given, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.prediction import Prediction
from ...types.deployments import prediction_create_params

__all__ = ["PredictionsResource", "AsyncPredictionsResource"]


class PredictionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PredictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return PredictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PredictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return PredictionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        input: object,
        stream: bool | NotGiven = NOT_GIVEN,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        prefer: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Create a prediction for the deployment and inputs you provide.

        Example cURL request:

        ```console
        curl -s -X POST -H 'Prefer: wait' \\
          -d '{"input": {"prompt": "A photo of a bear riding a bicycle over the moon"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator/predictions
        ```

        The request will wait up to 60 seconds for the model to run. If this time is
        exceeded the prediction will be returned in a `"starting"` state and need to be
        retrieved using the `predictions.get` endpiont.

        For a complete overview of the `deployments.predictions.create` API check out
        our documentation on
        [creating a prediction](https://replicate.com/docs/topics/predictions/create-a-prediction)
        which covers a variety of use cases.

        Args:
          input: The model's input as a JSON object. The input schema depends on what model you
              are running. To see the available inputs, click the "API" tab on the model you
              are running or [get the model version](#models.versions.get) and look at its
              `openapi_schema` property. For example,
              [stability-ai/sdxl](https://replicate.com/stability-ai/sdxl) takes `prompt` as
              an input.

              Files should be passed as HTTP URLs or data URLs.

              Use an HTTP URL when:

              - you have a large file > 256kb
              - you want to be able to use the file multiple times
              - you want your prediction metadata to be associable with your input files

              Use a data URL when:

              - you have a small file <= 256kb
              - you don't want to upload and host the file somewhere
              - you don't need to use the file again (Replicate will not store it)

          stream: **This field is deprecated.**

              Request a URL to receive streaming output using
              [server-sent events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events).

              This field is no longer needed as the returned prediction will always have a
              `stream` entry in its `url` property if the model supports streaming.

          webhook: An HTTPS URL for receiving a webhook when the prediction has new output. The
              webhook will be a POST request where the request body is the same as the
              response body of the [get prediction](#predictions.get) operation. If there are
              network problems, we will retry the webhook a few times, so make sure it can be
              safely called more than once. Replicate will not follow redirects when sending
              webhook requests to your service, so be sure to specify a URL that will resolve
              without redirecting.

          webhook_events_filter: By default, we will send requests to your webhook URL whenever there are new
              outputs or the prediction has finished. You can change which events trigger
              webhook requests by specifying `webhook_events_filter` in the prediction
              request:

              - `start`: immediately on prediction start
              - `output`: each time a prediction generates an output (note that predictions
                can generate multiple outputs)
              - `logs`: each time log output is generated by a prediction
              - `completed`: when the prediction reaches a terminal state
                (succeeded/canceled/failed)

              For example, if you only wanted requests to be sent at the start and end of the
              prediction, you would provide:

              ```json
              {
                "input": {
                  "text": "Alice"
                },
                "webhook": "https://example.com/my-webhook",
                "webhook_events_filter": ["start", "completed"]
              }
              ```

              Requests for event types `output` and `logs` will be sent at most once every
              500ms. If you request `start` and `completed` webhooks, then they'll always be
              sent regardless of throttling.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        extra_headers = {**strip_not_given({"Prefer": prefer}), **(extra_headers or {})}
        return self._post(
            f"/deployments/{deployment_owner}/{deployment_name}/predictions",
            body=maybe_transform(
                {
                    "input": input,
                    "stream": stream,
                    "webhook": webhook,
                    "webhook_events_filter": webhook_events_filter,
                },
                prediction_create_params.PredictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Prediction,
        )


class AsyncPredictionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPredictionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncPredictionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPredictionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncPredictionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        deployment_owner: str,
        deployment_name: str,
        input: object,
        stream: bool | NotGiven = NOT_GIVEN,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        prefer: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Create a prediction for the deployment and inputs you provide.

        Example cURL request:

        ```console
        curl -s -X POST -H 'Prefer: wait' \\
          -d '{"input": {"prompt": "A photo of a bear riding a bicycle over the moon"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/deployments/acme/my-app-image-generator/predictions
        ```

        The request will wait up to 60 seconds for the model to run. If this time is
        exceeded the prediction will be returned in a `"starting"` state and need to be
        retrieved using the `predictions.get` endpiont.

        For a complete overview of the `deployments.predictions.create` API check out
        our documentation on
        [creating a prediction](https://replicate.com/docs/topics/predictions/create-a-prediction)
        which covers a variety of use cases.

        Args:
          input: The model's input as a JSON object. The input schema depends on what model you
              are running. To see the available inputs, click the "API" tab on the model you
              are running or [get the model version](#models.versions.get) and look at its
              `openapi_schema` property. For example,
              [stability-ai/sdxl](https://replicate.com/stability-ai/sdxl) takes `prompt` as
              an input.

              Files should be passed as HTTP URLs or data URLs.

              Use an HTTP URL when:

              - you have a large file > 256kb
              - you want to be able to use the file multiple times
              - you want your prediction metadata to be associable with your input files

              Use a data URL when:

              - you have a small file <= 256kb
              - you don't want to upload and host the file somewhere
              - you don't need to use the file again (Replicate will not store it)

          stream: **This field is deprecated.**

              Request a URL to receive streaming output using
              [server-sent events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events).

              This field is no longer needed as the returned prediction will always have a
              `stream` entry in its `url` property if the model supports streaming.

          webhook: An HTTPS URL for receiving a webhook when the prediction has new output. The
              webhook will be a POST request where the request body is the same as the
              response body of the [get prediction](#predictions.get) operation. If there are
              network problems, we will retry the webhook a few times, so make sure it can be
              safely called more than once. Replicate will not follow redirects when sending
              webhook requests to your service, so be sure to specify a URL that will resolve
              without redirecting.

          webhook_events_filter: By default, we will send requests to your webhook URL whenever there are new
              outputs or the prediction has finished. You can change which events trigger
              webhook requests by specifying `webhook_events_filter` in the prediction
              request:

              - `start`: immediately on prediction start
              - `output`: each time a prediction generates an output (note that predictions
                can generate multiple outputs)
              - `logs`: each time log output is generated by a prediction
              - `completed`: when the prediction reaches a terminal state
                (succeeded/canceled/failed)

              For example, if you only wanted requests to be sent at the start and end of the
              prediction, you would provide:

              ```json
              {
                "input": {
                  "text": "Alice"
                },
                "webhook": "https://example.com/my-webhook",
                "webhook_events_filter": ["start", "completed"]
              }
              ```

              Requests for event types `output` and `logs` will be sent at most once every
              500ms. If you request `start` and `completed` webhooks, then they'll always be
              sent regardless of throttling.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not deployment_owner:
            raise ValueError(f"Expected a non-empty value for `deployment_owner` but received {deployment_owner!r}")
        if not deployment_name:
            raise ValueError(f"Expected a non-empty value for `deployment_name` but received {deployment_name!r}")
        extra_headers = {**strip_not_given({"Prefer": prefer}), **(extra_headers or {})}
        return await self._post(
            f"/deployments/{deployment_owner}/{deployment_name}/predictions",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "stream": stream,
                    "webhook": webhook,
                    "webhook_events_filter": webhook_events_filter,
                },
                prediction_create_params.PredictionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Prediction,
        )


class PredictionsResourceWithRawResponse:
    def __init__(self, predictions: PredictionsResource) -> None:
        self._predictions = predictions

        self.create = to_raw_response_wrapper(
            predictions.create,
        )


class AsyncPredictionsResourceWithRawResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_raw_response_wrapper(
            predictions.create,
        )


class PredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: PredictionsResource) -> None:
        self._predictions = predictions

        self.create = to_streamed_response_wrapper(
            predictions.create,
        )


class AsyncPredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_streamed_response_wrapper(
            predictions.create,
        )
