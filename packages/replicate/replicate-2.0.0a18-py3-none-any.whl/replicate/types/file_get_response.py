# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["FileGetResponse", "Checksums", "URLs"]


class Checksums(BaseModel):
    sha256: Optional[str] = None
    """SHA256 checksum of the file"""


class URLs(BaseModel):
    get: Optional[str] = None
    """A URL to the file resource"""


class FileGetResponse(BaseModel):
    id: str
    """A unique, randomly-generated identifier for the file resource"""

    checksums: Checksums
    """A dictionary of checksums for the file keyed by the algorithm name"""

    content_type: str
    """The content / MIME type of the file"""

    created_at: datetime
    """When the file was created"""

    expires_at: datetime
    """When the file expires"""

    metadata: object
    """Metadata provided by user when the file was created"""

    size: int
    """The length of the file in bytes"""

    urls: URLs
    """A dictionary of URLs associated with the file resource"""
