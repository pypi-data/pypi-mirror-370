"""
Google Sheets MCP Tools - Updated for Access Token Authentication

This module provides MCP tools for interacting with Google Sheets API using access token auth.
"""

import logging
import asyncio
from typing import List, Optional

from auth.token_auth import get_authenticated_google_service, GoogleAuthenticationError
from core.session_server import register_tool_with_transport
from core.utils import handle_http_errors

# Configure module logger
logger = logging.getLogger(__name__)

# Required scopes for Sheets operations
SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.readonly"
]

@handle_http_errors("list_spreadsheets", is_read_only=True)
async def list_spreadsheets(max_results: int = 25) -> str:
    """
    Lists spreadsheets from Google Drive that the user has access to.

    Args:
        max_results: Maximum number of spreadsheets to return (default: 25)

    Returns:
        str: A formatted list of spreadsheet files (name, ID, modified time).
    """
    try:
        service = await get_authenticated_google_service("drive", "v3", "list_spreadsheets")
        
        logger.info(f"[list_spreadsheets] Invoked")

        files_response = await asyncio.to_thread(
            service.files()
            .list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=max_results,
                fields="files(id,name,modifiedTime,webViewLink)",
                orderBy="modifiedTime desc",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            )
            .execute
        )

        files = files_response.get("files", [])
        if not files:
            return f"No spreadsheets found."

        spreadsheets_list = [
            f"- \"{file['name']}\" (ID: {file['id']}) | Modified: {file.get('modifiedTime', 'Unknown')} | Link: {file.get('webViewLink', 'No link')}"
            for file in files
        ]

        text_output = (
            f"Successfully listed {len(files)} spreadsheets:\n"
            + "\n".join(spreadsheets_list)
        )

        logger.info(f"Successfully listed {len(files)} spreadsheets.")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error listing spreadsheets: {e}")
        return f"Error listing spreadsheets: {str(e)}"

@handle_http_errors("get_spreadsheet_info", is_read_only=True)
async def get_spreadsheet_info(spreadsheet_id: str) -> str:
    """
    Gets information about a specific spreadsheet including its sheets.

    Args:
        spreadsheet_id: The ID of the spreadsheet to get info for

    Returns:
        str: Formatted spreadsheet information including title and sheets list.
    """
    try:
        service = await get_authenticated_google_service("sheets", "v4", "get_spreadsheet_info")
        
        logger.info(f"[get_spreadsheet_info] Invoked. Spreadsheet ID: {spreadsheet_id}")

        spreadsheet = await asyncio.to_thread(
            service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute
        )

        title = spreadsheet.get("properties", {}).get("title", "Unknown")
        sheets = spreadsheet.get("sheets", [])

        sheets_info = []
        for sheet in sheets:
            sheet_props = sheet.get("properties", {})
            sheet_name = sheet_props.get("title", "Unknown")
            sheet_id = sheet_props.get("sheetId", "Unknown")
            grid_props = sheet_props.get("gridProperties", {})
            rows = grid_props.get("rowCount", "Unknown")
            cols = grid_props.get("columnCount", "Unknown")

            sheets_info.append(
                f"  - \"{sheet_name}\" (ID: {sheet_id}) | Size: {rows}x{cols}"
            )

        text_output = (
            f"Spreadsheet: \"{title}\" (ID: {spreadsheet_id})\n"
            f"Sheets ({len(sheets)}):\n"
            + "\n".join(sheets_info) if sheets_info else "  No sheets found"
        )

        logger.info(f"Successfully retrieved info for spreadsheet {spreadsheet_id}.")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error getting spreadsheet info: {e}")
        return f"Error getting spreadsheet info: {str(e)}"

@handle_http_errors("read_sheet_values", is_read_only=True)
async def read_sheet_values(
    spreadsheet_id: str,
    range_name: str = "A1:Z1000",
) -> str:
    """
    Reads values from a specific range in a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The range to read (e.g., "Sheet1!A1:D10", "A1:D10") (default: "A1:Z1000")

    Returns:
        str: The formatted values from the specified range.
    """
    try:
        service = await get_authenticated_google_service("sheets", "v4", "read_sheet_values")
        
        logger.info(f"[read_sheet_values] Invoked. Spreadsheet: {spreadsheet_id}, Range: {range_name}")

        result = await asyncio.to_thread(
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute
        )

        values = result.get("values", [])
        if not values:
            return f"No data found in range '{range_name}'."

        # Format the output as a readable table
        formatted_rows = []
        for i, row in enumerate(values, 1):
            # Pad row with empty strings to show structure
            padded_row = row + [""] * max(0, len(values[0]) - len(row)) if values else row
            formatted_rows.append(f"Row {i:2d}: {padded_row}")

        text_output = (
            f"Successfully read {len(values)} rows from range '{range_name}' in spreadsheet {spreadsheet_id}:\n"
            + "\n".join(formatted_rows[:50])  # Limit to first 50 rows for readability
            + (f"\n... and {len(values) - 50} more rows" if len(values) > 50 else "")
        )

        logger.info(f"Successfully read {len(values)} rows.")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error reading sheet values: {e}")
        return f"Error reading sheet values: {str(e)}"

@handle_http_errors("modify_sheet_values")
async def modify_sheet_values(
    spreadsheet_id: str,
    range_name: str,
    values: Optional[List[List[str]]] = None,
    value_input_option: str = "USER_ENTERED",
    clear_values: bool = False,
) -> str:
    """
    Modifies values in a specific range of a Google Sheet - can write, update, or clear values.

    Args:
        spreadsheet_id: The ID of the spreadsheet
        range_name: The range to modify (e.g., "Sheet1!A1:D10", "A1:D10")
        values: 2D array of values to write/update (required unless clear_values=True)
        value_input_option: How to interpret input values ("RAW" or "USER_ENTERED") (default: "USER_ENTERED")
        clear_values: If True, clears the range instead of writing values (default: False)

    Returns:
        str: Confirmation message of the successful modification operation.
    """
    try:
        service = await get_authenticated_google_service("sheets", "v4", "modify_sheet_values")
        
        operation = "clear" if clear_values else "write"
        logger.info(f"[modify_sheet_values] Invoked. Operation: {operation}, Spreadsheet: {spreadsheet_id}, Range: {range_name}")

        if not clear_values and not values:
            raise Exception("Either 'values' must be provided or 'clear_values' must be True.")

        if clear_values:
            result = await asyncio.to_thread(
                service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name)
                .execute
            )

            cleared_range = result.get("clearedRange", range_name)
            text_output = f"Successfully cleared range '{cleared_range}' in spreadsheet {spreadsheet_id}."
            logger.info(f"Successfully cleared range '{cleared_range}'.")
        else:
            body = {"values": values}

            result = await asyncio.to_thread(
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute
            )

            updated_cells = result.get("updatedCells", 0)
            updated_rows = result.get("updatedRows", 0)
            updated_columns = result.get("updatedColumns", 0)

            text_output = (
                f"Successfully updated range '{range_name}' in spreadsheet {spreadsheet_id}. "
                f"Updated: {updated_cells} cells, {updated_rows} rows, {updated_columns} columns."
            )
            logger.info(f"Successfully updated {updated_cells} cells.")

        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error modifying sheet values: {e}")
        return f"Error modifying sheet values: {str(e)}"

@handle_http_errors("create_spreadsheet")
async def create_spreadsheet(
    title: str,
    sheet_names: Optional[List[str]] = None,
) -> str:
    """
    Creates a new Google Spreadsheet.

    Args:
        title: The title of the new spreadsheet
        sheet_names: List of sheet names to create (optional, if not provided creates one default sheet)

    Returns:
        str: Information about the newly created spreadsheet including ID and URL.
    """
    try:
        service = await get_authenticated_google_service("sheets", "v4", "create_spreadsheet")
        
        logger.info(f"[create_spreadsheet] Invoked. Title: {title}")

        spreadsheet_body = {
            "properties": {
                "title": title
            }
        }

        if sheet_names:
            spreadsheet_body["sheets"] = [
                {"properties": {"title": sheet_name}} for sheet_name in sheet_names
            ]

        spreadsheet = await asyncio.to_thread(
            service.spreadsheets().create(body=spreadsheet_body).execute
        )

        spreadsheet_id = spreadsheet.get("spreadsheetId")
        spreadsheet_url = spreadsheet.get("spreadsheetUrl")

        text_output = (
            f"Successfully created spreadsheet '{title}'. "
            f"ID: {spreadsheet_id} | URL: {spreadsheet_url}"
        )

        logger.info(f"Successfully created spreadsheet. ID: {spreadsheet_id}")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating spreadsheet: {e}")
        return f"Error creating spreadsheet: {str(e)}"

@handle_http_errors("create_sheet")
async def create_sheet(
    spreadsheet_id: str,
    sheet_name: str,
) -> str:
    """
    Creates a new sheet within an existing spreadsheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet
        sheet_name: The name of the new sheet

    Returns:
        str: Confirmation message of the successful sheet creation.
    """
    try:
        service = await get_authenticated_google_service("sheets", "v4", "create_sheet")
        
        logger.info(f"[create_sheet] Invoked. Spreadsheet: {spreadsheet_id}, Sheet: {sheet_name}")

        request_body = {
            "requests": [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheet_name
                        }
                    }
                }
            ]
        }

        response = await asyncio.to_thread(
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=request_body)
            .execute
        )

        sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]

        text_output = (
            f"Successfully created sheet '{sheet_name}' (ID: {sheet_id}) in spreadsheet {spreadsheet_id}."
        )

        logger.info(f"Successfully created sheet. Sheet ID: {sheet_id}")
        return text_output
        
    except GoogleAuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error creating sheet: {e}")
        return f"Error creating sheet: {str(e)}"

# Register tools with the transport manager
register_tool_with_transport("list_spreadsheets", list_spreadsheets)
register_tool_with_transport("get_spreadsheet_info", get_spreadsheet_info)
register_tool_with_transport("read_sheet_values", read_sheet_values)
register_tool_with_transport("modify_sheet_values", modify_sheet_values)
register_tool_with_transport("create_spreadsheet", create_spreadsheet)
register_tool_with_transport("create_sheet", create_sheet)

logger.info("Sheets tools registered with session-aware transport")