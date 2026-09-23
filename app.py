import streamlit as st
#streamlit run app.py

from core.translations import legal_caption_map, m1_text, m2_text, m3_text, m4_text
from core.ai_engine import configure_gemini
from core.config import MEDICARE_INFO_YEAR, CONTENT_COMPILED_DATE
from core.guide_text import LANGUAGES, text
from modules import guide, main_ai, switch_assist, ship_prep, calendar_ics

def persistent_radio(label, options, *, key, on_change=None, widget=st.radio, **kwargs):
    """Keep navigation state independent of translated widget identities.

    Only a user selection updates the durable value. Recreating or hiding a
    widget must not erase the current route, language, or consultation target.
    """
    widget_key = f"_widget_{key}"
    st.session_state[widget_key] = st.session_state[key]

    def save_selection():
        st.session_state[key] = st.session_state[widget_key]
        if on_change is not None:
            on_change()

    widget(
        label,
        options,
        key=widget_key,
        on_change=save_selection,
        **kwargs,
    )
    return st.session_state[key]


# --------------------------------------------------
# Page Configuration & Custom CSS
# --------------------------------------------------
st.set_page_config(
    page_title="Medicare Compass",
    page_icon="assets/medicare_compass_logo.png",
    layout="centered"
)

# 讀取並注入獨立的 CSS 檔案
def load_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    pass

# 初始化 Gemini (只在背景從 st.secrets 讀取)
configure_gemini()

# --------------------------------------------------
# Smart Reset Flow
# --------------------------------------------------
if "_do_full_reset" in st.session_state:
    reset_settings = st.session_state.get("_do_full_reset", {})

    saved_language = reset_settings.get("language", "English")
    saved_font_size = reset_settings.get("font_size", 20)

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.session_state["selected_language"] = saved_language
    st.session_state["font_size"] = saved_font_size
    st.session_state["persona"] = "self"
    st.session_state["persona_selector"] = "self"
    st.session_state["selected_app_mode"] = None
    st.session_state["_scroll_to_top"] = True

# --------------------------------------------------
# Global Route State
# --------------------------------------------------

if "selected_app_mode" not in st.session_state:
    st.session_state["selected_app_mode"] = None

# --------------------------------------------------
# Pending Route
# --------------------------------------------------
if "_pending_app_mode" in st.session_state:

    pending_mode = st.session_state.pop("_pending_app_mode")

    # 更新持久路由；選單在渲染時同步，不讓翻譯後的 widget 決定頁面。
    st.session_state["selected_app_mode"] = pending_mode

# --------------------------------------------------
# Global Persona State
# --------------------------------------------------

if "persona" not in st.session_state:
    st.session_state["persona"] = "self"

if "persona_selector" not in st.session_state:
    st.session_state["persona_selector"] = st.session_state["persona"]


# V1.5 presents journeys while keeping the existing route and durable-state mechanism.
st.session_state.setdefault("selected_language", "English")
st.session_state.setdefault("font_size", 20)
if st.session_state["font_size"] not in (18, 20, 24):
    st.session_state["font_size"] = min((18, 20, 24), key=lambda size: abs(size - st.session_state["font_size"]))

with st.sidebar:
    current_lang = persistent_radio(
        "Language / 語言", LANGUAGES, key="selected_language", widget=st.selectbox
    )
    ui = text(current_lang)
    sizes = {18: ui["standard"], 20: ui["large"], 24: ui["largest"]}
    font_size = persistent_radio(ui["size"], list(sizes), key="font_size", format_func=sizes.get)
    with st.expander(ui["about"]):
        st.write(ui["neutral"])
        st.caption(legal_caption_map.get(current_lang, legal_caption_map["English"]))

    st.divider()
    st.markdown(f"### {ui['modules']}")
    routes = [(None, ui["home"]), ("PROFILE", ui["explore"]),
              ("MAIN_AI", m1_text[current_lang]),
              ("SWITCH_ASSISTANT", m2_text[current_lang]),
              ("SHIP_PREP", m3_text[current_lang]),
              ("CALENDAR_ICS", m4_text[current_lang])]
    for route, label in routes:
        if st.button(label, key=f"nav_{route or 'HOME'}", use_container_width=True,
                     type="primary" if st.session_state.get("selected_app_mode") == route else "secondary"):
            if route == "MAIN_AI":
                st.session_state["main_presentation"] = "full"
            guide.go(route)
    with st.expander(ui["restart"]):
        st.caption(ui["reset_note"])
        if st.button(ui["confirm"], key="sidebar_confirm_restart"):
            st.session_state["_do_full_reset"] = {"language": current_lang, "font_size": font_size}
            st.rerun()

st.markdown(
    f"""<style>
    html {{ font-size: {font_size}px !important; }}
    body, [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p,
    .stButton > button, textarea, input {{ font-size: {font_size}px !important; }}
    </style>""", unsafe_allow_html=True,
)
st.markdown('<div id="medicare-top"></div>', unsafe_allow_html=True)
st.title("Medicare Compass")
st.caption(ui["tagline"])

app_mode = st.session_state.get("selected_app_mode")
if app_mode is None:
    guide.home(current_lang)
elif app_mode == "PROFILE":
    guide.guided(current_lang)
elif app_mode == "MAIN_AI":
    st.caption(ui["self"] if st.session_state.get("persona") == "self" else ui["family"])
    attachment = guide.main_attachment(current_lang)
    main_ai.render(current_lang, attachment)
elif app_mode == "SWITCH_ASSISTANT":
    switch_assist.render(current_lang)
elif app_mode == "GUIDE_RESULT":
    guide.result(current_lang)
elif app_mode in ("SHIP_PREP", "CALENDAR_ICS"):
    if st.button(ui["back"], key="tool_back"):
        guide.go("MAIN_AI" if st.session_state.get("messages") else None)
    if app_mode == "SHIP_PREP":
        ship_prep.render(current_lang)
    else:
        calendar_ics.render(current_lang)
else:
    # Old bookmarks/session routes still have a safe path back to the new entry.
    guide.go(None)

if st.session_state.pop("_scroll_to_top", False):
    main_ai.scroll_to_medicare_top()
st.divider()
st.caption(ui["advice"])
st.caption(ui["neutral"])
st.caption(ui["source"])
reference = ui["year"].format(year=MEDICARE_INFO_YEAR)
# Never substitute today's date for an actual content review/compilation date.
if CONTENT_COMPILED_DATE:
    reference += " | " + ui["date"].format(date=CONTENT_COMPILED_DATE)
st.markdown(f'<div class="reference-footer">{reference}</div>', unsafe_allow_html=True)
