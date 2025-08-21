import asyncio
import json
import os

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Import JaCoCoReport class
from .jacoco_reporter import JaCoCoReport

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

# Set default covered types for JaCoCo reporter
if "COVERED_TYPES" not in os.environ:
    os.environ["COVERED_TYPES"] = "nocovered,partiallycovered,fullcovered"

COVERED_TYPES = os.environ["COVERED_TYPES"].split(",")

server = Server("jacoco-reporter")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    print("handle_list_prompts called")
    return [
        types.Prompt(
            name="jacoco-report-analysis",
            description="analysis jacoco report",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="parse jacoco report",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="jacoco-reporter-server",
            description="Read jacoco report and return the coverage data in COVERED_TYPES",
            inputSchema={
                "type": "object",
                "properties": {
                    "jacoco_xmlreport_absolute_path": {"type": "string"},
                    "covered_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": COVERED_TYPES
                    },
                    "clazz": {"type": "string"}
                },
                "required": ["jacoco_xmlreport_absolute_path"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name == "jacoco-reporter-server":
        if not arguments:
            raise ValueError("Missing arguments")

        jacoco_xmlreport_absolute_path = arguments.get("jacoco_xmlreport_absolute_path")
        covered_types = arguments.get("covered_types", COVERED_TYPES)
        clazz = arguments.get("clazz")

        if not jacoco_xmlreport_absolute_path:
            raise ValueError("Missing jacoco_xmlreport_absolute_path")

        try:
            # Create JaCoCoReport instance and generate JSON data
            jacoco_report = JaCoCoReport(jacoco_xmlreport_absolute_path, covered_types)
            data = jacoco_report.jacoco_to_json()
            if clazz:
                all_reports = json.loads(data)
                classFileName = clazz if clazz.endswith(".java") else clazz + ".java"
                filtered_reports = [report for report in all_reports if report.get("sourcefile") == classFileName]
                data = json.dumps(filtered_reports, indent=4)
            
            return [
                types.TextContent(
                    type="text",
                    text=data,
                )
            ]
        except Exception as e:
            raise ValueError(f"Error processing JaCoCo report: {str(e)}")
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    print("xxxxxxxxxxxxxxxxxxxx")
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="jacoco-reporter",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )