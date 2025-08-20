# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["CollectionListResponse"]


class CollectionListResponse(BaseModel):
    description: str
    """A description of the collection"""

    name: str
    """The name of the collection"""

    slug: str
    """The slug of the collection (lowercase with dashes)"""
