# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx
import pytest
from httpx import URL

import replicate
from replicate import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES


def reset_state() -> None:
    replicate._reset_client()
    replicate.bearer_token = None or "My Bearer Token"
    replicate.base_url = None
    replicate.timeout = DEFAULT_TIMEOUT
    replicate.max_retries = DEFAULT_MAX_RETRIES
    replicate.default_headers = None
    replicate.default_query = None
    replicate.http_client = None


@pytest.fixture(autouse=True)
def reset_state_fixture() -> None:
    reset_state()


def test_base_url_option() -> None:
    assert replicate.base_url is None
    assert replicate.collections._client.base_url == URL("https://api.replicate.com/v1/")

    replicate.base_url = "http://foo.com"

    assert replicate.base_url == URL("http://foo.com")
    assert replicate.collections._client.base_url == URL("http://foo.com")


def test_timeout_option() -> None:
    assert replicate.timeout == replicate.DEFAULT_TIMEOUT
    assert replicate.collections._client.timeout == replicate.DEFAULT_TIMEOUT

    replicate.timeout = 3

    assert replicate.timeout == 3
    assert replicate.collections._client.timeout == 3


def test_max_retries_option() -> None:
    assert replicate.max_retries == replicate.DEFAULT_MAX_RETRIES
    assert replicate.collections._client.max_retries == replicate.DEFAULT_MAX_RETRIES

    replicate.max_retries = 1

    assert replicate.max_retries == 1
    assert replicate.collections._client.max_retries == 1


def test_default_headers_option() -> None:
    assert replicate.default_headers == None

    replicate.default_headers = {"Foo": "Bar"}

    assert replicate.default_headers["Foo"] == "Bar"
    assert replicate.collections._client.default_headers["Foo"] == "Bar"


def test_default_query_option() -> None:
    assert replicate.default_query is None
    assert replicate.collections._client._custom_query == {}

    replicate.default_query = {"Foo": {"nested": 1}}

    assert replicate.default_query["Foo"] == {"nested": 1}
    assert replicate.collections._client._custom_query["Foo"] == {"nested": 1}


def test_http_client_option() -> None:
    assert replicate.http_client is None

    original_http_client = replicate.collections._client._client
    assert original_http_client is not None

    new_client = httpx.Client()
    replicate.http_client = new_client

    assert replicate.collections._client._client is new_client
