# CNHK MCP Server

A comprehensive Model Context Protocol (MCP) server for quantitative trading platform integration. This package provides a complete set of tools for interacting with quantitative trading APIs, managing simulations, and accessing financial data.

## Features

- **API Integration**: Complete API client for quantitative trading platforms
- **Simulation Management**: Create, monitor, and manage trading simulations
- **Data Access**: Retrieve datasets, data fields, and financial information
- **Alpha Management**: Comprehensive alpha factor management and analysis
- **Forum Integration**: Access to support forums and documentation
- **Performance Analysis**: Advanced performance metrics and correlation analysis
- **Competition Support**: Tools for trading competitions and leaderboards

## Installation

```bash
pip install cnhkmcp
```

## Quick Start

```python
from cnhkmcp import BrainApiClient

# Initialize client
client = BrainApiClient()

# Authenticate
await client.authenticate("your_email@example.com", "your_password")

# Create a simulation
simulation_data = {
    "type": "REGULAR",
    "settings": {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000"
    },
    "regular": "your_alpha_formula"
}

result = await client.create_simulation(simulation_data)
print(f"Simulation created: {result}")
```

## Main Components

### API Client (`pythonmcp.py`)
- Authentication and session management
- Simulation creation and monitoring
- Alpha factor management
- Data retrieval and analysis
- Performance metrics

### Forum Client (`forum_functions.py`)
- Glossary term extraction
- Forum post search and reading
- Support documentation access

## Usage Examples

### Authentication
```python
from cnhkmcp import authenticate

result = await authenticate("email@example.com", "password")
print(f"Authentication status: {result}")
```

### Create Simulation
```python
from cnhkmcp import create_simulation

result = await create_simulation(
    type="REGULAR",
    instrument_type="EQUITY",
    region="USA",
    universe="TOP3000",
    regular="your_alpha_formula_here"
)
```

### Get Alpha Details
```python
from cnhkmcp import get_alpha_details

alpha_info = await get_alpha_details("alpha_id_here")
print(f"Alpha details: {alpha_info}")
```

### Search Forum Posts
```python
from cnhkmcp import search_forum_posts

results = await search_forum_posts(
    email="email@example.com",
    password="password",
    search_query="alpha formula"
)
```

## Configuration

The package supports configuration through JSON files:

- `user_config.json`: User-specific settings
- `brain_config.json`: Platform configuration

## Requirements

- Python 3.8+
- Chrome browser (for forum functionality)
- Valid platform credentials

## Dependencies

- requests
- pandas
- selenium
- beautifulsoup4
- mcp
- pydantic

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support and questions, please refer to the documentation or create an issue in the repository. 