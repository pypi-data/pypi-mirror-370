# jacoco-reporter MCP server

A MCP server project

## Components

### Resources

The server provides access to JaCoCo coverage reports through custom URI schemes.

### Prompts

The server provides a single prompt:
- jacoco-report-analysis: Analyzes JaCoCo coverage reports
  - Optional "style" argument to control detail level (brief/detailed)

### Tools

The server implements one tool:
- jacoco-reporter-server: Reads JaCoCo reports and returns coverage data
  - Takes "jacoco_xmlreport_absolute_path" as required argument
  - Optional "covered_types" and "clazz" arguments

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "jacoco-reporter": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/chaney/PycharmProjects/mcp/jacoco-reporter",
        "run",
        "jacoco-reporter"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "jacoco-reporter": {
      "command": "uvx",
      "args": [
        "jacoco-reporter"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/chaney/PycharmProjects/mcp-jacoco-reporter/jacoco-reporter run jacoco-reporter
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.