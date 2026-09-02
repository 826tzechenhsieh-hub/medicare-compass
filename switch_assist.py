import streamlit as st
from core.translations import m2_labels

def render(current_lang):
    l2 = m2_labels.get(current_lang, m2_labels["English"])
    st.markdown(l2["title"])
    st.caption(l2["caption"])
    st.markdown("---")

    st.subheader(l2["step1_title"])
    reason = st.selectbox(l2["step1_label"], l2["reasons"])

    if reason != l2["reasons"][0]:
        st.write("---")
        st.subheader(l2["step2_title"])
        move_recent = st.radio(l2["move_question"], l2["yes_no"])

        if move_recent in ["Yes", "是", "Sí", "예"]:
            st.markdown(l2["sep_alert"], unsafe_allow_html=True)
        else:
            st.info(l2["standard_windows"])

        st.write("---")
        st.subheader(l2["step3_title"])
        st.markdown(l2["warnings_box"], unsafe_allow_html=True)
        st.success(l2["next_step_tip"])