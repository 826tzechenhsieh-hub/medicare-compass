"""Global floating feedback entry and dialog."""

import streamlit as st

from core.feedback_translations import get_feedback_ui
from core.feedback_ui import draft, field, submit
from core.translations import m1_text, m2_text, m3_text, m4_text, router_labels


STATE = "user_feedback_state"


def render_form(current_lang, page, page_label, *, rerun_scope="app"):
    ui = get_feedback_ui(current_lang)
    if draft(STATE).get("saved"):
        st.success(ui["saved"])
        if st.button(ui["close"], key="user_feedback_close", use_container_width=True):
            st.rerun()
        return
    st.caption(f"{ui['page']}: {page_label}")
    category = field(
        STATE, "category", st.selectbox, ui["category"],
        options=[None, *ui["categories"]], initial=None,
        placeholder=ui["none"],
        format_func=lambda value: ui["categories"].get(value, ui["none"]),
    )
    rating = field(
        STATE, "rating", st.selectbox, ui["rating"],
        options=[None, 1, 2, 3, 4, 5], initial=None,
        placeholder=ui["none"],
        format_func=lambda value: ui["none"] if value is None else str(value),
    )
    st.caption(ui["rating_hint"])
    feedback = field(STATE, "feedback", st.text_area, ui["feedback"], max_chars=2000, height=140)
    st.caption(ui["privacy"])
    if st.button(ui["submit"], key="user_feedback_submit", type="primary", use_container_width=True):
        if category is None or not feedback.strip():
            st.warning(ui["required"])
        elif submit(STATE, "User Feedback", {
            "category": category, "rating": "" if rating is None else rating,
            "feedback": feedback.strip(), "page": page, "language": current_lang,
        }, ui):
            st.rerun(scope=rerun_scope)



def render(current_lang, page):
    ui = get_feedback_ui(current_lang)
    page = page or "HOME"
    page_names = {"MAIN_AI": m1_text, "SWITCH_ASSISTANT": m2_text,
                  "SHIP_PREP": m3_text, "CALENDAR_ICS": m4_text}
    if page == "PROFILE":
        page_label = router_labels.get(current_lang, router_labels["English"])["profile_btn"]
    else:
        labels = page_names.get(page, {})
        page_label = labels.get(current_lang, labels.get("English", ui["home"]))

    @st.dialog(ui["title"])
    def feedback_dialog():
        render_form(current_lang, page, page_label, rerun_scope="fragment")

    with st.container(key="global_feedback_launcher"):
        if st.button(ui["launcher"], key="global_feedback_open", use_container_width=True):
            if draft(STATE).get("saved"):
                st.session_state[STATE] = {}
                for name in ("category", "rating", "feedback"):
                    st.session_state.pop(f"_{STATE}_{name}", None)
            feedback_dialog()
