"""Cog integration utilities for Replicate."""

import os
from typing import Any, Union, Iterator, cast

from replicate._utils._logs import logger


def _get_api_token_from_environment() -> Union[str, None]:
    """Get API token from cog current scope if available, otherwise from environment."""
    try:
        import cog  # type: ignore[import-untyped, import-not-found]

        # Get the current scope - this might return None or raise an exception
        scope = getattr(cog, "current_scope", lambda: None)()
        if scope is None:
            return os.environ.get("REPLICATE_API_TOKEN")

        # Get the context from the scope
        context = getattr(scope, "context", None)
        if context is None:
            return os.environ.get("REPLICATE_API_TOKEN")

        # Get the items method and call it
        items_method = getattr(context, "items", None)
        if not callable(items_method):
            return os.environ.get("REPLICATE_API_TOKEN")

        # Iterate through context items looking for the API token
        items = cast(Iterator["tuple[Any, Any]"], items_method())
        for key, value in items:
            if str(key).upper() == "REPLICATE_API_TOKEN":
                return str(value) if value is not None else value

    except Exception as e:  # Catch all exceptions to ensure robust fallback
        logger.debug("Failed to retrieve API token from cog.current_scope(): %s", e)

    return os.environ.get("REPLICATE_API_TOKEN")


__all__ = ["_get_api_token_from_environment"]
