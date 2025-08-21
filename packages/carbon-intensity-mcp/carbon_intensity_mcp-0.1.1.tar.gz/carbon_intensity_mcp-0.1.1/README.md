# Carbon Intensity MCP Server

An MCP (Model Context Protocol) server that provides access to the UK Carbon Intensity API from National Energy System Operator (NESO).

## Features

- Get current carbon intensity data for Great Britain
- Retrieve historical and forecast carbon intensity data
- Access regional carbon intensity data by postcode or region ID
- Get generation mix data (renewable vs non-renewable sources)
- Statistical analysis of carbon intensity trends
- Carbon intensity factors for different fuel types

## Installation

### From PyPI (Recommended)

```bash
# No installation needed - uvx will handle it automatically
uvx carbon-intensity-mcp --help
```

### From Source

```bash
git clone https://github.com/benomahony/carbon-intensity-mcp.git
cd carbon-intensity-mcp
uv sync
```

## Usage

### If using from PyPI

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "carbon-intensity": {
      "command": "uvx",
      "args": ["carbon-intensity-mcp"]
    }
  }
}
```

### If installed from source

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "carbon-intensity": {
      "command": "uv",
      "args": ["--directory", "/path/to/carbon-intensity-mcp", "run", "carbon-intensity-mcp"]
    }
  }
}
```

**Important**: Replace `/path/to/carbon-intensity-mcp` with the actual absolute path to your cloned repository.

For the example configuration provided:
```bash
cp example-config.json ~/.config/claude/mcp_servers.json
# Edit the path in the file to match your setup
```

## Testing

Test the server works:
```bash
# If using from PyPI
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | uvx carbon-intensity-mcp

# If installed from source
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | uv run carbon-intensity-mcp
```

## Available Tools

### National Intensity
- `get_current_intensity` - Get carbon intensity for current half hour
- `get_intensity_today` - Get carbon intensity for today
- `get_intensity_by_date` - Get carbon intensity for specific date
- `get_intensity_by_date_period` - Get carbon intensity for specific date and period
- `get_intensity_by_datetime` - Get carbon intensity for specific datetime
- `get_intensity_forward_24h` - Get 24h forward forecast
- `get_intensity_forward_48h` - Get 48h forward forecast  
- `get_intensity_past_24h` - Get past 24h data
- `get_intensity_range` - Get data for date range (max 14 days)

### Statistics
- `get_intensity_statistics` - Get statistics for date range (max 30 days)
- `get_intensity_statistics_blocks` - Get block average statistics

### Generation Mix
- `get_current_generation_mix` - Get current fuel mix
- `get_generation_mix_past_24h` - Get past 24h generation mix
- `get_generation_mix_range` - Get generation mix for date range

### Regional Data
- `get_regional_current` - Get all GB regions current data
- `get_regional_england` - Get England data
- `get_regional_scotland` - Get Scotland data
- `get_regional_wales` - Get Wales data
- `get_regional_by_postcode` - Get data by UK postcode
- `get_regional_by_region_id` - Get data by region ID

### Factors
- `get_intensity_factors` - Get carbon intensity factors by fuel type

## API Coverage

This server provides access to the complete UK Carbon Intensity API v2.0.0:

- **National Intensity**: Current, historical and forecast carbon intensity
- **Regional Intensity**: Regional data by postcode or region ID  
- **Generation Mix**: Fuel mix breakdown (gas, nuclear, renewables, etc.)
- **Statistics**: Statistical analysis of carbon intensity trends
- **Factors**: Carbon intensity factors by fuel type

## License

CC BY 4.0 (following the source API license)
