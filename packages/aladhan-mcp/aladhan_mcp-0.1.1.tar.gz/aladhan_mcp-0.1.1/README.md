# Aladhan MCP Server

A Model Context Protocol (MCP) server that provides comprehensive tools for accessing Islamic prayer times and calendar data through the Aladhan API. Built with FastMCP for modern MCP compatibility and type safety.

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/aladhan-mcp.svg?logo=pypi&logoColor=white)](https://pypi.org/project/aladhan-mcp/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0-purple.svg)](https://github.com/jlowin/fastmcp)
[![Aladhan API](https://img.shields.io/badge/Aladhan-6.1.0-yellow.svg)](https://aladhan.com/prayer-times-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Installation](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Documentation](#available-tools)

</div>

## Table of Contents

  - [Features](#features)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Quick Test](#quick-test)
  - [Usage](#usage)
    - [As an MCP Server](#as-an-mcp-server)
    - [Direct Usage](#direct-usage)
    - [Testing](#testing)
  - [Available Tools](#available-tools)
    - [Date Conversion Tools](#date-conversion-tools)
    - [Prayer Time Tools](#prayer-time-tools)
    - [Qibla Tool](#qibla-tool)
    - [Calendar Tools](#calendar-tools)
  - [Configuration Options](#configuration-options)
  - [Examples](#examples)
  - [Development](#development)
    - [Setup Development Environment](#setup-development-environment)
    - [Running Tests](#running-tests)
    - [Code Quality](#code-quality)
    - [Project Commands](#project-commands)
  - [API Reference](#api-reference)
  - [Contributing](#contributing)
    - [Development Guidelines](#development-guidelines)
  - [License](#license)
  - [Acknowledgments](#acknowledgments)
  - [Current Status](#current-status)
  - [Support](#support)

## Features

- **Prayer Times**: Get daily prayer times by coordinates or city with multiple calculation methods
- **Qibla Direction**: Calculate qibla direction (bearing) from any coordinates
- **Date Conversion**: Convert between Gregorian and Hijri calendars
- **Calendar Data**: Monthly prayer calendars in both Gregorian and Hijri formats
- **Calculation Methods**: Support for 24+ prayer calculation methods worldwide
- **Global Coverage**: Support for cities worldwide with timezone handling
- **Modern Architecture**: FastMCP with type annotations for robust tool schemas
- **Easy Integration**: Simple setup and configuration for MCP clients

## Quick Start

```bash
pip install aladhan-mcp
python -m aladhan_mcp.server
```

### Prerequisites

- Python 3.8 or higher
- pip or another Python package manager

### Installation

You can install directly from PyPI:

```bash
pip install aladhan-mcp
```

Or, if you want the latest development version:

```bash
git clone https://github.com/rawsab/aladhan-MCP-server.git
cd aladhan-mcp
pip install -e ".[dev]"
```

### Quick Test

```bash
# Test that all tools register correctly
python -c "from aladhan_mcp.server import register_all_tools; register_all_tools(); print('All tools registered successfully!')"

# Run tests
pytest -v
```

## Usage

### As an MCP Server

The server can be used with any MCP client. Configure your MCP client to use:

```json
{
  "mcpServers": {
    "aladhan": {
      "command": "python",
      "args": ["-m", "aladhan_mcp.server"]
    }
  }
}
```

**Note**: This server uses FastMCP with type annotations for tool schemas, ensuring compatibility with modern MCP clients.

### Direct Usage

```bash
# Run the server directly
python -m aladhan_mcp.server

# Test that tools register correctly
python -c "from aladhan_mcp.server import register_all_tools; register_all_tools(); print('All tools registered!')"
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v
```

## Available Tools

### Date Conversion Tools
- **`list_calculation_methods`** - List all  prayer calculation methods
- **`convert_gregorian_to_hijri`** - Convert Gregorian date to Hijri (YYYY-MM-DD format)
- **`convert_hijri_to_gregorian`** - Convert Hijri date to Gregorian (DD-MM-YYYY format)

### Prayer Time Tools
- **`get_prayer_times`** - Get daily prayer times by coordinates
- **`get_prayer_times_by_city`** - Get daily prayer times by city/country
- **`get_next_prayer`** - Get the next prayer time for given coordinates

### Qibla Tool
- **`get_qibla`** - Get Qibla direction (bearing in degrees) from coordinates

### Calendar Tools
- **`get_hijri_calendar_by_city`** - Get Hijri month prayer times by city
- **`get_hijri_calendar`** - Get Hijri month prayer times by coordinates
- **`get_monthly_calendar`** - Get Gregorian month prayer times by coordinates
- **`get_monthly_calendar_by_city`** - Get Gregorian month prayer times by city

## Configuration Options

### Prayer Calculation Methods

The server supports 24+ prayer calculation methods worldwide:

| Method | Name | Region |
|--------|------|--------|
| **0** | Shia Ithna-Ashari | Shia |
| **1** | University of Islamic Sciences, Karachi | Pakistan |
| **2** | Islamic Society of North America (ISNA) | North America |
| **3** | Muslim World League | Worldwide |
| **4** | Umm Al-Qura University, Makkah | Saudi Arabia |
| **5** | Egyptian General Authority of Survey | Egypt |
| **6** | Institute of Geophysics, University of Tehran | Iran |
| **7** | Gulf Region | Gulf Countries |
| **8** | Kuwait | Kuwait |
| **9** | Qatar | Qatar |
| **10** | Majlis Ugama Islam Singapura | Singapore |
| **11** | Union Organization islamic de France | France |
| **12** | Diyanet İşleri Başkanlığı | Turkey |
| **13** | Spiritual Administration of Muslims of Russia | Russia |
| **14** | Moonsighting Committee Worldwide | Worldwide |
| **15** | Dubai (unofficial) | Dubai |
| **16-23** | University of Tehran variants | Iran |
| **99** | Custom | Custom |

### Islamic Schools

- **0**: Shafi (default) - Used in most of the world
- **1**: Hanafi - Used in South Asia and Turkey

### Latitude Adjustment Methods

- **1**: Middle of the night
- **2**: One seventh of the night  
- **3**: Angle-based method

## Examples

### Prayer Times

```python
# Get prayer times for London
get_prayer_times_by_city(
    city="London",
    country="United Kingdom",
    date="15-01-2025",
    method=3,  # Muslim World League
    school=0   # Shafi
)

# Get prayer times for New York coordinates
get_prayer_times(
    lat=40.7128,
    lon=-74.0060,
    date="15-01-2025",
    method=3,  # Muslim World League
    school=0   # Shafi
)

# Get next prayer time
get_next_prayer(
    lat=40.7128,
    lon=-74.0060,
    method=3
)
```

### Qibla Direction

```python
# Get qibla direction from New York
get_qibla(
    lat=40.7128,
    lon=-74.0060
)
```

### Date Conversion

```python
# Convert Gregorian to Hijri
convert_gregorian_to_hijri(date="2025-01-15")

# Convert Hijri to Gregorian
convert_hijri_to_gregorian(date="15-07-1446")

# List all calculation methods
list_calculation_methods()
```

### Calendar Data

```python
# Get Gregorian month calendar by coordinates
get_monthly_calendar(
    year=2025,
    month=1,
    lat=40.7128,
    lon=-74.0060,
    method=3,  # Muslim World League
    school=0   # Shafi
)

# Get Gregorian month calendar by city
get_monthly_calendar_by_city(
    year=2025,
    month=1,
    city="London",
    country="United Kingdom",
    method=3,  # Muslim World League
    school=0   # Shafi
)

# Get Hijri month calendar by coordinates
get_hijri_calendar(
    year=1446,
    month=7,
    lat=40.7128,
    lon=-74.0060,
    method=3,  # Muslim World League
    school=0   # Shafi
)

# Get Hijri month calendar by city
get_hijri_calendar_by_city(
    year=1446,
    month=7,
    city="London",
    country="United Kingdom",
    method=3,  # Muslim World League
    school=0   # Shafi
)
```

## Development

### Setup Development Environment

You can install development dependencies directly from PyPI:

```bash
pip install "aladhan-mcp[dev]"
```

Or clone the repository if you want to work on the source:

```bash
# Clone the repository
git clone https://github.com/rawsab/aladhan-MCP-server.git
cd aladhan-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=aladhan_mcp

# Run specific test file
pytest tests/test_prayer_times.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black aladhan_mcp/

# Sort imports
isort aladhan_mcp/

# Lint code
flake8 aladhan_mcp/

# Type checking
mypy aladhan_mcp/
```

### Project Commands

```bash
# Test tool registration
python -c "from aladhan_mcp.server import register_all_tools; register_all_tools(); print('All tools registered!')"

# Start server
python -m aladhan_mcp.server
```

## API Reference

The server uses the [Aladhan API](https://aladhan.com/prayer-times-api) for all prayer time calculations. All tools return structured JSON responses with comprehensive prayer time data.

### Tool Parameters

All tools use Python type annotations for parameter validation:

- **Required parameters**: Must be provided
- **Optional parameters**: Can be omitted (default to `None`)
- **Type validation**: Automatic validation based on type hints
- **Return type**: All tools return `str` (JSON-formatted response)

### Error Handling

Tools will raise `ValueError` for invalid parameters or missing required fields. The server handles these gracefully and returns appropriate error messages.

### Response Format

All tools return JSON-formatted strings containing:
- **Success responses**: Structured data from the Aladhan API
- **Error responses**: Error messages with details about what went wrong
- **Validation errors**: Clear messages about invalid parameters

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style (use `black` and `isort`)
- Add tests for new functionality
- Update documentation for new features
- Ensure all tests pass before submitting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Aladhan API](https://aladhan.com/) for providing the prayer times data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP framework
- [FastMCP](https://github.com/jlowin/fastmcp) for the modern MCP server framework

## Current Status

### Working Features
- **Date Conversion Tools**: All 3 date conversion tools fully functional
- **Prayer Time Tools**: All 3 prayer time tools work with coordinates and cities
- **Qibla Tool**: Qibla direction calculation working perfectly
- **Calendar Tools**: All 4 calendar tools converted to FastMCP format
- **FastMCP Integration**: Modern MCP compatibility with type annotations
- **Server Transport**: Fully functional stdio transport
- **Testing**: Comprehensive test suite with passing tests
- **Documentation**: Complete API reference and usage examples

### In Progress
- **Enhanced Testing**: Adding more comprehensive integration tests
- **Performance Optimization**: Caching improvements and response optimization

### Roadmap
- Additional prayer calculation methods
- Enhanced error handling and validation
- Performance optimizations
- Extended calendar functionality

## Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/rawsab/aladhan-mcp/issues) page
2. Create a new issue with detailed information
3. Include your Python version, operating system, and any error messages
4. Provide example code that reproduces the issue

### Common Issues

- **Transport errors**: Ensure you're using the correct MCP client configuration
- **Tool registration errors**: Verify all dependencies are installed correctly
- **API errors**: Check your internet connection and the Aladhan API status

---

<div align="center">

**Made with ❤️ by [Rawsab Said](https://github.com/rawsabsaid)**

[GitHub](https://github.com/rawsab/aladhan-MCP-server) • [PyPI](https://pypi.org/project/aladhan-mcp/) • [Issues](https://github.com/rawsab/aladhan-mcp/issues)

</div>
