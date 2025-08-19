"""
Google Gmail MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with the Gmail API using access token auth.
"""

import logging
import asyncio
import base64
import os
import mimetypes
from typing import Optional, List, Dict, Literal
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

logger = logging.getLogger(__name__)

# Required scopes for Gmail operations
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels"
]

def _extract_email_content(payload):
    """
    Enhanced helper function to extract both plain text and HTML content from Gmail message payload.
    Handles complex email structures with nested parts more robustly.
    """
    text_content = ""
    html_content = ""
    
    def process_part(part):
        nonlocal text_content, html_content
        
        # If the part has body data, process it based on MIME type
        if part.get("body", {}).get("data"):
            try:
                content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                
                if part.get("mimeType") == "text/plain":
                    text_content += content
                elif part.get("mimeType") == "text/html":
                    html_content += content
            except Exception:
                pass  # Skip malformed parts
        
        # Recursively process nested parts
        if part.get("parts"):
            for subpart in part["parts"]:
                process_part(subpart)
    
    # Start processing from the root payload
    if payload:
        process_part(payload)
    
    return {"text": text_content, "html": html_content}

def _extract_headers(payload: dict, header_names: List[str]) -> Dict[str, str]:
    """Extract specified headers from a Gmail message payload."""
    headers = {}
    for header in payload.get("headers", []):
        if header.get("name") in header_names:
            headers[header["name"]] = header.get("value", "")
    return headers

def _extract_attachments(payload: dict) -> List[Dict[str, str]]:
    """Extract attachment information from Gmail message payload."""
    attachments = []
    
    def process_part(part, path=""):
        # Check if this part is an attachment
        if part.get("body", {}).get("attachmentId"):
            filename = part.get("filename") or f"attachment-{part['body']['attachmentId']}"
            attachments.append({
                "id": part["body"]["attachmentId"],
                "filename": filename,
                "mimeType": part.get("mimeType", "application/octet-stream"),
                "size": part.get("body", {}).get("size", 0)
            })
        
        # Recursively process nested parts
        if part.get("parts"):
            for i, subpart in enumerate(part["parts"]):
                process_part(subpart, f"{path}/parts[{i}]")
    
    if payload:
        process_part(payload)
    
    return attachments

def _generate_gmail_web_url(item_id: str, account_index: int = 0) -> str:
    """Generate Gmail web interface URL for a message or thread ID."""
    return f"https://mail.google.com/mail/u/{account_index}/#all/{item_id}"

def _format_gmail_results_plain(messages: list, query: str) -> str:
    """Format Gmail search results in clean, LLM-friendly plain text."""
    if not messages:
        return f"No messages found for query: '{query}'"

    lines = [
        f"Found {len(messages)} messages matching '{query}':",
        "",
        "📧 MESSAGES:",
    ]

    for i, msg in enumerate(messages, 1):
        message_url = _generate_gmail_web_url(msg["id"])
        thread_url = _generate_gmail_web_url(msg["threadId"])

        lines.extend(
            [
                f"  {i}. Message ID: {msg['id']}",
                f"     Web Link: {message_url}",
                f"     Thread ID: {msg['threadId']}",
                f"     Thread Link: {thread_url}",
                "",
            ]
        )

    lines.extend(
        [
            "💡 USAGE:",
            "  • Pass the Message IDs **as a list** to get_gmail_messages_content_batch()",
            "    e.g. get_gmail_messages_content_batch(message_ids=[...])",
            "  • Pass the Thread IDs to get_gmail_thread_content() (single) or get_gmail_threads_content_batch() (batch)",
        ]
    )

    return "\n".join(lines)

@handle_http_errors("search_gmail_messages", is_read_only=True)
async def search_gmail_messages(
    query: str,
    max_results: int = 10
) -> str:
    """
    Search Gmail messages using Gmail search syntax.
    
    Args:
        query: Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting')
        max_results: Maximum number of messages to return (default: 10)
    
    Returns:
        Formatted search results with full email content (body always included)
    """
    try:
        # Get authenticated Gmail service
        service = await get_authenticated_google_service("gmail", "v1", "search_gmail_messages")
        
        logger.info(f"[search_gmail_messages] Query: '{query}', Include body: True (always)")

        # Search for messages
        response = await asyncio.to_thread(
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute
        )
        
        messages = response.get("messages", [])
        if not messages:
            return f"No messages found for query: '{query}'"

        # Always get detailed information for each message with full content
        result_lines = [f"Found {len(messages)} messages matching '{query}':", ""]
        
        for i, message in enumerate(messages, 1):
            msg_detail = await asyncio.to_thread(
                service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute
            )
            
            # Extract headers
            headers = _extract_headers(
                msg_detail['payload'], 
                ['From', 'To', 'Subject', 'Date']
            )
            
            # Extract email content (both text and HTML)
            content = _extract_email_content(msg_detail['payload'])
            body_content = content.get("text") or content.get("html") or "[No content found]"
            
            # Extract attachments
            attachments = _extract_attachments(msg_detail['payload'])
            attachment_info = ""
            if attachments:
                attachment_info = f"\n\nAttachments ({len(attachments)}):\n"
                attachment_info += "\n".join([
                    f"- {att['filename']} ({att['mimeType']}, {att['size']} bytes, ID: {att['id']})"
                    for att in attachments
                ])
            
            # Add content type note if only HTML is available
            content_note = ""
            if not content.get("text") and content.get("html"):
                content_note = "[Note: HTML-only email, plain text not available]\n\n"
            
            # Add message details to result
            result_lines.extend([
                f"=== Message {i} ===",
                f"Message ID: {message['id']}",
                f"Subject: {headers.get('Subject', 'No Subject')}",
                f"From: {headers.get('From', 'Unknown')}",
                f"To: {headers.get('To', 'Unknown')}",
                f"Date: {headers.get('Date', 'Unknown')}",
                f"Thread ID: {msg_detail.get('threadId', 'Unknown')}",
                f"Web Link: {_generate_gmail_web_url(message['id'])}",
                "",
                "--- EMAIL CONTENT ---",
                content_note + body_content + attachment_info,
                "",
            ])

        logger.info(f"[search_gmail_messages] Found {len(messages)} messages with content")
        return "\n".join(result_lines)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error searching Gmail messages: {e}")
        return f"Error searching Gmail messages: {str(e)}"

@handle_http_errors("get_gmail_message_content", is_read_only=True)
async def get_gmail_message_content(message_id: str) -> str:
    """
    Get detailed information about a specific Gmail message.
    
    Args:
        message_id: The Gmail message ID
    
    Returns:
        Detailed message information
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_message_content")
        
        logger.info(f"[get_gmail_message_content] Invoked. Message ID: '{message_id}'")

        # Fetch message metadata first to get headers
        message_metadata = await asyncio.to_thread(
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Subject", "From"],
            )
            .execute
        )

        headers = {
            h["name"]: h["value"]
            for h in message_metadata.get("payload", {}).get("headers", [])
        }
        subject = headers.get("Subject", "(no subject)")
        sender = headers.get("From", "(unknown sender)")

        # Now fetch the full message to get the body parts
        message_full = await asyncio.to_thread(
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",  # Request full payload for body
            )
            .execute
        )

        # Extract email content using enhanced helper function
        payload = message_full.get("payload", {})
        content = _extract_email_content(payload)
        body_data = content.get("text") or content.get("html") or "[No content found]"
        
        # Extract attachments
        attachments = _extract_attachments(payload)
        attachment_info = ""
        if attachments:
            attachment_info = f"\n\nAttachments ({len(attachments)}):\n"
            attachment_info += "\n".join([
                f"- {att['filename']} ({att['mimeType']}, {att['size']} bytes, ID: {att['id']})"
                for att in attachments
            ])
        
        # Add content type note if only HTML is available
        content_note = ""
        if not content.get("text") and content.get("html"):
            content_note = "\n[Note: HTML-only email, plain text not available]\n"

        content_text = "\n".join(
            [
                f"Subject: {subject}",
                f"From:    {sender}",
                f"Thread ID: {message_full.get('threadId', 'Unknown')}",
                f"\n--- BODY ---{content_note}\n{body_data}{attachment_info}",
            ]
        )
        return content_text
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail message: {e}")
        return f"Error getting Gmail message: {str(e)}"

@handle_http_errors("get_gmail_messages_content_batch", is_read_only=True)
async def get_gmail_messages_content_batch(
    message_ids: List[str],
    format: Literal["full", "metadata"] = "full",
) -> str:
    """
    Retrieves the content of multiple Gmail messages in a single batch request.
    Supports up to 100 messages per request using Google's batch API.

    Args:
        message_ids (List[str]): List of Gmail message IDs to retrieve (max 100).
        format (Literal["full", "metadata"]): Message format. "full" includes body, "metadata" only headers.

    Returns:
        str: A formatted list of message contents with separators.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_messages_content_batch")
        
        logger.info(
            f"[get_gmail_messages_content_batch] Invoked. Message count: {len(message_ids)}"
        )

        if not message_ids:
            raise Exception("No message IDs provided")

        output_messages = []

        # Process in chunks of 100 (Gmail batch limit)
        for chunk_start in range(0, len(message_ids), 100):
            chunk_ids = message_ids[chunk_start : chunk_start + 100]
            results: Dict[str, Dict] = {}

            def _batch_callback(request_id, response, exception):
                """Enhanced callback for batch requests with better error handling"""
                if exception:
                    logger.warning(f"Batch request failed for {request_id}: {exception}")
                results[request_id] = {"data": response, "error": exception}

            # Try to use batch API with enhanced error handling
            try:
                batch = service.new_batch_http_request(callback=_batch_callback)

                for mid in chunk_ids:
                    if format == "metadata":
                        req = (
                            service.users()
                            .messages()
                            .get(
                                userId="me",
                                id=mid,
                                format="metadata",
                                metadataHeaders=["Subject", "From", "Date"],
                            )
                        )
                    else:
                        req = (
                            service.users()
                            .messages()
                            .get(userId="me", id=mid, format="full")
                        )
                    batch.add(req, request_id=mid)

                # Execute batch request with timeout
                await asyncio.wait_for(
                    asyncio.to_thread(batch.execute),
                    timeout=30.0  # 30 second timeout for batch operations
                )

            except Exception as batch_error:
                # Fallback to parallel individual requests if batch API fails
                logger.warning(
                    f"[get_gmail_messages_content_batch] Batch API failed, falling back to parallel requests: {batch_error}"
                )

                async def fetch_message(mid: str):
                    try:
                        if format == "metadata":
                            msg = await asyncio.wait_for(
                                asyncio.to_thread(
                                    service.users()
                                    .messages()
                                    .get(
                                        userId="me",
                                        id=mid,
                                        format="metadata",
                                        metadataHeaders=["Subject", "From", "Date"],
                                    )
                                    .execute
                                ),
                                timeout=10.0  # 10 second timeout per message
                            )
                        else:
                            msg = await asyncio.wait_for(
                                asyncio.to_thread(
                                    service.users()
                                    .messages()
                                    .get(userId="me", id=mid, format="full")
                                    .execute
                                ),
                                timeout=15.0  # 15 second timeout for full message
                            )
                        return mid, msg, None
                    except Exception as e:
                        return mid, None, e

                # Fetch all messages in parallel with controlled concurrency
                semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
                
                async def fetch_with_semaphore(mid):
                    async with semaphore:
                        return await fetch_message(mid)
                
                fetch_results = await asyncio.gather(
                    *[fetch_with_semaphore(mid) for mid in chunk_ids], 
                    return_exceptions=True  # Don't fail entire batch on single error
                )

                # Convert to results format with error handling
                for i, result in enumerate(fetch_results):
                    mid = chunk_ids[i]
                    if isinstance(result, Exception):
                        results[mid] = {"data": None, "error": result}
                    else:
                        mid_result, msg, error = result
                        results[mid] = {"data": msg, "error": error}

            # Process results for this chunk
            for mid in chunk_ids:
                entry = results.get(mid, {"data": None, "error": "No result"})

                if entry["error"]:
                    output_messages.append(f"⚠️ Message {mid}: {entry['error']}\n")
                else:
                    message = entry["data"]
                    if not message:
                        output_messages.append(f"⚠️ Message {mid}: No data returned\n")
                        continue

                    # Extract content based on format
                    payload = message.get("payload", {})

                    if format == "metadata":
                        headers = _extract_headers(payload, ["Subject", "From"])
                        subject = headers.get("Subject", "(no subject)")
                        sender = headers.get("From", "(unknown sender)")

                        output_messages.append(
                            f"Message ID: {mid}\n"
                            f"Subject: {subject}\n"
                            f"From: {sender}\n"
                            f"Web Link: {_generate_gmail_web_url(mid)}\n"
                        )
                    else:
                        # Full format - extract body too
                        headers = _extract_headers(payload, ["Subject", "From"])
                        subject = headers.get("Subject", "(no subject)")
                        sender = headers.get("From", "(unknown sender)")
                        content = _extract_email_content(payload)
                        body = content.get("text") or content.get("html") or "[No content found]"
                        
                        # Extract attachments
                        attachments = _extract_attachments(payload)
                        attachment_info = ""
                        if attachments:
                            attachment_info = f"\n\nAttachments ({len(attachments)}):\n"
                            attachment_info += "\n".join([
                                f"- {att['filename']} ({att['mimeType']}, {att['size']} bytes)"
                                for att in attachments
                            ])

                        output_messages.append(
                            f"Message ID: {mid}\n"
                            f"Subject: {subject}\n"
                            f"From: {sender}\n"
                            f"Web Link: {_generate_gmail_web_url(mid)}\n"
                            f"\n{body}{attachment_info}\n"
                        )

        # Combine all messages with separators
        final_output = f"Retrieved {len(message_ids)} messages:\n\n"
        final_output += "\n---\n\n".join(output_messages)

        return final_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail messages batch: {e}")
        return f"Error getting Gmail messages batch: {str(e)}"

def _create_simple_message(to: str, subject: str, body: str, html_body: Optional[str] = None,
                         cc: Optional[str] = None, bcc: Optional[str] = None, 
                         is_html_content: bool = False, in_reply_to: Optional[str] = None):
    """Create a simple email message without attachments."""
    if is_html_content:
        from email.mime.text import MIMEText as MIMETextPart
        import re
        
        html_content = html_body if html_body else body
        plain_content = re.sub(r'<[^>]+>', '', html_content)
        plain_content = re.sub(r'\s+', ' ', plain_content).strip()
        
        message = MIMEMultipart('alternative')
        message.attach(MIMETextPart(plain_content, 'plain'))
        message.attach(MIMETextPart(html_content, 'html'))
    else:
        message = MIMEText(body, 'plain')
    
    message['to'] = to
    message['subject'] = subject
    
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc
    if in_reply_to:
        message['In-Reply-To'] = in_reply_to
        message['References'] = in_reply_to
    
    return message

async def _create_message_with_attachments(to: str, subject: str, body: str, 
                                         html_body: Optional[str] = None,
                                         cc: Optional[str] = None, bcc: Optional[str] = None,
                                         attachments: List[str] = None,
                                         in_reply_to: Optional[str] = None) -> str:
    """Create RFC-compliant email message with attachments using a Node.js-like approach."""
    
    logger.info(f"[_create_message_with_attachments] Creating message with {len(attachments)} attachments")
    
    # Generate boundary for multipart message
    import random
    import string
    boundary = '----=_NextPart_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Start building the raw message
    lines = []
    
    # Headers
    lines.append('MIME-Version: 1.0')
    lines.append(f'To: {to}')
    lines.append(f'Subject: {subject}')
    
    if cc:
        lines.append(f'Cc: {cc}')
    if bcc:
        lines.append(f'Bcc: {bcc}')
    if in_reply_to:
        lines.append(f'In-Reply-To: {in_reply_to}')
        lines.append(f'References: {in_reply_to}')
    
    lines.append(f'Content-Type: multipart/mixed; boundary="{boundary}"')
    lines.append('')
    
    # Body part
    lines.append(f'--{boundary}')
    
    # Determine if we need HTML handling
    is_html_content = html_body or (
        '<' in body and '>' in body and 
        any(tag in body.lower() for tag in ['<b>', '<i>', '<u>', '<div>', '<p>', '<br>', '<ul>', '<ol>', '<li>', '<span>', '<a'])
    )
    
    if is_html_content:
        # Create alternative content for HTML emails
        import re
        html_content = html_body if html_body else body
        plain_content = re.sub(r'<[^>]+>', '', html_content)
        plain_content = re.sub(r'\s+', ' ', plain_content).strip()
        
        alt_boundary = '----=_Alt_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        lines.append(f'Content-Type: multipart/alternative; boundary="{alt_boundary}"')
        lines.append('')
        
        # Plain text part
        lines.append(f'--{alt_boundary}')
        lines.append('Content-Type: text/plain; charset=UTF-8')
        lines.append('Content-Transfer-Encoding: 7bit')
        lines.append('')
        lines.append(plain_content)
        lines.append('')
        
        # HTML part
        lines.append(f'--{alt_boundary}')
        lines.append('Content-Type: text/html; charset=UTF-8')
        lines.append('Content-Transfer-Encoding: 7bit')
        lines.append('')
        lines.append(html_content)
        lines.append('')
        lines.append(f'--{alt_boundary}--')
    else:
        # Simple plain text
        lines.append('Content-Type: text/plain; charset=UTF-8')
        lines.append('Content-Transfer-Encoding: 7bit')
        lines.append('')
        lines.append(body)
    
    lines.append('')
    
    # Add attachments
    for file_path in attachments:
        if not os.path.exists(file_path):
            logger.warning(f"[_create_message_with_attachments] Skipping missing file: {file_path}")
            continue
        
        filename = os.path.basename(file_path)
        
        # Guess MIME type
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        
        logger.info(f"[_create_message_with_attachments] Attaching {filename} as {content_type}")
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Base64 encode the file data
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            # Add attachment part
            lines.append(f'--{boundary}')
            lines.append(f'Content-Type: {content_type}')
            lines.append('Content-Transfer-Encoding: base64')
            lines.append(f'Content-Disposition: attachment; filename="{filename}"')
            lines.append('')
            
            # Split base64 data into 76-character lines (RFC requirement)
            for i in range(0, len(encoded_data), 76):
                lines.append(encoded_data[i:i+76])
            
            lines.append('')
            logger.info(f"[_create_message_with_attachments] Successfully processed attachment: {filename}")
            
        except Exception as e:
            logger.error(f"[_create_message_with_attachments] Failed to process attachment {file_path}: {e}")
            continue
    
    # Close the boundary
    lines.append(f'--{boundary}--')
    
    message = '\r\n'.join(lines)
    logger.info(f"[_create_message_with_attachments] Created message with {len(message)} characters")
    
    return message

@handle_http_errors("send_gmail_message", is_read_only=False)
async def send_gmail_message(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    attachments: Optional[List[str]] = None
) -> str:
    """
    Send an email through Gmail with enhanced features.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content (plain text)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML version of email body (optional)
        thread_id: Thread ID to reply to (optional)
        in_reply_to: Message ID being replied to (optional)
        attachments: List of file paths to attach (optional)
    
    Returns:
        Success message with sent message ID
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "send_gmail_message")
        
        # Auto-detect HTML content in body
        is_html_content = html_body or (
            '<' in body and '>' in body and 
            any(tag in body.lower() for tag in ['<b>', '<i>', '<u>', '<div>', '<p>', '<br>', '<ul>', '<ol>', '<li>', '<span>', '<a'])
        )
        
        # Determine if we need multipart (attachments or HTML)
        has_attachments = attachments and len(attachments) > 0
        
        logger.info(f"[send_gmail_message] Attachments provided: {attachments}")
        logger.info(f"[send_gmail_message] Has attachments: {has_attachments}, Is HTML: {is_html_content}")
        
        # Use Node.js style approach for attachments (like the GitHub repo)
        if has_attachments:
            logger.info(f"[send_gmail_message] Using enhanced attachment handling for {len(attachments)} files")
            
            # Validate all attachment files exist
            valid_attachments = []
            for file_path in attachments:
                if os.path.exists(file_path):
                    valid_attachments.append(file_path)
                    logger.info(f"[send_gmail_message] Validated attachment: {file_path}")
                else:
                    logger.warning(f"[send_gmail_message] Attachment file not found: {file_path}")
            
            if not valid_attachments:
                logger.error("[send_gmail_message] No valid attachments found")
                raise Exception("No valid attachment files found")
            
            # Create RFC-compliant message with attachments
            message = await _create_message_with_attachments(
                to=to, subject=subject, body=body, html_body=html_body,
                cc=cc, bcc=bcc, attachments=valid_attachments,
                in_reply_to=in_reply_to
            )
        else:
            # Simple message without attachments
            message = _create_simple_message(
                to=to, subject=subject, body=body, html_body=html_body,
                cc=cc, bcc=bcc, is_html_content=is_html_content,
                in_reply_to=in_reply_to
            )
        
        # Encode message for Gmail API (URL-safe base64)
        if isinstance(message, str):
            # Already a raw RFC822 message string
            raw_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode()
        else:
            # MIME object that needs to be converted
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Clean base64 for Gmail API
        raw_message = raw_message.replace('+', '-').replace('/', '_').rstrip('=')
        
        # Prepare send request
        send_body = {"raw": raw_message}
        if thread_id:
            send_body["threadId"] = thread_id
        
        # Send message
        sent_message = await asyncio.to_thread(
            service.users().messages().send(userId="me", body=send_body).execute
        )
        
        message_id = sent_message.get('id')
        attachment_info = ""
        if attachments:
            valid_attachments = [f for f in attachments if os.path.exists(f)]
            logger.info(f"[send_gmail_message] Valid attachments: {valid_attachments}")
            if valid_attachments:
                attachment_info = f" with {len(valid_attachments)} attachment(s): {', '.join([os.path.basename(f) for f in valid_attachments])}"
        
        logger.info(f"[send_gmail_message] Email sent successfully! Message ID: {message_id}")
        return f"Email sent successfully{attachment_info}! Message ID: {message_id}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error sending Gmail message: {e}")
        return f"Error sending Gmail message: {str(e)}"

@handle_http_errors("draft_gmail_message", is_read_only=False)
async def draft_gmail_message(
    subject: str,
    body: str,
    to: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    thread_id: Optional[str] = None,
    attachments: Optional[List[str]] = None
) -> str:
    """
    Create a draft email in Gmail with enhanced features.
    
    Args:
        subject: Email subject
        body: Email body content (plain text)
        to: Optional recipient email address
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html_body: HTML version of email body (optional)
        thread_id: Thread ID to reply to (optional)
        attachments: List of file paths to attach (optional)
    
    Returns:
        Success message with draft ID
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "draft_gmail_message")
        
        logger.info(f"[draft_gmail_message] Invoked. Subject: '{subject}'")

        # Auto-detect HTML content in body
        is_html_content = html_body or (
            '<' in body and '>' in body and 
            any(tag in body.lower() for tag in ['<b>', '<i>', '<u>', '<div>', '<p>', '<br>', '<ul>', '<ol>', '<li>', '<span>', '<a'])
        )
        
        # Determine if we need multipart (attachments or HTML)
        has_attachments = attachments and len(attachments) > 0
        
        logger.info(f"[draft_gmail_message] Attachments provided: {attachments}")
        logger.info(f"[draft_gmail_message] Has attachments: {has_attachments}, Is HTML: {is_html_content}")
        
        # Use same approach as send_gmail_message
        if has_attachments:
            logger.info(f"[draft_gmail_message] Using enhanced attachment handling for {len(attachments)} files")
            
            # Validate all attachment files exist
            valid_attachments = []
            for file_path in attachments:
                if os.path.exists(file_path):
                    valid_attachments.append(file_path)
                    logger.info(f"[draft_gmail_message] Validated attachment: {file_path}")
                else:
                    logger.warning(f"[draft_gmail_message] Attachment file not found: {file_path}")
            
            if not valid_attachments:
                logger.error("[draft_gmail_message] No valid attachments found")
                raise Exception("No valid attachment files found")
            
            # Create RFC-compliant message with attachments
            message = await _create_message_with_attachments(
                to=to or "", subject=subject, body=body, html_body=html_body,
                cc=cc, bcc=bcc, attachments=valid_attachments
            )
        else:
            # Simple message without attachments
            message = _create_simple_message(
                to=to or "", subject=subject, body=body, html_body=html_body,
                cc=cc, bcc=bcc, is_html_content=is_html_content
            )
        
        # Encode message for Gmail API (URL-safe base64)
        if isinstance(message, str):
            # Already a raw RFC822 message string
            raw_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode()
        else:
            # MIME object that needs to be converted
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Clean base64 for Gmail API
        raw_message = raw_message.replace('+', '-').replace('/', '_').rstrip('=')

        # Create a draft instead of sending
        message_data = {"raw": raw_message}
        if thread_id:
            message_data["threadId"] = thread_id
        
        draft_body = {"message": message_data}

        # Create the draft
        created_draft = await asyncio.to_thread(
            service.users().drafts().create(userId="me", body=draft_body).execute
        )
        draft_id = created_draft.get("id")
        attachment_info = ""
        if attachments:
            valid_attachments = [f for f in attachments if os.path.exists(f)]
            logger.info(f"[draft_gmail_message] Valid attachments: {valid_attachments}")
            if valid_attachments:
                attachment_info = f" with {len(valid_attachments)} attachment(s): {', '.join([os.path.basename(f) for f in valid_attachments])}"
        
        logger.info(f"[draft_gmail_message] Draft created successfully! Draft ID: {draft_id}")
        return f"Draft created{attachment_info}! Draft ID: {draft_id}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating Gmail draft: {e}")
        return f"Error creating Gmail draft: {str(e)}"

def _format_thread_content(thread_data: dict, thread_id: str) -> str:
    """
    Helper function to format thread content from Gmail API response.

    Args:
        thread_data (dict): Thread data from Gmail API
        thread_id (str): Thread ID for display

    Returns:
        str: Formatted thread content
    """
    messages = thread_data.get("messages", [])
    if not messages:
        return f"No messages found in thread '{thread_id}'."

    # Extract thread subject from the first message
    first_message = messages[0]
    first_headers = {
        h["name"]: h["value"]
        for h in first_message.get("payload", {}).get("headers", [])
    }
    thread_subject = first_headers.get("Subject", "(no subject)")

    # Build the thread content
    content_lines = [
        f"Thread ID: {thread_id}",
        f"Subject: {thread_subject}",
        f"Messages: {len(messages)}",
        "",
    ]

    # Process each message in the thread
    for i, message in enumerate(messages, 1):
        # Extract headers
        headers = {
            h["name"]: h["value"] for h in message.get("payload", {}).get("headers", [])
        }

        sender = headers.get("From", "(unknown sender)")
        date = headers.get("Date", "(unknown date)")
        subject = headers.get("Subject", "(no subject)")

        # Extract message body
        payload = message.get("payload", {})
        content = _extract_email_content(payload)
        body_data = content.get("text") or content.get("html") or "[No content found]"

        # Add message to content
        content_lines.extend(
            [
                f"=== Message {i} ===",
                f"From: {sender}",
                f"Date: {date}",
            ]
        )

        # Only show subject if it's different from thread subject
        if subject != thread_subject:
            content_lines.append(f"Subject: {subject}")

        # Extract attachments for this message
        attachments = _extract_attachments(payload)
        attachment_info = ""
        if attachments:
            attachment_info = f"\n\nAttachments ({len(attachments)}):\n"
            attachment_info += "\n".join([
                f"- {att['filename']} ({att['mimeType']}, {att['size']} bytes)"
                for att in attachments
            ])
        
        content_lines.extend(
            [
                "",
                body_data + attachment_info,
                "",
            ]
        )

    return "\n".join(content_lines)

@handle_http_errors("get_gmail_thread_content", is_read_only=True)
async def get_gmail_thread_content(thread_id: str) -> str:
    """
    Retrieves the complete content of a Gmail conversation thread, including all messages.

    Args:
        thread_id (str): The unique ID of the Gmail thread to retrieve.

    Returns:
        str: The complete thread content with all messages formatted for reading.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_thread_content")
        
        logger.info(f"[get_gmail_thread_content] Invoked. Thread ID: '{thread_id}'")

        # Fetch the complete thread with all messages
        thread_response = await asyncio.to_thread(
            service.users().threads().get(userId="me", id=thread_id, format="full").execute
        )

        return _format_thread_content(thread_response, thread_id)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail thread: {e}")
        return f"Error getting Gmail thread: {str(e)}"

@handle_http_errors("get_gmail_threads_content_batch", is_read_only=True)
async def get_gmail_threads_content_batch(thread_ids: List[str]) -> str:
    """
    Retrieves the content of multiple Gmail threads in a single batch request.
    Supports up to 100 threads per request using Google's batch API.

    Args:
        thread_ids (List[str]): A list of Gmail thread IDs to retrieve. The function will automatically batch requests in chunks of 100.

    Returns:
        str: A formatted list of thread contents with separators.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "get_gmail_threads_content_batch")
        
        logger.info(f"[get_gmail_threads_content_batch] Invoked. Thread count: {len(thread_ids)}")

        if not thread_ids:
            raise ValueError("No thread IDs provided")

        output_threads = []

        def _batch_callback(request_id, response, exception):
            """Callback for batch requests"""
            results[request_id] = {"data": response, "error": exception}

        # Process in chunks of 100 (Gmail batch limit)
        for chunk_start in range(0, len(thread_ids), 100):
            chunk_ids = thread_ids[chunk_start : chunk_start + 100]
            results: Dict[str, Dict] = {}

            # Try to use batch API
            try:
                batch = service.new_batch_http_request(callback=_batch_callback)

                for tid in chunk_ids:
                    req = service.users().threads().get(userId="me", id=tid, format="full")
                    batch.add(req, request_id=tid)

                # Execute batch request
                await asyncio.to_thread(batch.execute)

            except Exception as batch_error:
                # Fallback to asyncio.gather if batch API fails
                logger.warning(
                    f"[get_gmail_threads_content_batch] Batch API failed, falling back to asyncio.gather: {batch_error}"
                )

                async def fetch_thread(tid: str):
                    try:
                        thread = await asyncio.to_thread(
                            service.users()
                            .threads()
                            .get(userId="me", id=tid, format="full")
                            .execute
                        )
                        return tid, thread, None
                    except Exception as e:
                        return tid, None, e

                # Fetch all threads in parallel
                fetch_results = await asyncio.gather(
                    *[fetch_thread(tid) for tid in chunk_ids], return_exceptions=False
                )

                # Convert to results format
                for tid, thread, error in fetch_results:
                    results[tid] = {"data": thread, "error": error}

            # Process results for this chunk
            for tid in chunk_ids:
                entry = results.get(tid, {"data": None, "error": "No result"})

                if entry["error"]:
                    output_threads.append(f"⚠️ Thread {tid}: {entry['error']}\n")
                else:
                    thread = entry["data"]
                    if not thread:
                        output_threads.append(f"⚠️ Thread {tid}: No data returned\n")
                        continue

                    output_threads.append(_format_thread_content(thread, tid))

        # Combine all threads with separators
        header = f"Retrieved {len(thread_ids)} threads:"
        return header + "\n\n" + "\n---\n\n".join(output_threads)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting Gmail threads batch: {e}")
        return f"Error getting Gmail threads batch: {str(e)}"

@handle_http_errors("list_gmail_labels", is_read_only=True)
async def list_gmail_labels() -> str:
    """
    List all Gmail labels.
    
    Returns:
        List of Gmail labels
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "list_gmail_labels")
        
        logger.info(f"[list_gmail_labels] Invoked")

        # Get labels
        response = await asyncio.to_thread(
            service.users().labels().list(userId="me").execute
        )
        labels = response.get("labels", [])

        if not labels:
            return "No labels found."

        lines = [f"Found {len(labels)} labels:", ""]

        system_labels = []
        user_labels = []

        for label in labels:
            if label.get("type") == "system":
                system_labels.append(label)
            else:
                user_labels.append(label)

        if system_labels:
            lines.append("📂 SYSTEM LABELS:")
            for label in system_labels:
                lines.append(f"  • {label['name']} (ID: {label['id']})")
            lines.append("")

        if user_labels:
            lines.append("🏷️  USER LABELS:")
            for label in user_labels:
                lines.append(f"  • {label['name']} (ID: {label['id']})")

        return "\n".join(lines)
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error listing Gmail labels: {e}")
        return f"Error listing Gmail labels: {str(e)}"

@handle_http_errors("manage_gmail_label", is_read_only=False)
async def manage_gmail_label(
    action: Literal["create", "update", "delete"],
    name: Optional[str] = None,
    label_id: Optional[str] = None,
    label_list_visibility: Literal["labelShow", "labelHide"] = "labelShow",
    message_list_visibility: Literal["show", "hide"] = "show",
) -> str:
    """
    Manages Gmail labels: create, update, or delete labels.

    Args:
        action (Literal["create", "update", "delete"]): Action to perform on the label.
        name (Optional[str]): Label name. Required for create, optional for update.
        label_id (Optional[str]): Label ID. Required for update and delete operations.
        label_list_visibility (Literal["labelShow", "labelHide"]): Whether the label is shown in the label list.
        message_list_visibility (Literal["show", "hide"]): Whether the label is shown in the message list.

    Returns:
        str: Confirmation message of the label operation.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "manage_gmail_label")
        
        logger.info(f"[manage_gmail_label] Invoked. Action: '{action}'")

        if action == "create" and not name:
            raise Exception("Label name is required for create action.")

        if action in ["update", "delete"] and not label_id:
            raise Exception("Label ID is required for update and delete actions.")

        if action == "create":
            label_object = {
                "name": name,
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
            }
            created_label = await asyncio.to_thread(
                service.users().labels().create(userId="me", body=label_object).execute
            )
            return f"Label created successfully!\nName: {created_label['name']}\nID: {created_label['id']}"

        elif action == "update":
            current_label = await asyncio.to_thread(
                service.users().labels().get(userId="me", id=label_id).execute
            )

            label_object = {
                "id": label_id,
                "name": name if name is not None else current_label["name"],
                "labelListVisibility": label_list_visibility,
                "messageListVisibility": message_list_visibility,
            }

            updated_label = await asyncio.to_thread(
                service.users()
                .labels()
                .update(userId="me", id=label_id, body=label_object)
                .execute
            )
            return f"Label updated successfully!\nName: {updated_label['name']}\nID: {updated_label['id']}"

        elif action == "delete":
            label = await asyncio.to_thread(
                service.users().labels().get(userId="me", id=label_id).execute
            )
            label_name = label["name"]

            await asyncio.to_thread(
                service.users().labels().delete(userId="me", id=label_id).execute
            )
            return f"Label '{label_name}' (ID: {label_id}) deleted successfully!"
            
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error managing Gmail label: {e}")
        return f"Error managing Gmail label: {str(e)}"

@handle_http_errors("modify_gmail_message_labels", is_read_only=False)
async def modify_gmail_message_labels(
    message_id: str,
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
) -> str:
    """
    Adds or removes labels from a Gmail message.

    Args:
        message_id (str): The ID of the message to modify.
        add_label_ids (Optional[List[str]]): List of label IDs to add to the message.
        remove_label_ids (Optional[List[str]]): List of label IDs to remove from the message.

    Returns:
        str: Confirmation message of the label changes applied to the message.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "modify_gmail_message_labels")
        
        logger.info(f"[modify_gmail_message_labels] Invoked. Message ID: '{message_id}'")

        if not add_label_ids and not remove_label_ids:
            raise Exception(
                "At least one of add_label_ids or remove_label_ids must be provided."
            )

        body = {}
        if add_label_ids:
            body["addLabelIds"] = add_label_ids
        if remove_label_ids:
            body["removeLabelIds"] = remove_label_ids

        await asyncio.to_thread(
            service.users().messages().modify(userId="me", id=message_id, body=body).execute
        )

        actions = []
        if add_label_ids:
            actions.append(f"Added labels: {', '.join(add_label_ids)}")
        if remove_label_ids:
            actions.append(f"Removed labels: {', '.join(remove_label_ids)}")

        return f"Message labels updated successfully!\nMessage ID: {message_id}\n{'; '.join(actions)}"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error modifying Gmail message labels: {e}")
        return f"Error modifying Gmail message labels: {str(e)}"

@handle_http_errors("download_gmail_attachment", is_read_only=True)
async def download_gmail_attachment(
    message_id: str,
    attachment_id: str,
    filename: Optional[str] = None
) -> str:
    """
    Download an email attachment from Gmail.
    
    Args:
        message_id: The Gmail message ID containing the attachment
        attachment_id: The attachment ID to download
        filename: Optional filename override
    
    Returns:
        Attachment information and data summary
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "download_gmail_attachment")
        
        logger.info(f"[download_gmail_attachment] Message ID: {message_id}, Attachment ID: {attachment_id}")

        # Get attachment data
        attachment = await asyncio.to_thread(
            service.users().messages().attachments().get(
                userId="me",
                messageId=message_id,
                id=attachment_id
            ).execute
        )
        
        if not attachment.get("data"):
            return "Error: No attachment data received"
        
        # Decode attachment data
        attachment_data = base64.urlsafe_b64decode(attachment["data"])
        
        # Get original filename if not provided
        if not filename:
            message = await asyncio.to_thread(
                service.users().messages().get(
                    userId="me",
                    id=message_id,
                    format="full"
                ).execute
            )
            
            def find_attachment_filename(part):
                if part.get("body", {}).get("attachmentId") == attachment_id:
                    return part.get("filename", f"attachment-{attachment_id}")
                if part.get("parts"):
                    for subpart in part["parts"]:
                        result = find_attachment_filename(subpart)
                        if result:
                            return result
                return None
            
            filename = find_attachment_filename(message.get("payload", {})) or f"attachment-{attachment_id}"
        
        return f"Attachment downloaded successfully:\nFilename: {filename}\nSize: {len(attachment_data)} bytes\nData available in memory for processing"
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error downloading Gmail attachment: {e}")
        return f"Error downloading Gmail attachment: {str(e)}"

@handle_http_errors("batch_modify_gmail_message_labels", is_read_only=False)
async def batch_modify_gmail_message_labels(
    message_ids: List[str],
    add_label_ids: Optional[List[str]] = None,
    remove_label_ids: Optional[List[str]] = None,
    batch_size: int = 50
) -> str:
    """
    Adds or removes labels from multiple Gmail messages with enhanced batch processing.

    Args:
        message_ids (List[str]): A list of message IDs to modify.
        add_label_ids (Optional[List[str]]): List of label IDs to add to the messages.
        remove_label_ids (Optional[List[str]]): List of label IDs to remove from the messages.
        batch_size (int): Number of messages to process per batch (default: 50).

    Returns:
        str: Detailed confirmation message of the label changes applied to the messages.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "batch_modify_gmail_message_labels")
        
        logger.info(f"[batch_modify_gmail_message_labels] Invoked. Message IDs: '{message_ids}'")

        if not add_label_ids and not remove_label_ids:
            raise Exception(
                "At least one of add_label_ids or remove_label_ids must be provided."
            )

        # Process in batches for better performance and reliability
        total_processed = 0
        total_failed = 0
        failed_ids = []
        
        for i in range(0, len(message_ids), batch_size):
            batch_ids = message_ids[i:i + batch_size]
            
            try:
                body = {"ids": batch_ids}
                if add_label_ids:
                    body["addLabelIds"] = add_label_ids
                if remove_label_ids:
                    body["removeLabelIds"] = remove_label_ids

                await asyncio.wait_for(
                    asyncio.to_thread(
                        service.users().messages().batchModify(userId="me", body=body).execute
                    ),
                    timeout=30.0
                )
                total_processed += len(batch_ids)
                
            except Exception as e:
                logger.warning(f"Batch modify failed for batch {i//batch_size + 1}: {e}")
                # Try individual messages in failed batch
                for msg_id in batch_ids:
                    try:
                        individual_body = {"ids": [msg_id]}
                        if add_label_ids:
                            individual_body["addLabelIds"] = add_label_ids
                        if remove_label_ids:
                            individual_body["removeLabelIds"] = remove_label_ids
                        
                        await asyncio.to_thread(
                            service.users().messages().batchModify(userId="me", body=individual_body).execute
                        )
                        total_processed += 1
                    except Exception:
                        total_failed += 1
                        failed_ids.append(msg_id)

        actions = []
        if add_label_ids:
            actions.append(f"Added labels: {', '.join(add_label_ids)}")
        if remove_label_ids:
            actions.append(f"Removed labels: {', '.join(remove_label_ids)}")

        result = f"Batch label modification complete.\nSuccessfully processed: {total_processed} messages"
        if total_failed > 0:
            result += f"\nFailed: {total_failed} messages"
            if len(failed_ids) <= 10:  # Show failed IDs if not too many
                result += f"\nFailed message IDs: {', '.join(failed_ids[:10])}"
        if actions:
            result += f"\nActions: {'; '.join(actions)}"
        
        return result
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error batch modifying Gmail message labels: {e}")
        return f"Error batch modifying Gmail message labels: {str(e)}"

@handle_http_errors("batch_delete_gmail_messages", is_read_only=False)
async def batch_delete_gmail_messages(
    message_ids: List[str],
    batch_size: int = 50
) -> str:
    """
    Delete multiple Gmail messages with enhanced batch processing.

    Args:
        message_ids (List[str]): A list of message IDs to delete.
        batch_size (int): Number of messages to process per batch (default: 50).

    Returns:
        str: Detailed confirmation message of the deletion operation.
    """
    try:
        service = await get_authenticated_google_service("gmail", "v1", "batch_delete_gmail_messages")
        
        logger.info(f"[batch_delete_gmail_messages] Deleting {len(message_ids)} messages")

        if not message_ids:
            raise Exception("No message IDs provided")

        # Process in batches for better performance and reliability
        total_deleted = 0
        total_failed = 0
        failed_ids = []
        
        for i in range(0, len(message_ids), batch_size):
            batch_ids = message_ids[i:i + batch_size]
            
            # Try batch delete first
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(
                        service.users().messages().batchDelete(
                            userId="me", 
                            body={"ids": batch_ids}
                        ).execute
                    ),
                    timeout=30.0
                )
                total_deleted += len(batch_ids)
                
            except Exception as e:
                logger.warning(f"Batch delete failed for batch {i//batch_size + 1}: {e}")
                # Try individual deletions for failed batch
                for msg_id in batch_ids:
                    try:
                        await asyncio.to_thread(
                            service.users().messages().delete(
                                userId="me", 
                                id=msg_id
                            ).execute
                        )
                        total_deleted += 1
                    except Exception:
                        total_failed += 1
                        failed_ids.append(msg_id)

        result = f"Batch delete operation complete.\nSuccessfully deleted: {total_deleted} messages"
        if total_failed > 0:
            result += f"\nFailed to delete: {total_failed} messages"
            if len(failed_ids) <= 10:  # Show failed IDs if not too many
                result += f"\nFailed message IDs: {', '.join(failed_ids[:10])}"
        
        return result
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error batch deleting Gmail messages: {e}")
        return f"Error batch deleting Gmail messages: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("search_gmail_messages", search_gmail_messages)
register_tool_with_transport("get_gmail_message_content", get_gmail_message_content)
register_tool_with_transport("get_gmail_messages_content_batch", get_gmail_messages_content_batch)
register_tool_with_transport("send_gmail_message", send_gmail_message)
register_tool_with_transport("draft_gmail_message", draft_gmail_message)
register_tool_with_transport("get_gmail_thread_content", get_gmail_thread_content)
register_tool_with_transport("get_gmail_threads_content_batch", get_gmail_threads_content_batch)
register_tool_with_transport("list_gmail_labels", list_gmail_labels)
register_tool_with_transport("manage_gmail_label", manage_gmail_label)
register_tool_with_transport("modify_gmail_message_labels", modify_gmail_message_labels)
register_tool_with_transport("batch_modify_gmail_message_labels", batch_modify_gmail_message_labels)
register_tool_with_transport("download_gmail_attachment", download_gmail_attachment)
register_tool_with_transport("batch_delete_gmail_messages", batch_delete_gmail_messages)

logger.info("Gmail tools registered with session-aware transport")