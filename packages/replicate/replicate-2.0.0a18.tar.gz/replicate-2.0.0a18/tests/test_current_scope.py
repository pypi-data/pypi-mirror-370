"""Tests for current_scope token functionality."""

import os
import sys
from unittest import mock

import pytest

from replicate import Replicate, AsyncReplicate
from replicate.lib.cog import _get_api_token_from_environment
from replicate._exceptions import ReplicateError


class TestGetApiTokenFromEnvironment:
    """Test the _get_api_token_from_environment function."""

    def test_cog_no_current_scope_method_falls_back_to_env(self):
        """Test fallback when cog exists but has no current_scope method."""
        mock_cog = mock.MagicMock()
        del mock_cog.current_scope  # Remove the method
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_cog_current_scope_returns_none_falls_back_to_env(self):
        """Test fallback when current_scope() returns None."""
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = None
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_cog_scope_no_context_attr_falls_back_to_env(self):
        """Test fallback when scope has no context attribute."""
        mock_scope = mock.MagicMock()
        del mock_scope.context  # Remove the context attribute
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_cog_scope_context_not_dict_falls_back_to_env(self):
        """Test fallback when scope.context is not a dictionary."""
        mock_scope = mock.MagicMock()
        mock_scope.context = "not a dict"
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_cog_scope_no_replicate_api_token_key_falls_back_to_env(self):
        """Test fallback when replicate_api_token key is missing from context."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"other_key": "other_value"}  # Missing replicate_api_token
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_cog_scope_replicate_api_token_valid_string(self):
        """Test successful retrieval of non-empty token from cog."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"REPLICATE_API_TOKEN": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "cog-token"

    def test_cog_scope_replicate_api_token_case_insensitive(self):
        """Test successful retrieval of non-empty token from cog ignoring case."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"replicate_api_token": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "cog-token"

    def test_cog_scope_replicate_api_token_empty_string(self):
        """Test that empty string from cog is returned (not falling back to env)."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"replicate_api_token": ""}  # Empty string
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == ""  # Should return empty string, not env token

    def test_cog_scope_replicate_api_token_none(self):
        """Test that None from cog is returned (not falling back to env)."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"replicate_api_token": None}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token is None  # Should return None, not env token

    def test_cog_current_scope_raises_exception_falls_back_to_env(self):
        """Test fallback when current_scope() raises an exception."""
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.side_effect = RuntimeError("Scope error")
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                token = _get_api_token_from_environment()
                assert token == "env-token"

    def test_no_env_token_returns_none(self):
        """Test that None is returned when no environment token is set and cog unavailable."""
        with mock.patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            with mock.patch.dict(sys.modules, {"cog": None}):
                token = _get_api_token_from_environment()
                assert token is None

    def test_env_token_empty_string(self):
        """Test that empty string from environment is returned."""
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": ""}):
            with mock.patch.dict(sys.modules, {"cog": None}):
                token = _get_api_token_from_environment()
                assert token == ""

    def test_env_token_valid_string(self):
        """Test that valid token from environment is returned."""
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": None}):
                token = _get_api_token_from_environment()
                assert token == "env-token"


class TestClientCurrentScopeIntegration:
    """Test that the client uses current_scope functionality."""

    def test_sync_client_uses_current_scope_token(self):
        """Test that sync client retrieves token from current_scope."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"REPLICATE_API_TOKEN": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope

        # Clear environment variable to ensure we're using cog
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                client = Replicate(base_url="http://test.example.com")
                assert client.bearer_token == "cog-token"

    def test_async_client_uses_current_scope_token(self):
        """Test that async client retrieves token from current_scope."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"REPLICATE_API_TOKEN": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope

        # Clear environment variable to ensure we're using cog
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.dict(sys.modules, {"cog": mock_cog}):
                client = AsyncReplicate(base_url="http://test.example.com")
                assert client.bearer_token == "cog-token"

    def test_sync_client_falls_back_to_env_when_cog_unavailable(self):
        """Test that sync client falls back to env when cog is unavailable."""
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": None}):
                client = Replicate(base_url="http://test.example.com")
                assert client.bearer_token == "env-token"

    def test_async_client_falls_back_to_env_when_cog_unavailable(self):
        """Test that async client falls back to env when cog is unavailable."""
        with mock.patch.dict(os.environ, {"REPLICATE_API_TOKEN": "env-token"}):
            with mock.patch.dict(sys.modules, {"cog": None}):
                client = AsyncReplicate(base_url="http://test.example.com")
                assert client.bearer_token == "env-token"

    def test_sync_client_raises_error_when_no_token_available(self):
        """Test that sync client raises error when no token is available."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.dict(sys.modules, {"cog": None}):
                with pytest.raises(ReplicateError, match="bearer_token client option must be set"):
                    Replicate(base_url="http://test.example.com")

    def test_async_client_raises_error_when_no_token_available(self):
        """Test that async client raises error when no token is available."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.dict(sys.modules, {"cog": None}):
                with pytest.raises(ReplicateError, match="bearer_token client option must be set"):
                    AsyncReplicate(base_url="http://test.example.com")

    def test_explicit_token_overrides_current_scope(self):
        """Test that explicitly provided token overrides current_scope."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"REPLICATE_API_TOKEN": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope

        with mock.patch.dict(sys.modules, {"cog": mock_cog}):
            client = Replicate(bearer_token="explicit-token", base_url="http://test.example.com")
            assert client.bearer_token == "explicit-token"

    def test_explicit_async_token_overrides_current_scope(self):
        """Test that explicitly provided token overrides current_scope for async client."""
        mock_scope = mock.MagicMock()
        mock_scope.context = {"REPLICATE_API_TOKEN": "cog-token"}
        mock_cog = mock.MagicMock()
        mock_cog.current_scope.return_value = mock_scope

        with mock.patch.dict(sys.modules, {"cog": mock_cog}):
            client = AsyncReplicate(bearer_token="explicit-token", base_url="http://test.example.com")
            assert client.bearer_token == "explicit-token"
