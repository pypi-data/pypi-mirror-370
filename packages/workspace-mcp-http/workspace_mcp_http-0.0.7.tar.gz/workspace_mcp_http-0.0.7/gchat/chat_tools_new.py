"""
Google Chat MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with Google Chat API using access token auth.
"""
import logging
import asyncio
from typing import Optional

from googleapiclient.errors import HttpError

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

logger = logging.getLogger(__name__)

# Required scopes for Chat operations
CHAT_SCOPES = [
    "https://www.googleapis.com/auth/chat.spaces",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
    "https://www.googleapis.com/auth/chat.messages",
    "https://www.googleapis.com/auth/chat.messages.readonly"
]

@handle_http_errors("list_spaces")
async def list_spaces(
    page_size: int = 100,
    space_type: str = "all"  # "all", "room", "dm"
) -> str:
    """
    Lists Google Chat spaces (rooms and direct messages) accessible to the user.

    Args:
        page_size: Maximum number of spaces to return (default: 100)
        space_type: Type of spaces to list - "all", "room", or "dm" (default: "all")

    Returns:
        str: A formatted list of Google Chat spaces accessible to the user.
    """
    try:
        service = await get_authenticated_google_service("chat", "v1", "list_spaces")
        
        logger.info(f"[list_spaces] Type={space_type}")

        # Build filter based on space_type
        filter_param = None
        if space_type == "room":
            filter_param = "spaceType = SPACE"
        elif space_type == "dm":
            filter_param = "spaceType = DIRECT_MESSAGE"

        request_params = {"pageSize": page_size}
        if filter_param:
            request_params["filter"] = filter_param

        response = await asyncio.to_thread(
            service.spaces().list(**request_params).execute
        )

        spaces = response.get('spaces', [])
        if not spaces:
            return f"No Chat spaces found for type '{space_type}'."

        output = [f"Found {len(spaces)} Chat spaces (type: {space_type}):"]
        for space in spaces:
            space_name = space.get('displayName', 'Unnamed Space')
            space_id = space.get('name', '')
            space_type_actual = space.get('spaceType', 'UNKNOWN')
            output.append(f"- {space_name} (ID: {space_id}, Type: {space_type_actual})")

        return "\n".join(output)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error listing spaces: {e}")
        return f"Error listing spaces: {str(e)}"

@handle_http_errors("get_messages")
async def get_messages(
    space_id: str,
    page_size: int = 50,
    order_by: str = "createTime desc"
) -> str:
    """
    Retrieves messages from a Google Chat space.

    Args:
        space_id: The ID of the space to get messages from
        page_size: Maximum number of messages to return (default: 50)
        order_by: Order to sort messages (default: "createTime desc")

    Returns:
        str: Formatted messages from the specified space.
    """
    try:
        service = await get_authenticated_google_service("chat", "v1", "get_messages")
        
        logger.info(f"[get_messages] Space ID: '{space_id}'")

        # Get space info first
        space_info = await asyncio.to_thread(
            service.spaces().get(name=space_id).execute
        )
        space_name = space_info.get('displayName', 'Unknown Space')

        # Get messages
        response = await asyncio.to_thread(
            service.spaces().messages().list(
                parent=space_id,
                pageSize=page_size,
                orderBy=order_by
            ).execute
        )

        messages = response.get('messages', [])
        if not messages:
            return f"No messages found in space '{space_name}' (ID: {space_id})."

        output = [f"Messages from '{space_name}' (ID: {space_id}):\n"]
        for msg in messages:
            sender = msg.get('sender', {}).get('displayName', 'Unknown Sender')
            create_time = msg.get('createTime', 'Unknown Time')
            text_content = msg.get('text', 'No text content')
            msg_name = msg.get('name', '')

            output.append(f"[{create_time}] {sender}:")
            output.append(f"  {text_content}")
            output.append(f"  (Message ID: {msg_name})\n")

        return "\n".join(output)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return f"Error getting messages: {str(e)}"

@handle_http_errors("send_message")
async def send_message(
    space_id: str,
    message_text: str,
    thread_key: Optional[str] = None
) -> str:
    """
    Sends a message to a Google Chat space.

    Args:
        space_id: The ID of the space to send the message to
        message_text: The text content of the message
        thread_key: Optional thread key for threaded replies

    Returns:
        str: Confirmation message with sent message details.
    """
    try:
        service = await get_authenticated_google_service("chat", "v1", "send_message")
        
        logger.info(f"[send_message] Space: '{space_id}'")

        message_body = {
            'text': message_text
        }

        # Add thread key if provided (for threaded replies)
        request_params = {
            'parent': space_id,
            'body': message_body
        }
        if thread_key:
            request_params['threadKey'] = thread_key

        message = await asyncio.to_thread(
            service.spaces().messages().create(**request_params).execute
        )

        message_name = message.get('name', '')
        create_time = message.get('createTime', '')

        msg = f"Message sent to space '{space_id}'. Message ID: {message_name}, Time: {create_time}"
        logger.info(f"Successfully sent message to space '{space_id}'")
        return msg
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return f"Error sending message: {str(e)}"

@handle_http_errors("search_messages")
async def search_messages(
    query: str,
    space_id: Optional[str] = None,
    page_size: int = 25
) -> str:
    """
    Searches for messages in Google Chat spaces by text content.

    Args:
        query: The search query text
        space_id: Optional specific space ID to search in (if not provided, searches across spaces)
        page_size: Maximum number of results to return (default: 25)

    Returns:
        str: A formatted list of messages matching the search query.
    """
    try:
        service = await get_authenticated_google_service("chat", "v1", "search_messages")
        
        logger.info(f"[search_messages] Query='{query}'")

        # If specific space provided, search within that space
        if space_id:
            response = await asyncio.to_thread(
                service.spaces().messages().list(
                    parent=space_id,
                    pageSize=page_size,
                    filter=f'text:"{query}"'
                ).execute
            )
            messages = response.get('messages', [])
            context = f"space '{space_id}'"
        else:
            # Search across all accessible spaces (this may require iterating through spaces)
            # For simplicity, we'll search the user's spaces first
            spaces_response = await asyncio.to_thread(
                service.spaces().list(pageSize=100).execute
            )
            spaces = spaces_response.get('spaces', [])

            messages = []
            for space in spaces[:10]:  # Limit to first 10 spaces to avoid timeout
                try:
                    space_messages = await asyncio.to_thread(
                        service.spaces().messages().list(
                            parent=space.get('name'),
                            pageSize=5,
                            filter=f'text:"{query}"'
                        ).execute
                    )
                    space_msgs = space_messages.get('messages', [])
                    for msg in space_msgs:
                        msg['_space_name'] = space.get('displayName', 'Unknown')
                    messages.extend(space_msgs)
                except HttpError:
                    continue  # Skip spaces we can't access
            context = "all accessible spaces"

        if not messages:
            return f"No messages found matching '{query}' in {context}."

        output = [f"Found {len(messages)} messages matching '{query}' in {context}:"]
        for msg in messages:
            sender = msg.get('sender', {}).get('displayName', 'Unknown Sender')
            create_time = msg.get('createTime', 'Unknown Time')
            text_content = msg.get('text', 'No text content')
            space_name = msg.get('_space_name', 'Unknown Space')

            # Truncate long messages
            if len(text_content) > 100:
                text_content = text_content[:100] + "..."

            output.append(f"- [{create_time}] {sender} in '{space_name}': {text_content}")

        return "\n".join(output)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        return f"Error searching messages: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("list_spaces", list_spaces)
register_tool_with_transport("get_messages", get_messages)
register_tool_with_transport("send_message", send_message)
register_tool_with_transport("search_messages", search_messages)

logger.info("Chat tools registered with session-aware transport")