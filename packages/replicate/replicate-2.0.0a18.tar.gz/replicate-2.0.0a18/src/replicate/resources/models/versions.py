# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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
from ...types.models.version_get_response import VersionGetResponse
from ...types.models.version_list_response import VersionListResponse

__all__ = ["VersionsResource", "AsyncVersionsResource"]


class VersionsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return VersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return VersionsResourceWithStreamingResponse(self)

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
    ) -> SyncCursorURLPage[VersionListResponse]:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions
        ```

        The response will be a JSON array of model version objects, sorted with the most
        recent version first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "id": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
              "created_at": "2022-04-26T19:29:04.418669Z",
              "cog_version": "0.3.0",
              "openapi_schema": {...}
            }
          ]
        }
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
        return self._get_api_list(
            f"/models/{model_owner}/{model_name}/versions",
            page=SyncCursorURLPage[VersionListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=VersionListResponse,
        )

    def delete(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a model version and all associated predictions, including all output
        files.

        Model version deletion has some restrictions:

        - You can only delete versions from models you own.
        - You can only delete versions from private models.
        - You cannot delete a version if someone other than you has run predictions with
          it.
        - You cannot delete a version if it is being used as the base model for a fine
          tune/training.
        - You cannot delete a version if it has an associated deployment.
        - You cannot delete a version if another model version is overridden to use it.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions/5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa
        ```

        The response will be an empty 202, indicating the deletion request has been
        accepted. It might take a few minutes to be processed.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/models/{model_owner}/{model_name}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VersionGetResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions/5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa
        ```

        The response will be the version object:

        ```json
        {
          "id": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
          "created_at": "2022-04-26T19:29:04.418669Z",
          "cog_version": "0.3.0",
          "openapi_schema": {...}
        }
        ```

        Every model describes its inputs and outputs with
        [OpenAPI Schema Objects](https://spec.openapis.org/oas/latest.html#schemaObject)
        in the `openapi_schema` property.

        The `openapi_schema.components.schemas.Input` property for the
        [replicate/hello-world](https://replicate.com/replicate/hello-world) model looks
        like this:

        ```json
        {
          "type": "object",
          "title": "Input",
          "required": ["text"],
          "properties": {
            "text": {
              "x-order": 0,
              "type": "string",
              "title": "Text",
              "description": "Text to prefix with 'hello '"
            }
          }
        }
        ```

        The `openapi_schema.components.schemas.Output` property for the
        [replicate/hello-world](https://replicate.com/replicate/hello-world) model looks
        like this:

        ```json
        {
          "type": "string",
          "title": "Output"
        }
        ```

        For more details, see the docs on
        [Cog's supported input and output types](https://github.com/replicate/cog/blob/75b7802219e7cd4cee845e34c4c22139558615d4/docs/python.md#input-and-output-types)

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return self._get(
            f"/models/{model_owner}/{model_name}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VersionGetResponse,
        )


class AsyncVersionsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVersionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncVersionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVersionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncVersionsResourceWithStreamingResponse(self)

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
    ) -> AsyncPaginator[VersionListResponse, AsyncCursorURLPage[VersionListResponse]]:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions
        ```

        The response will be a JSON array of model version objects, sorted with the most
        recent version first:

        ```json
        {
          "next": null,
          "previous": null,
          "results": [
            {
              "id": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
              "created_at": "2022-04-26T19:29:04.418669Z",
              "cog_version": "0.3.0",
              "openapi_schema": {...}
            }
          ]
        }
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
        return self._get_api_list(
            f"/models/{model_owner}/{model_name}/versions",
            page=AsyncCursorURLPage[VersionListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=VersionListResponse,
        )

    async def delete(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a model version and all associated predictions, including all output
        files.

        Model version deletion has some restrictions:

        - You can only delete versions from models you own.
        - You can only delete versions from private models.
        - You cannot delete a version if someone other than you has run predictions with
          it.
        - You cannot delete a version if it is being used as the base model for a fine
          tune/training.
        - You cannot delete a version if it has an associated deployment.
        - You cannot delete a version if another model version is overridden to use it.

        Example cURL request:

        ```command
        curl -s -X DELETE \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions/5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa
        ```

        The response will be an empty 202, indicating the deletion request has been
        accepted. It might take a few minutes to be processed.

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/models/{model_owner}/{model_name}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        *,
        model_owner: str,
        model_name: str,
        version_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VersionGetResponse:
        """
        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Bearer $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/models/replicate/hello-world/versions/5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa
        ```

        The response will be the version object:

        ```json
        {
          "id": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
          "created_at": "2022-04-26T19:29:04.418669Z",
          "cog_version": "0.3.0",
          "openapi_schema": {...}
        }
        ```

        Every model describes its inputs and outputs with
        [OpenAPI Schema Objects](https://spec.openapis.org/oas/latest.html#schemaObject)
        in the `openapi_schema` property.

        The `openapi_schema.components.schemas.Input` property for the
        [replicate/hello-world](https://replicate.com/replicate/hello-world) model looks
        like this:

        ```json
        {
          "type": "object",
          "title": "Input",
          "required": ["text"],
          "properties": {
            "text": {
              "x-order": 0,
              "type": "string",
              "title": "Text",
              "description": "Text to prefix with 'hello '"
            }
          }
        }
        ```

        The `openapi_schema.components.schemas.Output` property for the
        [replicate/hello-world](https://replicate.com/replicate/hello-world) model looks
        like this:

        ```json
        {
          "type": "string",
          "title": "Output"
        }
        ```

        For more details, see the docs on
        [Cog's supported input and output types](https://github.com/replicate/cog/blob/75b7802219e7cd4cee845e34c4c22139558615d4/docs/python.md#input-and-output-types)

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
        if not version_id:
            raise ValueError(f"Expected a non-empty value for `version_id` but received {version_id!r}")
        return await self._get(
            f"/models/{model_owner}/{model_name}/versions/{version_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VersionGetResponse,
        )


class VersionsResourceWithRawResponse:
    def __init__(self, versions: VersionsResource) -> None:
        self._versions = versions

        self.list = to_raw_response_wrapper(
            versions.list,
        )
        self.delete = to_raw_response_wrapper(
            versions.delete,
        )
        self.get = to_raw_response_wrapper(
            versions.get,
        )


class AsyncVersionsResourceWithRawResponse:
    def __init__(self, versions: AsyncVersionsResource) -> None:
        self._versions = versions

        self.list = async_to_raw_response_wrapper(
            versions.list,
        )
        self.delete = async_to_raw_response_wrapper(
            versions.delete,
        )
        self.get = async_to_raw_response_wrapper(
            versions.get,
        )


class VersionsResourceWithStreamingResponse:
    def __init__(self, versions: VersionsResource) -> None:
        self._versions = versions

        self.list = to_streamed_response_wrapper(
            versions.list,
        )
        self.delete = to_streamed_response_wrapper(
            versions.delete,
        )
        self.get = to_streamed_response_wrapper(
            versions.get,
        )


class AsyncVersionsResourceWithStreamingResponse:
    def __init__(self, versions: AsyncVersionsResource) -> None:
        self._versions = versions

        self.list = async_to_streamed_response_wrapper(
            versions.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            versions.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            versions.get,
        )
