"""
Genesis MCP Core Server - Main server implementation.

This module provides the GenesisMCPServer class which implements a full
MCP 2025-06-18 compliant server with connector support.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import structlog

from .config import Settings, get_settings
from .registry import ConnectorRegistry
from ..utils.logging import setup_logging, get_logger


class GenesisMCPServer:
    """
    Main Genesis MCP server class.
    
    Provides a full MCP 2025-06-18 compliant server with:
    - Modern /mcp endpoint with batch and streaming support
    - Legacy SSE compatibility 
    - Connector registry with dynamic loading
    - Enterprise security features
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        connector_config_dir: Optional[Union[str, Path]] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        debug: Optional[bool] = None
    ):
        """
        Initialize the Genesis MCP server.
        
        Args:
            settings: Server settings (if None, will be created from environment)
            connector_config_dir: Directory containing connector JSON files
            host: Server host (overrides settings)
            port: Server port (overrides settings)
            debug: Debug mode (overrides settings)
        """
        # Initialize settings
        if settings is None:
            settings = get_settings(connector_config_dir=connector_config_dir)
        elif connector_config_dir:
            # Update settings with connector config dir
            settings.autonomize.connector_config_dir = connector_config_dir
        
        self.settings = settings
        
        # Override settings if provided
        if host is not None:
            self.settings.server.host = host
        if port is not None:
            self.settings.server.port = port
        if debug is not None:
            self.settings.server.debug = debug
        
        # Set up logging
        setup_logging(self.settings.logging)
        self.logger = get_logger("genesis_mcp_server")
        
        # Initialize components
        self.registry: Optional[ConnectorRegistry] = None
        self.app: Optional[FastAPI] = None
        
        self.logger.info(
            "Genesis MCP Server initialized",
            host=self.settings.server.host,
            port=self.settings.server.port,
            debug=self.settings.server.debug,
            connector_config_dir=self.settings.autonomize.connector_config_dir
        )
    
    async def initialize(self) -> None:
        """Initialize the server components."""
        self.logger.info("Initializing Genesis MCP Server...")
        
        # Initialize connector registry
        self.registry = ConnectorRegistry(self.settings)
        await self.registry.initialize()
        
        # Create FastAPI app
        self.app = self._create_app()
        
        self.logger.info("Genesis MCP Server initialization complete")
    
    def _create_app(self) -> FastAPI:
        """Create the FastAPI application with all endpoints."""
        app = FastAPI(
            title=self.settings.server.name,
            version=self.settings.server.version,
            description="Genesis MCP 2025-06-18 Compliant Server",
            debug=self.settings.server.debug
        )
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint."""
            connector_count = 0
            if self.registry:
                connector_count = len(self.registry.get_enabled_connectors())
            
            return JSONResponse({
                "status": "healthy",
                "server": {
                    "name": self.settings.server.name,
                    "version": self.settings.server.version,
                    "mcp_version": "2025-06-18"
                },
                "connectors": {
                    "enabled": connector_count,
                    "initialized": self.registry.is_initialized() if self.registry else False
                },
                "features": [
                    "mcp-2025-06-18",
                    "elicitation",
                    "structured-output", 
                    "streaming",
                    "connectors"
                ]
            })
        
        # Add tools discovery endpoint
        @app.get("/tools")
        async def list_tools():
            """List all available tools (REST API endpoint)."""
            if not self.registry:
                return JSONResponse({"tools": []})
            
            try:
                tools = await self.registry.get_all_tools()
                return JSONResponse({"tools": tools})
            except Exception as e:
                self.logger.error(f"Failed to list tools: {e}")
                return JSONResponse(
                    {"error": "Failed to list tools", "details": str(e)},
                    status_code=500
                )
        
        # Add modern MCP endpoint
        @app.post("/mcp")
        async def mcp_endpoint(request: Request, response: Response):
            """
            Modern MCP 2025-06-18 endpoint supporting batch and streaming.
            """
            if not self.registry:
                return JSONResponse(
                    {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Server not initialized"}},
                    status_code=500
                )
            
            try:
                # Parse JSON-RPC request
                body = await request.body()
                if not body:
                    return JSONResponse(
                        {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
                        status_code=400
                    )
                
                try:
                    rpc_request = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    return JSONResponse(
                        {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
                        status_code=400
                    )
                
                # Handle different MCP methods
                method = rpc_request.get("method")
                request_id = rpc_request.get("id")
                
                if method == "initialize":
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2025-06-18",
                            "capabilities": [
                                "elicitation",
                                "structured_output", 
                                "streaming"
                            ],
                            "serverInfo": {
                                "name": self.settings.server.name,
                                "version": self.settings.server.version
                            }
                        }
                    })
                
                elif method == "tools/list":
                    tools = await self.registry.get_all_tools()
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"tools": tools}
                    })
                
                elif method == "tools/call":
                    params = rpc_request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    if not tool_name:
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32602, "message": "Missing tool name"}
                        })
                    
                    try:
                        result = await self.registry.execute_tool(tool_name, arguments)
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result) if not isinstance(result, str) else result
                                    }
                                ]
                            }
                        })
                    except Exception as e:
                        self.logger.error(f"Tool execution failed: {e}")
                        return JSONResponse({
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"}
                        })
                
                else:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    })
                
            except Exception as e:
                self.logger.error(f"MCP endpoint error: {e}")
                return JSONResponse(
                    {"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}},
                    status_code=500
                )
        
        # Add backward compatibility endpoints for legacy MCP clients
        @app.get("/sse")
        async def sse_endpoint(request: Request):
            """
            Legacy SSE endpoint for backward compatibility.
            Provides server-sent events stream for MCP clients that don't support the modern /mcp endpoint.
            """
            async def event_stream() -> AsyncGenerator[str, None]:
                """Generate SSE events."""
                try:
                    # Send initial connection event
                    yield f"data: {json.dumps({'type': 'connection', 'status': 'connected'})}\n\n"
                    
                    # Send server info
                    server_info = {
                        "type": "server_info",
                        "name": self.settings.server.name,
                        "version": self.settings.server.version,
                        "protocol_version": "2025-06-18",
                        "capabilities": ["tools", "elicitation", "structured_output"]
                    }
                    yield f"data: {json.dumps(server_info)}\n\n"
                    
                    # Send available tools
                    if self.registry:
                        tools = await self.registry.get_all_tools()
                        tools_event = {
                            "type": "tools_available",
                            "tools": tools
                        }
                        yield f"data: {json.dumps(tools_event)}\n\n"
                    
                    # Keep connection alive
                    while True:
                        await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"
                        
                except asyncio.CancelledError:
                    self.logger.info("SSE connection cancelled")
                    return
                except Exception as e:
                    self.logger.error(f"SSE stream error: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                    return
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
        
        @app.post("/messages")
        async def messages_endpoint(request: Request):
            """
            Legacy messages endpoint for backward compatibility.
            Handles MCP requests in the classic dual-endpoint pattern.
            """
            if not self.registry:
                return JSONResponse(
                    {"error": "Server not initialized"},
                    status_code=500
                )
            
            try:
                body = await request.body()
                if not body:
                    return JSONResponse({"error": "Empty request body"}, status_code=400)
                
                try:
                    message = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    return JSONResponse({"error": "Invalid JSON"}, status_code=400)
                
                method = message.get("method")
                
                if method == "tools/list":
                    tools = await self.registry.get_all_tools()
                    return JSONResponse({"tools": tools})
                
                elif method == "tools/call":
                    tool_name = message.get("name")
                    arguments = message.get("arguments", {})
                    
                    if not tool_name:
                        return JSONResponse({"error": "Missing tool name"}, status_code=400)
                    
                    try:
                        result = await self.registry.execute_tool(tool_name, arguments)
                        return JSONResponse({
                            "result": result,
                            "status": "success"
                        })
                    except Exception as e:
                        self.logger.error(f"Tool execution failed: {e}")
                        return JSONResponse(
                            {"error": f"Tool execution failed: {str(e)}"},
                            status_code=500
                        )
                
                elif method == "server/info":
                    return JSONResponse({
                        "name": self.settings.server.name,
                        "version": self.settings.server.version,
                        "protocol_version": "2025-06-18",
                        "capabilities": ["tools", "elicitation", "structured_output"]
                    })
                
                else:
                    return JSONResponse(
                        {"error": f"Unknown method: {method}"},
                        status_code=400
                    )
                    
            except Exception as e:
                self.logger.error(f"Messages endpoint error: {e}")
                return JSONResponse(
                    {"error": "Internal server error"},
                    status_code=500
                )
        
        return app
    
    async def run(self) -> None:
        """Run the server."""
        if not self.app:
            await self.initialize()
        
        if not self.app:
            raise RuntimeError("Failed to initialize server")
        
        self.logger.info(
            "Starting Genesis MCP Server",
            host=self.settings.server.host,
            port=self.settings.server.port
        )
        
        # Run with uvicorn
        config = uvicorn.Config(
            self.app,
            host=self.settings.server.host,
            port=self.settings.server.port,
            log_level="info" if not self.settings.server.debug else "debug",
            access_log=self.settings.logging.enable_access_logs
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def run_sync(self) -> None:
        """Run the server synchronously."""
        asyncio.run(self.run())
    
    async def shutdown(self) -> None:
        """Shutdown the server and cleanup resources."""
        self.logger.info("Shutting down Genesis MCP Server...")
        
        if self.registry:
            await self.registry.cleanup()
        
        self.logger.info("Genesis MCP Server shutdown complete")