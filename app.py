import streamlit as st
from PIL import Image
import base64
#streamlit run app.py

# 載入核心模組
from core.translations import (
    sidebar_labels, nav_title_map, nav_label_map,
    m1_text, m2_text, m3_text, m4_text,
    upload_label_map, legal_title_map, legal_caption_map,
    reset_btn_map, quick_btn_map, font_size_map,
    router_labels, header_labels,
    ship_flow_map, new_assessment_map
)

from core.ai_engine import configure_gemini
from core.config import MEDICARE_INFO_YEAR

# 🚨 這裡的路徑已經從 pages 改成 views，避免 Streamlit 自動生成選單
from modules import main_ai, switch_assist, ship_prep, calendar_ics, profile

# --------------------------------------------------
# Page Configuration & Custom CSS
# --------------------------------------------------
page_icon = Image.open("assets/medicare_compass_logo.png")

with open("assets/medicare_compass_logo.png", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="Medicare Compass",
    page_icon=page_icon,
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
    saved_font_size = reset_settings.get("font_size", 19)

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.session_state["selected_language"] = saved_language
    st.session_state["font_size"] = saved_font_size
    st.session_state["persona"] = "self"
    st.session_state["persona_selector"] = "self"
    st.session_state["selected_app_mode"] = None

# --------------------------------------------------
# Global Route State
# --------------------------------------------------

if "selected_app_mode" not in st.session_state:
    st.session_state["selected_app_mode"] = None

# 主畫面的入口按鈕不能直接修改 radio 的 key，
# 所以先暫存在 pending，下一次 rerun 再切換。
if "_pending_app_mode" in st.session_state:
    st.session_state["selected_app_mode"] = st.session_state.pop(
        "_pending_app_mode"
    )

# --------------------------------------------------
# Global Persona State
# --------------------------------------------------

if "persona" not in st.session_state:
    st.session_state["persona"] = "self"

if "persona_selector" not in st.session_state:
    st.session_state["persona_selector"] = st.session_state["persona"]


def handle_persona_change():
    new_persona = st.session_state["persona_selector"]
    old_persona = st.session_state.get("persona", "self")

    # 如果從「本人」切成「協助他人」或反過來，
    # 清除上一個人的詢問單資料，避免資料混用。
    if new_persona != old_persona:
        profile_keys = [
            "profile_data",
            "profile_step",
            "profile_completed",
            "profile_coverage_select",
            "profile_monthly_premium",
            "profile_has_part_ab",
            "profile_has_commercial",
            "profile_has_low_income",
            "profile_priority_select",
            "profile_priority_other",
            "profile_health_notes",
            "profile_zip",
            "profile_medications",
            "profile_pharmacy",
        ]

        for key in profile_keys:
            st.session_state.pop(key, None)

    st.session_state["persona"] = new_persona

# --------------------------------------------------
# Sidebar Setup & 功能模組選單
# --------------------------------------------------
with st.sidebar:
    if "selected_language" not in st.session_state:
        st.session_state["selected_language"] = "English"

    # ==================================================
    # Smart Reset Flow
    # 放在 Sidebar 最上方、語言設定之前
    # ==================================================
    reset_lang = st.session_state["selected_language"]

    reset_ui = new_assessment_map.get(
        reset_lang,
        new_assessment_map["English"],
    )

    @st.dialog(reset_ui["title"])
    def confirm_new_assessment():
        st.write(reset_ui["message"])

        col_cancel, col_confirm = st.columns(2)

        with col_cancel:
            if st.button(
                reset_ui["cancel"],
                use_container_width=True,
                key="new_assessment_cancel",
            ):
                st.rerun()

        with col_confirm:
            if st.button(
                reset_ui["confirm"],
                type="primary",
                use_container_width=True,
                key="new_assessment_confirm",
            ):
                st.session_state["_do_full_reset"] = {
                    "language": st.session_state.get(
                        "selected_language",
                        "English",
                    ),
                    "font_size": st.session_state.get(
                        "font_size",
                        19,
                    ),
                }

                st.rerun()

    if st.button(
        reset_ui["btn"],
        use_container_width=True,
        key="start_new_profile",
    ):
        confirm_new_assessment()

    st.caption(reset_ui["caption"])

    st.markdown("---")

    # ==================================================
    # 語言設定
    # ==================================================
    current_ui = sidebar_labels[st.session_state["selected_language"]]
    st.markdown(current_ui["header"])

    current_lang = st.radio(
        current_ui["select"],
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        key="selected_language"
    )

    st.markdown("---")

    router_ui = router_labels.get(
        current_lang,
        router_labels["English"]
    )

    st.markdown(f"### {nav_title_map[current_lang]}")

    nav_display = {
        "MAIN_AI": m1_text[current_lang],
        "PROFILE": router_ui["nav_profile"],
        "SWITCH_ASSISTANT": m2_text[current_lang],
        "SHIP_PREP": m3_text[current_lang],
        "CALENDAR_ICS": m4_text[current_lang],
    }

    app_mode = st.radio(
        nav_label_map[current_lang],
        list(nav_display.keys()),
        format_func=lambda mode: nav_display[mode],
        index=None,
        key="selected_app_mode",
    )

    ship_flow_ui = ship_flow_map.get(
        current_lang,
        ship_flow_map["English"],
    )

    st.link_button(
        ship_flow_ui["sidebar_btn"],
        "https://www.shiphelp.org/",
        use_container_width=True,
    )

    # 模組切換狀態：僅用於控制 Main AI 的捲動行為，不做行為追蹤或外部紀錄。
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

    font_ui = font_size_map.get(current_lang, font_size_map["English"])

    st.markdown(font_ui["title"])

    font_size = st.slider(
        font_ui["label"],
        min_value=16,
        max_value=26,
        value=19,
        step=1,
        key="font_size"
    )

    st.markdown("---")
    if (
        app_mode == "MAIN_AI"
        and not st.session_state.get("conversation_finished", False)
        and "saved_user_input" in st.session_state
        and st.session_state.saved_user_input
    ):
        with st.container(border=True):

            st.markdown("#### 💾 Saved Input")

            saved_text = st.session_state.saved_user_input

            st.caption(saved_text)

            quick_btn_label = quick_btn_map.get(
                current_lang,
                quick_btn_map["English"]
            ).format(input="")

            if st.button(
                quick_btn_label,
                use_container_width=True,
                key="sidebar_resubmit_saved"
            ):
                st.session_state["resubmit_saved_input"] = True
                st.rerun()
        
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

    st.markdown("---")
    with st.expander(legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False):
        st.caption(legal_caption_map.get(current_lang, legal_caption_map["English"]))

    st.markdown("---")
    if app_mode == "MAIN_AI":
        reset_label = reset_btn_map.get(current_lang, reset_btn_map["繁體中文"])

        if st.button(reset_label, use_container_width=True):

            # 只重設目前 Medicare 對話，不刪除 Saved Input
            conversation_keys = [
                "messages",
                "user_state",
                "user_zip",
                "conversation_finished",
                "auto_submit",
                "resubmit_saved_input",
                "ship_auto_zip",
                "ship_auto_state",
                "ship_auto_notes",
                "_scroll_to_message",
                "_initial_top_done",
            ]

            for key in conversation_keys:
                st.session_state.pop(key, None)

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
# Global Header & Persona
# --------------------------------------------------

router_ui = router_labels.get(
    current_lang,
    router_labels["English"]
)

header_ui = header_labels.get(
    current_lang,
    header_labels["English"]
)

st.markdown(
    f"""<div id="medicare-top" class="header-box">
<div class="brand-title-row">
<img src="data:image/png;base64,{logo_base64}" class="brand-title-icon">
<div class="brand-text">
<span class="main-title">Medicare Compass</span>
<div class="sub-title">Powered by CareCompass™</div>
</div>
</div>
<div class="info-base-badge">
<div>{header_ui["info_base"].format(year=MEDICARE_INFO_YEAR)}</div>
<div class="info-base-reviewed">{header_ui["last_reviewed"]}</div>
</div>
</div>""",
    unsafe_allow_html=True,
)

# 全域諮詢對象
st.markdown(router_ui["persona_title"])

st.radio(
    router_ui["persona_label"],
    ["self", "helping_others"],
    format_func=lambda value: (
        router_ui["persona_self"]
        if value == "self"
        else router_ui["persona_helping"]
    ),
    key="persona_selector",
    horizontal=True,
    on_change=handle_persona_change,
)

st.divider()

# --------------------------------------------------
# 頁面路由派發
# --------------------------------------------------

if app_mode is None:

    ui = router_labels.get(
        current_lang,
        router_labels["English"]
    )

    st.markdown(ui["action_title"])

    st.write("")

    col_profile, col_ai = st.columns(2)

    # -----------------------------
    # 詢問單資料
    # -----------------------------
    with col_profile:
        if st.button(
            ui["profile_btn"],
            type="primary",
            use_container_width=True,
            key="entry_profile_btn",
        ):
            st.session_state["_pending_app_mode"] = "PROFILE"
            st.rerun()

        st.caption(ui["profile_caption"])

    # -----------------------------
    # 直接詢問 AI
    # -----------------------------
    with col_ai:
        if st.button(
            ui["ai_btn"],
            use_container_width=True,
            key="entry_ai_btn",
        ):
            st.session_state["_pending_app_mode"] = "MAIN_AI"
            st.rerun()

        st.caption(ui["ai_caption"])

    st.write("")
    with st.expander(ui["scope_title"], expanded=False):
        scope_col1, scope_col2 = st.columns(2)
        with scope_col1:
            st.markdown(ui["scope_can"])
        with scope_col2:
            st.markdown(ui["scope_cannot"])


elif app_mode == "PROFILE":
    profile.render(current_lang)


elif app_mode == "MAIN_AI":
    main_ai.render(current_lang, img_data)


elif app_mode == "SWITCH_ASSISTANT":
    switch_assist.render(current_lang)


elif app_mode == "SHIP_PREP":
    ship_prep.render(current_lang)


elif app_mode == "CALENDAR_ICS":
    calendar_ics.render(current_lang)

# --------------------------------------------------
# Global Footer Disclaimer
# --------------------------------------------------

st.markdown("---")

st.markdown(
    f"""
    <div class="global-disclaimer">
        {header_ui["disclaimer"]}
    </div>
    """,
    unsafe_allow_html=True,
)
