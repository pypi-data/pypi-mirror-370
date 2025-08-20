from __future__ import annotations

import io
import base64
import mimetypes
from types import GeneratorType
from typing import TYPE_CHECKING, Any, Literal, Iterator, Optional, AsyncIterator
from pathlib import Path
from typing_extensions import override

import httpx

from .._utils import is_mapping, is_sequence

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .._client import Replicate, AsyncReplicate

FileEncodingStrategy = Literal["base64", "url"]


try:
    import numpy as np  # type: ignore

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False  # type: ignore


# pylint: disable=too-many-return-statements
def encode_json(
    obj: Any,  # noqa: ANN401
    client: Replicate,
    file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
) -> Any:  # noqa: ANN401
    """
    Return a JSON-compatible version of the object.
    """

    if isinstance(obj, dict):
        return {
            key: encode_json(value, client, file_encoding_strategy)
            for key, value in obj.items()  # type: ignore
        }  # type: ignore
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        return [encode_json(value, client, file_encoding_strategy) for value in obj]  # type: ignore
    if isinstance(obj, Path):
        with obj.open("rb") as file:
            return encode_json(file, client, file_encoding_strategy)
    if isinstance(obj, io.IOBase):
        if file_encoding_strategy == "base64":
            return base64_encode_file(obj)
        else:
            response = client.files.create(content=obj.read())
            return response.urls.get
    if HAS_NUMPY:
        if isinstance(obj, np.integer):  # type: ignore
            return int(obj)
        if isinstance(obj, np.floating):  # type: ignore
            return float(obj)
        if isinstance(obj, np.ndarray):  # type: ignore
            return obj.tolist()
    return obj


async def async_encode_json(
    obj: Any,  # noqa: ANN401
    client: AsyncReplicate,
    file_encoding_strategy: Optional["FileEncodingStrategy"] = None,
) -> Any:  # noqa: ANN401
    """
    Asynchronously return a JSON-compatible version of the object.
    """

    if isinstance(obj, dict):
        return {
            key: (await async_encode_json(value, client, file_encoding_strategy))
            for key, value in obj.items()  # type: ignore
        }  # type: ignore
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        return [
            (await async_encode_json(value, client, file_encoding_strategy))
            for value in obj  # type: ignore
        ]
    if isinstance(obj, Path):
        with obj.open("rb") as file:
            return await async_encode_json(file, client, file_encoding_strategy)
    if isinstance(obj, io.IOBase):
        if file_encoding_strategy == "base64":
            # TODO: This should ideally use an async based file reader path.
            return base64_encode_file(obj)
        else:
            response = await client.files.create(content=obj.read())
            return response.urls.get
    if HAS_NUMPY:
        if isinstance(obj, np.integer):  # type: ignore
            return int(obj)
        if isinstance(obj, np.floating):  # type: ignore
            return float(obj)
        if isinstance(obj, np.ndarray):  # type: ignore
            return obj.tolist()
    return obj


def base64_encode_file(file: io.IOBase) -> str:
    """
    Base64 encode a file.

    Args:
        file: A file handle to upload.
    Returns:
        str: A base64-encoded data URI.
    """

    file.seek(0)
    body = file.read()

    # Ensure the file handle is in bytes
    body = body.encode("utf-8") if isinstance(body, str) else body
    encoded_body = base64.b64encode(body).decode("utf-8")

    mime_type = mimetypes.guess_type(getattr(file, "name", ""))[0] or "application/octet-stream"
    return f"data:{mime_type};base64,{encoded_body}"


class FileOutput(httpx.SyncByteStream):
    """
    An object that can be used to read the contents of an output file
    created by running a Replicate model.
    """

    url: str
    """
    The file URL.
    """

    _client: Replicate

    def __init__(self, url: str, client: Replicate) -> None:
        self.url = url
        self._client = client

    def read(self) -> bytes:
        if self.url.startswith("data:"):
            _, encoded = self.url.split(",", 1)
            return base64.b64decode(encoded)

        with self._client._client.stream("GET", self.url) as response:
            response.raise_for_status()
            return response.read()

    @override
    def __iter__(self) -> Iterator[bytes]:
        if self.url.startswith("data:"):
            yield self.read()
            return

        with self._client._client.stream("GET", self.url) as response:
            response.raise_for_status()
            yield from response.iter_bytes()

    @override
    def __str__(self) -> str:
        return self.url

    @override
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.url}")'


class AsyncFileOutput(httpx.AsyncByteStream):
    """
    An object that can be used to read the contents of an output file
    created by running a Replicate model.
    """

    url: str
    """
    The file URL.
    """

    _client: AsyncReplicate

    def __init__(self, url: str, client: AsyncReplicate) -> None:
        self.url = url
        self._client = client

    async def read(self) -> bytes:
        if self.url.startswith("data:"):
            _, encoded = self.url.split(",", 1)
            return base64.b64decode(encoded)

        async with self._client._client.stream("GET", self.url) as response:
            response.raise_for_status()
            return await response.aread()

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        if self.url.startswith("data:"):
            yield await self.read()
            return

        async with self._client._client.stream("GET", self.url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk

    @override
    def __str__(self) -> str:
        return self.url

    @override
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.url}")'


def transform_output(value: object, client: "Replicate | AsyncReplicate") -> Any:
    """
    Transform the output of a prediction to a `FileOutput` object if it's a URL.
    """

    def transform(obj: Any) -> Any:
        if is_mapping(obj):
            return {k: transform(v) for k, v in obj.items()}
        elif is_sequence(obj) and not isinstance(obj, str):
            return [transform(item) for item in obj]
        elif isinstance(obj, str) and (obj.startswith("https:") or obj.startswith("data:")):
            # Check if the client is async by looking for async in the class name
            # we're doing this to avoid circular imports
            if "Async" in client.__class__.__name__:
                return AsyncFileOutput(obj, client)  # type: ignore
            return FileOutput(obj, client)  # type: ignore
        return obj

    return transform(value)
