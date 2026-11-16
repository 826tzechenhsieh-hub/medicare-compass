"""Shared Google Sheets connection for feedback modules."""

import gspread


SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets"

FEEDBACK_HEADERS = {
    "Product Feedback": [
        "timestamp", "session_id", "helpfulness", "confusion",
        "future_request", "status", "language",
    ],
    "User Feedback": [
        "timestamp", "session_id", "category", "rating", "feedback",
        "status", "page", "language",
    ],
}


class FeedbackSchemaError(ValueError):
    """The remote header row does not match the agreed feedback schema."""


def get_feedback_spreadsheet(settings=None):
    """Open the configured spreadsheet without requiring Google Drive access.

    Streamlit callers use st.secrets by default. Standalone connection checks
    may supply the same settings as a mapping.
    """
    if settings is None:
        import streamlit as st

        settings = st.secrets

    credentials = dict(settings["gcp_service_account"])
    spreadsheet_id = settings["google_sheets"]["spreadsheet_id"]
    client = gspread.service_account_from_dict(
        credentials, scopes=[SHEETS_SCOPE]
    )
    client.set_timeout(30)
    return client.open_by_key(spreadsheet_id)


def save_feedback(sheet_name, record, *, spreadsheet=None):
    """Append literal values, and recognize retries of the same submission.

    The caller retains timestamp/session_id across retries. Only these two
    columns are read for duplicate detection; existing feedback is not changed.
    """
    headers = FEEDBACK_HEADERS[sheet_name]
    if set(record) != set(headers):
        raise FeedbackSchemaError("Feedback fields do not match the schema.")
    if not record["timestamp"] or not record["session_id"]:
        raise ValueError("Submission identity is required.")
    if spreadsheet is None:
        spreadsheet = get_feedback_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    if worksheet.row_values(1) != headers:
        raise FeedbackSchemaError("Worksheet headers do not match the schema.")
    identity = [record["timestamp"], record["session_id"]]
    if any(list(row[:2]) == identity for row in worksheet.get("A2:B")):
        return
    worksheet.append_row(
        [record[field] for field in headers],
        value_input_option="RAW",
        insert_data_option="INSERT_ROWS",
        table_range="A1",
    )
