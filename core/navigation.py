"""Durable route state and applicant boundaries for the guided workflow."""
import streamlit as st

CONVERSATION_KEYS = {
    "messages", "user_state", "user_zip", "conversation_finished", "auto_submit",
    "saved_user_input", "resubmit_saved_input", "_scroll_to_message", "_initial_top_done",
    "feedback_rating", "feedback_comment", "feedback_submitted",
    "conversation_attachment",
}


def clear_downstream():
    for key in list(st.session_state):
        if (key in CONVERSATION_KEYS or key.startswith("ship_")
                or key.startswith("switch_") or key.startswith("calendar_")
                or "bilingual" in key or "product_feedback" in key):
            del st.session_state[key]


def start_route(route):
    clear_downstream()
    if route in ("guided", "unsure") and route != st.session_state.get("entry_route"):
        for key in list(st.session_state):
            if key.startswith("profile_"):
                del st.session_state[key]
    st.session_state["entry_route"] = route
    st.session_state["profile_completed"] = False
    if route in ("guided", "unsure"):
        st.session_state["profile_step"] = 1
        st.session_state["profile_intro_seen"] = False
    st.session_state["selected_app_mode"] = {
        "guided": "PROFILE", "unsure": "PROFILE",
        "switch": "SWITCH_ASSISTANT", "direct": "MAIN_AI",
    }[route]
    st.session_state["entry_stage"] = "work"
    st.session_state["_scroll_to_top"] = True


def choose_persona(persona):
    if persona != st.session_state.get("persona"):
        clear_downstream()
        for key in list(st.session_state):
            if key.startswith("profile_"):
                del st.session_state[key]
    st.session_state["persona"] = persona
    st.session_state["entry_stage"] = "topics"
    st.session_state["selected_app_mode"] = None


def init_navigation():
    st.session_state.setdefault("selected_language", "English")
    st.session_state.setdefault("font_size", 19)
    st.session_state.setdefault("persona", "self")
    st.session_state.setdefault("entry_stage", "welcome")
    st.session_state.setdefault("selected_app_mode", None)
    pending = st.session_state.pop("_pending_app_mode", None)
    if pending:
        st.session_state["selected_app_mode"] = pending
        st.session_state["entry_stage"] = "work"
        st.session_state["_initial_top_done"] = False
