#!/usr/bin/env python3

import asyncio
import logging
import os
import signal
from typing import Optional
from importlib import metadata

from core.session_transport import (
    create_session_aware_server, 
    SessionAwareTransportManager
)

# Configure logging
logger = logging.getLogger(__name__)

# Global transport manager instance
transport_manager: Optional[SessionAwareTransportManager] = None

async def create_workspace_mcp_server(
    port: int = 8000,
    host: str = "0.0.0.0"
) -> tuple[any, SessionAwareTransportManager]:
    """
    Create the Google Workspace MCP server with session-aware transport.
    
    Args:
        port: Port to run the server on
        host: Host to bind to
        
    Returns:
        Tuple of (FastAPI app, SessionAwareTransportManager)
    """
    global transport_manager
    
    logger.info("Creating Google Workspace MCP Server with session-aware transport")
    
    # Create session-aware server
    app, transport_manager = await create_session_aware_server(port, host)
    
    # Set up periodic session cleanup (every 15 minutes)
    async def cleanup_sessions():
        while True:
            try:
                await asyncio.sleep(15 * 60)  # 15 minutes
                transport_manager.cleanup_expired_sessions(60 * 60)  # 1 hour expiry
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during session cleanup: {e}")
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(cleanup_sessions())
    
    return app, transport_manager

def register_tool_with_transport(tool_name: str, handler):
    """
    Register a tool with the global transport manager.
    This should be called by tool modules during import.
    
    Args:
        tool_name: Name of the tool
        handler: Tool handler function
    """
    global transport_manager
    if transport_manager:
        transport_manager.register_tool(tool_name, handler)
    else:
        logger.warning(f"Transport manager not initialized when registering tool: {tool_name}")

async def shutdown_server():
    """Gracefully shutdown the server"""
    global transport_manager
    if transport_manager:
        await transport_manager.destroy()
        logger.info("Server shutdown completed")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        if transport_manager:
            asyncio.create_task(shutdown_server())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

# Legacy compatibility functions for existing code
def set_transport_mode(mode: str):
    """Legacy function for compatibility - no longer needed"""
    logger.info(f"Transport mode setting ignored (always session-aware-http): {mode}")

def get_oauth_redirect_uri_for_current_mode() -> str:
    """Legacy function for compatibility - OAuth no longer used"""
    logger.warning("get_oauth_redirect_uri_for_current_mode called but OAuth is disabled")
    return "http://localhost:8000/oauth2callback"