"""Consultation feedback, rendered after the completed AI conversation."""

import streamlit as st

from core.feedback_translations import get_feedback_ui
from core.feedback_ui import draft, field, submit
from core.translations import feedback_labels


STATE = "product_feedback_state"


def render(current_lang):
    ui = get_feedback_ui(current_lang)
    labels = feedback_labels.get(current_lang, feedback_labels["English"])
    with st.container(border=True):
        st.markdown(f"#### {labels['title']}")
        if draft(STATE).get("saved"):
            st.success(ui["saved"])
            return
        st.caption(labels["caption"])
        options = {"Helpful": labels["helpful"], "Neutral": labels["neutral"], "Unclear": labels["unclear"]}
        helpfulness = field(
            STATE, "helpfulness", st.radio, labels["rating_label"],
            options=list(options), index=None, initial=None,
            format_func=options.get, horizontal=True,
        )
        confusion = field(STATE, "confusion", st.text_area, ui["confusion"], max_chars=2000)
        future = field(STATE, "future_request", st.text_area, ui["future_request"], max_chars=2000)
        st.caption(ui["privacy"])
        if st.button(ui["submit"], key="product_feedback_submit", use_container_width=True):
            if helpfulness is None:
                st.warning(ui["choose_rating"])
            elif submit(STATE, "Product Feedback", {
                "helpfulness": helpfulness, "confusion": confusion.strip(),
                "future_request": future.strip(), "language": current_lang,
            }, ui):
                st.rerun()
