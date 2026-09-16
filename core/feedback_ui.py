"""Feedback session state and submission handling shared by both forms."""

from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st

from core.google_sheets import save_feedback


def draft(name):
    return st.session_state.setdefault(name, {})


def field(state_name, field_name, widget, label, **kwargs):
    """Keep drafts when widgets disappear after navigation or dialog dismissal."""
    state = draft(state_name)
    key = f"_{state_name}_{field_name}"
    if key not in st.session_state:
        st.session_state[key] = state.get(field_name, kwargs.pop("initial", ""))
    else:
        kwargs.pop("initial", None)

    def remember():
        draft(state_name)[field_name] = st.session_state[key]

    value = widget(label, key=key, on_change=remember, **kwargs)
    state[field_name] = value
    return value


def submit(state_name, sheet_name, values, ui):
    state = draft(state_name)
    if state.get("saved"):
        return True
    session_id = st.session_state.setdefault("feedback_session_id", str(uuid4()))
    # Freeze a submission identity for retries, including a lost HTTP response.
    # A changed form represents a new submission.
    if state.get("pending_values") != values:
        state["pending_values"] = dict(values)
        state["pending_record"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            **values,
            "status": "new",
        }
    try:
        with st.spinner(ui["saving"]):
            save_feedback(sheet_name, state["pending_record"])
    except Exception:
        # Do not render exceptions that could contain credentials or feedback.
        st.error(ui["error"])
        return False
    state["saved"] = True
    return True
