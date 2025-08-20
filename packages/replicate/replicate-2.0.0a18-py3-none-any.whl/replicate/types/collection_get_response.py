# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from replicate.types.models.version_get_response import VersionGetResponse

from .._models import BaseModel

__all__ = ["CollectionGetResponse", "Model"]


class Model(BaseModel):
    cover_image_url: Optional[str] = None
    """A URL for the model's cover image"""

    default_example: Optional[object] = None
    """The model's default example prediction"""

    description: Optional[str] = None
    """A description of the model"""

    github_url: Optional[str] = None
    """A URL for the model's source code on GitHub"""

    latest_version: Optional[VersionGetResponse] = None
    """The model's latest version"""

    license_url: Optional[str] = None
    """A URL for the model's license"""

    name: Optional[str] = None
    """The name of the model"""

    owner: Optional[str] = None
    """The name of the user or organization that owns the model"""

    paper_url: Optional[str] = None
    """A URL for the model's paper"""

    run_count: Optional[int] = None
    """The number of times the model has been run"""

    url: Optional[str] = None
    """The URL of the model on Replicate"""

    visibility: Optional[Literal["public", "private"]] = None
    """Whether the model is public or private"""


class CollectionGetResponse(BaseModel):
    description: str
    """A description of the collection"""

    models: List[Model]
    """The models in this collection"""

    name: str
    """The name of the collection"""

    slug: str
    """The slug of the collection (lowercase with dashes)"""
