"""
MCP Server for dom_parser with basic APIs for web automation.
"""

import asyncio
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from dom_parser.src import DOMParser, Action, ActionType
from dom_parser.src.py.types import ParsedPage, Action
import logging

logger = logging.getLogger(__name__)
class DOMParserMCPServer:
    """MCP Server that provides dom_parser functionality."""
    
    def __init__(self):
        self.server = Server("dom_parser")
        self.dom_parser: Optional[DOMParser] = None
        self.current_url: Optional[str] = None

        logger.error("Initializing DOMParserMCPServer")
        
        # Register handlers properly using request_handlers dictionary
        self.server.request_handlers[ListToolsRequest] = self.list_tools
        self.server.request_handlers[CallToolRequest] = self.call_tool
        
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        logger.debug("ListToolsRequest received — returning tools")
        logger.error("ListToolsRequest received — returning tools")
        return ListToolsResult(
            tools=[
                Tool(
                    name="execute_action",
                    title="Execute Action",
                    description=(
                        "Execute an action on the current page.\n"
                        "CRITICAL: Use the exact parameter format from available_action_types "
                        "returned by get_page_details. Each action type has specific required "
                        "parameters — always check available_action_types first."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ui_action": {
                                "type": "object",
                                "description": (
                                    "The UI action to execute. Use the exact parameter format "
                                    "from available_action_types returned by get_page_details."
                                )
                            }
                        },
                        "required": ["ui_action"]
                    }
                ),
                Tool(
                    name="get_page_details",
                    title="Get Page Details",
                    description=(
                        "Analyze the current web page and return comprehensive details including "
                        "actions, forms, elements, and a screenshot."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "headless": {
                                "type": "boolean",
                                "default": False,
                                "description": "Whether to run browser in headless mode"
                            }
                        }
                    }
                )
            ]
        )
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        logger.debug(f"CallToolRequest received — tool: {request.params.name}")
        try:
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            if tool_name == "execute_action":
                return await self._execute_action(arguments)
            elif tool_name == "get_page_details":
                return await self._get_page_details(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {tool_name}")]
                )
        except Exception as e:
            logger.exception("Error in call_tool")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )

    async def _execute_action(self, args: Dict[str, Any]) -> CallToolResult:
        """Execute a UI action and return results"""
        try:
            # Initialize DOMParser if not already done
            if not self.dom_parser:
                self.dom_parser = DOMParser(headless=False)
                await self.dom_parser.__aenter__()

            ui_action = args['ui_action']
            # Create Action object
            action = Action.from_json(ui_action)
            
            # Execute the action
            result = await self.dom_parser.execute_action(action, wait_for_idle=True, translate_element_id=True)
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing action: {str(e)}")]
            )
    
    async def _get_page_details(self, args: Dict[str, Any]) -> CallToolResult:
        """Get comprehensive page details."""
        headless = args.get("headless", False)
        
        try:
            # Initialize DOMParser if not already done
            if not self.dom_parser:
                self.dom_parser = DOMParser(headless=headless)
                await self.dom_parser.__aenter__()
            
            logger.error("Analyzing page1")
            # Analyze the page
            parsed_page = await self.dom_parser.analyze_page()
            logger.error("Analyzing page2")

            # Get site actions
            site_actions = parsed_page.actions if hasattr(parsed_page, 'actions') else []
            logger.error("Analyzing page3")
            # Get available actions
            available_actions = self.dom_parser.get_available_actions()
            logger.error("Analyzing page4")
            
            # Take screenshot
            screenshot_path = Path("/tmp/dom_parser_screenshot.png")
            screenshot = await self.dom_parser.take_screenshot(
                screenshot_path,
                full_page=True,
                return_base64=True
            )
            # logger.error("Analyzing page5")
            # with open(screenshot_path, "rb") as f:
            #     screenshot_data = base64.b64encode(f.read()).decode()
            # screenshot_path.unlink()  # Clean up
            logger.error("Analyzing page6")
            # Format the response
            content = []
            logger.error("Analyzing page778")

            # logger.error(site_actions.to_json())

            # Create JSON response
            site_details = {
                "url": parsed_page.metadata.url,
                "title": parsed_page.metadata.title,
                "parsed_actions": site_actions.to_json(),
                "available_action_types": available_actions,
                "screenshot": {
                    "data": screenshot,
                    "mime_type": "image/png",
                    "encoding": "base64"
                }
            }
            
            # logger.error("Analyzing page779")
            # logger.error(json.dumps(site_details, indent=2))
            logger.error("Analyzing page8")
            content.append(TextContent(type="text", text=json.dumps(site_details, indent=2)))
            logger.error("Analyzing page9")
            return CallToolResult(content=content)
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
            )
    
    async def cleanup(self):
        """Clean up resources."""
        if self.dom_parser:
            await self.dom_parser.__aexit__(None, None, None)


async def main():
    """Main entry point for the MCP server."""
    server = DOMParserMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dom_parser",
                server_version="1.0.0",
                server_description="""
                DOM Parser MCP Server for web automation and analysis.
                
                This server provides tools to:
                - Execute actions on web pages (click, type, navigate, scroll, wait)
                - Analyze web pages and extract structured data
                - Capture screenshots of web pages
                
                Usage Guidelines:
                - Always navigate to a page first before executing actions
                - Use get_page_details to understand the page structure
                - Actions require element IDs which can be found in page analysis
                - The server maintains browser session across multiple calls
                - Screenshots are returned as base64-encoded PNG images
                
                IMPORTANT: When executing actions, use the exact format from available_action_types:
                - The available_action_types from get_page_details shows the exact parameter structure
                - Each action type has specific required parameters (element_id, text_to_type, url, etc.)
                - Always check the available_action_types to see what parameters are needed
                - Use the exact parameter names and types shown in available_action_types
                
                Example workflow:
                1. Call get_page_details to analyze the page
                2. Look at available_action_types to see exact parameter formats
                3. Use execute_action with the exact format from available_action_types
                """,
                capabilities={
                    "tools": {
                        "listChanged": True
                    },
                    "resources": {
                        "subscribe": True
                    },
                    "prompts": {
                        "listChanged": True
                    }
                }
            ),
        )


if __name__ == "__main__":
    asyncio.run(main()) 