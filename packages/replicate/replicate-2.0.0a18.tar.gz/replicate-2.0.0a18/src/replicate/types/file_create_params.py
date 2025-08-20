# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["FileCreateParams"]


class FileCreateParams(TypedDict, total=False):
    content: Required[FileTypes]
    """The file content"""

    filename: str
    """The filename"""

    metadata: object
    """User-provided metadata associated with the file"""

    type: str
    """The content / MIME type for the file"""
