
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


class NTATool(str, Enum):
    """
    A class modeling the names of tools available for interacting with the NTA API.
    This enumeration defines the set of supported tool names that can be used to fetch
    trip updates, position updates, and service alerts from the NTA API.
    Attributes:
        - GET_TRIP_UPDATES: Retrieve trip update information.
        - GET_VEHICLES: Retrieve vehicle position information.
        - GTFSR: Retrieve raw GTFS real-time feed.
    """
    GTFSR = "get_gtfs_realtime"
    GET_TRIP_UPDATES = "get_trip_updates"
    GET_VEHICLES = "get_vehicles"

async def get_trip_updates(api_key: str) -> dict:
    """
    Fetch trip updates from the nta API.

    Args:
        api_key: API key for authentication.
        url: Endpoint URL for trip updates.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://api.nationaltransport.ie/gtfsr/v2/TripUpdates"
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'Cache-Control': 'no-cache',
                "x-api-key": api_key
            }
            response = await client.get(base_url, headers=headers)
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

async def get_vehicles(api_key: str) -> dict:
    """
    Fetch position updates from the nta API.

    Args:
        api_key: API key for authentication.
        url: Endpoint URL for position updates.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://api.nationaltransport.ie/gtfsr/v2/Vehicles"
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'Cache-Control': 'no-cache',
                "x-api-key": api_key
            }
            response = await client.get(base_url, headers=headers)
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

async def get_gtfs_realtime(api_key: str) -> dict:
    """
    Fetch service alerts from the nta API.

    Args:
        api_key: API key for authentication.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        McpError: If the request fails or returns an error.
    """
    base_url = "https://api.nationaltransport.ie/gtfsr/v2/gtfsr"
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'Cache-Control': 'no-cache',
                "x-api-key": api_key
            }
            response = await client.get(base_url, headers=headers)
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

    server = Server("mcp-nta")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=NTATool.GET_TRIP_UPDATES.value,
                description="Retrieves trip update information from the NTA API.",
                inputSchema={}),
            Tool(
                name=NTATool.GET_VEHICLES.value,
                description="Retrieves vehicle information from the NTA API.",
                inputSchema={}),
            Tool(
                name=NTATool.GTFSR.value,
                description="Retrieves real-time transit information from the NTA API.",
                inputSchema={}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        match name:
            case NTATool.GET_TRIP_UPDATES:
                result = await get_trip_updates(api_key)
                return result

            case NTATool.GET_VEHICLES:
                result = await get_vehicles(api_key)
                return result

            case NTATool.GTFSR:
                result = await get_gtfs_realtime(api_key)
                return result

            case _:
                raise ValueError(f"Unknown tool: {name}")


    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)