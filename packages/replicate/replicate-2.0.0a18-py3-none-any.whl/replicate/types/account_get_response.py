# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AccountGetResponse"]


class AccountGetResponse(BaseModel):
    type: Literal["organization", "user"]
    """The account type. Can be a user or an organization."""

    username: str
    """The username of the account."""

    avatar_url: Optional[str] = None
    """The avatar URL for the account."""

    github_url: Optional[str] = None
    """The GitHub URL of the account."""

    name: Optional[str] = None
    """The name of the account."""
