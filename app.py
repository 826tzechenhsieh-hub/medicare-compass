import streamlit as st
from PIL import Image
#streamlit run app.py

# 載入核心模組
from core.translations import (
    sidebar_labels, nav_title_map, nav_label_map, m1_text, m2_text, m3_text, m4_text,
    upload_label_map, legal_title_map, legal_caption_map, summary_btn_map, reset_btn_map
)
from core.ai_engine import configure_gemini

# 🚨 這裡的路徑已經從 pages 改成 views，避免 Streamlit 雞婆自動生成選單
from modules import main_ai, switch_assist, ship_prep, calendar_ics

# --------------------------------------------------
# Page Configuration & Custom CSS
# --------------------------------------------------
st.set_page_config(
    page_title="Medicare Compass",
    page_icon="🧭",
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
# Sidebar Setup & 功能模組選單
# --------------------------------------------------
with st.sidebar:
    if "selected_language" not in st.session_state:
        st.session_state["selected_language"] = "English"

    current_ui = sidebar_labels[st.session_state["selected_language"]]
    st.markdown(current_ui["header"])
    current_lang = st.radio(
        current_ui["select"],
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        key="selected_language"
    )

    st.markdown("---")

    st.markdown(f"### {nav_title_map[current_lang]}")
    c_m1, c_m2, c_m3, c_m4 = m1_text[current_lang], m2_text[current_lang], m3_text[current_lang], m4_text[current_lang]
    selected_module_label = st.radio(
        nav_label_map[current_lang],
        [c_m1, c_m2, c_m3, c_m4],
        index=0,
    )

    if selected_module_label == c_m1:
        app_mode = "MAIN_AI"
    elif selected_module_label == c_m2:
        app_mode = "SWITCH_ASSISTANT"
    elif selected_module_label == c_m3:
        app_mode = "SHIP_PREP"
    else:
        app_mode = "CALENDAR_ICS"

    # 🎯 PUT THE TRACKER RIGHT HERE:
    # 1. Initialize a memory of what module we are currently looking at
    if "current_module" not in st.session_state:
        st.session_state["current_module"] = app_mode

    # 2. Check if the user just clicked a NEW module in the sidebar
    if st.session_state["current_module"] != app_mode:
        
        # 3. Update the memory to the new module
        st.session_state["current_module"] = app_mode
        
        # 4. If they just switched BACK to the Main AI, reset the scroll flag!
        if app_mode == "MAIN_AI":
            st.session_state["_initial_top_done"] = False

    st.markdown("---")
    st.markdown("#### 🔠 Font Size")
    font_size = st.slider("Adjust font size", min_value=16, max_value=26, value=19, step=1, key="font_size")

    st.markdown("---")
    if "saved_user_input" in st.session_state and st.session_state.saved_user_input:
        st.info("Saved user input found.")
        
    st.markdown("---")
    uploaded_file = st.file_uploader(upload_label_map.get(current_lang, "📷 上傳照片"), type=["png", "jpg", "jpeg", "pdf"])
    
    img_data = None
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            st.success("File attached!")
        except Exception:
            pass
        st.warning("File uploaded.")

    # (API Key 輸入框已經被移除了 🗑️)

    st.markdown("---")
    with st.expander(legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False):
        st.caption(legal_caption_map.get(current_lang, legal_caption_map["English"]))

    st.markdown("---")
    if app_mode == "MAIN_AI":
        summary_btn_label = summary_btn_map.get(current_lang, summary_btn_map["繁體中文"])
        reset_label = reset_btn_map.get(current_lang, reset_btn_map["繁體中文"])

        if st.button(summary_btn_label, use_container_width=True, type="primary"):
            st.session_state.show_summary = True

        if st.button(reset_label, use_container_width=True):
            # 徹底清除所有 session_state 鍵值
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# --------------------------------------------------
# 動態字體大小注入
# --------------------------------------------------
st.markdown(
    f"""
    <style>
    html {{ font-size: {font_size}px !important; }}
    body, [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ font-size: {font_size}px !important; }}
    .stChatMessage {{ font-size: {font_size}px !important; line-height: 1.7 !important; }}
    .stButton > button {{ font-size: {font_size - 1}px !important; }}
    .stChatInput input {{ font-size: {font_size}px !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# 頁面路由派發
# --------------------------------------------------
if app_mode == "MAIN_AI":
    main_ai.render(current_lang, img_data)
elif app_mode == "SWITCH_ASSISTANT":
    switch_assist.render(current_lang)
elif app_mode == "SHIP_PREP":
    ship_prep.render(current_lang)
elif app_mode == "CALENDAR_ICS":
    calendar_ics.render(current_lang)