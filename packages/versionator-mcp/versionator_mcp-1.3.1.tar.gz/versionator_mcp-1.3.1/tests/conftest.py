"""
Shared test configuration and fixtures for Versionator MCP Server tests
"""

import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

# Skip tests that hit GitHub API during CI to avoid rate limits
skip_github_api = pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Skip GitHub API tests in CI to avoid rate limits"
)


class MockResponse:
    """Mock HTTP response for testing"""

    def __init__(self, status: int, json_data=None, text_data=None):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data

    async def json(self):
        if self._json_data is not None:
            return self._json_data
        raise aiohttp.ContentTypeError("", "")

    async def text(self):
        return self._text_data or ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockSession:
    """Mock HTTP session for testing"""

    def __init__(self, response: MockResponse):
        self.response = response

    def get(self, url, **kwargs):
        return self.response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_response_200():
    """Fixture for successful HTTP response"""
    return MockResponse(200, json_data={"version": "1.0.0"})


@pytest.fixture
def mock_response_404():
    """Fixture for not found HTTP response"""
    return MockResponse(404, text_data="Not found")


@pytest.fixture
def mock_response_500():
    """Fixture for server error HTTP response"""
    return MockResponse(500, text_data="Internal server error")


@pytest.fixture
def mock_session_200(mock_response_200):
    """Fixture for successful HTTP session"""
    return MockSession(mock_response_200)


@pytest.fixture
def mock_session_404(mock_response_404):
    """Fixture for not found HTTP session"""
    return MockSession(mock_response_404)


@pytest.fixture
def mock_session_500(mock_response_500):
    """Fixture for server error HTTP session"""
    return MockSession(mock_response_500)
