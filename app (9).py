from pathlib import Path

import streamlit as st
from PIL import Image

from core.ai_engine import configure_gemini
from core.navigation import init_navigation
from core.translations import header_labels
from modules import (
    home, sidebar, profile, main_ai, switch_assist, ship_prep, calendar_ics, user_feedback,
)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Medicare Compass",
                   page_icon=Image.open(ROOT / "assets/medicare_compass_logo.png"),
                   layout="centered")
st.markdown(f"<style>{(ROOT / 'style.css').read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True)
configure_gemini()
init_navigation()
language = sidebar.render()
header = header_labels.get(language, header_labels["English"])

st.markdown("""<div id="medicare-top" class="header-box">
<div class="brand-title-row"><div class="brand-text">
<span class="main-title">Medicare-Compass</span>
<div class="sub-title">Powered by CareCompass™</div>
</div></div></div>""", unsafe_allow_html=True)

mode = st.session_state["selected_app_mode"]
if st.session_state["entry_stage"] in ("welcome", "topics"):
    home.render(language)
else:
    if mode == "PROFILE":
        profile.render(language)
    elif mode == "MAIN_AI":
        main_ai.render(language, None)
    elif mode == "SWITCH_ASSISTANT":
        switch_assist.render(language)
    elif mode == "SHIP_PREP":
        ship_prep.render(language)
    elif mode == "CALENDAR_ICS":
        calendar_ics.render(language)

user_feedback.render(language, mode)
if st.session_state.pop("_scroll_to_top", False):
    main_ai.scroll_to_medicare_top()
st.divider()
st.markdown(f"<div class='global-disclaimer'>{header['disclaimer']}</div>",
            unsafe_allow_html=True)
