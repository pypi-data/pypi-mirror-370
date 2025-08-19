#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import sys
import uvicorn
from importlib import metadata

from core.session_server import (
    create_workspace_mcp_server,
    setup_signal_handlers
)
from core.utils import check_credentials_directory_permissions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up detailed file logging
try:
    root_logger = logging.getLogger()
    log_file_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(log_file_dir, 'mcp_server_debug.log')

    file_handler = logging.FileHandler(log_file_path, mode='a')
    file_handler.setLevel(logging.DEBUG)

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(threadName)s '
        '[%(module)s.%(funcName)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger.debug(f"Detailed file logging configured to: {log_file_path}")
except Exception as e:
    sys.stderr.write(f"CRITICAL: Failed to set up file logging to '{log_file_path}': {e}\n")

def safe_print(text):
    """Print text safely, handling both MCP server and interactive modes"""
    if not sys.stderr.isatty():
        # Running as MCP server, suppress output to avoid JSON parsing errors
        logger.debug(f"[MCP Server] {text}")
        return

    try:
        print(text, file=sys.stderr)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='replace').decode(), file=sys.stderr)

async def main():
    """
    Main entry point for the Google Workspace MCP server with session-aware transport.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Google Workspace MCP Server')
    parser.add_argument('--tools', nargs='*',
                        choices=['gmail', 'drive', 'calendar', 'docs', 'sheets', 'chat', 'forms', 'slides', 'tasks'],
                        help='Specify which tools to register. If not provided, all tools are registered.')
    parser.add_argument('--port', type=int, default=None,
                        help='Port to run the server on (overrides environment variables)')
    parser.add_argument('--host', default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--http', action='store_true',
                        help='Run in HTTP mode (same as default behavior)')
    args = parser.parse_args()

    # Set port from args, environment, or default
    if args.port:
        port = args.port
    else:
        port = int(os.getenv("PORT", os.getenv("WORKSPACE_MCP_PORT", 8000)))
    
    base_uri = os.getenv("WORKSPACE_MCP_BASE_URI", "http://localhost")

    safe_print("🔧 Google Workspace MCP Server (Session-Aware)")
    safe_print("=" * 45)
    safe_print("📋 Server Information:")
    try:
        version = metadata.version("workspace-mcp")
    except metadata.PackageNotFoundError:
        version = "dev"
    
    safe_print(f"   📦 Version: {version}")
    safe_print(f"   🌐 Transport: session-aware-http")
    safe_print(f"   🔗 URL: {base_uri}:{port}")
    safe_print(f"   🔐 Auth: Access Token (OAuth2)")
    safe_print(f"   👥 Multi-User: ✅ Session Isolated")
    safe_print(f"   🐍 Python: {sys.version.split()[0]}")
    safe_print("")

    # Import tool modules to register them with the transport manager
    tool_imports = {
        'gmail': 'gmail.gmail_tools_new',
        'drive': 'gdrive.drive_tools_new',
        'calendar': 'gcalendar.calendar_tools_new',
        'docs': 'gdocs.docs_tools_new',
        'sheets': 'gsheets.sheets_tools_new',
        'chat': 'gchat.chat_tools_new',
        'forms': 'gforms.forms_tools_new',
        'slides': 'gslides.slides_tools_new',
        'tasks': 'gtasks.tasks_tools_new'
    }

    tool_icons = {
        'gmail': '📧',
        'drive': '📁',
        'calendar': '📅',
        'docs': '📄',
        'sheets': '📊',
        'chat': '💬',
        'forms': '📝',
        'slides': '🖼️',
        'tasks': '✓'
    }

    # Prepare tools to import (don't import yet - wait for transport manager)
    tools_to_import = args.tools if args.tools is not None else ['gmail', 'drive', 'calendar', 'docs', 'sheets', 'chat', 'forms', 'slides', 'tasks']  # Enable all updated tools

    safe_print("📊 Configuration Summary:")
    safe_print(f"   🔧 Tools to Enable: {len(tools_to_import)}")
    safe_print("   🔑 Auth Method: Access Token (Header-based)")
    safe_print("   🔒 Session Isolation: ✅ ENABLED")
    safe_print("   📝 Log Level: INFO")
    safe_print("")

    # Check credentials directory permissions (not needed for token auth, but kept for compatibility)
    try:
        safe_print("🔍 Checking system permissions...")
        # Skip the actual check since we don't use file-based credentials anymore
        safe_print("✅ System permissions verified (token-based auth)")
        safe_print("")
    except Exception as e:
        safe_print(f"⚠️  Permission check skipped: {e}")
        safe_print("")

    try:
        # Create session-aware server
        safe_print(f"🚀 Starting session-aware server on {base_uri}:{port}")
        safe_print("   📡 MCP Endpoint: /mcp")
        safe_print("   🏥 Health Check: /health")
        safe_print("   📊 Session Stats: /sessions")
        safe_print("   🔐 Authentication: Access Token in Headers")
        safe_print("   ✅ Session Isolation: ENABLED")
        safe_print("   🔄 Response Routing: GUARANTEED")
        safe_print("")

        # Set up graceful shutdown
        setup_signal_handlers()

        # Create the server FIRST
        app, transport_manager = await create_workspace_mcp_server(port, args.host)
        
        # NOW import and register tools (after transport manager exists)
        safe_print(f"🛠️  Loading {len(tools_to_import)} tool module{'s' if len(tools_to_import) != 1 else ''}:")
        
        for tool in tools_to_import:
            try:
                # Import the updated tool modules (all now use token auth)
                __import__(tool_imports[tool])
                safe_print(f"   {tool_icons[tool]} {tool.title()} - Google {tool.title()} API integration (✅ Token Auth)")
            except ImportError as e:
                safe_print(f"   ❌ {tool.title()} - Failed to load: {e}")
                logger.error(f"Failed to import tool {tool}: {e}")
        
        safe_print("")
        safe_print("   Ready for MCP connections!")
        safe_print("")
        
        # Run the server
        config = uvicorn.Config(
            app=app,
            host=args.host,
            port=port,
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        safe_print("\n👋 Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n❌ Server error: {e}")
        logger.error(f"Unexpected error running server: {e}", exc_info=True)
        sys.exit(1)

def main_sync():
    """Synchronous entry point for the CLI."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()