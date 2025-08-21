[English](README.md) | [日本語](README_ja.md) | **README**

# DateTime MCP Server

A Model Context Protocol (MCP) server that provides tools to get the current date and time in various formats. This is a Python implementation of the datetime MCP server, demonstrating how to build MCP servers using the Python SDK.

## Features

- Get current date and time in multiple formats (ISO, Unix timestamp, human-readable, etc.)
- Configurable output format via environment variables
- Timezone support
- Custom date format support
- Simple tool: `get_current_time`

## Usage

Choose one of these examples based on your needs:

**Basic usage (ISO format):**

```json
{
  "mcpServers": {
    "datetime": {
      "command": "uvx",
      "args": ["takanarishimbo-datetime-mcp-server"]
    }
  }
}
```

**Human-readable format with timezone:**

```json
{
  "mcpServers": {
    "datetime": {
      "command": "uvx",
      "args": ["takanarishimbo-datetime-mcp-server"],
      "env": {
        "DATETIME_FORMAT": "human",
        "TIMEZONE": "America/New_York"
      }
    }
  }
}
```

**Unix timestamp format:**

```json
{
  "mcpServers": {
    "datetime": {
      "command": "uvx",
      "args": ["takanarishimbo-datetime-mcp-server"],
      "env": {
        "DATETIME_FORMAT": "unix",
        "TIMEZONE": "UTC"
      }
    }
  }
}
```

**Custom format:**

```json
{
  "mcpServers": {
    "datetime": {
      "command": "uvx",
      "args": ["takanarishimbo-datetime-mcp-server"],
      "env": {
        "DATETIME_FORMAT": "custom",
        "DATE_FORMAT_STRING": "%Y/%m/%d %H:%M",
        "TIMEZONE": "Asia/Tokyo"
      }
    }
  }
}
```

## Configuration

The server can be configured using environment variables:

### `DATETIME_FORMAT`

Controls the default output format of the datetime (default: "iso")

Supported formats:

- `iso`: ISO 8601 format (2024-01-01T12:00:00.000000+00:00)
- `unix`: Unix timestamp in seconds
- `unix_ms`: Unix timestamp in milliseconds
- `human`: Human-readable format (Mon, Jan 1, 2024 12:00:00 PM UTC)
- `date`: Date only (2024-01-01)
- `time`: Time only (12:00:00)
- `custom`: Custom format using DATE_FORMAT_STRING environment variable

### `DATE_FORMAT_STRING`

Custom date format string (only used when DATETIME_FORMAT="custom")
Default: "%Y-%m-%d %H:%M:%S"

Uses Python's strftime format codes:

- `%Y`: 4-digit year
- `%y`: 2-digit year
- `%m`: 2-digit month
- `%d`: 2-digit day
- `%H`: 2-digit hour (24-hour)
- `%M`: 2-digit minute
- `%S`: 2-digit second

### `TIMEZONE`

Timezone to use (default: "UTC")
Examples: "UTC", "America/New_York", "Asia/Tokyo"

## Available Tools

### `get_current_time`

Get the current date and time

Parameters:

- `format` (optional): Output format, overrides DATETIME_FORMAT env var
- `timezone` (optional): Timezone to use, overrides TIMEZONE env var

## Development

1. **Clone this repository**

   ```bash
   git clone https://github.com/TakanariShimbo/uvx-datetime-mcp-server.git
   cd uvx-datetime-mcp-server
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Run the server**

   ```bash
   uv run takanarishimbo-datetime-mcp-server
   ```

4. **Test with MCP Inspector (optional)**

   ```bash
   npx @modelcontextprotocol/inspector uv run takanarishimbo-datetime-mcp-server
   ```

## Publishing to PyPI

This project uses PyPI's Trusted Publishers feature for secure, token-less publishing via GitHub Actions.

### 1. Configure PyPI Trusted Publisher

1. **Log in to PyPI** (create account if needed)

   - Go to https://pypi.org/

2. **Navigate to Publishing Settings**

   - Go to your account settings
   - Click on "Publishing" or go to https://pypi.org/manage/account/publishing/

3. **Add GitHub Publisher**
   - Click "Add a new publisher"
   - Select "GitHub" as the publisher
   - Fill in:
     - **Owner**: `TakanariShimbo` (your GitHub username/org)
     - **Repository**: `uvx-datetime-mcp-server`
     - **Workflow name**: `pypi-publish.yml`
     - **Environment**: `pypi` (optional but recommended)
   - Click "Add"

### 2. Configure GitHub Environment (Recommended)

1. **Navigate to Repository Settings**

   - Go to your GitHub repository
   - Click "Settings" → "Environments"

2. **Create PyPI Environment**
   - Click "New environment"
   - Name: `pypi`
   - Configure protection rules (optional):
     - Add required reviewers
     - Restrict to specific branches/tags

### 3. Setup GitHub Personal Access Token (for release script)

The release script needs to push to GitHub, so you'll need a GitHub token:

1. **Create GitHub Personal Access Token**

   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Set expiration (recommended: 90 days or custom)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - Copy the generated token (starts with `ghp_`)

2. **Configure Git with Token**

   ```bash
   # Option 1: Use GitHub CLI (recommended)
   gh auth login

   # Option 2: Configure git to use token
   git config --global credential.helper store
   # Then when prompted for password, use your token instead
   ```

### 4. Release New Version

Use the release script to automatically version, tag, and trigger publishing:

```bash
# First time setup
chmod +x scripts/release.sh

# Increment patch version (0.1.0 → 0.1.1)
./scripts/release.sh patch

# Increment minor version (0.1.0 → 0.2.0)
./scripts/release.sh minor

# Increment major version (0.1.0 → 1.0.0)
./scripts/release.sh major

# Set specific version
./scripts/release.sh 1.2.3
```

### 5. Verify Publication

1. **Check GitHub Actions**

   - Go to "Actions" tab in your repository
   - Verify the "Publish to PyPI" workflow completed successfully

2. **Verify PyPI Package**
   - Visit: https://pypi.org/project/takanarishimbo-datetime-mcp-server/
   - Or run: `pip show takanarishimbo-datetime-mcp-server`

### Release Process Flow

1. `release.sh` script updates version in all files
2. Creates git commit and tag
3. Pushes to GitHub
4. GitHub Actions workflow triggers on new tag
5. Workflow uses OIDC to authenticate with PyPI (no tokens needed!)
6. Workflow builds project and publishes to PyPI
7. Package becomes available globally via `pip install` or `uvx`

## Code Quality

This project uses `ruff` for linting and formatting:

```bash
# Run linter
uv run ruff check

# Fix linting issues
uv run ruff check --fix

# Format code
uv run ruff format
```

## Project Structure

```
uvx-datetime-mcp-server/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Main entry point
│   └── server.py                # Server implementation
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
├── .github/
│   └── workflows/
│       └── pypi-publish.yml     # PyPI publish workflow with Trusted Publishers
├── scripts/
│   └── release.sh               # Release automation script
├── docs/
│   ├── README.md                # This file
│   └── README_ja.md             # Japanese documentation
└── .gitignore                   # Git ignore file
```

## License

MIT
