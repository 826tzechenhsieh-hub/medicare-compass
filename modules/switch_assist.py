import streamlit as st
import re
from core.translations import m2_labels
from core.flow_translations import flow_labels, SWITCH_NEXT


def plain_text(text):
    """Option labels may contain emphasis; the SHIP field must be literal text."""
    return re.sub(r"[*_`#]", "", str(text)).strip()

def render(current_lang):
    l2 = m2_labels.get(current_lang, m2_labels["English"])
    st.markdown(l2["title"])
    st.caption(l2["caption"])
    st.markdown("---")

    st.subheader(l2["step1_title"])
    # Store stable option codes so changing the UI language keeps the selection.
    reason_index = st.selectbox(
        l2["step1_label"], list(range(len(l2["reasons"]))),
        format_func=lambda index: l2["reasons"][index], key="switch_reason",
        persist_state="session",
    )
    reason = l2["reasons"][reason_index]

    if reason != l2["reasons"][0]:
        st.write("---")
        st.subheader(l2["step2_title"])
        move_index = st.radio(
            l2["move_question"], list(range(len(l2["yes_no"]))),
            format_func=lambda index: l2["yes_no"][index], key="switch_move",
            persist_state="session",
        )
        move_recent = l2["yes_no"][move_index]

        if move_recent in ["Yes", "是", "Sí", "예"]:
            st.markdown(l2["sep_alert"], unsafe_allow_html=True)
        else:
            st.info(l2["standard_windows"])

        st.write("---")
        st.subheader(l2["step3_title"])
        st.markdown(l2["warnings_box"], unsafe_allow_html=True)
        st.success(SWITCH_NEXT.get(current_lang, SWITCH_NEXT["English"]))

        flow = flow_labels(current_lang)
        if st.button(flow["ship"], key="switch_to_ship", type="primary", width="stretch"):
            concern = plain_text(reason)
            previous = st.session_state.get("ship_switch_concern_source", "")
            if concern != previous:
                draft = st.session_state.get("ship_draft_concern", "")
                st.session_state["ship_draft_concern"] = (
                    draft.replace(previous, concern, 1) if previous and previous in draft else concern
                )
            st.session_state["ship_switch_concern_source"] = concern
            st.session_state["ship_auto_notes"] = {
                "primary_concern": concern,
            }
            st.session_state["_pending_app_mode"] = "SHIP_PREP"
            st.rerun()
