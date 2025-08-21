import asyncio
import pytest
from unittest.mock import patch, AsyncMock

from carbon_intensity_mcp.server import make_api_request, call_tool
from mcp.types import TextContent


@pytest.mark.asyncio
async def test_make_api_request_success():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"data": [{"test": "value"}]}
        mock_response.raise_for_status = AsyncMock()
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await make_api_request("https://test.com")
        assert result == {"data": [{"test": "value"}]}


@pytest.mark.asyncio
async def test_make_api_request_error():
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
        
        result = await make_api_request("https://test.com")
        assert "error" in result


@pytest.mark.asyncio
async def test_get_current_intensity():
    mock_data = {
        "data": [
            {
                "from": "2018-01-20T12:00Z",
                "to": "2018-01-20T12:30Z",
                "intensity": {
                    "forecast": 266,
                    "actual": 263,
                    "index": "moderate"
                }
            }
        ]
    }
    
    with patch("carbon_intensity_mcp.server.make_api_request", return_value=mock_data):
        result = await call_tool("get_current_intensity", {})
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "moderate" in result[0].text


@pytest.mark.asyncio
async def test_unknown_tool():
    result = await call_tool("unknown_tool", {})
    assert len(result) == 1
    assert "Unknown tool" in result[0].text
