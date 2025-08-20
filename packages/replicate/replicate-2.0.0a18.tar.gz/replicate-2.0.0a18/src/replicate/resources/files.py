# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ..types import file_create_params, file_download_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ..pagination import SyncCursorURLPage, AsyncCursorURLPage
from .._base_client import AsyncPaginator, make_request_options
from ..types.file_get_response import FileGetResponse
from ..types.file_list_response import FileListResponse
from ..types.file_create_response import FileCreateResponse

__all__ = ["FilesResource", "AsyncFilesResource"]


class FilesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return FilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return FilesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        content: FileTypes,
        filename: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileCreateResponse:
        """
        Create a file by uploading its content and optional metadata.

        Example cURL request:

        ```console
        curl -X POST https://api.replicate.com/v1/files \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: multipart/form-data' \\
          -F 'content=@/path/to/archive.zip;type=application/zip;filename=example.zip' \\
          -F 'metadata={"customer_reference_id": 123};type=application/json'
        ```

        The request must include:

        - `content`: The file content (required)
        - `type`: The content / MIME type for the file (defaults to
          `application/octet-stream`)
        - `filename`: The filename (required, ≤ 255 bytes, valid UTF-8)
        - `metadata`: User-provided metadata associated with the file (defaults to `{}`,
          must be valid JSON)

        Args:
          content: The file content

          filename: The filename

          metadata: User-provided metadata associated with the file

          type: The content / MIME type for the file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "content": content,
                "filename": filename,
                "metadata": metadata,
                "type": type,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["content"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/files",
            body=maybe_transform(body, file_create_params.FileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorURLPage[FileListResponse]:
        """
        Get a paginated list of all files created by the user or organization associated
        with the provided API token.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files
        ```

        The response will be a paginated JSON array of file objects, sorted with the
        most recent file first.
        """
        return self._get_api_list(
            "/files",
            page=SyncCursorURLPage[FileListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=FileListResponse,
        )

    def delete(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Delete a file.

        Once a file has been deleted, subsequent requests to the file
        resource return 404 Not found.

        Example cURL request:

        ```console
        curl -X DELETE \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def download(
        self,
        *,
        file_id: str,
        expiry: int,
        owner: str,
        signature: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Download a file by providing the file owner, access expiry, and a valid
        signature.

        Example cURL request:

        ```console
        curl -X GET "https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o/download?expiry=1708515345&owner=mattt&signature=zuoghqlrcnw8YHywkpaXQlHsVhWen%2FDZ4aal76dLiOo%3D"
        ```

        Args:
          expiry: A Unix timestamp with expiration date of this download URL

          owner: The username of the user or organization that uploaded the file

          signature: A base64-encoded HMAC-SHA256 checksum of the string '{owner} {id} {expiry}'
              generated with the Files API signing secret

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._get(
            f"/files/{file_id}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "expiry": expiry,
                        "owner": owner,
                        "signature": signature,
                    },
                    file_download_params.FileDownloadParams,
                ),
            ),
            cast_to=BinaryAPIResponse,
        )

    def get(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileGetResponse:
        """
        Get the details of a file.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return self._get(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileGetResponse,
        )


class AsyncFilesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFilesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#accessing-raw-response-data-eg-headers
        """
        return AsyncFilesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFilesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/replicate/replicate-python-stainless#with_streaming_response
        """
        return AsyncFilesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        content: FileTypes,
        filename: str | NotGiven = NOT_GIVEN,
        metadata: object | NotGiven = NOT_GIVEN,
        type: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileCreateResponse:
        """
        Create a file by uploading its content and optional metadata.

        Example cURL request:

        ```console
        curl -X POST https://api.replicate.com/v1/files \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          -H 'Content-Type: multipart/form-data' \\
          -F 'content=@/path/to/archive.zip;type=application/zip;filename=example.zip' \\
          -F 'metadata={"customer_reference_id": 123};type=application/json'
        ```

        The request must include:

        - `content`: The file content (required)
        - `type`: The content / MIME type for the file (defaults to
          `application/octet-stream`)
        - `filename`: The filename (required, ≤ 255 bytes, valid UTF-8)
        - `metadata`: User-provided metadata associated with the file (defaults to `{}`,
          must be valid JSON)

        Args:
          content: The file content

          filename: The filename

          metadata: User-provided metadata associated with the file

          type: The content / MIME type for the file

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "content": content,
                "filename": filename,
                "metadata": metadata,
                "type": type,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["content"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/files",
            body=await async_maybe_transform(body, file_create_params.FileCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileCreateResponse,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[FileListResponse, AsyncCursorURLPage[FileListResponse]]:
        """
        Get a paginated list of all files created by the user or organization associated
        with the provided API token.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files
        ```

        The response will be a paginated JSON array of file objects, sorted with the
        most recent file first.
        """
        return self._get_api_list(
            "/files",
            page=AsyncCursorURLPage[FileListResponse],
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            model=FileListResponse,
        )

    async def delete(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Delete a file.

        Once a file has been deleted, subsequent requests to the file
        resource return 404 Not found.

        Example cURL request:

        ```console
        curl -X DELETE \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def download(
        self,
        *,
        file_id: str,
        expiry: int,
        owner: str,
        signature: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Download a file by providing the file owner, access expiry, and a valid
        signature.

        Example cURL request:

        ```console
        curl -X GET "https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o/download?expiry=1708515345&owner=mattt&signature=zuoghqlrcnw8YHywkpaXQlHsVhWen%2FDZ4aal76dLiOo%3D"
        ```

        Args:
          expiry: A Unix timestamp with expiration date of this download URL

          owner: The username of the user or organization that uploaded the file

          signature: A base64-encoded HMAC-SHA256 checksum of the string '{owner} {id} {expiry}'
              generated with the Files API signing secret

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return await self._get(
            f"/files/{file_id}/download",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "expiry": expiry,
                        "owner": owner,
                        "signature": signature,
                    },
                    file_download_params.FileDownloadParams,
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def get(
        self,
        *,
        file_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FileGetResponse:
        """
        Get the details of a file.

        Example cURL request:

        ```console
        curl -s \\
          -H "Authorization: Token $REPLICATE_API_TOKEN" \\
          https://api.replicate.com/v1/files/cneqzikepnug6xezperrr4z55o
        ```

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not file_id:
            raise ValueError(f"Expected a non-empty value for `file_id` but received {file_id!r}")
        return await self._get(
            f"/files/{file_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FileGetResponse,
        )


class FilesResourceWithRawResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.create = to_raw_response_wrapper(
            files.create,
        )
        self.list = to_raw_response_wrapper(
            files.list,
        )
        self.delete = to_raw_response_wrapper(
            files.delete,
        )
        self.download = to_custom_raw_response_wrapper(
            files.download,
            BinaryAPIResponse,
        )
        self.get = to_raw_response_wrapper(
            files.get,
        )


class AsyncFilesResourceWithRawResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.create = async_to_raw_response_wrapper(
            files.create,
        )
        self.list = async_to_raw_response_wrapper(
            files.list,
        )
        self.delete = async_to_raw_response_wrapper(
            files.delete,
        )
        self.download = async_to_custom_raw_response_wrapper(
            files.download,
            AsyncBinaryAPIResponse,
        )
        self.get = async_to_raw_response_wrapper(
            files.get,
        )


class FilesResourceWithStreamingResponse:
    def __init__(self, files: FilesResource) -> None:
        self._files = files

        self.create = to_streamed_response_wrapper(
            files.create,
        )
        self.list = to_streamed_response_wrapper(
            files.list,
        )
        self.delete = to_streamed_response_wrapper(
            files.delete,
        )
        self.download = to_custom_streamed_response_wrapper(
            files.download,
            StreamedBinaryAPIResponse,
        )
        self.get = to_streamed_response_wrapper(
            files.get,
        )


class AsyncFilesResourceWithStreamingResponse:
    def __init__(self, files: AsyncFilesResource) -> None:
        self._files = files

        self.create = async_to_streamed_response_wrapper(
            files.create,
        )
        self.list = async_to_streamed_response_wrapper(
            files.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            files.delete,
        )
        self.download = async_to_custom_streamed_response_wrapper(
            files.download,
            AsyncStreamedBinaryAPIResponse,
        )
        self.get = async_to_streamed_response_wrapper(
            files.get,
        )
