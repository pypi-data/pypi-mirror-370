#!/usr/bin/env python3
"""
Google Workspace MCP Server - Stateless Version

A stateless Model Context Protocol server for Google Workspace services using Bearer token authentication.
Based on the official Python MCP SDK with complete request isolation and no session management.
"""

import contextlib
import json
import logging
import os
import sys
from collections.abc import AsyncIterator
from typing import Any, Dict, Optional
from datetime import datetime

import click
import mcp.types as types
import uvicorn
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount

# Local imports - Google Workspace components  
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from auth.scopes import SCOPES

# Tool imports - we'll import these dynamically to avoid dependency issues

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BearerTokenMiddleware:
    """Middleware to extract Bearer token and make it available to the request context"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create request to extract headers
            request = Request(scope, receive)
            auth_header = request.headers.get("authorization")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                # Set token in environment for this request context
                os.environ["GOOGLE_ACCESS_TOKEN_FOR_REQUEST"] = token
            else:
                # Clear any existing token
                os.environ.pop("GOOGLE_ACCESS_TOKEN_FOR_REQUEST", None)
        
        await self.app(scope, receive, send)


def get_google_service_from_request(service_name: str, version: str):
    """Get Google API service from current request context using Bearer token"""
    token = os.environ.get("GOOGLE_ACCESS_TOKEN_FOR_REQUEST")
    if not token:
        raise Exception(
            "Authentication required. Please provide Authorization: Bearer <google_access_token> header"
        )
    
    try:
        # Create credentials from the access token
        credentials = Credentials(token=token)
        # Build and return the Google API service
        return build(service_name, version, credentials=credentials)
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google {service_name}: {str(e)}")


# Simple Gmail tools for stateless server
async def gmail_list_labels_stateless(**kwargs) -> Dict:
    """List Gmail labels using stateless authentication"""
    try:
        service = get_google_service_from_request('gmail', 'v1')
        result = service.users().labels().list(userId='me').execute()
        labels = result.get('labels', [])
        
        return {
            'success': True,
            'labels': [
                {
                    'id': label['id'],
                    'name': label['name'],
                    'type': label.get('type', 'user')
                }
                for label in labels
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def gmail_search_messages_stateless(query: str = "", max_results: int = 10, **kwargs) -> Dict:
    """Search Gmail messages using stateless authentication"""
    try:
        service = get_google_service_from_request('gmail', 'v1')
        
        # Search for messages
        request_params = {'userId': 'me', 'maxResults': max_results}
        if query:
            request_params['q'] = query
            
        result = service.users().messages().list(**request_params).execute()
        messages = result.get('messages', [])
        
        # Get details for each message
        detailed_messages = []
        for message in messages[:5]:  # Limit to avoid long responses
            msg_detail = service.users().messages().get(userId='me', id=message['id']).execute()
            
            # Extract headers
            headers = msg_detail.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            detailed_messages.append({
                'id': message['id'],
                'subject': subject,
                'sender': sender,
                'snippet': msg_detail.get('snippet', '')
            })
        
        return {
            'success': True,
            'messages': detailed_messages,
            'query': query,
            'total_found': len(messages)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Simple Drive tools
async def drive_list_files_stateless(query: str = "", max_results: int = 10, **kwargs) -> Dict:
    """List Google Drive files using stateless authentication"""
    try:
        service = get_google_service_from_request('drive', 'v3')
        
        request_params = {
            'pageSize': max_results,
            'fields': 'files(id,name,mimeType,modifiedTime,size,webViewLink)'
        }
        if query:
            request_params['q'] = f"name contains '{query}'"
            
        result = service.files().list(**request_params).execute()
        files = result.get('files', [])
        
        return {
            'success': True,
            'files': [
                {
                    'id': file['id'],
                    'name': file['name'],
                    'mimeType': file['mimeType'],
                    'modifiedTime': file.get('modifiedTime'),
                    'size': file.get('size'),
                    'webViewLink': file.get('webViewLink')
                }
                for file in files
            ],
            'query': query
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Simple Calendar tools
async def calendar_list_events_stateless(max_results: int = 10, **kwargs) -> Dict:
    """List Google Calendar events using stateless authentication"""
    try:
        service = get_google_service_from_request('calendar', 'v3')
        
        # Get primary calendar events
        result = service.events().list(
            calendarId='primary',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = result.get('items', [])
        
        return {
            'success': True,
            'events': [
                {
                    'id': event['id'],
                    'summary': event.get('summary', 'No Title'),
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                    'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date')),
                    'description': event.get('description', '')
                }
                for event in events
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Additional Gmail Tools
async def gmail_get_message_content_stateless(message_id: str, **kwargs) -> Dict:
    """Get detailed information about a specific Gmail message"""
    try:
        service = get_google_service_from_request('gmail', 'v1')
        
        # Get message
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = {}
        for header in message.get('payload', {}).get('headers', []):
            headers[header['name']] = header.get('value', '')
        
        # Extract body content (simplified)
        payload = message.get('payload', {})
        body = ''
        if payload.get('body', {}).get('data'):
            import base64
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        elif payload.get('parts'):
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
        
        return {
            'success': True,
            'message': {
                'id': message['id'],
                'threadId': message.get('threadId'),
                'subject': headers.get('Subject', 'No Subject'),
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'date': headers.get('Date', 'Unknown'),
                'body': body or 'No content found'
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def gmail_send_message_stateless(to: str, subject: str, body: str, **kwargs) -> Dict:
    """Send a Gmail message using stateless authentication"""
    try:
        service = get_google_service_from_request('gmail', 'v1')
        
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return {
            'success': True,
            'message_id': sent_message.get('id'),
            'details': f'Email sent to {to} with subject "{subject}"'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Drive Tools - Stateless Versions
async def drive_get_file_content_stateless(file_id: str, **kwargs) -> Dict:
    """Get Google Drive file content using stateless authentication"""
    try:
        service = get_google_service_from_request('drive', 'v3')
        
        # Get file metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        
        # Get file content (simplified - text files only)
        file_content = service.files().get_media(fileId=file_id).execute()
        
        return {
            'success': True,
            'file': {
                'id': file_metadata['id'],
                'name': file_metadata['name'],
                'mimeType': file_metadata['mimeType'],
                'content': file_content.decode('utf-8', errors='ignore') if isinstance(file_content, bytes) else str(file_content)
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def drive_create_file_stateless(name: str, content: str, parent_folder_id: Optional[str] = None, **kwargs) -> Dict:
    """Create a Google Drive file using stateless authentication"""
    try:
        service = get_google_service_from_request('drive', 'v3')
        
        file_metadata = {'name': name}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
        
        from googleapiclient.http import MediaIoBaseUpload
        import io
        
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')), 
            mimetype='text/plain'
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media
        ).execute()
        
        return {
            'success': True,
            'file': {
                'id': file.get('id'),
                'name': file.get('name'),
                'webViewLink': file.get('webViewLink')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Calendar Tools - Stateless Versions
async def calendar_list_calendars_stateless(**kwargs) -> Dict:
    """List Google Calendars using stateless authentication"""
    try:
        service = get_google_service_from_request('calendar', 'v3')
        
        result = service.calendarList().list().execute()
        calendars = result.get('items', [])
        
        return {
            'success': True,
            'calendars': [
                {
                    'id': cal['id'],
                    'summary': cal.get('summary', ''),
                    'description': cal.get('description', ''),
                    'primary': cal.get('primary', False)
                }
                for cal in calendars
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def calendar_create_event_stateless(summary: str, start_time: str, end_time: str, **kwargs) -> Dict:
    """Create a Google Calendar event using stateless authentication"""
    try:
        service = get_google_service_from_request('calendar', 'v3')
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time}
        }
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        return {
            'success': True,
            'event': {
                'id': created_event.get('id'),
                'summary': created_event.get('summary'),
                'htmlLink': created_event.get('htmlLink')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Docs Tools - Stateless Versions
async def docs_get_document_stateless(document_id: str, **kwargs) -> Dict:
    """Get Google Docs document content using stateless authentication"""
    try:
        service = get_google_service_from_request('docs', 'v1')
        
        document = service.documents().get(documentId=document_id).execute()
        
        # Extract text content (simplified)
        content = []
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for text_element in element['paragraph'].get('elements', []):
                    if 'textRun' in text_element:
                        content.append(text_element['textRun'].get('content', ''))
        
        return {
            'success': True,
            'document': {
                'documentId': document.get('documentId'),
                'title': document.get('title'),
                'content': ''.join(content)
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def docs_create_document_stateless(title: str, content: Optional[str] = None, **kwargs) -> Dict:
    """Create a Google Docs document using stateless authentication"""
    try:
        service = get_google_service_from_request('docs', 'v1')
        
        document = {'title': title}
        created_doc = service.documents().create(body=document).execute()
        
        # Add content if provided
        if content:
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            service.documents().batchUpdate(
                documentId=created_doc['documentId'],
                body={'requests': requests}
            ).execute()
        
        return {
            'success': True,
            'document': {
                'documentId': created_doc.get('documentId'),
                'title': created_doc.get('title'),
                'revisionId': created_doc.get('revisionId')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Sheets Tools - Stateless Versions
async def sheets_get_spreadsheet_stateless(spreadsheet_id: str, **kwargs) -> Dict:
    """Get Google Sheets spreadsheet information using stateless authentication"""
    try:
        service = get_google_service_from_request('sheets', 'v4')
        
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        return {
            'success': True,
            'spreadsheet': {
                'spreadsheetId': spreadsheet.get('spreadsheetId'),
                'title': spreadsheet.get('properties', {}).get('title'),
                'sheets': [
                    {
                        'sheetId': sheet['properties']['sheetId'],
                        'title': sheet['properties']['title']
                    }
                    for sheet in spreadsheet.get('sheets', [])
                ]
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def sheets_read_values_stateless(spreadsheet_id: str, range_name: str, **kwargs) -> Dict:
    """Read values from Google Sheets using stateless authentication"""
    try:
        service = get_google_service_from_request('sheets', 'v4')
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return {
            'success': True,
            'values': result.get('values', []),
            'range': result.get('range')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def sheets_create_spreadsheet_stateless(title: str, **kwargs) -> Dict:
    """Create a Google Sheets spreadsheet using stateless authentication"""
    try:
        service = get_google_service_from_request('sheets', 'v4')
        
        spreadsheet = {'properties': {'title': title}}
        created = service.spreadsheets().create(body=spreadsheet).execute()
        
        return {
            'success': True,
            'spreadsheet': {
                'spreadsheetId': created.get('spreadsheetId'),
                'title': created.get('properties', {}).get('title'),
                'spreadsheetUrl': created.get('spreadsheetUrl')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Slides Tools - Stateless Versions
async def slides_get_presentation_stateless(presentation_id: str, **kwargs) -> Dict:
    """Get Google Slides presentation using stateless authentication"""
    try:
        service = get_google_service_from_request('slides', 'v1')
        
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        
        return {
            'success': True,
            'presentation': {
                'presentationId': presentation.get('presentationId'),
                'title': presentation.get('title'),
                'slides': [
                    {
                        'objectId': slide.get('objectId'),
                        'slideType': slide.get('slideProperties', {}).get('layoutProperties', {}).get('masterObjectId')
                    }
                    for slide in presentation.get('slides', [])
                ]
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def slides_create_presentation_stateless(title: str, **kwargs) -> Dict:
    """Create a Google Slides presentation using stateless authentication"""
    try:
        service = get_google_service_from_request('slides', 'v1')
        
        presentation = {'title': title}
        created = service.presentations().create(body=presentation).execute()
        
        return {
            'success': True,
            'presentation': {
                'presentationId': created.get('presentationId'),
                'title': created.get('title'),
                'revisionId': created.get('revisionId')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Tasks Tools - Stateless Versions
async def tasks_list_task_lists_stateless(**kwargs) -> Dict:
    """List Google Tasks task lists using stateless authentication"""
    try:
        service = get_google_service_from_request('tasks', 'v1')
        
        result = service.tasklists().list().execute()
        task_lists = result.get('items', [])
        
        return {
            'success': True,
            'taskLists': [
                {
                    'id': tl.get('id'),
                    'title': tl.get('title'),
                    'updated': tl.get('updated')
                }
                for tl in task_lists
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def tasks_list_tasks_stateless(task_list_id: str, **kwargs) -> Dict:
    """List tasks from a Google Tasks list using stateless authentication"""
    try:
        service = get_google_service_from_request('tasks', 'v1')
        
        result = service.tasks().list(tasklist=task_list_id).execute()
        tasks = result.get('items', [])
        
        return {
            'success': True,
            'tasks': [
                {
                    'id': task.get('id'),
                    'title': task.get('title'),
                    'status': task.get('status'),
                    'due': task.get('due'),
                    'updated': task.get('updated')
                }
                for task in tasks
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def tasks_create_task_stateless(task_list_id: str, title: str, notes: Optional[str] = None, **kwargs) -> Dict:
    """Create a task in Google Tasks using stateless authentication"""
    try:
        service = get_google_service_from_request('tasks', 'v1')
        
        task = {'title': title}
        if notes:
            task['notes'] = notes
        
        created = service.tasks().insert(
            tasklist=task_list_id,
            body=task
        ).execute()
        
        return {
            'success': True,
            'task': {
                'id': created.get('id'),
                'title': created.get('title'),
                'status': created.get('status')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Forms Tools - Stateless Versions
async def forms_create_form_stateless(title: str, **kwargs) -> Dict:
    """Create a Google Form using stateless authentication"""
    try:
        service = get_google_service_from_request('forms', 'v1')
        
        form = {
            'info': {
                'title': title
            }
        }
        
        created = service.forms().create(body=form).execute()
        
        return {
            'success': True,
            'form': {
                'formId': created.get('formId'),
                'responderUri': created.get('responderUri'),
                'title': created.get('info', {}).get('title')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def forms_get_form_stateless(form_id: str, **kwargs) -> Dict:
    """Get Google Form information using stateless authentication"""
    try:
        service = get_google_service_from_request('forms', 'v1')
        
        form = service.forms().get(formId=form_id).execute()
        
        return {
            'success': True,
            'form': {
                'formId': form.get('formId'),
                'title': form.get('info', {}).get('title'),
                'description': form.get('info', {}).get('description', ''),
                'responderUri': form.get('responderUri')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Chat Tools - Stateless Versions
async def chat_list_spaces_stateless(**kwargs) -> Dict:
    """List Google Chat spaces using stateless authentication"""
    try:
        service = get_google_service_from_request('chat', 'v1')
        
        result = service.spaces().list().execute()
        spaces = result.get('spaces', [])
        
        return {
            'success': True,
            'spaces': [
                {
                    'name': space.get('name'),
                    'displayName': space.get('displayName'),
                    'type': space.get('type')
                }
                for space in spaces
            ]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

async def chat_send_message_stateless(space_name: str, text: str, **kwargs) -> Dict:
    """Send a message to Google Chat using stateless authentication"""
    try:
        service = get_google_service_from_request('chat', 'v1')
        
        message = {'text': text}
        
        sent = service.spaces().messages().create(
            parent=space_name,
            body=message
        ).execute()
        
        return {
            'success': True,
            'message': {
                'name': sent.get('name'),
                'text': sent.get('text'),
                'createTime': sent.get('createTime')
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_stateless_server(enabled_tools: Optional[list] = None) -> Server:
    """Create a fresh MCP server instance for stateless operation"""
    
    app = Server("google-workspace-mcp-stateless")
    
    # Define available tools directly (comprehensive stateless operation)
    all_tools = {
        # Gmail Tools
        'gmail_list_labels': {
            'function': gmail_list_labels_stateless,
            'description': 'List all Gmail labels',
            'inputSchema': {'type': 'object', 'properties': {}}
        },
        'gmail_search_messages': {
            'function': gmail_search_messages_stateless,
            'description': 'Search Gmail messages',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Gmail search query'},
                    'max_results': {'type': 'integer', 'description': 'Maximum results (default: 10)', 'default': 10}
                }
            }
        },
        'gmail_get_message_content': {
            'function': gmail_get_message_content_stateless,
            'description': 'Get detailed information about a specific Gmail message',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'message_id': {'type': 'string', 'description': 'The Gmail message ID'}
                },
                'required': ['message_id']
            }
        },
        'gmail_send_message': {
            'function': gmail_send_message_stateless,
            'description': 'Send a Gmail message',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'to': {'type': 'string', 'description': 'Recipient email address'},
                    'subject': {'type': 'string', 'description': 'Email subject'},
                    'body': {'type': 'string', 'description': 'Email body content'}
                },
                'required': ['to', 'subject', 'body']
            }
        },
        
        # Drive Tools
        'drive_list_files': {
            'function': drive_list_files_stateless,
            'description': 'List Google Drive files',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Search query for file names'},
                    'max_results': {'type': 'integer', 'description': 'Maximum results (default: 10)', 'default': 10}
                }
            }
        },
        'drive_get_file_content': {
            'function': drive_get_file_content_stateless,
            'description': 'Get Google Drive file content',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'file_id': {'type': 'string', 'description': 'The Drive file ID'}
                },
                'required': ['file_id']
            }
        },
        'drive_create_file': {
            'function': drive_create_file_stateless,
            'description': 'Create a Google Drive file',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'File name'},
                    'content': {'type': 'string', 'description': 'File content'},
                    'parent_folder_id': {'type': 'string', 'description': 'Parent folder ID (optional)'}
                },
                'required': ['name', 'content']
            }
        },
        
        # Calendar Tools
        'calendar_list_events': {
            'function': calendar_list_events_stateless,
            'description': 'List Google Calendar events',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'max_results': {'type': 'integer', 'description': 'Maximum events (default: 10)', 'default': 10}
                }
            }
        },
        'calendar_list_calendars': {
            'function': calendar_list_calendars_stateless,
            'description': 'List Google Calendars',
            'inputSchema': {'type': 'object', 'properties': {}}
        },
        'calendar_create_event': {
            'function': calendar_create_event_stateless,
            'description': 'Create a Google Calendar event',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'summary': {'type': 'string', 'description': 'Event title'},
                    'start_time': {'type': 'string', 'description': 'Start time (ISO format)'},
                    'end_time': {'type': 'string', 'description': 'End time (ISO format)'}
                },
                'required': ['summary', 'start_time', 'end_time']
            }
        },
        
        # Docs Tools
        'docs_get_document': {
            'function': docs_get_document_stateless,
            'description': 'Get Google Docs document content',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'document_id': {'type': 'string', 'description': 'The document ID'}
                },
                'required': ['document_id']
            }
        },
        'docs_create_document': {
            'function': docs_create_document_stateless,
            'description': 'Create a Google Docs document',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Document title'},
                    'content': {'type': 'string', 'description': 'Initial content (optional)'}
                },
                'required': ['title']
            }
        },
        
        # Sheets Tools
        'sheets_get_spreadsheet': {
            'function': sheets_get_spreadsheet_stateless,
            'description': 'Get Google Sheets spreadsheet information',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'spreadsheet_id': {'type': 'string', 'description': 'The spreadsheet ID'}
                },
                'required': ['spreadsheet_id']
            }
        },
        'sheets_read_values': {
            'function': sheets_read_values_stateless,
            'description': 'Read values from Google Sheets',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'spreadsheet_id': {'type': 'string', 'description': 'The spreadsheet ID'},
                    'range_name': {'type': 'string', 'description': 'Range to read (e.g., "A1:C10")'}
                },
                'required': ['spreadsheet_id', 'range_name']
            }
        },
        'sheets_create_spreadsheet': {
            'function': sheets_create_spreadsheet_stateless,
            'description': 'Create a Google Sheets spreadsheet',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Spreadsheet title'}
                },
                'required': ['title']
            }
        },
        
        # Slides Tools
        'slides_get_presentation': {
            'function': slides_get_presentation_stateless,
            'description': 'Get Google Slides presentation',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'presentation_id': {'type': 'string', 'description': 'The presentation ID'}
                },
                'required': ['presentation_id']
            }
        },
        'slides_create_presentation': {
            'function': slides_create_presentation_stateless,
            'description': 'Create a Google Slides presentation',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Presentation title'}
                },
                'required': ['title']
            }
        },
        
        # Tasks Tools
        'tasks_list_task_lists': {
            'function': tasks_list_task_lists_stateless,
            'description': 'List Google Tasks task lists',
            'inputSchema': {'type': 'object', 'properties': {}}
        },
        'tasks_list_tasks': {
            'function': tasks_list_tasks_stateless,
            'description': 'List tasks from a Google Tasks list',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'task_list_id': {'type': 'string', 'description': 'The task list ID'}
                },
                'required': ['task_list_id']
            }
        },
        'tasks_create_task': {
            'function': tasks_create_task_stateless,
            'description': 'Create a task in Google Tasks',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'task_list_id': {'type': 'string', 'description': 'The task list ID'},
                    'title': {'type': 'string', 'description': 'Task title'},
                    'notes': {'type': 'string', 'description': 'Task notes (optional)'}
                },
                'required': ['task_list_id', 'title']
            }
        },
        
        # Forms Tools
        'forms_create_form': {
            'function': forms_create_form_stateless,
            'description': 'Create a Google Form',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Form title'}
                },
                'required': ['title']
            }
        },
        'forms_get_form': {
            'function': forms_get_form_stateless,
            'description': 'Get Google Form information',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'form_id': {'type': 'string', 'description': 'The form ID'}
                },
                'required': ['form_id']
            }
        },
        
        # Chat Tools
        'chat_list_spaces': {
            'function': chat_list_spaces_stateless,
            'description': 'List Google Chat spaces',
            'inputSchema': {'type': 'object', 'properties': {}}
        },
        'chat_send_message': {
            'function': chat_send_message_stateless,
            'description': 'Send a message to Google Chat',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'space_name': {'type': 'string', 'description': 'The chat space name'},
                    'text': {'type': 'string', 'description': 'Message text'}
                },
                'required': ['space_name', 'text']
            }
        }
    }
    
    # Filter tools if specific services are requested
    if enabled_tools:
        filtered_tools = {}
        for tool_name, tool_info in all_tools.items():
            service_name = tool_name.split('_')[0]  # Extract service name (gmail, drive, etc.)
            if service_name in enabled_tools:
                filtered_tools[tool_name] = tool_info
        available_tools = filtered_tools
    else:
        available_tools = all_tools

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available Google Workspace tools"""
        tool_list = []
        
        for tool_name, tool_info in available_tools.items():
            tool_list.append(
                types.Tool(
                    name=tool_name,
                    description=tool_info.get("description", f"Google Workspace {tool_name} tool"),
                    inputSchema=tool_info.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                )
            )
        
        return tool_list

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        """Handle tool calls with Google OAuth token from Bearer header"""
        try:
            # Check if access token is available (set by middleware)
            if not os.environ.get("GOOGLE_ACCESS_TOKEN_FOR_REQUEST"):
                raise Exception("Authentication required. Please provide Authorization: Bearer <google_access_token> header")
            
            if name not in available_tools:
                raise ValueError(f"Unknown tool: {name}")
            
            tool_info = available_tools[name]
            tool_function = tool_info["function"]
            
            # Call the tool function with arguments (access token is retrieved from environment)
            try:
                result = await tool_function(**arguments)
            except TypeError:
                # Handle sync functions
                result = tool_function(**arguments)
            
            # Format the result as JSON
            if isinstance(result, dict):
                result_text = json.dumps(result, indent=2, default=str)
            else:
                result_text = str(result)
            
            return [
                types.TextContent(
                    type="text",
                    text=result_text
                )
            ]
            
        except Exception as e:
            logger.error(f"Tool execution error for {name}: {e}")
            error_response = {
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "tool": name
            }
            
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(error_response, indent=2)
                )
            ]
    
    return app


@click.command()
@click.option("--port", default=30000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO", 
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=True,
    help="Enable JSON responses instead of SSE streams",
)
@click.option(
    "--tools",
    help="Comma-separated list of tools to enable (gmail,drive,calendar,docs,sheets,chat,forms,slides,tasks). If not specified, all tools are enabled.",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
    tools: Optional[str],
) -> int:
    """Main entry point for the stateless Google Workspace MCP server"""
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Parse enabled tools
    enabled_tools = None
    if tools:
        enabled_tools = [tool.strip() for tool in tools.split(",")]
        logger.info(f"Enabling tools: {enabled_tools}")
    else:
        logger.info("Enabling all tools")

    # Create server instance
    app = create_stateless_server(enabled_tools)
    
    # Get tool count for logging
    tool_count = 25 if not enabled_tools else len([s for s in enabled_tools if s in ['gmail', 'drive', 'calendar', 'docs', 'sheets', 'chat', 'forms', 'slides', 'tasks']])

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,          # No event store in stateless mode
        json_response=json_response, # Use JSON responses instead of SSE
        stateless=True,            # Enable stateless mode
    )

    async def handle_streamable_http(scope, receive, send):
        """Handle incoming HTTP requests for MCP protocol"""
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("🚀 Stateless Google Workspace MCP Server started!")
            logger.info(f"📡 Endpoint: http://localhost:{port}/mcp/")
            logger.info("🔓 Session management: DISABLED (stateless)")
            logger.info("🔑 Authentication: Bearer token required")
            logger.info("📋 Available services: Gmail, Drive, Calendar, Docs, Sheets, Chat, Forms, Slides, Tasks")
            logger.info(f"🔧 Total tools available: {tool_count}")
            try:
                yield
            finally:
                logger.info("🔽 MCP Server shutting down...")

    # Create ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )
    
    # Add Bearer token middleware
    starlette_app = BearerTokenMiddleware(starlette_app)

    # Start server
    logger.info(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)