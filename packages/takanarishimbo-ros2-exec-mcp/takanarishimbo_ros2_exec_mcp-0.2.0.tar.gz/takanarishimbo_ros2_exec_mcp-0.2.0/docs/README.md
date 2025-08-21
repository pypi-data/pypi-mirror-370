[English](README.md) | [日本語](README_ja.md) | **README**

# ROS2 Exec MCP Server

A Model Context Protocol (MCP) server that executes ROS 2 (`ros2`) CLI commands.

## Features

- Execute ROS 2 CLI commands (e.g., `ros2 topic list`, `ros2 node list`)
- Configurable default timeout via environment variable
- Optional working directory control
- Secure by default: only allows commands starting with `ros2` (overridable)

## Usage

Below are examples for both stdio and streamable-http.

### Stdio (default)

MCP client example:

```json
{
  "mcpServers": {
    "ros2": {
      "command": "uvx",
      "args": ["takanarishimbo-ros2-exec-mcp"]
    }
  }
}
```

You can also configure timeout, default working directory, or allow non-ros2 commands:

```json
{
  "mcpServers": {
    "ros2": {
      "command": "uvx",
      "args": ["takanarishimbo-ros2-exec-mcp"],
      "env": {
        "ROS2_EXEC_TIMEOUT": "60",
        "DEFAULT_CWD": "/your/ros2/ws",
        "ALLOW_NON_ROS2": "true",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### streamable-http

Start the MCP server on the robot side first:

```bash
MCP_TRANSPORT=streamable-http uv run takanarishimbo-ros2-exec-mcp
```

MCP client example:

```json
{
  "mcpServers": {
    "ros2": {
      "url": "http://xxx.xxx.xxx.xxx:8000",
      "env": {
        "MCP_TRANSPORT": "streamable-http"
      }
    }
  }
}
```

## Environment Variables

- `ROS2_EXEC_TIMEOUT`: Default timeout seconds for command execution (default: `30`)
- `DEFAULT_CWD`: Default working directory for command execution (optional)
- `ALLOW_NON_ROS2`: If set to `true`, allows executing non-`ros2` commands (default: `false`)
- `MCP_TRANSPORT`: Transport mode. `stdio` (default) or `streamable-http`

## Available Tools

### `ros2_exec`

Execute a ROS 2 CLI command.

Parameters:

- `command` (required): Full command string, e.g., `"ros2 topic list"`
- `timeout` (optional): Timeout seconds (overrides `ROS2_EXEC_TIMEOUT`)
- `cwd` (optional): Working directory (overrides `DEFAULT_CWD`)

Returns combined stdout/stderr and exit code.

## Development

1.  Clone and install dependencies with `uv`:

    ```bash
    uv sync
    ```

2.  Run the server:

    ```bash
    uv run takanarishimbo-ros2-exec-mcp
    ```

3.  Test with MCP Inspector (optional):

    ```bash
    npx @modelcontextprotocol/inspector uv run takanarishimbo-ros2-exec-mcp
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
     - **Repository**: `ros2-exec-mcp`
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
   - Visit: https://pypi.org/project/takanarishimbo-ros2-exec-mcp/
   - Or run: `pip show takanarishimbo-ros2-exec-mcp`

### Release Process Flow

1. `release.sh` script updates version in all files
2. Creates git commit and tag
3. Pushes to GitHub
4. GitHub Actions workflow triggers on new tag
5. Workflow uses OIDC to authenticate with PyPI (no tokens needed!)
6. Workflow builds project and publishes to PyPI
7. Package becomes available globally via `pip install` or `uvx`

## Code Quality

Uses `ruff` for linting and formatting:

```bash
uv run ruff check
uv run ruff check --fix
uv run ruff format
```

## Project Structure

```
ros2-exec-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   └── server.py
├── pyproject.toml
├── uv.lock
├── .github/
│   └── workflows/
│       └── pypi-publish.yml
├── scripts/
│   └── release.sh
├── docs/
│   ├── README.md
│   └── README_ja.md
└── .gitignore
```

## License

MIT
