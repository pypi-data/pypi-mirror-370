"""
Shared pytest fixtures for the MCP Server tests.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.transit.gtfs_realtime_pb2 import FeedMessage  # pyright: ignore


@pytest.fixture
def mock_api_key():
    """Fixture to provide a mock API key for testing."""
    return "test-api-key"


@pytest.fixture
def mock_feed_message():
    """Fixture to create a mock FeedMessage."""
    feed = FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.timestamp = 0
    return feed.SerializeToString()


@pytest.fixture
def mock_http_response():
    """Fixture to provide a mock HTTP response."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    return mock_response


@pytest.fixture
def mock_server():
    """Fixture to provide a mock MCP Server."""
    server = MagicMock()
    server.list_tools.return_value = lambda f: f
    server.call_tool.return_value = lambda f: f
    server.create_initialization_options.return_value = {}
    return server


@pytest.fixture
def mock_httpx_client():
    """Fixture to provide a mock httpx client."""
    client_mock = AsyncMock()
    client_cm = AsyncMock()
    client_cm.__aenter__.return_value = client_mock
    
    with patch('httpx.AsyncClient', return_value=client_cm):
        yield client_mock
