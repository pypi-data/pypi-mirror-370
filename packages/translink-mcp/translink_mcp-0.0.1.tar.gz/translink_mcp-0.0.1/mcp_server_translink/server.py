
import logging
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    INTERNAL_ERROR,
)
import httpx
import json
from enum import Enum
from google.protobuf.json_format import MessageToJson
from google.transit.gtfs_realtime_pb2 import FeedMessage  # pyright: ignore


class TranslinkTool(str, Enum):
    """
    A class modeling the names of tools available for interacting with the Translink API.
    This enumeration defines the set of supported tool names that can be used to fetch
    trip updates, position updates, and service alerts from the Translink API.
    Attributes:
        GET_TRIP_UPDATES: Tool name for retrieving trip update information.
        GET_POSITION_UPDATES: Tool name for retrieving position update information.
        GET_SERVICE_ALERTS: Tool name for retrieving service alert information.
    """
    GET_TRIP_UPDATES = "get_trip_updates"
    GET_POSITION_UPDATES = "get_position_updates"
    GET_SERVICE_ALERTS = "get_service_alerts"

async def get_trip_updates(api_key: str) -> dict:
    """
    Fetch trip updates from the Translink API.

    Args:
        api_key: API key for authentication.
        url: Endpoint URL for trip updates.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://gtfsapi.translink.ca/v3/gtfsrealtime?apikey="
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/x-protobuf"}
            response = await client.get(f"{base_url}{api_key}", headers=headers)
            response.raise_for_status()
            
            # Parse the protobuf message
            feed = FeedMessage()
            feed.ParseFromString(response.content)
            
            # Convert to JSON using MessageToJson
            json_str = MessageToJson(feed)
            result = json.loads(json_str)
            
            return result
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch trip updates: {e}"))

async def get_position_updates(api_key: str) -> dict:
    """
    Fetch position updates from the Translink API.

    Args:
        api_key: API key for authentication.
        url: Endpoint URL for position updates.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://gtfsapi.translink.ca/v3/gtfsposition?apikey="
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/x-protobuf"}
            response = await client.get(f"{base_url}{api_key}", headers=headers)
            response.raise_for_status()
            
            # Parse the protobuf message
            feed = FeedMessage()
            feed.ParseFromString(response.content)
            
            # Convert to JSON using MessageToJson
            json_str = MessageToJson(feed)
            result = json.loads(json_str)
            
            return result
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch position updates: {e}"))

async def get_service_alerts(api_key: str) -> dict:
    """
    Fetch service alerts from the Translink API.

    Args:
        api_key: API key for authentication.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://gtfsapi.translink.ca/v3/gtfsalerts?apikey="
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/x-protobuf"}
            response = await client.get(f"{base_url}{api_key}", headers=headers)
            response.raise_for_status()
            
            # Parse the protobuf message
            feed = FeedMessage()
            feed.ParseFromString(response.content)
            
            # Convert to JSON using MessageToJson
            json_str = MessageToJson(feed)
            result = json.loads(json_str)
            
            return result
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch service alerts: {e}"))

async def serve(
    api_key: str,
) -> None:
    """Run the fetch MCP server.

    Args:
        api_key: API key to use for requests
    """
    logger = logging.getLogger(__name__)

    server = Server("mcp-translink")

    logger.info("The Translink MCP server has started.")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=TranslinkTool.GET_TRIP_UPDATES.value,
                description="Retrieves trip update information from the Translink API.",
                inputSchema={}),
            Tool(
                name=TranslinkTool.GET_POSITION_UPDATES.value,
                description="Retrieves position update information from the Translink API.",
                inputSchema={}),
            Tool(
                name=TranslinkTool.GET_SERVICE_ALERTS.value,
                description="Retrieves service alert information from the Translink API.",
                inputSchema={}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        match name:
            case TranslinkTool.GET_TRIP_UPDATES:
                result = await get_trip_updates(api_key)
                return result

            case TranslinkTool.GET_POSITION_UPDATES:
                result = await get_position_updates(api_key)
                return result

            case TranslinkTool.GET_SERVICE_ALERTS:
                result = await get_service_alerts(api_key)
                return result

            case _:
                raise ValueError(f"Unknown tool: {name}")


    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)