# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["FileDownloadParams"]


class FileDownloadParams(TypedDict, total=False):
    file_id: Required[str]

    expiry: Required[int]
    """A Unix timestamp with expiration date of this download URL"""

    owner: Required[str]
    """The username of the user or organization that uploaded the file"""

    signature: Required[str]
    """
    A base64-encoded HMAC-SHA256 checksum of the string '{owner} {id} {expiry}'
    generated with the Files API signing secret
    """
