# Translink MCP Server

A Model Context Protocol server that interfaces with Vancouver's Translink [API](https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources).

## Available Tools

This package provides the following tools for interacting with the TransLink API:

-   `get_trip_updates`

    -   Retrieves real-time trip update information from the TransLink API. This includes data about transit vehicle schedules, delays, and timing.
    -   No input parameters required.

-   `get_position_updates`

    -   Retrieves real-time position update information from the TransLink API. This includes current location data for transit vehicles.
    -   No input parameters required.

-   `get_service_alerts`
    -   Retrieves service alert information from the TransLink API. This includes notifications about disruptions, detours, and other service-related announcements.
    -   No input parameters required.

### Prompts

-   "Get the current trip updates from TransLink and show me buses that are running late."
-   "List all TransLink route 99 buses and their current schedule status."
-   "Create a summary of transit delays on major routes based on TransLink data."
-   "Check if my bus (route 14) is on time and when it will arrive at Commercial Drive."
-   "Where are all the SkyTrain trains currently located?"
-   "Show me all buses near downtown Vancouver right now."
-   "Find the closest buses to Science World station at this moment."
-   "Track the current positions of SeaBus vessels crossing Burrard Inlet."
-   "Are there any service disruptions on the Canada Line today?"
-   "Check if there are any alerts affecting bus routes in Surrey."
-   "Give me a list of all current TransLink service alerts as bullet points."
-   "Are there any planned maintenance or closures on the SkyTrain system this weekend?"

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run _mcp-server-translink_.

### Using PIP

Alternatively you can install `mcp-server-translink` via pip:

```
pip install mcp-server-translink
```

After installation, you can run it as a script using:

```
python -m mcp_server_translink
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
	"mcpServers": {
		"translink": {
			"command": "uvx",
			"args": ["mcp-server-translink"],
			"env": {
				"TRANSLINK_API_KEY": "PROVIDE_API_KEY"
			}
		}
	}
}
```

</details>

<details>
<summary>Using pip installation</summary>

```json
{
	"mcpServers": {
		"translink": {
			"command": "python",
			"args": ["-m", "mcp_server_translink"],
			"env": {
				"TRANSLINK_API_KEY": "PROVIDE_API_KEY"
			}
		}
	}
}
```

</details>

### Configure for VS Code

For manual installation, add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

Optionally, you can add it to a file called `.vscode/mcp.json` in your workspace. This will allow you to share the configuration with others.

> Note that the `mcp` key is needed when using the `mcp.json` file.

<details>
<summary>Using uvx</summary>

```json
{
	"mcp": {
		"servers": {
			"translink": {
				"command": "uvx",
				"args": ["mcp-server-translink"],
				"env": {
					"TRANSLINK_API_KEY": "PROVIDE_API_KEY"
				}
			}
		}
	}
}
```

</details>

### Customization - API Key

An API Key will be required to interface with the Translink API. This API key can be requested by creating an account with the service and requesting one. Provide this

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-translink
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/translink
npx @modelcontextprotocol/inspector uv run mcp-server-translink
```

## Testing

The project includes a comprehensive test suite using pytest. You can run the tests with:

### Using uv (Recommended)

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v
```

### Using pip

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with verbose output
pytest -v
```

For more details on the test suite, see the [test README](mcp_server_translink/test/README.md).

## Contributing

We encourage contributions to help expand and improve mcp-server-translink. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-translink even more powerful and useful.

## License

mcp-server-translink is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
