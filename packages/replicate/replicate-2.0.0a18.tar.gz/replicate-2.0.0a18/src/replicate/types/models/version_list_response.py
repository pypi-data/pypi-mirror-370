# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["VersionListResponse"]


class VersionListResponse(BaseModel):
    id: Optional[str] = None
    """The ID of the version"""

    cog_version: Optional[str] = None
    """The version of Cog used to create this version"""

    created_at: Optional[datetime] = None
    """The date and time the version was created"""

    openapi_schema: Optional[object] = None
    """The OpenAPI schema for the model's inputs and outputs"""
