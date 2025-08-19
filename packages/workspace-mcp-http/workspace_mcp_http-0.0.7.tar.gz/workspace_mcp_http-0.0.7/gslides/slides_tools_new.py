"""
Google Slides MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with Google Slides API using access token auth.
"""

import logging
import asyncio
from typing import List, Dict, Any

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

logger = logging.getLogger(__name__)

# Required scopes for Slides operations
SLIDES_SCOPES = [
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/presentations.readonly"
]

@handle_http_errors("create_presentation")
async def create_presentation(title: str = "Untitled Presentation") -> str:
    """
    Create a new Google Slides presentation.

    Args:
        title: The title for the new presentation (default: "Untitled Presentation")

    Returns:
        str: Details about the created presentation including ID and URL.
    """
    try:
        service = await get_authenticated_google_service("slides", "v1", "create_presentation")
        
        logger.info(f"[create_presentation] Invoked. Title: '{title}'")

        body = {
            'title': title
        }

        result = await asyncio.to_thread(
            service.presentations().create(body=body).execute
        )

        presentation_id = result.get('presentationId')
        presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"

        confirmation_message = f"""Presentation Created Successfully:
- Title: {title}
- Presentation ID: {presentation_id}
- URL: {presentation_url}
- Slides: {len(result.get('slides', []))} slide(s) created"""

        logger.info(f"Presentation created successfully")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating presentation: {e}")
        return f"Error creating presentation: {str(e)}"

@handle_http_errors("get_presentation", is_read_only=True)
async def get_presentation(presentation_id: str) -> str:
    """
    Get details about a Google Slides presentation.

    Args:
        presentation_id: The ID of the presentation to retrieve

    Returns:
        str: Details about the presentation including title, slides count, and metadata.
    """
    try:
        service = await get_authenticated_google_service("slides", "v1", "get_presentation")
        
        logger.info(f"[get_presentation] Invoked. ID: '{presentation_id}'")

        result = await asyncio.to_thread(
            service.presentations().get(presentationId=presentation_id).execute
        )

        title = result.get('title', 'Untitled')
        slides = result.get('slides', [])
        page_size = result.get('pageSize', {})

        slides_info = []
        for i, slide in enumerate(slides, 1):
            slide_id = slide.get('objectId', 'Unknown')
            page_elements = slide.get('pageElements', [])
            slides_info.append(f"  Slide {i}: ID {slide_id}, {len(page_elements)} element(s)")

        confirmation_message = f"""Presentation Details:
- Title: {title}
- Presentation ID: {presentation_id}
- URL: https://docs.google.com/presentation/d/{presentation_id}/edit
- Total Slides: {len(slides)}
- Page Size: {page_size.get('width', {}).get('magnitude', 'Unknown')} x {page_size.get('height', {}).get('magnitude', 'Unknown')} {page_size.get('width', {}).get('unit', '')}

Slides Breakdown:
{chr(10).join(slides_info) if slides_info else '  No slides found'}"""

        logger.info(f"Presentation retrieved successfully")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting presentation: {e}")
        return f"Error getting presentation: {str(e)}"

@handle_http_errors("batch_update_presentation")
async def batch_update_presentation(
    presentation_id: str,
    requests: List[Dict[str, Any]]
) -> str:
    """
    Apply batch updates to a Google Slides presentation.

    Args:
        presentation_id: The ID of the presentation to update
        requests: List of update requests to apply

    Returns:
        str: Details about the batch update operation results.
    """
    try:
        service = await get_authenticated_google_service("slides", "v1", "batch_update_presentation")
        
        logger.info(f"[batch_update_presentation] Invoked. ID: '{presentation_id}', Requests: {len(requests)}")

        body = {
            'requests': requests
        }

        result = await asyncio.to_thread(
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body=body
            ).execute
        )

        replies = result.get('replies', [])

        confirmation_message = f"""Batch Update Completed:
- Presentation ID: {presentation_id}
- URL: https://docs.google.com/presentation/d/{presentation_id}/edit
- Requests Applied: {len(requests)}
- Replies Received: {len(replies)}"""

        if replies:
            confirmation_message += "\n\nUpdate Results:"
            for i, reply in enumerate(replies, 1):
                if 'createSlide' in reply:
                    slide_id = reply['createSlide'].get('objectId', 'Unknown')
                    confirmation_message += f"\n  Request {i}: Created slide with ID {slide_id}"
                elif 'createShape' in reply:
                    shape_id = reply['createShape'].get('objectId', 'Unknown')
                    confirmation_message += f"\n  Request {i}: Created shape with ID {shape_id}"
                else:
                    confirmation_message += f"\n  Request {i}: Operation completed"

        logger.info(f"Batch update completed successfully")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error batch updating presentation: {e}")
        return f"Error batch updating presentation: {str(e)}"

@handle_http_errors("get_page", is_read_only=True)
async def get_page(
    presentation_id: str,
    page_object_id: str
) -> str:
    """
    Get details about a specific page (slide) in a presentation.

    Args:
        presentation_id: The ID of the presentation
        page_object_id: The object ID of the page/slide to retrieve

    Returns:
        str: Details about the specific page including elements and layout.
    """
    try:
        service = await get_authenticated_google_service("slides", "v1", "get_page")
        
        logger.info(f"[get_page] Invoked. Presentation: '{presentation_id}', Page: '{page_object_id}'")

        result = await asyncio.to_thread(
            service.presentations().pages().get(
                presentationId=presentation_id,
                pageObjectId=page_object_id
            ).execute
        )

        page_type = result.get('pageType', 'Unknown')
        page_elements = result.get('pageElements', [])

        elements_info = []
        for element in page_elements:
            element_id = element.get('objectId', 'Unknown')
            if 'shape' in element:
                shape_type = element['shape'].get('shapeType', 'Unknown')
                elements_info.append(f"  Shape: ID {element_id}, Type: {shape_type}")
            elif 'table' in element:
                table = element['table']
                rows = table.get('rows', 0)
                cols = table.get('columns', 0)
                elements_info.append(f"  Table: ID {element_id}, Size: {rows}x{cols}")
            elif 'line' in element:
                line_type = element['line'].get('lineType', 'Unknown')
                elements_info.append(f"  Line: ID {element_id}, Type: {line_type}")
            else:
                elements_info.append(f"  Element: ID {element_id}, Type: Unknown")

        confirmation_message = f"""Page Details:
- Presentation ID: {presentation_id}
- Page ID: {page_object_id}
- Page Type: {page_type}
- Total Elements: {len(page_elements)}

Page Elements:
{chr(10).join(elements_info) if elements_info else '  No elements found'}"""

        logger.info(f"Page retrieved successfully")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting page: {e}")
        return f"Error getting page: {str(e)}"

@handle_http_errors("get_page_thumbnail", is_read_only=True)
async def get_page_thumbnail(
    presentation_id: str,
    page_object_id: str,
    thumbnail_size: str = "MEDIUM"
) -> str:
    """
    Generate a thumbnail URL for a specific page (slide) in a presentation.

    Args:
        presentation_id: The ID of the presentation
        page_object_id: The object ID of the page/slide
        thumbnail_size: Size of thumbnail ("LARGE", "MEDIUM", "SMALL") (default: "MEDIUM")

    Returns:
        str: URL to the generated thumbnail image.
    """
    try:
        service = await get_authenticated_google_service("slides", "v1", "get_page_thumbnail")
        
        logger.info(f"[get_page_thumbnail] Invoked. Presentation: '{presentation_id}', Page: '{page_object_id}', Size: '{thumbnail_size}'")

        result = await asyncio.to_thread(
            service.presentations().pages().getThumbnail(
                presentationId=presentation_id,
                pageObjectId=page_object_id,
                thumbnailPropertiesImageSize=thumbnail_size
            ).execute
        )

        thumbnail_url = result.get('contentUrl', '')

        confirmation_message = f"""Thumbnail Generated:
- Presentation ID: {presentation_id}
- Page ID: {page_object_id}
- Thumbnail Size: {thumbnail_size}
- Thumbnail URL: {thumbnail_url}

You can view or download the thumbnail using the provided URL."""

        logger.info(f"Thumbnail generated successfully")
        return confirmation_message
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting page thumbnail: {e}")
        return f"Error getting page thumbnail: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("create_presentation", create_presentation)
register_tool_with_transport("get_presentation", get_presentation)
register_tool_with_transport("batch_update_presentation", batch_update_presentation)
register_tool_with_transport("get_page", get_page)
register_tool_with_transport("get_page_thumbnail", get_page_thumbnail)

logger.info("Slides tools registered with session-aware transport")