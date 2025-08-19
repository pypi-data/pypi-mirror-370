"""
AkShare MCP Server
A Model Context Protocol server that provides access to AkShare financial data APIs
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from .wrapper import AkShareWrapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AkShareMCPServer:
    """MCP Server for AkShare financial data APIs"""
    
    def __init__(self):
        self.server = Server("akshare-mcp-server")
        self.wrapper = AkShareWrapper()
        self._setup_tools()
        self._setup_handlers()
    
    def _setup_tools(self):
        """Setup MCP tools based on discovered AkShare functions"""
        
        # Tool for listing available functions
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            tools = [
                Tool(
                    name="akshare_list_functions",
                    description="List all available AkShare functions, optionally filtered by category",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Filter functions by category (stock, futures, bond, macro, etc.)",
                                "enum": list(self.wrapper.get_categories().keys())
                            }
                        }
                    }
                ),
                Tool(
                    name="akshare_get_categories",
                    description="Get all available function categories",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="akshare_call_function",
                    description="Call any AkShare function with specified parameters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "function_name": {
                                "type": "string",
                                "description": "Name of the AkShare function to call"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters to pass to the function",
                                "additionalProperties": True
                            }
                        },
                        "required": ["function_name"]
                    }
                ),
                Tool(
                    name="akshare_get_function_info",
                    description="Get detailed information about a specific AkShare function",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "function_name": {
                                "type": "string",
                                "description": "Name of the AkShare function"
                            }
                        },
                        "required": ["function_name"]
                    }
                )
            ]
            
            # Add some commonly used AkShare functions as dedicated tools
            common_functions = [
                'stock_zh_a_hist',  # Stock historical data
                'stock_info_a_code_name',  # Stock basic info
                'macro_china_gdp',  # GDP data
                'futures_main_sina',  # Futures data
                'bond_zh_hs_cov_daily'  # Bond data
            ]
            
            for func_name in common_functions:
                if func_name in self.wrapper.functions:
                    func_info = self.wrapper.functions[func_name]
                    
                    # Create schema for this specific function
                    properties = {}
                    required = []
                    
                    for param_name, param_info in func_info['parameters'].items():
                        properties[param_name] = {
                            "type": param_info['type'],
                            "description": f"Parameter: {param_name}"
                        }
                        if param_info['required']:
                            required.append(param_name)
                    
                    tools.append(Tool(
                        name=f"akshare_{func_name}",
                        description=func_info['description'][:200] + ('...' if len(func_info['description']) > 200 else ''),
                        inputSchema={
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    ))
            
            return tools
    
    def _setup_handlers(self):
        """Setup tool call handlers"""
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "akshare_list_functions":
                    category = arguments.get('category')
                    functions = self.wrapper.get_function_list(category)
                    return [TextContent(
                        type="text",
                        text=json.dumps(functions, indent=2, ensure_ascii=False)
                    )]
                
                elif name == "akshare_get_categories":
                    categories = self.wrapper.get_categories()
                    result = {
                        "categories": list(categories.keys()),
                        "details": {k: len(v) for k, v in categories.items()}
                    }
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, ensure_ascii=False)
                    )]
                
                elif name == "akshare_call_function":
                    function_name = arguments.get('function_name')
                    parameters = arguments.get('parameters', {})
                    
                    if not function_name:
                        raise ValueError("function_name is required")
                    
                    result = self.wrapper.call_function(function_name, **parameters)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, ensure_ascii=False, default=str)
                    )]
                
                elif name == "akshare_get_function_info":
                    function_name = arguments.get('function_name')
                    
                    if not function_name:
                        raise ValueError("function_name is required")
                    
                    if function_name not in self.wrapper.functions:
                        raise ValueError(f"Function {function_name} not found")
                    
                    func_info = self.wrapper.functions[function_name]
                    info = {
                        "name": func_info['name'],
                        "description": func_info['description'],
                        "parameters": func_info['parameters']
                    }
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(info, indent=2, ensure_ascii=False, default=str)
                    )]
                
                elif name.startswith("akshare_") and name != "akshare_list_functions" and name != "akshare_get_categories" and name != "akshare_call_function" and name != "akshare_get_function_info":
                    # Handle specific function calls
                    function_name = name.replace("akshare_", "")
                    result = self.wrapper.call_function(function_name, **arguments)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, ensure_ascii=False, default=str)
                    )]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "tool": name,
                        "arguments": arguments
                    }, indent=2, ensure_ascii=False)
                )]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting AkShare MCP Server...")
        logger.info(f"Discovered {len(self.wrapper.functions)} AkShare functions")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

def main():
    """Main entry point"""
    server = AkShareMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
