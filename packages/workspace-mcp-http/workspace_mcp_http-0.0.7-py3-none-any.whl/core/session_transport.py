#!/usr/bin/env python3

import asyncio
import contextvars
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from contextvars import ContextVar

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from mcp.server.fastmcp import FastMCP
from mcp.types import JSONRPCRequest, JSONRPCResponse

# Configure logging
logger = logging.getLogger(__name__)

# Context variable to store current request context
request_context: ContextVar[Optional['RequestContext']] = ContextVar('request_context', default=None)

class RequestContext:
    """Context for current request with session and auth information"""
    def __init__(self, session_id: str, auth_session_id: str, request_id: str, access_token: str, start_time: float):
        self.session_id = session_id
        self.auth_session_id = auth_session_id
        self.request_id = request_id
        self.access_token = access_token
        self.start_time = start_time

class SessionData:
    """Data for an isolated session"""
    def __init__(self, session_id: str, auth_session_id: str, mcp_server: FastMCP):
        self.session_id = session_id
        self.auth_session_id = auth_session_id
        self.mcp_server = mcp_server
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.request_count = 0

class SessionAwareTransportManager:
    """
    Manages session-aware transport instances with complete isolation.
    Python equivalent of the TypeScript SessionAwareTransportManager.
    """
    
    def __init__(self):
        self.sessions: Dict[str, SessionData] = {}
        self.tool_registry: Dict[str, Callable] = {}
        
    def register_tool(self, name: str, handler: Callable):
        """Register a tool handler that will be available to all sessions"""
        self.tool_registry[name] = handler
        logger.debug(f"Registered tool: {name}")
    
    def extract_access_token_from_headers(self, request: Request) -> Optional[str]:
        """Extract access token from request headers"""
        # Check Authorization header
        auth_header = request.headers.get('authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check alternative headers
        for header_name in ['x-access-token', 'access-token']:
            token = request.headers.get(header_name)
            if token:
                return token
                
        return None
    
    def is_initialize_request(self, request_body: dict) -> bool:
        """Check if this is an MCP initialize request"""
        return (
            request_body.get('method') == 'initialize' and
            'params' in request_body and
            'capabilities' in request_body.get('params', {})
        )
    
    async def get_or_create_session(
        self, 
        session_id: Optional[str], 
        request: Request,
        is_init_request: bool
    ) -> SessionData:
        """Get or create an isolated session with dedicated MCP server"""
        
        if not session_id and is_init_request:
            # Create new session with complete isolation
            auth_session_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            logger.info(f"🆕 Creating new isolated session: {session_id} (Auth: {auth_session_id})")
            
            # Create completely isolated MCP server for this session
            mcp_server = FastMCP(
                name="google_workspace_session"
            )
            
            # Register all tools for this session's server
            for tool_name, handler in self.tool_registry.items():
                # Create a wrapper that preserves the request context
                async def tool_wrapper(*args, **kwargs):
                    # The actual tool implementation will access the context
                    return await handler(*args, **kwargs)
                
                mcp_server.tool(name=tool_name)(tool_wrapper)
            
            session_data = SessionData(session_id, auth_session_id, mcp_server)
            self.sessions[session_id] = session_data
            
            logger.info(f"✅ Session created successfully: {session_id}")
            return session_data
            
        elif session_id and session_id in self.sessions:
            # Reuse existing session
            session_data = self.sessions[session_id]
            session_data.last_activity = datetime.now()
            logger.info(f"🔄 Reusing existing session: {session_id} (Auth: {session_data.auth_session_id})")
            return session_data
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No existing session data found for session ID: {session_id}"
            )
    
    async def handle_session_request(
        self,
        session_data: SessionData,
        request: Request,
        request_body: dict
    ) -> dict:
        """Handle request with complete session isolation and context preservation"""
        
        request_id = str(uuid.uuid4())
        session_data.request_count += 1
        
        # Extract access token
        access_token = self.extract_access_token_from_headers(request)
        if not access_token:
            raise HTTPException(
                status_code=401,
                detail="Authentication Error: No access token provided. Please provide OAuth2 access token in Authorization header."
            )
        
        # Create request context
        context = RequestContext(
            session_id=session_data.session_id,
            auth_session_id=session_data.auth_session_id,
            request_id=request_id,
            access_token=access_token,
            start_time=time.time()
        )
        
        logger.info(f"🔄 Using session-aware context - MCP: {session_data.session_id}, Auth: {session_data.auth_session_id}, Request: {request_id}")
        
        # Set context for this request
        token = request_context.set(context)
        
        try:
            # Process the JSON-RPC request through the session's MCP server
            # Note: This is a simplified approach - in a full implementation,
            # you'd need to integrate more closely with FastMCP's request handling
            
            method = request_body.get('method')
            if method == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_body.get('id'),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "google_workspace_session",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == 'tools/list':
                # Return list of available tools
                tools = []
                for tool_name in self.tool_registry.keys():
                    # Generate more detailed schema based on tool name
                    input_schema = {"type": "object", "properties": {}}
                    
                    if tool_name == 'send_gmail_message':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "to": {"type": "string", "description": "Recipient email address"},
                                "subject": {"type": "string", "description": "Email subject"},
                                "body": {"type": "string", "description": "Email body content"},
                                "cc": {"type": "string", "description": "CC recipients (optional)"},
                                "bcc": {"type": "string", "description": "BCC recipients (optional)"},
                                "html_body": {"type": "string", "description": "HTML version of email body (optional)"},
                                "thread_id": {"type": "string", "description": "Thread ID to reply to (optional)"},
                                "in_reply_to": {"type": "string", "description": "Message ID being replied to (optional)"},
                                "attachments": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to attach (optional)"}
                            },
                            "required": ["to", "subject", "body"]
                        }
                    elif tool_name == 'search_gmail_messages':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Gmail search query"},
                                "max_results": {"type": "integer", "description": "Maximum number of results"}
                            },
                            "required": ["query"]
                        }
                    elif tool_name == 'get_gmail_message_content':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "message_id": {"type": "string", "description": "Gmail message ID"}
                            },
                            "required": ["message_id"]
                        }
                    elif tool_name == 'get_gmail_messages_content_batch':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "message_ids": {"type": "array", "items": {"type": "string"}, "description": "List of Gmail message IDs (max 100)"},
                                "format": {"type": "string", "enum": ["full", "metadata"], "description": "Message format - full includes body, metadata only headers"}
                            },
                            "required": ["message_ids"]
                        }
                    elif tool_name == 'draft_gmail_message':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "subject": {"type": "string", "description": "Email subject"},
                                "body": {"type": "string", "description": "Email body content"},
                                "to": {"type": "string", "description": "Optional recipient email address"},
                                "cc": {"type": "string", "description": "CC recipients (optional)"},
                                "bcc": {"type": "string", "description": "BCC recipients (optional)"},
                                "html_body": {"type": "string", "description": "HTML version of email body (optional)"},
                                "thread_id": {"type": "string", "description": "Thread ID to reply to (optional)"},
                                "attachments": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to attach (optional)"}
                            },
                            "required": ["subject", "body"]
                        }
                    elif tool_name == 'get_gmail_thread_content':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "thread_id": {"type": "string", "description": "Gmail thread ID"}
                            },
                            "required": ["thread_id"]
                        }
                    elif tool_name == 'get_gmail_threads_content_batch':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "thread_ids": {"type": "array", "items": {"type": "string"}, "description": "List of Gmail thread IDs (max 100)"}
                            },
                            "required": ["thread_ids"]
                        }
                    elif tool_name == 'list_gmail_labels':
                        input_schema = {
                            "type": "object",
                            "properties": {}
                        }
                    elif tool_name == 'manage_gmail_label':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["create", "update", "delete"], "description": "Action to perform on the label"},
                                "name": {"type": "string", "description": "Label name (required for create, optional for update)"},
                                "label_id": {"type": "string", "description": "Label ID (required for update and delete)"},
                                "label_list_visibility": {"type": "string", "enum": ["labelShow", "labelHide"], "description": "Whether label is shown in label list"},
                                "message_list_visibility": {"type": "string", "enum": ["show", "hide"], "description": "Whether label is shown in message list"}
                            },
                            "required": ["action"]
                        }
                    elif tool_name == 'modify_gmail_message_labels':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "message_id": {"type": "string", "description": "Gmail message ID"},
                                "add_label_ids": {"type": "array", "items": {"type": "string"}, "description": "List of label IDs to add"},
                                "remove_label_ids": {"type": "array", "items": {"type": "string"}, "description": "List of label IDs to remove"}
                            },
                            "required": ["message_id"]
                        }
                    elif tool_name == 'batch_modify_gmail_message_labels':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "message_ids": {"type": "array", "items": {"type": "string"}, "description": "List of Gmail message IDs"},
                                "add_label_ids": {"type": "array", "items": {"type": "string"}, "description": "List of label IDs to add"},
                                "remove_label_ids": {"type": "array", "items": {"type": "string"}, "description": "List of label IDs to remove"}
                            },
                            "required": ["message_ids"]
                        }
                    # Drive tools
                    elif tool_name == 'search_drive_files':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query string (supports Google Drive search operators)"},
                                "page_size": {"type": "integer", "description": "Maximum number of files to return (default: 10)"},
                                "drive_id": {"type": "string", "description": "ID of shared drive to search"},
                                "include_items_from_all_drives": {"type": "boolean", "description": "Include shared drive items"},
                                "corpora": {"type": "string", "enum": ["user", "domain", "drive", "allDrives"], "description": "Bodies of items to query"}
                            },
                            "required": ["query"]
                        }
                    elif tool_name == 'get_drive_file_content':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "file_id": {"type": "string", "description": "Google Drive file ID"}
                            },
                            "required": ["file_id"]
                        }
                    elif tool_name == 'list_drive_items':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "folder_id": {"type": "string", "description": "Google Drive folder ID (default: 'root')"},
                                "page_size": {"type": "integer", "description": "Maximum number of items to return (default: 100)"},
                                "drive_id": {"type": "string", "description": "ID of shared drive"},
                                "include_items_from_all_drives": {"type": "boolean", "description": "Include shared drive items"},
                                "corpora": {"type": "string", "enum": ["user", "domain", "drive", "allDrives"], "description": "Bodies of items to query"}
                            }
                        }
                    elif tool_name == 'create_drive_file':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "file_name": {"type": "string", "description": "Name for the new file"},
                                "content": {"type": "string", "description": "Content to write to the file"},
                                "folder_id": {"type": "string", "description": "Parent folder ID (default: 'root')"},
                                "mime_type": {"type": "string", "description": "MIME type of the file (default: 'text/plain')"},
                                "fileUrl": {"type": "string", "description": "URL to fetch file content from"}
                            },
                            "required": ["file_name"]
                        }
                    # Calendar tools
                    elif tool_name == 'list_calendars':
                        input_schema = {
                            "type": "object",
                            "properties": {}
                        }
                    elif tool_name == 'get_events':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                                "time_min": {"type": "string", "description": "Start of time range (RFC3339 format)"},
                                "time_max": {"type": "string", "description": "End of time range (RFC3339 format)"},
                                "max_results": {"type": "integer", "description": "Maximum number of events to return (default: 25)"}
                            }
                        }
                    elif tool_name == 'create_event':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string", "description": "Event title"},
                                "start_time": {"type": "string", "description": "Start time (RFC3339 format)"},
                                "end_time": {"type": "string", "description": "End time (RFC3339 format)"},
                                "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                                "description": {"type": "string", "description": "Event description"},
                                "location": {"type": "string", "description": "Event location"},
                                "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee email addresses"},
                                "timezone": {"type": "string", "description": "Timezone (e.g., 'America/New_York')"},
                                "attachments": {"type": "array", "items": {"type": "string"}, "description": "Google Drive file URLs or IDs"}
                            },
                            "required": ["summary", "start_time", "end_time"]
                        }
                    elif tool_name == 'modify_event':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string", "description": "Event ID to modify"},
                                "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"},
                                "summary": {"type": "string", "description": "New event title"},
                                "start_time": {"type": "string", "description": "New start time (RFC3339 format)"},
                                "end_time": {"type": "string", "description": "New end time (RFC3339 format)"},
                                "description": {"type": "string", "description": "New event description"},
                                "location": {"type": "string", "description": "New event location"},
                                "attendees": {"type": "array", "items": {"type": "string"}, "description": "New attendee email addresses"},
                                "timezone": {"type": "string", "description": "New timezone"}
                            },
                            "required": ["event_id"]
                        }
                    elif tool_name == 'delete_event':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string", "description": "Event ID to delete"},
                                "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"}
                            },
                            "required": ["event_id"]
                        }
                    elif tool_name == 'get_event':
                        input_schema = {
                            "type": "object",
                            "properties": {
                                "event_id": {"type": "string", "description": "Event ID to retrieve"},
                                "calendar_id": {"type": "string", "description": "Calendar ID (default: 'primary')"}
                            },
                            "required": ["event_id"]
                        }
                    
                    tools.append({
                        "name": tool_name,
                        "description": f"Google Workspace {tool_name.replace('_', ' ').title()} tool",
                        "inputSchema": input_schema
                    })
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_body.get('id'),
                    "result": {"tools": tools}
                }
            elif method == 'tools/call':
                # Handle tool calls
                tool_name = request_body.get('params', {}).get('name')
                # Check both 'arguments' (MCP standard) and direct params (for compatibility)
                tool_args = request_body.get('params', {}).get('arguments', {})
                if not tool_args:
                    # If no 'arguments', check if parameters are directly in params
                    params = request_body.get('params', {})
                    tool_args = {k: v for k, v in params.items() if k != 'name'}
                
                if tool_name in self.tool_registry:
                    try:
                        result = await self.tool_registry[tool_name](**tool_args)
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_body.get('id'),
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": str(result)
                                    }
                                ]
                            }
                        }
                    except Exception as e:
                        logger.error(f"Tool execution error for {tool_name}: {e}")
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_body.get('id'),
                            "error": {
                                "code": -32603,
                                "message": f"Tool execution failed: {str(e)}"
                            }
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_body.get('id'),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_body.get('id'),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
            
            logger.info(f"✅ Request completed successfully for session {session_data.session_id}, request {request_id}")
            return response
            
        except Exception as error:
            logger.error(f"❌ Request failed for session {session_data.session_id}, request {request_id}: {error}")
            raise
        finally:
            # Reset context
            request_context.reset(token)
    
    def cleanup_expired_sessions(self, max_age_seconds: int = 3600):
        """Clean up expired sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            age = (now - session_data.last_activity).total_seconds()
            if age > max_age_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"🧹 Cleaned up expired session: {session_id}")
        
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_session_stats(self) -> dict:
        """Get current session statistics"""
        sessions = []
        for session_data in self.sessions.values():
            age_seconds = (datetime.now() - session_data.created_at).total_seconds()
            sessions.append({
                "sessionId": session_data.session_id,
                "authSessionId": session_data.auth_session_id,
                "requestCount": session_data.request_count,
                "age": f"{int(age_seconds)}s"
            })
        
        return {
            "totalSessions": len(self.sessions),
            "sessions": sessions
        }
    
    async def destroy_session(self, session_id: str) -> bool:
        """Manually destroy a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"🗑️ Manually destroyed session: {session_id}")
            return True
        return False
    
    async def destroy(self):
        """Cleanup all sessions and resources"""
        logger.info(f"🔥 Destroying transport manager with {len(self.sessions)} sessions")
        self.sessions.clear()
        logger.info("✅ Transport manager destroyed")

def get_current_request_context() -> Optional[RequestContext]:
    """Get the current request context"""
    return request_context.get()

def get_current_access_token() -> Optional[str]:
    """Get the access token from current request context"""
    context = get_current_request_context()
    return context.access_token if context else None

async def create_session_aware_server(
    port: int = 8000,
    host: str = "0.0.0.0"
) -> tuple[FastAPI, SessionAwareTransportManager]:
    """Create a FastAPI server with session-aware transport"""
    
    app = FastAPI(title="Google Workspace MCP Server")
    transport_manager = SessionAwareTransportManager()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.options("/mcp")
    async def mcp_options():
        """Handle CORS preflight"""
        return Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, mcp-session-id, Authorization, X-Access-Token, Access-Token"
            }
        )
    
    @app.post("/mcp")
    @app.get("/mcp")
    async def mcp_endpoint(request: Request):
        """Main MCP endpoint with session isolation"""
        try:
            # Parse request body
            if request.method == "POST":
                request_body = await request.json()
            else:
                return JSONResponse({"error": "Only POST requests supported"}, status_code=405)
            
            session_id = request.headers.get('mcp-session-id')
            is_init_request = transport_manager.is_initialize_request(request_body)
            
            # Validate access token for initialize requests
            if is_init_request:
                access_token = transport_manager.extract_access_token_from_headers(request)
                if not access_token:
                    return JSONResponse({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32001,
                            "message": "Authentication Failed",
                            "data": {
                                "reason": "Missing OAuth2 access token",
                                "details": "Please provide access token in Authorization header (Bearer token) or X-Access-Token header",
                                "action": "Add Authorization: Bearer <token> header"
                            }
                        },
                        "id": request_body.get('id')
                    }, status_code=401)
            
            # Validate session ID for non-initialize requests
            if not is_init_request and not session_id:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": "Bad Request: Session ID required for non-initialize requests"
                    },
                    "id": request_body.get('id')
                }, status_code=400)
            
            # Get or create session with complete isolation
            session_data = await transport_manager.get_or_create_session(
                session_id, request, is_init_request
            )
            
            # Handle the request through session-aware transport
            response = await transport_manager.handle_session_request(
                session_data, request, request_body
            )
            
            # For initialize requests, return session ID in header
            headers = {}
            if is_init_request:
                headers["Mcp-Session-Id"] = session_data.session_id
            
            return JSONResponse(response, headers=headers)
            
        except HTTPException as e:
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e.detail)
                },
                "id": None
            }, status_code=e.status_code)
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal server error"
                },
                "id": None
            }, status_code=500)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        session_stats = transport_manager.get_session_stats()
        return {
            "status": "ok",
            "transport": "session-aware-http",
            "timestamp": datetime.now().isoformat(),
            "activeSessions": {
                "total": session_stats["totalSessions"],
                "details": session_stats["sessions"]
            }
        }
    
    @app.get("/sessions")
    async def get_sessions():
        """Get session statistics"""
        return transport_manager.get_session_stats()
    
    @app.delete("/sessions/{session_id}")
    async def delete_session(session_id: str):
        """Delete a specific session"""
        destroyed = await transport_manager.destroy_session(session_id)
        if destroyed:
            return {"message": f"Session {session_id} destroyed successfully"}
        else:
            return JSONResponse(
                {"error": f"Session {session_id} not found"}, 
                status_code=404
            )
    
    return app, transport_manager