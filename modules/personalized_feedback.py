import streamlit as st
from core.translations import feedback_labels


# ==================================================
# Personalized Feedback UI
# 使用者滿意度回饋
# 目前只儲存在 Session State
# 不連接 Google Sheets / Database
# ==================================================

# ==================================================
# Feedback Module
# ==================================================

def render(current_lang):

    ui = feedback_labels.get(
        current_lang,
        feedback_labels["English"]
    )

    # --------------------------------------------------
    # Session State 初始化
    # --------------------------------------------------
    if "feedback_rating" not in st.session_state:
        st.session_state.feedback_rating = None

    if "feedback_comment" not in st.session_state:
        st.session_state.feedback_comment = ""

    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

    # --------------------------------------------------
    # Feedback UI
    # --------------------------------------------------
    with st.container(border=True):

        st.markdown(f"#### {ui['title']}")

        st.caption(ui["caption"])

        rating_options = [
            "Helpful",
            "Neutral",
            "Unclear",
        ]

        rating_labels = {
            "Helpful": ui["helpful"],
            "Neutral": ui["neutral"],
            "Unclear": ui["unclear"],
        }

        selected_rating = st.radio(
            ui["rating_label"],
            rating_options,
            index=None,
            format_func=lambda value: rating_labels[value],
            horizontal=True,
            key="feedback_rating",
        )

        feedback_comment = st.text_area(
            ui["comment_label"],
            placeholder=ui["comment_placeholder"],
            height=110,
            key="feedback_comment",
        )

        if st.button(
            ui["submit"],
            use_container_width=True,
            key="feedback_submit",
        ):

            # 目前只存在 Session State
            st.session_state["personalized_feedback"] = {
                "rating": selected_rating,
                "comment": feedback_comment.strip(),
            }

            st.session_state.feedback_submitted = True

        if st.session_state.feedback_submitted:
            st.success(ui["saved"])