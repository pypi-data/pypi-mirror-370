# FB MCP Bratrax

A Model Context Protocol (MCP) server for Facebook/Meta Ads API integration, enabling programmatic access to Meta Ads data and management features.

## Features

- **Ad Account Management**: List and get details of ad accounts
- **Campaign Analytics**: Retrieve performance insights for campaigns, ad sets, and ads
- **Comprehensive Insights**: Access detailed metrics including impressions, clicks, spend, CTR, and more
- **Flexible Filtering**: Support for date ranges, breakdowns, and custom filtering
- **Pagination Support**: Automatic handling of large result sets

## Installation

```bash
pip install fb-mcp-bratrax
```

## Usage

Run the MCP server with your Facebook access token:

```bash
fb-mcp-bratrax --fb-token YOUR_FACEBOOK_ACCESS_TOKEN
```

## Requirements

- Python 3.8+
- Valid Facebook/Meta Ads API access token
- `mcp>=1.6.0`
- `requests>=2.32.3`

## Available Tools

The server provides access to Facebook Ads API through various MCP tools including account insights, campaign management, ad set analytics, and creative management.

For detailed documentation and setup instructions, visit the project repository.
