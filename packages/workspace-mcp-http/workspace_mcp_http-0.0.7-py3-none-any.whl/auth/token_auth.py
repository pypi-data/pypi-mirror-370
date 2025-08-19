#!/usr/bin/env python3

import logging
from typing import Optional, List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.session_transport import get_current_access_token

# Configure logging
logger = logging.getLogger(__name__)

class GoogleAuthenticationError(Exception):
    """Exception raised when Google authentication is required or fails."""
    
    def __init__(self, message: str):
        super().__init__(message)

def create_google_client_from_token(access_token: str) -> Any:
    """
    Create a Google OAuth2 client from an access token.
    
    Args:
        access_token: The OAuth2 access token
        
    Returns:
        OAuth2 client configured with the access token
    """
    credentials = Credentials(token=access_token)
    return credentials

async def get_authenticated_google_service(
    service_name: str,  # "gmail", "calendar", "drive", "docs"
    version: str,       # "v1", "v3"
    tool_name: str,     # For logging/debugging
    required_scopes: Optional[List[str]] = None,  # Not used but kept for compatibility
) -> Any:
    """
    Get authenticated Google service using access token from current request context.
    
    Args:
        service_name: The Google service name ("gmail", "calendar", "drive", "docs")
        version: The API version ("v1", "v3", etc.)
        tool_name: The name of the calling tool (for logging/debugging)
        required_scopes: List of required OAuth scopes (not used in token auth)
        
    Returns:
        Google API service client
        
    Raises:
        GoogleAuthenticationError: When authentication fails
    """
    logger.info(f"[{tool_name}] Attempting to get authenticated {service_name} service")
    
    # Get access token from current request context
    access_token = get_current_access_token()
    if not access_token:
        error_msg = f"Authentication required for {tool_name}. No access token provided in request headers."
        logger.error(f"[{tool_name}] {error_msg}")
        raise GoogleAuthenticationError(error_msg)
    
    try:
        # Create credentials from access token
        credentials = create_google_client_from_token(access_token)
        
        # Validate the token by building the service
        service = build(service_name, version, credentials=credentials)
        
        # Test the credentials with a simple API call (if possible)
        try:
            if service_name == "gmail":
                # Test Gmail access
                service.users().getProfile(userId='me').execute()
            elif service_name == "calendar":
                # Test Calendar access
                service.calendarList().list(maxResults=1).execute()
            elif service_name == "drive":
                # Test Drive access
                service.files().list(pageSize=1).execute()
            # Add more service-specific validation as needed
            
            logger.info(f"[{tool_name}] Successfully authenticated {service_name} service")
            return service
            
        except HttpError as e:
            if e.resp.status == 401:
                error_msg = f"Authentication Error: Invalid or expired OAuth2 access token for {service_name}."
                logger.error(f"[{tool_name}] {error_msg}")
                raise GoogleAuthenticationError(error_msg)
            elif e.resp.status == 403:
                error_msg = f"Permission Error: Access token lacks required {service_name} API permissions."
                logger.error(f"[{tool_name}] {error_msg}")
                raise GoogleAuthenticationError(error_msg)
            else:
                error_msg = f"API Error: {service_name} API returned {e.resp.status}: {e.content}"
                logger.error(f"[{tool_name}] {error_msg}")
                raise GoogleAuthenticationError(error_msg)
        
    except Exception as e:
        if isinstance(e, GoogleAuthenticationError):
            raise
        error_msg = f"Failed to build {service_name} service: {str(e)}"
        logger.error(f"[{tool_name}] {error_msg}", exc_info=True)
        raise GoogleAuthenticationError(error_msg)

def validate_access_token(access_token: str) -> bool:
    """
    Validate an access token by making a simple API call.
    
    Args:
        access_token: The OAuth2 access token to validate
        
    Returns:
        True if token is valid, False otherwise
    """
    try:
        credentials = create_google_client_from_token(access_token)
        # Use OAuth2 API to validate token
        service = build("oauth2", "v2", credentials=credentials)
        service.userinfo().get().execute()
        return True
    except Exception as e:
        logger.debug(f"Token validation failed: {e}")
        return False

def get_user_info_from_token(access_token: str) -> Optional[dict]:
    """
    Get user information from access token.
    
    Args:
        access_token: The OAuth2 access token
        
    Returns:
        User info dict or None if failed
    """
    try:
        credentials = create_google_client_from_token(access_token)
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()
        logger.info(f"Successfully fetched user info: {user_info.get('email')}")
        return user_info
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return None