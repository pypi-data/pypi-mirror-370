#!/usr/bin/env python3
"""Carbon Intensity MCP Server - UK Carbon Intensity API via MCP."""

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from .models import (
    ErrorResponse,
    FactorsResponse,
    GenerationResponse,
    IntensityResponse,
    RegionalByIdResponse,
    RegionalResponse,
    StatisticsResponse,
)

__version__ = "0.1.0"

mcp = FastMCP("carbon-intensity")
BASE_URL = "https://api.carbonintensity.org.uk"


class APIError(Exception):
    """Exception raised when API request fails."""
    pass


async def make_api_request(url: str) -> dict[str, Any]:
    """Make an API request to the Carbon Intensity API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise APIError(f"API request failed: {e}")


@mcp.tool()
async def get_current_intensity() -> dict[str, Any]:
    """Get carbon intensity data for the current half hour."""
    url = f"{BASE_URL}/intensity"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_today() -> dict[str, Any]:
    """Get carbon intensity data for today."""
    url = f"{BASE_URL}/intensity/date"
    data = await make_api_request(url)
    return data

@mcp.tool()
async def get_intensity_by_date(date: str) -> dict[str, Any]:
    """Get carbon intensity data for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., 2017-08-25)
    """
    url = f"{BASE_URL}/intensity/date/{date}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_by_date_period(date: str, period: int) -> dict[str, Any]:
    """Get carbon intensity data for a specific date and half hour period.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., 2017-08-25)
        period: Half hour settlement period between 1-48 (e.g., 42)
    """
    url = f"{BASE_URL}/intensity/date/{date}/{period}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_factors() -> dict[str, Any]:
    """Get carbon intensity factors for each fuel type."""
    url = f"{BASE_URL}/intensity/factors"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_by_datetime(datetime: str) -> dict[str, Any]:
    """Get carbon intensity data for a specific datetime.
    
    Args:
        datetime: Datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/intensity/{datetime}"
    data = await make_api_request(url)
    return data

@mcp.tool()
async def get_intensity_forward_24h(datetime: str) -> dict[str, Any]:
    """Get carbon intensity data 24hrs forwards from specific datetime.
    
    Args:
        datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/intensity/{datetime}/fw24h"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_forward_48h(datetime: str) -> dict[str, Any]:
    """Get carbon intensity data 48hrs forwards from specific datetime.
    
    Args:
        datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/intensity/{datetime}/fw48h"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_past_24h(datetime: str) -> dict[str, Any]:
    """Get carbon intensity data 24hrs in the past of a specific datetime.
    
    Args:
        datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/intensity/{datetime}/pt24h"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_range(from_datetime: str, to_datetime: str) -> dict[str, Any]:
    """Get carbon intensity data between from and to datetime (max 14 days).
    
    Args:
        from_datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
        to_datetime: End datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/intensity/{from_datetime}/{to_datetime}"
    data = await make_api_request(url)
    return data

@mcp.tool()
async def get_intensity_statistics(from_datetime: str, to_datetime: str) -> dict[str, Any]:
    """Get carbon intensity statistics between from and to datetime (max 30 days).
    
    Args:
        from_datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
        to_datetime: End datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-26T17:00Z)
    """
    url = f"{BASE_URL}/intensity/stats/{from_datetime}/{to_datetime}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_intensity_statistics_blocks(from_datetime: str, to_datetime: str, block_hours: int) -> dict[str, Any]:
    """Get block average carbon intensity statistics (max 30 days).
    
    Args:
        from_datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
        to_datetime: End datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-26T17:00Z)
        block_hours: Block length in hours (1-24)
    """
    url = f"{BASE_URL}/intensity/stats/{from_datetime}/{to_datetime}/{block_hours}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_current_generation_mix() -> dict[str, Any]:
    """Get generation mix for current half hour."""
    url = f"{BASE_URL}/generation"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_generation_mix_past_24h(datetime: str) -> dict[str, Any]:
    """Get generation mix for the past 24 hours.
    
    Args:
        datetime: Datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/generation/{datetime}/pt24h"
    data = await make_api_request(url)
    return data

@mcp.tool()
async def get_generation_mix_range(from_datetime: str, to_datetime: str) -> dict[str, Any]:
    """Get generation mix between from and to datetimes.
    
    Args:
        from_datetime: Start datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
        to_datetime: End datetime in ISO8601 format YYYY-MM-DDThh:mmZ (e.g., 2017-08-25T12:35Z)
    """
    url = f"{BASE_URL}/generation/{from_datetime}/{to_datetime}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_regional_current() -> dict[str, Any]:
    """Get carbon intensity data for current half hour for all GB regions."""
    url = f"{BASE_URL}/regional"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_regional_england() -> dict[str, Any]:
    """Get carbon intensity data for current half hour for England."""
    url = f"{BASE_URL}/regional/england"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_regional_scotland() -> dict[str, Any]:
    """Get carbon intensity data for current half hour for Scotland."""
    url = f"{BASE_URL}/regional/scotland"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_regional_wales() -> dict[str, Any]:
    """Get carbon intensity data for current half hour for Wales."""
    url = f"{BASE_URL}/regional/wales"
    data = await make_api_request(url)
    return data

@mcp.tool()
async def get_regional_by_postcode(postcode: str) -> dict[str, Any]:
    """Get carbon intensity data for current half hour by postcode.
    
    Args:
        postcode: Outward postcode (e.g., RG41, SW1, TF8) - do not include full postcode
    """
    url = f"{BASE_URL}/regional/postcode/{postcode}"
    data = await make_api_request(url)
    return data


@mcp.tool()
async def get_regional_by_region_id(region_id: int) -> dict[str, Any]:
    """Get carbon intensity data for current half hour by region ID.
    
    Args:
        region_id: Region ID of GB region
    """
    url = f"{BASE_URL}/regional/regionid/{region_id}"
    data = await make_api_request(url)
    return data


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
