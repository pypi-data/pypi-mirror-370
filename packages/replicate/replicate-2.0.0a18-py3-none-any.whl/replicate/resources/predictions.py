# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from replicate.lib._files import FileEncodingStrategy, encode_json, async_encode_json

from ..types import prediction_list_params, prediction_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, strip_not_given, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncCursorURLPageWithCreatedFilters, AsyncCursorURLPageWithCreatedFilters
from .._base_client import AsyncPaginator, make_request_options
from ..types.prediction import Prediction

__all__ = ["PredictionsResource", "AsyncPredictionsResource"]

PREDICTION_TERMINAL_STATES = {"succeeded", "failed", "canceled"}


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

    def wait(self, prediction_id: str) -> Prediction:
        """Wait for prediction to finish."""
        prediction = self.get(prediction_id=prediction_id)
        while prediction.status not in PREDICTION_TERMINAL_STATES:
            self._sleep(self._client.poll_interval)
            prediction = self.get(prediction_id=prediction.id)
        return prediction

    def create(
        self,
        *,
        input: object,
        version: str,
        stream: bool | NotGiven = NOT_GIVEN,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        prefer: str | NotGiven = NOT_GIVEN,
        file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Create a prediction for the model version and inputs you provide.

        Example cURL request:

        ```console
        curl -s -X POST -H 'Prefer: wait' \\
          -d '{"version": "replicate/hello-world:5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa", "input": {"text": "Alice"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/predictions
        ```

        The request will wait up to 60 seconds for the model to run. If this time is
        exceeded the prediction will be returned in a `"starting"` state and need to be
        retrieved using the `predictions.get` endpiont.

        For a complete overview of the `predictions.create` API check out our
        documentation on
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

          version: The identifier for the model or model version that you want to run. This can be
              specified in a few different formats:

              - `{owner_name}/{model_name}` - Use this format for
                [official models](https://replicate.com/docs/topics/models/official-models).
                For example, `black-forest-labs/flux-schnell`. For all other models, the
                specific version is required.
              - `{owner_name}/{model_name}:{version_id}` - The owner and model name, plus the
                full 64-character version ID. For example,
                `replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426`.
              - `{version_id}` - Just the 64-character version ID. For example,
                `9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426`

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
                "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
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
        extra_headers = {**strip_not_given({"Prefer": prefer}), **(extra_headers or {})}
        return self._post(
            "/predictions",
            body=maybe_transform(
                {
                    "input": encode_json(input, self._client, file_encoding_strategy=file_encoding_strategy),
                    "version": version,
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

    def list(
        self,
        *,
        created_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        created_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorURLPageWithCreatedFilters[Prediction]:
        """
        Get a paginated list of all predictions created by the user or organization
        associated with the provided API token.

        This will include predictions created from the API and the website. It will
        return 100 records per page.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions
        ```

        The response will be a paginated JSON array of prediction objects, sorted with
        the most recent prediction first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "completed_at": "2023-09-08T16:19:34.791859Z",
              "created_at": "2023-09-08T16:19:34.907244Z",
              "data_removed": false,
              "error": null,
              "id": "gm3qorzdhgbfurvjtvhg6dckhu",
              "input": {
                "text": "Alice"
              },
              "metrics": {
                "predict_time": 0.012683
              },
              "output": "hello Alice",
              "started_at": "2023-09-08T16:19:34.779176Z",
              "source": "api",
              "status": "succeeded",
              "urls": {
                "web": "https://replicate.com/p/gm3qorzdhgbfurvjtvhg6dckhu",
                "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
                "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
              },
              "model": "replicate/hello-world",
              "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa"
            }
          ]
        }
        ```

        `id` will be the unique ID of the prediction.

        `source` will indicate how the prediction was created. Possible values are `web`
        or `api`.

        `status` will be the status of the prediction. Refer to
        [get a single prediction](#predictions.get) for possible values.

        `urls` will be a convenience object that can be used to construct new API
        requests for the given prediction. If the requested model version supports
        streaming, this will have a `stream` entry with an HTTPS URL that you can use to
        construct an
        [`EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource).

        `model` will be the model identifier string in the format of
        `{model_owner}/{model_name}`.

        `version` will be the unique ID of model version used to create the prediction.

        `data_removed` will be `true` if the input and output data has been deleted.

        Args:
          created_after: Include only predictions created at or after this date-time, in ISO 8601 format.

          created_before: Include only predictions created before this date-time, in ISO 8601 format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/predictions",
            page=SyncCursorURLPageWithCreatedFilters[Prediction],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                    },
                    prediction_list_params.PredictionListParams,
                ),
            ),
            model=Prediction,
        )

    def cancel(
        self,
        *,
        prediction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Cancel a prediction that is currently running.

        Example cURL request that creates a prediction and then cancels it:

        ```console
        # First, create a prediction
        PREDICTION_ID=$(curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{
            "input": {
              "prompt": "a video that may take a while to generate"
            }
          }' \\
          https://api.replicate.com/v1/models/minimax/video-01/predictions | jq -r '.id')

        # Echo the prediction ID
        echo "Created prediction with ID: $PREDICTION_ID"

        # Cancel the prediction
        curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions/$PREDICTION_ID/cancel
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return self._post(
            f"/predictions/{prediction_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Prediction,
        )

    def get(
        self,
        *,
        prediction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Get the current state of a prediction.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu
        ```

        The response will be the prediction object:

        ```json
        {
          "id": "gm3qorzdhgbfurvjtvhg6dckhu",
          "model": "replicate/hello-world",
          "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
          "input": {
            "text": "Alice"
          },
          "logs": "",
          "output": "hello Alice",
          "error": null,
          "status": "succeeded",
          "created_at": "2023-09-08T16:19:34.765994Z",
          "data_removed": false,
          "started_at": "2023-09-08T16:19:34.779176Z",
          "completed_at": "2023-09-08T16:19:34.791859Z",
          "metrics": {
            "predict_time": 0.012683
          },
          "urls": {
            "web": "https://replicate.com/p/gm3qorzdhgbfurvjtvhg6dckhu",
            "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
            "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
          }
        }
        ```

        `status` will be one of:

        - `starting`: the prediction is starting up. If this status lasts longer than a
          few seconds, then it's typically because a new worker is being started to run
          the prediction.
        - `processing`: the `predict()` method of the model is currently running.
        - `succeeded`: the prediction completed successfully.
        - `failed`: the prediction encountered an error during processing.
        - `canceled`: the prediction was canceled by its creator.

        In the case of success, `output` will be an object containing the output of the
        model. Any files will be represented as HTTPS URLs. You'll need to pass the
        `Authorization` header to request them.

        In the case of failure, `error` will contain the error encountered during the
        prediction.

        Terminated predictions (with a status of `succeeded`, `failed`, or `canceled`)
        will include a `metrics` object with a `predict_time` property showing the
        amount of CPU or GPU time, in seconds, that the prediction used while running.
        It won't include time waiting for the prediction to start.

        All input parameters, output values, and logs are automatically removed after an
        hour, by default, for predictions created through the API.

        You must save a copy of any data or files in the output if you'd like to
        continue using them. The `output` key will still be present, but it's value will
        be `null` after the output has been removed.

        Output files are served by `replicate.delivery` and its subdomains. If you use
        an allow list of external domains for your assets, add `replicate.delivery` and
        `*.replicate.delivery` to it.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return self._get(
            f"/predictions/{prediction_id}",
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

    async def wait(self, prediction_id: str) -> Prediction:
        """Wait for prediction to finish."""
        prediction = await self.get(prediction_id=prediction_id)
        while prediction.status not in PREDICTION_TERMINAL_STATES:
            await self._sleep(self._client.poll_interval)
            prediction = await self.get(prediction_id=prediction.id)
        return prediction

    async def create(
        self,
        *,
        input: object,
        version: str,
        stream: bool | NotGiven = NOT_GIVEN,
        webhook: str | NotGiven = NOT_GIVEN,
        webhook_events_filter: List[Literal["start", "output", "logs", "completed"]] | NotGiven = NOT_GIVEN,
        prefer: str | NotGiven = NOT_GIVEN,
        file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Create a prediction for the model version and inputs you provide.

        Example cURL request:

        ```console
        curl -s -X POST -H 'Prefer: wait' \\
          -d '{"version": "replicate/hello-world:5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa", "input": {"text": "Alice"}}' \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: application/json' \\
          https://api.replicate.com/v1/predictions
        ```

        The request will wait up to 60 seconds for the model to run. If this time is
        exceeded the prediction will be returned in a `"starting"` state and need to be
        retrieved using the `predictions.get` endpiont.

        For a complete overview of the `predictions.create` API check out our
        documentation on
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

          version: The identifier for the model or model version that you want to run. This can be
              specified in a few different formats:

              - `{owner_name}/{model_name}` - Use this format for
                [official models](https://replicate.com/docs/topics/models/official-models).
                For example, `black-forest-labs/flux-schnell`. For all other models, the
                specific version is required.
              - `{owner_name}/{model_name}:{version_id}` - The owner and model name, plus the
                full 64-character version ID. For example,
                `replicate/hello-world:9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426`.
              - `{version_id}` - Just the 64-character version ID. For example,
                `9dcd6d78e7c6560c340d916fe32e9f24aabfa331e5cce95fe31f77fb03121426`

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
                "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
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
        extra_headers = {**strip_not_given({"Prefer": prefer}), **(extra_headers or {})}
        return await self._post(
            "/predictions",
            body=await async_maybe_transform(
                {
                    "input": await async_encode_json(
                        input, self._client, file_encoding_strategy=file_encoding_strategy
                    ),
                    "version": version,
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

    def list(
        self,
        *,
        created_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        created_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Prediction, AsyncCursorURLPageWithCreatedFilters[Prediction]]:
        """
        Get a paginated list of all predictions created by the user or organization
        associated with the provided API token.

        This will include predictions created from the API and the website. It will
        return 100 records per page.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions
        ```

        The response will be a paginated JSON array of prediction objects, sorted with
        the most recent prediction first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "completed_at": "2023-09-08T16:19:34.791859Z",
              "created_at": "2023-09-08T16:19:34.907244Z",
              "data_removed": false,
              "error": null,
              "id": "gm3qorzdhgbfurvjtvhg6dckhu",
              "input": {
                "text": "Alice"
              },
              "metrics": {
                "predict_time": 0.012683
              },
              "output": "hello Alice",
              "started_at": "2023-09-08T16:19:34.779176Z",
              "source": "api",
              "status": "succeeded",
              "urls": {
                "web": "https://replicate.com/p/gm3qorzdhgbfurvjtvhg6dckhu",
                "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
                "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
              },
              "model": "replicate/hello-world",
              "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa"
            }
          ]
        }
        ```

        `id` will be the unique ID of the prediction.

        `source` will indicate how the prediction was created. Possible values are `web`
        or `api`.

        `status` will be the status of the prediction. Refer to
        [get a single prediction](#predictions.get) for possible values.

        `urls` will be a convenience object that can be used to construct new API
        requests for the given prediction. If the requested model version supports
        streaming, this will have a `stream` entry with an HTTPS URL that you can use to
        construct an
        [`EventSource`](https://developer.mozilla.org/en-US/docs/Web/API/EventSource).

        `model` will be the model identifier string in the format of
        `{model_owner}/{model_name}`.

        `version` will be the unique ID of model version used to create the prediction.

        `data_removed` will be `true` if the input and output data has been deleted.

        Args:
          created_after: Include only predictions created at or after this date-time, in ISO 8601 format.

          created_before: Include only predictions created before this date-time, in ISO 8601 format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/predictions",
            page=AsyncCursorURLPageWithCreatedFilters[Prediction],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "created_after": created_after,
                        "created_before": created_before,
                    },
                    prediction_list_params.PredictionListParams,
                ),
            ),
            model=Prediction,
        )

    async def cancel(
        self,
        *,
        prediction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Cancel a prediction that is currently running.

        Example cURL request that creates a prediction and then cancels it:

        ```console
        # First, create a prediction
        PREDICTION_ID=$(curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{
            "input": {
              "prompt": "a video that may take a while to generate"
            }
          }' \\
          https://api.replicate.com/v1/models/minimax/video-01/predictions | jq -r '.id')

        # Echo the prediction ID
        echo "Created prediction with ID: $PREDICTION_ID"

        # Cancel the prediction
        curl -s -X POST \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions/$PREDICTION_ID/cancel
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return await self._post(
            f"/predictions/{prediction_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Prediction,
        )

    async def get(
        self,
        *,
        prediction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Prediction:
        """
        Get the current state of a prediction.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu
        ```

        The response will be the prediction object:

        ```json
        {
          "id": "gm3qorzdhgbfurvjtvhg6dckhu",
          "model": "replicate/hello-world",
          "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
          "input": {
            "text": "Alice"
          },
          "logs": "",
          "output": "hello Alice",
          "error": null,
          "status": "succeeded",
          "created_at": "2023-09-08T16:19:34.765994Z",
          "data_removed": false,
          "started_at": "2023-09-08T16:19:34.779176Z",
          "completed_at": "2023-09-08T16:19:34.791859Z",
          "metrics": {
            "predict_time": 0.012683
          },
          "urls": {
            "web": "https://replicate.com/p/gm3qorzdhgbfurvjtvhg6dckhu",
            "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
            "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel"
          }
        }
        ```

        `status` will be one of:

        - `starting`: the prediction is starting up. If this status lasts longer than a
          few seconds, then it's typically because a new worker is being started to run
          the prediction.
        - `processing`: the `predict()` method of the model is currently running.
        - `succeeded`: the prediction completed successfully.
        - `failed`: the prediction encountered an error during processing.
        - `canceled`: the prediction was canceled by its creator.

        In the case of success, `output` will be an object containing the output of the
        model. Any files will be represented as HTTPS URLs. You'll need to pass the
        `Authorization` header to request them.

        In the case of failure, `error` will contain the error encountered during the
        prediction.

        Terminated predictions (with a status of `succeeded`, `failed`, or `canceled`)
        will include a `metrics` object with a `predict_time` property showing the
        amount of CPU or GPU time, in seconds, that the prediction used while running.
        It won't include time waiting for the prediction to start.

        All input parameters, output values, and logs are automatically removed after an
        hour, by default, for predictions created through the API.

        You must save a copy of any data or files in the output if you'd like to
        continue using them. The `output` key will still be present, but it's value will
        be `null` after the output has been removed.

        Output files are served by `replicate.delivery` and its subdomains. If you use
        an allow list of external domains for your assets, add `replicate.delivery` and
        `*.replicate.delivery` to it.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not prediction_id:
            raise ValueError(f"Expected a non-empty value for `prediction_id` but received {prediction_id!r}")
        return await self._get(
            f"/predictions/{prediction_id}",
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
        self.list = to_raw_response_wrapper(
            predictions.list,
        )
        self.cancel = to_raw_response_wrapper(
            predictions.cancel,
        )
        self.get = to_raw_response_wrapper(
            predictions.get,
        )


class AsyncPredictionsResourceWithRawResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_raw_response_wrapper(
            predictions.create,
        )
        self.list = async_to_raw_response_wrapper(
            predictions.list,
        )
        self.cancel = async_to_raw_response_wrapper(
            predictions.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            predictions.get,
        )


class PredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: PredictionsResource) -> None:
        self._predictions = predictions

        self.create = to_streamed_response_wrapper(
            predictions.create,
        )
        self.list = to_streamed_response_wrapper(
            predictions.list,
        )
        self.cancel = to_streamed_response_wrapper(
            predictions.cancel,
        )
        self.get = to_streamed_response_wrapper(
            predictions.get,
        )


class AsyncPredictionsResourceWithStreamingResponse:
    def __init__(self, predictions: AsyncPredictionsResource) -> None:
        self._predictions = predictions

        self.create = async_to_streamed_response_wrapper(
            predictions.create,
        )
        self.list = async_to_streamed_response_wrapper(
            predictions.list,
        )
        self.cancel = async_to_streamed_response_wrapper(
            predictions.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            predictions.get,
        )
