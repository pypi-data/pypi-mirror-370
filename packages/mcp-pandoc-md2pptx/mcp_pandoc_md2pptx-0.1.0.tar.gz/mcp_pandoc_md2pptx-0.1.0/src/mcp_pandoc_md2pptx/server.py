import pypandoc
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import os
from pathlib import Path

server = Server("mcp-pandoc-md2pptx")

# Get the path to the diagram.lua filter
DIAGRAM_FILTER_PATH = Path(__file__).parent / "diagram.lua"


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="convert-contents",
            description=(
                "Converts Markdown content to PowerPoint (PPTX) format.\n\n"
                "🚨 REQUIREMENTS:\n"
                "1. Input: Only Markdown format is supported\n"
                "2. Output: Only PPTX format is supported\n"
                "3. File Path: Complete output path with filename and .pptx extension is required\n\n"
                "✅ Usage Example:\n"
                "'Convert this markdown to PowerPoint and save as /presentations/demo.pptx'\n\n"
                "🎨 PPTX STYLING:\n"
                "* Use template parameter to apply custom PowerPoint templates\n"
                "* Create templates with your branding, fonts, and slide layouts\n"
                "* Example: 'Convert markdown to PPTX using /templates/theme.pptx as template and save as /presentations/pitch.pptx'\n\n"
                "➡️ Diagram Support:\n"
                "* Diagram using mermaid, plantuml, graphviz is supported by default. Referencing external resource in plantuml is also supported.\n"
                """* Example: \n```plantuml
@startuml Two Modes - Technical View
' Uncomment the line below for "dark mode" styling
'!$AWS_DARK = true

!define AWSPuml https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/v20.0/dist
!include AWSPuml/AWSCommon.puml

!include AWSPuml/AWSSimplified.puml
!include AWSPuml/General/Users.puml
!include AWSPuml/NetworkingContentDelivery/APIGateway.puml
!include AWSPuml/SecurityIdentityCompliance/Cognito.puml
!include AWSPuml/Compute/Lambda.puml
!include AWSPuml/Database/DynamoDB.puml

left to right direction

Users(sources, "Events", "millions of users")
APIGateway(votingAPI, "Voting API", "user votes")
Cognito(userAuth, "User Authentication", "jwt to submit votes")
Lambda(generateToken, "User Credentials", "return jwt")
Lambda(recordVote, "Record Vote", "enter or update vote per user")
DynamoDB(voteDb, "Vote Database", "one entry per user")

sources --> userAuth
sources --> votingAPI
userAuth <--> generateToken
votingAPI --> recordVote
recordVote --> voteDb
@enduml
```\n\n"""
                "📋 Creating Reference Documents:\n"
                "* Generate PPTX template: pandoc -o template.pptx --print-default-data-file reference.pptx\n"
                "* Customize in PowerPoint: fonts, colors, slide layouts\n"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "contents": {
                        "type": "string",
                        "description": "Markdown content to be converted (required if input_file not provided)"
                    },
                    "input_file": {
                        "type": "string",
                        "description": "Complete path to Markdown input file (e.g., '/path/to/input.md')"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "Complete path where to save the PPTX output including filename and .pptx extension (required)"
                    },
                    "template": {
                        "type": "string",
                        "description": "Path to a template PPTX document to use for styling"
                    }
                },
                "oneOf": [
                    {"required": ["contents", "output_file"]},
                    {"required": ["input_file", "output_file"]}
                ]
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
    if name not in ["convert-contents"]:
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments:
        raise ValueError("Missing arguments")

    # Extract arguments
    contents = arguments.get("contents")
    input_file = arguments.get("input_file")
    output_file = arguments.get("output_file")
    template = arguments.get("template")
    
    # Validate input parameters
    if not contents and not input_file:
        raise ValueError("Either 'contents' or 'input_file' must be provided")
    
    if not output_file:
        raise ValueError("output_file path is required")
    
    # Validate template if provided
    if template and not os.path.exists(template):
        raise ValueError(f"Template document not found: {template}")
    
    try:
        # Prepare conversion arguments
        extra_args = []
        
        # Add diagram filter by default
        if DIAGRAM_FILTER_PATH.exists():
            extra_args.extend(["--lua-filter", str(DIAGRAM_FILTER_PATH)])
        
        # Handle template for pptx format
        if template:
            extra_args.extend(["--reference-doc", template])
        
        # Convert content using pypandoc
        if input_file:
            if not os.path.exists(input_file):
                raise ValueError(f"Input file not found: {input_file}")
            
            pypandoc.convert_file(
                input_file,
                "pptx",
                outputfile=output_file,
                extra_args=extra_args
            )
        else:
            pypandoc.convert_text(
                contents,
                "pptx",
                format="markdown",
                outputfile=output_file,
                extra_args=extra_args
            )
        
        result_message = f"Markdown successfully converted to PPTX and saved to: {output_file}"
        
        return [
            types.TextContent(
                type="text",
                text=result_message
            )
        ]
        
    except Exception as e:
        error_msg = f"Error converting markdown to PPTX: {str(e)}"
        raise ValueError(error_msg)

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-pandoc-md2pptx",
                server_version="0.7.0",  # Updated version with defaults file support
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
