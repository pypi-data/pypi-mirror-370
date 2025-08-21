# EPAM AI/Run CodeMie Plugins CLI

A command-line interface for running AI/Run CodeMie Plugins toolkits.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
  - [Using pip](#using-pip)
  - [From Source](#from-source)
- [Configuration](#configuration)
  - [Setting Up Your Plugin Key](#setting-up-your-plugin-key)
  - [Configuration File](#configuration-file)
  - [Environment Variables](#environment-variables)
- [Commands](#commands)
  - [Global Options](#global-options)
  - [List Command](#list-command)
  - [Config Command](#config-command)
  - [MCP Command](#mcp-command)
  - [Development Command](#development-command)
- [Code Command](#code-command)
- [Custom MCP Servers](#custom-mcp-servers)
- [Graceful Shutdown](#graceful-shutdown)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

The CodeMie Plugins CLI provides a convenient way to interact with CodeMie toolkits and MCP (Model Context Protocol) servers. It offers a unified interface for:

- Running development toolkits on repositories
- Managing and running MCP servers
- Configuring plugin settings
- Listing available commands and toolkits

This CLI is designed to be cross-platform and easy to use, with a focus on developer experience.

## Installation

### Using uvx (Recommended)

Recommended option to install cli is to use `uvx`(For installation instructions for `uvx`, see the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/#upgrading-uv)):

```bash
# Install
uvx pip install codemie-plugins

# Run
uvx codemie-plugins
```

### Using pip

Pip installation:

```bash
pip install codemie-plugins
```

### From Source

To install from source:

```bash
# Clone the repository
git clone https://gitbud.epam.com/epm-cdme/codemie-plugins.git
cd codemie-plugins

# Install using pip
pip install -e .

# Or using poetry
poetry install
```

## Configuration

### Setting Up Your Plugin Key

Before using the CLI, you need to set up your plugin key:

1. Generate a plugin key using the built-in command:
   ```bash
   codemie-plugins config generate-key
   ```
   This will generate a random UUID and set it as your plugin key.

2. Alternatively, set a specific plugin key in your configuration:
   ```bash
   codemie-plugins config set PLUGIN_KEY your-plugin-key
   ```

3. Or set it as an environment variable:
   ```bash
   export PLUGIN_KEY=your-plugin-key
   ```

### Configuration File

The CLI uses a configuration file located at `$HOME/.codemie/config.json`. You can manage this configuration using the `config` command:

```bash
# View current configuration
codemie-plugins config list

# Set a configuration value
codemie-plugins config set KEY VALUE

# Get a specific configuration value
codemie-plugins config get KEY
```

### Environment Variables

The following environment variables can be used to configure the CLI:

- `PLUGIN_KEY`: Authentication key for the plugin engine
- `PLUGIN_ENGINE_URI`: URI for the plugin engine (typically a NATS server)
- `COMMAND_LINE_TOOL_TIMEOUT`: Timeout for command line tools (in seconds)
- `LEGACY_PROTOCOL`: Set to "true" to use the legacy protocol instead of the new improved protocol.
  The new protocol is now enabled by default as it's faster and more efficient. The legacy protocol is maintained for backward compatibility.

## Commands

### Global Options

The following options are available for all commands:

```
--plugin-key TEXT          Authentication key for the plugin engine
--plugin-engine-uri TEXT   URI for the plugin engine (typically a NATS server)
--debug / --no-debug       Enable debug mode
--version                  Show the version and exit
--help                     Show help message and exit
```

### List Command

The `list` command displays available CLI commands:

```bash
codemie-plugins list [OPTIONS]
```

Options:
- `--verbose, -v`: Display detailed information about each command

Example:
```bash
# List available commands
codemie-plugins list
# or with uvx
uvx codemie-plugins list

# List commands with detailed information
codemie-plugins list -v
# or with uvx
uvx codemie-plugins list -v
```

### Config Command

The `config` command manages CLI configuration settings:

```bash
codemie-plugins config SUBCOMMAND [OPTIONS]
```

Subcommands:
- `list`: List current configuration settings
  - `--all`: Show all configuration including environment variables
- `set KEY VALUE`: Set a configuration value
- `get KEY`: Get a specific configuration value
- `generate-key`: Generate a random UUID and set it as the plugin key

Examples:
```bash
# List current configuration
codemie-plugins config list
# or with uvx
uvx codemie-plugins config list

# Show all configuration
codemie-plugins config list --all
# or with uvx
uvx codemie-plugins config list --all

# Set a configuration value
codemie-plugins config set PLUGIN_KEY your-plugin-key
# or with uvx
uvx codemie-plugins config set PLUGIN_KEY your-plugin-key

# Get a specific configuration value
codemie-plugins config get PLUGIN_KEY
# or with uvx
uvx codemie-plugins config get PLUGIN_KEY

# Generate a random UUID and set it as the plugin key
codemie-plugins config generate-key
# or with uvx
uvx codemie-plugins config generate-key
```

### MCP Command

The `mcp` command manages Model Context Protocol servers and connections:

```bash
codemie-plugins mcp SUBCOMMAND [OPTIONS]
```

Subcommands:
- `list`: List available MCP servers
- `run`: Run MCP with specified servers
  - `--servers, -s TEXT`: Comma-separated list of server names to run (required)
  - `--env, -e TEXT`: Server-specific environment variables (format: 'server_name=VAR1,VAR2')
  - `--timeout, -t INTEGER`: Timeout in seconds

Examples:
```bash
# List available MCP servers
codemie-plugins mcp list
# or with uvx
uvx codemie-plugins mcp list

# Run a single server
codemie-plugins mcp run -s filesystem
# or with uvx
uvx codemie-plugins mcp run -s filesystem

# Run multiple servers
codemie-plugins mcp run -s filesystem,cli-mcp-server -e cli-mcp-server=ALLOWED_DIR
# or with uvx
uvx codemie-plugins mcp run -s filesystem,cli-mcp-server -e cli-mcp-server=ALLOWED_DIR

# Run with environment variables
codemie-plugins mcp run -s filesystem -e filesystem=FILE_PATHS
# or with uvx
uvx codemie-plugins mcp run -s filesystem -e filesystem=FILE_PATHS
```

### Development Command

The `development` command provides development toolkit commands for working with repositories:

```bash
codemie-plugins development SUBCOMMAND [OPTIONS]
```

Subcommands:
- `run`: Run development toolkit on a repository
  - `--repo-path PATH`: Path to the repository directory
  - `--timeout, -t INTEGER`: Timeout in seconds for command execution

Examples:
```bash
# Run development toolkit on current directory
codemie-plugins development run
# or with uvx
uvx codemie-plugins development run

# Run development toolkit on a specific repository
codemie-plugins development run --repo-path /path/to/repo
# or with uvx
uvx codemie-plugins development run --repo-path /path/to/repo

# Run with a custom timeout
codemie-plugins development run --timeout 600
# or with uvx
uvx codemie-plugins development run --timeout 600
```

### Code Command

The `code` command launches an interactive AI-powered coding assistant that helps with various programming tasks:

```bash
codemie-plugins code [OPTIONS]
```

Options:
- `--model, -m TEXT`: The model to use for the coding assistant (default: gpt-4o)
- `--temperature, -t FLOAT`: Temperature setting for the model (0.0-1.0) (default: 0.7)
- `--allowed-dir, -d TEXT`: Directories the agent is allowed to access (can specify multiple)
- `--verbose, -v`: Verbose mode to avoid logs truncation
- `--recursion-limit, -r INTEGER`: Maximum recursion limit for the agent (default: 50)
- `--global-prompt, -g`: Use the default global prompt even if a local prompt is configured
- `--mcp-servers TEXT`: Comma-separated list of MCP server names to include in the agent

#### Examples:
Start the interactive coding assistant
```bash
# Default run
codemie-plugins code
# or with uvx
uvx codemie-plugins code
```

Use a specific model
```bash
# gpt-4o example
codemie-plugins code --model gpt-4o
# or with uvx
uvx codemie-plugins code --model gpt-4o

# Claude Sonnet 3.7
codemie-plugins code --model anthropic.claude-3-7-sonnet-20250219-v1:0
# or with uvx
uvx codemie-plugins code --model anthropic.claude-3-7-sonnet-20250219-v1:0
```

Set a custom temperature
```bash
# Configure agent temperature
codemie-plugins code --temperature 0.2
# or with uvx
uvx codemie-plugins code --temperature 0.2
```

Specify allowed directories to access on local file system
```bash
# Specify allowed directories (Absolute path should be provided)
codemie-plugins code --allowed-dir /path/to/project
# or with uvx
uvx codemie-plugins code --allowed-dir /path/to/project
```

Use with specific LLM service configuration
```bash
# Pass api key and url
codemie-plugins code --llm-api-key your-api-key --llm-base-url https://your-llm-service.com
# or with uvx
uvx codemie-plugins code --llm-api-key your-api-key --llm-base-url https://your-llm-service.com
```

Overwrite default prompt
```bash
# Use with a local prompt (overrides default)
codemie-plugins config local-prompt "Your custom prompt"
codemie-plugins code
# or with uvx
uvx codemie-plugins config local-prompt "Your custom prompt"
uvx codemie-plugins code
```

Force usage of global prompt
```bash
# Force using the default global prompt
codemie-plugins code -g
# or with uvx
uvx codemie-plugins code -g
```

Use MCP servers (should be configured in advance). See [Custom MCP Servers](#custom-mcp-servers) section
```bash
# Use with MCP servers
codemie-plugins code --mcp-servers jetbrains
# or with uvx
uvx codemie-plugins code --mcp-servers jetbrains
```

#### Interactive Mode Commands

Once in the interactive mode, you can use the following commands:
- `exit`: Exit the interactive mode
- `reset`: Reset the conversation history

#### Custom Prompts

You can customize the agent's behavior by providing a custom prompt:

1. Create a file at `$HOME/.codemie/prompt.txt` with your custom instructions
2. Run the code command, and it will automatically use your custom prompt
3. To force using the default prompt, use the `--global-prompt` flag

#### For Development
For local development it's recommended to use default agent with sonnet-3.5 or 3.7 models and point to specific 
directory to work with.
As an example you are developing in `$HOME/repos/EPMCDME/codemie` and `$HOME/repos/EPMCDME/codemie-ui` directories.
Run the following commands to start `codemie-plugins code` with claude 3.7 model

```bash
codemie-plugins code --allowed-dir $HOME/repos/EPMCDME/codemie --allowed-dir $HOME/repos/EPMCDME/codemie-ui --model anthropic.claude-3-7-sonnet-20250219-v1:0
# or with uvx
uvx codemie-plugins code --allowed-dir $HOME/repos/EPMCDME/codemie --allowed-dir $HOME/repos/EPMCDME/codemie-ui --model anthropic.claude-3-7-sonnet-20250219-v1:0
```

## Custom MCP Servers

You can define custom MCP servers in your global configuration file (`$HOME/.codemie/config.json`). These servers will be automatically recognized and can be used alongside the predefined servers.

Configuration Format:

```json
{
  "mcpServers": {
    "my-custom-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "transport": "stdio"
    }
  }
}
```

Using Custom Servers:

```bash
# List all available servers including custom ones
codemie-plugins mcp list
# or with uvx
uvx codemie-plugins mcp list

# Run a custom server
codemie-plugins mcp run -s my-custom-server
# or with uvx
uvx codemie-plugins mcp run -s my-custom-server
```

## Graceful Shutdown

The CLI implements graceful shutdown handling to ensure that all processes are properly terminated when the CLI is interrupted (e.g., with Ctrl+C). This includes:

- Cancelling running asyncio tasks
- Terminating subprocesses
- Closing connections

## Troubleshooting

If you encounter issues with the CLI, try the following:

1. Enable debug mode:
   ```bash
   codemie-plugins --debug COMMAND
   # or with uvx
   uvx codemie-plugins --debug COMMAND
   ```

2. Check your configuration:
   ```bash
   codemie-plugins config list --all
   # or with uvx
   uvx codemie-plugins config list --all
   ```

3. Ensure your plugin key is correctly set:
   ```bash
   codemie-plugins config get PLUGIN_KEY
   # or with uvx
   uvx codemie-plugins config get PLUGIN_KEY
   ```

4. Verify that required environment variables are set for specific servers.

5. If you're experiencing compatibility issues with existing integrations, try setting the `LEGACY_PROTOCOL=true` environment variable:
   ```bash
   # Linux/macOS
   export LEGACY_PROTOCOL=true
   codemie-plugins COMMAND
   
   # Windows PowerShell
   $env:LEGACY_PROTOCOL="true"
   codemie-plugins COMMAND
   ```

## Contributing

Contributions to the CodeMie Plugins CLI are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

© 2025 EPAM AI/Run CodeMie Team