import calendar
import datetime
from datetime import timedelta
import re
import urllib.parse
from PIL import Image
import google.generativeai as genai
import streamlit as st
from translations import (
    sidebar_labels, guide_labels, m2_labels, m3_labels, m4_labels,
    nav_title_map, nav_label_map, m1_text, m2_text, m3_text, m4_text,
    upload_label_map, legal_title_map, legal_caption_map,
    summary_btn_map, reset_btn_map,
    q_caption_map, btn1_map, btn2_map, quick_btn_map,
    input_placeholder_first_map, input_placeholder_followup_map,
    default_upload_msg_map, spinner_msg_map, timeline_template_map,
    tip_suffix_map, summary_title_map, ui_bottom_map, official_links_map
)


# --------------------------------------------------
# 1. AI 回應清洗與衛生處理函式 (強效防草稿與思考過程洩漏)
# --------------------------------------------------
def clean_response(text: str) -> str:
    """過濾 AI 內部的思考過程、草稿標籤與 Prompt 殘留"""
    if not text:
        return ""
    
    text = re.sub(r"<(think|thought)>.*?</\1>", "", text, flags=re.DOTALL)
    
    patterns = [
        r"User Profile:.*?\n",
        r"Key Constraint Checklist:.*?\n",
        r"Personal Medicare Timeline:.*?\n",
        r"Persona/Role:.*?\n",
        r"\(Self-Correction\):.*?\n",
        r"Final Content Plan:.*?\n",
        r"Comparison Table:.*?\n",
        r"Key decision making question:.*?\n",
        r"```json.*?```",
        r"^\s*[\*\-]?\s*Directly print.*$",
        r"^\s*[\*\-]?\s*Markdown bullets\?.*$",
        r"^\s*[\*\-]?\s*Final Polish\..*$",
        r"^\s*[\*\-]?\s*Self-Correction:.*$",
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
    return cleaned.strip()

def sanitize_ai_output(raw_text, target_lang="English"):
    """第二層安全網：利用特徵錨點擷取真正給使用者的對話"""
    if not raw_text:
        return raw_text

    content_anchors = [
        "Hello!", "In New Jersey", "In California", "In Virginia",
        "Path 1:", "Path 2:", "Option 1:", "Option 2:", "Actionable Steps",
        "How to Apply:", "Where to Apply:", "To give you the most accurate",
        "Which state do you live in?", "您好", "你好", "¡Hola", "안녕하세요",
    ]

    for anchor in content_anchors:
        if anchor in raw_text:
            idx = raw_text.rfind(anchor)
            candidate = raw_text[idx:].strip()
            if len(candidate) > 15 and not any(
                bad in candidate for bad in [
                    "*Review against rules:*", "*Final Polish:*",
                    "*Correction on", "*Final Content Construction:*",
                ]
            ):
                return candidate

    lines = raw_text.split("\n")
    clean_lines = []
    bad_keywords = [
        "*Review against rules:*", "*Final Polish:*", "*Correction on",
        "*Final Content Construction:*", "*Ready.*", "*One more check:*",
        "*Constraint Check:*", "*Final check on rules:*", "User's goal:",
        "Constraint:", "Instruction:", "Concise bullet points?", "No drafts",
    ]

    for line in lines:
        stripped = line.strip()
        if any(bad.lower() in stripped.lower() for bad in bad_keywords):
            continue
        clean_lines.append(line)

    final_text = "\n".join(clean_lines).strip()
    return final_text if final_text else raw_text.strip()


def generate_clean_response(user_input, target_lang="English", img_data=None):
    """呼叫 Gemini 模型並強制以目標語言輸出乾淨的結果"""
    
    preferred_models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash",
    ]

    valid_models = []

    try:
        available_models = {}

        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                # list_models() 通常會回 models/gemini-xxx
                model_id = m.name.replace("models/", "")
                available_models[model_id] = m.name

        # 按照我們指定的優先順序排列
        valid_models = [
            available_models[model_id]
            for model_id in preferred_models
            if model_id in available_models
        ]

    except Exception:
        pass

    # 如果 list_models() 本身失敗，就直接照順序嘗試
    if not valid_models:
        valid_models = [
            f"models/{model_id}"
            for model_id in preferred_models
        ]

    # 💡 關鍵修改：強制要求 AI 連同標題、表格都必須使用 Target Language
    strict_system_instruction = (
        f"You are Medicare Compass, an expert assistant.\n"
        f"CRITICAL RULE: You MUST respond ENTIRELY in {target_lang}. "
        f"All headings, table headers, bullet points, advice, and tips MUST be accurately translated into {target_lang}.\n\n"
        "Task: Present Medicare choices concisely.\n\n"
        "CRITICAL OUTPUT RULES:\n"
        "1. NEVER output internal system logic, user profiles, timeline tags, or checklists (e.g., 'User Profile:', 'Key Constraint Checklist:').\n"
        "2. DO NOT show your thinking process or meta details to the user.\n"
        "3. START IMMEDIATELY with direct, warm, and friendly Medicare guidance.\n\n"
        "FINAL OUTPUT FORMAT:\n"
        "1. A Summary Comparison table contrasting Pathway A (Original Medicare) vs Pathway B (Medicare Advantage).\n"
        "2. 2 Key Decision-Making Questions.\n"
        "3. 1 Official Enrollment Tip."
    )

    last_exception = None
    for m_name in valid_models:
        try:
            model = genai.GenerativeModel(
                model_name=m_name, system_instruction=strict_system_instruction
            )

            formatted_history = []
            if "messages" in st.session_state:
                for m in st.session_state.messages[:-1]:
                    role = "user" if m["role"] == "user" else "model"
                    formatted_history.append(
                        {"role": role, "parts": [str(m["content"])]}
                    )

            chat = model.start_chat(history=formatted_history)

            if img_data:
                response = model.generate_content([user_input, img_data])
            else:
                response = chat.send_message(user_input)

            raw_text = response.text
            clean_text = sanitize_ai_output(
                clean_response(raw_text), target_lang=target_lang
            )
            return clean_text

        except Exception as inner_e:
            last_exception = inner_e
            continue

    if last_exception:
        raise last_exception


# --------------------------------------------------
# 2. Page Configuration & Custom CSS (視覺顏色優化)
# --------------------------------------------------
st.set_page_config(
    page_title="Medicare Compass",
    page_icon="🧭",
    layout="centered"
)


def scroll_to_medicare_top():
    st.html(
        """
        <script>
        (() => {
            if ("scrollRestoration" in history) {
                history.scrollRestoration = "manual";
            }

            function goTop() {
                const target = document.getElementById("medicare-top");

                if (target) {
                    target.scrollIntoView({
                        behavior: "auto",
                        block: "start"
                    });
                }
            }

            setTimeout(goTop, 400);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

def scroll_to_message(anchor_id):
    st.html(
        f"""
        <script>
        (() => {{
            const anchorId = "{anchor_id}";

            let lastHeight = -1;
            let stableFrames = 0;
            let attempts = 0;

            function waitUntilStable() {{
                const target = document.getElementById(anchorId);
                const currentHeight = document.documentElement.scrollHeight;

                if (currentHeight === lastHeight) {{
                    stableFrames++;
                }} else {{
                    stableFrames = 0;
                    lastHeight = currentHeight;
                }}

                attempts++;

                // 等整頁真的穩定後，只滾動一次
                if (target && stableFrames >= 45) {{

                    // 避免輸入框 focus 又把畫面拉到底部
                    if (document.activeElement) {{
                        document.activeElement.blur();
                    }}

                    const y =
                        target.getBoundingClientRect().top +
                        window.scrollY -
                        90;

                    window.scrollTo({{
                        top: Math.max(0, y),
                        behavior: "auto"
                    }});

                    return;
                }}

                if (attempts < 300) {{
                    requestAnimationFrame(waitUntilStable);
                }}
            }}

            if ("scrollRestoration" in history) {{
                history.scrollRestoration = "manual";
            }}

            requestAnimationFrame(waitUntilStable);

        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

st.markdown(
    """
    <style>
        .chat-anchor {
            scroll-margin-top: 5rem;
        }
        
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 0rem !important;
        }
        
        [data-testid="stChatMessageContainer"] {
            scroll-margin-top: 0px !important;
        }
        .stChatMessage {
            line-height: 1.7 !important;
        }
        .stButton>button {
            padding: 10px 20px !important;
            border-radius: 8px !important;
        }
        
        
        /* 雙色路徑卡片視覺樣式 (無 Tension 柔和色系) */
        .pathway-a-box {
            background-color: #f0f7ff;
            border-left: 6px solid #2563eb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            color: #111827 !important;
        }

        .pathway-b-box {
            background-color: #f0fdf4;
            border-left: 6px solid #16a34a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            color: #111827 !important;
        }

        .warning-card {
            background-color: #fffbe2;
            border-left: 5px solid #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            margin-bottom: 10px;
            color: #111827 !important;
        }

        .card-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            color: #111827 !important;
        }

        /* 所有自訂淺色卡片：不受 Streamlit 深色模式影響 */
        .pathway-a-box,
        .pathway-a-box *,
        .pathway-b-box,
        .pathway-b-box *,
        .warning-card,
        .warning-card *,
        .card-box,
        .card-box *,
        .official-links-box,
        .official-links-box *,
        .summary-box,
        .summary-box * {
            color: #111827 !important;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# API Keys 設定區塊
# ==========================================
try:
    # 程式碼會試著去系統的「密碼本」裡面找一個叫做 GEMINI_API_KEY 的東西
    primary_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    # 如果找不到密碼本，或是裡面沒有這個 Key，就不強求，設為空值
    primary_key = None

if primary_key:
    # 如果有順利拿到 Key，就啟動 AI 引擎
    genai.configure(api_key=primary_key)

# --------------------------------------------------
# 3. Sidebar Setup & 功能模組選單 (支援多語言同步)
# --------------------------------------------------
with st.sidebar:
    # 1. 初始化記憶體
    if "selected_language" not in st.session_state:
        st.session_state["selected_language"] = "English"

    # 2. 渲染語言選擇區塊
    current_ui = sidebar_labels[st.session_state["selected_language"]]
    st.markdown(current_ui["header"])
    current_lang = st.radio(
        current_ui["select"],
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        key="selected_language"
    )

    st.markdown("---")

    # 3. 渲染功能導航模組
    st.markdown(f"### {nav_title_map[current_lang]}")
    
    # 從字典中抓取當前語言的選項文字
    c_m1 = m1_text[current_lang]
    c_m2 = m2_text[current_lang]
    c_m3 = m3_text[current_lang]
    c_m4 = m4_text[current_lang]

    selected_module_label = st.radio(
        nav_label_map[current_lang],
        [c_m1, c_m2, c_m3, c_m4],
        index=0,
    )

    # 判斷使用者選了哪個模組
    if selected_module_label == c_m1:
        app_mode = "MAIN_AI"
    elif selected_module_label == c_m2:
        app_mode = "SWITCH_ASSISTANT"
    elif selected_module_label == c_m3:
        app_mode = "SHIP_PREP"
    else:
        app_mode = "CALENDAR_ICS"

    st.markdown("---")

    # 🔠 字體大小調整
    st.markdown("#### 🔠 Font Size")

    font_size = st.slider(
        "Adjust font size",
        min_value=16,
        max_value=26,
        value=19,
        step=1,
        key="font_size"
    )

    st.markdown("---")

    if ("saved_user_input" in st.session_state and st.session_state.saved_user_input):
        st.info("Saved user input found.")
        
    st.markdown("---")

    # 4. 渲染照片上傳區塊
    uploaded_file = st.file_uploader(
        upload_label_map.get(current_lang, "📷 上傳照片"),
        type=["png", "jpg", "jpeg", "pdf"],
    )
    img_data = None
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            st.success("File attached!")
        except Exception:
            pass
        st.warning("File uploaded.")

    if not primary_key:
        user_api_key = st.text_input("Gemini API Key:", type="password")
        if user_api_key:
            genai.configure(api_key=user_api_key)

    st.markdown("---")

    # 5. 渲染法律聲明與隱私區塊
    with st.expander(legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False):
        st.caption(legal_caption_map.get(current_lang, legal_caption_map["English"]))

    st.markdown("---")

    # 6. 渲染重置與總結按鈕 (僅在 MAIN_AI 顯示)
    if app_mode == "MAIN_AI":
        summary_btn_label = summary_btn_map.get(current_lang, summary_btn_map["繁體中文"])
        reset_label = reset_btn_map.get(current_lang, reset_btn_map["繁體中文"])

        if st.button(summary_btn_label, use_container_width=True, type="primary"):
            st.session_state.show_summary = True

        if st.button(reset_label, use_container_width=True):
            st.session_state.messages = []
            st.rerun()
# --------------------------------------------------
# 動態字體大小
# --------------------------------------------------
font_size = st.session_state.get("font_size", 19)

st.markdown(
    f"""
    <style>

    html {{
        font-size: {font_size}px !important;
    }}

    body,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        font-size: {font_size}px !important;
    }}

    .stChatMessage {{
        font-size: {font_size}px !important;
        line-height: 1.7 !important;
    }}

    .stButton > button {{
        font-size: {font_size - 1}px !important;
    }}

    .stChatInput input {{
        font-size: {font_size}px !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 4. 模組分流與執行邏輯
# --------------------------------------------------

# --------------------------------------------------
# 🅰️ 模組 1: 💬 智慧醫保諮詢 (Main AI Navigator)
# --------------------------------------------------
if app_mode == "MAIN_AI":
    top_container = st.container()

    with top_container:
        # 1. 顶部大标题 (大 Logo 居中)
        st.markdown("""
            <style>
            .header-box {
                text-align: center;
                padding: 10px 0;
            }

            #medicare-top {
                scroll-margin-top: 70px;
            }

            .main-title {
                font-size: 2.3rem !important;
                font-weight: bold;
                color: #1E3A8A;
            }

            .sub-title {
                font-size: 1.0rem;
                color: #6B7280;
                margin-top: -5px;
            }
            </style>

            <div id="medicare-top" class="header-box">
                <span class="main-title">🧭 Medicare Compass</span>
                <div class="sub-title">Powered by CareCompass™</div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # --------------------------------------------------
        # 📖 1分鐘 Medicare 快速指南區塊
        # --------------------------------------------------
        g_ui = guide_labels.get(current_lang, guide_labels["English"])
        
        with st.expander(g_ui["btn_text"], expanded=False):
            st.markdown(g_ui["guide_title"])
            col1, col2 = st.columns(2)
            with col1:
                st.info(g_ui["p_ab"])
                st.warning(g_ui["p_c"])
            with col2:
                st.success(g_ui["p_d"])
                st.error(g_ui["medigap"])
        st.markdown("---")

    if "user_role_type" not in st.session_state:
        st.session_state.user_role_type = "self"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "show_summary" not in st.session_state:
        st.session_state.show_summary = False
    if "saved_user_input" not in st.session_state:
        st.session_state.saved_user_input = ""

    for i, message in enumerate(st.session_state.messages):

        # 每一則使用者問題前面放一個定位點
        if message["role"] == "user":
            st.markdown(
                f'<div id="message-{i}" class="chat-anchor"></div>',
                unsafe_allow_html=True
            )

        with st.chat_message(message["role"]):
            if message["role"] in ["assistant", "model"]:
                st.markdown(clean_response(message["content"]))
            else:
                st.markdown(message["content"])

    if len(st.session_state.messages) == 0:
        st.caption(q_caption_map.get(current_lang, q_caption_map["English"]))

        col_start1, col_start2 = st.columns(2)
        with col_start1:
            btn1_label = btn1_map.get(current_lang, btn1_map["English"])
            btn_type1 = "primary" if st.session_state.user_role_type == "self" else "secondary"
            if st.button(btn1_label, use_container_width=True, type=btn_type1):
                st.session_state.user_role_type = "self"
                st.rerun()

        with col_start2:
            btn2_label = btn2_map.get(current_lang, btn2_map["English"])
            btn_type2 = "primary" if st.session_state.user_role_type == "family" else "secondary"
            if st.button(btn2_label, use_container_width=True, type=btn_type2):
                st.session_state.user_role_type = "family"
                st.rerun()

    prompt = None

    if st.session_state.get("saved_user_input"):
        st.markdown("<br>", unsafe_allow_html=True)
        q_btn = quick_btn_map.get(current_lang, quick_btn_map["English"])
        quick_btn_label = q_btn.format(input=st.session_state.saved_user_input)
        if st.button(quick_btn_label, type="primary", use_container_width=True):
            prompt = st.session_state.saved_user_input

    # 判斷 Placeholder 顯示內容
    has_history = len(st.session_state.get("messages", [])) > 0
    if not has_history:
        input_placeholder = input_placeholder_first_map.get(current_lang, input_placeholder_first_map["English"])
    else:
        input_placeholder = input_placeholder_followup_map.get(current_lang, input_placeholder_followup_map["English"])

    input_prompt = st.chat_input(input_placeholder)

    if input_prompt:
        role_prefix = "[Applying for Myself] " if st.session_state.get("user_role_type") == "self" else "[Helping Family/Parents] "
        prompt = role_prefix + input_prompt
        st.session_state.saved_user_input = prompt

    if prompt or uploaded_file:
        user_text = prompt if prompt else default_upload_msg_map.get(current_lang, "Please review this uploaded document.")

        if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_text:
            st.session_state.messages.append({
                "role": "user",
                "content": user_text
            })

            # 記住這一則問題的位置
            user_message_index = len(st.session_state.messages) - 1
            st.session_state["_scroll_to_message"] = f"message-{user_message_index}"

        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant", avatar="👵"):
            sp_msg = spinner_msg_map.get(current_lang, "Analyzing...")
            with st.spinner(sp_msg):
                date_match = re.search(r"(\d{1,2})/(?:(?:\d{1,2})/)?(\d{4})", user_text)
                is_first_input = len(st.session_state.messages) <= 2

                if date_match and is_first_input:
                    try:
                        month = int(date_match.group(1))
                        year = int(date_match.group(2))
                        turn_65_year = year + 65

                        start_m = month - 3 if month > 3 else month - 3 + 12
                        start_y = turn_65_year if month > 3 else turn_65_year - 1
                        end_m = month + 3 if month <= 9 else month + 3 - 12
                        end_y = turn_65_year if month <= 9 else turn_65_year + 1

                        start_m_name = calendar.month_name[start_m]
                        end_m_name = calendar.month_name[end_m]
                        birth_m_name = calendar.month_name[month]
                        end_day = calendar.monthrange(end_y, end_m)[1]

                        # 使用字典模板套用語系
                        tmpl = timeline_template_map.get(current_lang, timeline_template_map["English"])
                        final_output = tmpl.format(
                            birth_m_name=birth_m_name, turn_65_year=turn_65_year,
                            start_m_name=start_m_name, start_y=start_y,
                            end_m_name=end_m_name, end_y=end_y, end_day=end_day
                        )
                    except Exception:
                        final_output = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                else:
                    raw_response = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                    tip_suffix = tip_suffix_map.get(current_lang, tip_suffix_map["English"])
                    final_output = raw_response.strip() + tip_suffix

                st.markdown(final_output)
                st.session_state.messages.append(
                    {
                        "role": "model",
                        "content": final_output
                    }
                )
                
                st.rerun()

        if st.session_state.show_summary and len(st.session_state.messages) >= 2:
            st.markdown("---")
            s_title = summary_title_map.get(current_lang, "📋 Your Medicare Quick Summary")
            st.markdown(f'<h2 style="text-align: center; color: #1E3A8A;">{s_title}</h2>', unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)

    user_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") == "user"
    ]

    ai_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") in ["assistant", "model"]
    ]

    if len(ai_msgs) >= 2:
        links_html = official_links_map.get(
            current_lang,
            official_links_map["English"]
        )
        st.markdown(links_html, unsafe_allow_html=True)

    user_msgs = [m["content"] for m in st.session_state.messages if m.get("role") == "user"]
    ai_msgs = [m["content"] for m in st.session_state.messages if m.get("role") in ["assistant", "model"]]

    # 使用字典渲染底部 UI
    uib = ui_bottom_map.get(current_lang, ui_bottom_map["English"])
    pretty_summary_html = "<div class='summary-box' style='background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 25px; border-radius: 12px; font-size: 19px; line-height: 1.8;'>"

    if user_msgs:
      pretty_summary_html += f"<h4 style='color: #0F172A; margin-top:0; font-size: 20px;'>{uib['bg_title']}</h4><ul>"
      for u in user_msgs:
        pretty_summary_html += f"<li style='margin-bottom: 8px;'>{u}</li>"
      pretty_summary_html += "</ul><hr style='border: none; border-top: 1px solid #CBD5E1; margin: 20px 0;'>"

    if ai_msgs:
      pretty_summary_html += f"<h4 style='color: #0F172A; font-size: 20px;'>{uib['adv_title']}</h4>"
      formatted_last_ai = ai_msgs[-1].replace("\n", "<br>")
      pretty_summary_html += f"<div style='background-color: #FFFFFF; color: #111827 !important; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0;'>{formatted_last_ai}</div>"

    pretty_summary_html += "</div>"

    short_summary_text = "【Medicare Compass - Summary】\n\n"
    if user_msgs:
      short_summary_text += "📌 KEY USER INPUTS:\n"
      for u in user_msgs:
        short_summary_text += f"- {u}\n"
      short_summary_text += "\n"
    if ai_msgs:
      short_summary_text += f"💡 LATEST ADVICE:\n{ai_msgs[-1]}\n"

    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    for m in st.session_state.messages:
      role_title = "Compass Advisor" if m["role"] in ["assistant", "model"] else "User"
      full_log_text += f"[{role_title}]:\n{m['content']}\n\n" + "-" * 40 + "\n\n"

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs([uib["tab1"], uib["tab2"]])

    with tab1:
      st.markdown("<br>", unsafe_allow_html=True)
      st.markdown(pretty_summary_html, unsafe_allow_html=True)
      st.markdown("<br>", unsafe_allow_html=True)

      col1, col2 = st.columns(2)
      with col1:
        st.download_button(uib["dl_txt"], data=short_summary_text, file_name="medicare_summary.txt", use_container_width=True)
      with col2:
        st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="width:100%; height:46px; border-radius:8px; background-color:#2563EB; color:white; border:none; cursor:pointer; font-size:17px; font-weight:bold;">{uib["email_btn"]}</button></a>', unsafe_allow_html=True)

    with tab2:
      st.markdown("<br>", unsafe_allow_html=True)
      st.text_area(uib["log_label"], value=full_log_text, height=300, key="full_log_area")
      st.download_button(uib["dl_log"], data=full_log_text, file_name="medicare_full_log.txt", use_container_width=True)

# --------------------------------------------------
# 🆕 模組 2: 🔄 Plan 轉換決策助理 (Switching Assistant)
# --------------------------------------------------
elif app_mode == "SWITCH_ASSISTANT":
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


# --------------------------------------------------
# 🆕 模組 3: 📋 1-Page SHIP 諮詢準備單 (SHIP Prep)
# --------------------------------------------------
elif app_mode == "SHIP_PREP":
    l3 = m3_labels.get(current_lang, m3_labels["English"])
    st.markdown(l3["title"])
    st.caption(l3["caption"])
    st.markdown("---")

    with st.form("ship_prep_form"):
        col1, col2 = st.columns(2)
        with col1:
            zip_code = st.text_input(l3["zip_label"], "90210")
            current_plan = st.text_input(l3["plan_label"], l3["plan_placeholder"])
        with col2:
            monthly_cost = st.text_input(l3["cost_label"], "0")
            primary_concern = st.text_input(l3["concern_label"], l3["concern_default"])

        meds = st.text_area(l3["meds_label"], l3["meds_default"])
        submitted = st.form_submit_button(l3["btn_label"])

    if submitted:
        st.markdown("---")
        st.markdown(
            f"""
            <div class="card-box" style="border: 2px solid #2563eb; background-color: #ffffff;">
                <h3 style="text-align:center; color:#1e3a8a; margin-top:0;">🩺 Medicare Compass - SHIP Counseling Summary</h3>
                <hr>
                <p><b>📍 ZIP Code:</b> {zip_code} | <b>Current Plan:</b> {current_plan} (${monthly_cost}/mo)</p>
                <p><b>❓ Primary Concern:</b> {primary_concern}</p>
                <p><b>💊 Medication List:</b><br>{meds.replace(chr(10), '<br>')}</p>
                <hr>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom:0;">{l3['footer_note']}</p>
            </div>
            """, unsafe_allow_html=True
        )


# --------------------------------------------------
# 🆕 模組 4: 📅 SHIP 預約行事曆提醒 (Calendar ICS)
# --------------------------------------------------
elif app_mode == "CALENDAR_ICS":
    l4 = m4_labels.get(current_lang, m4_labels["English"])
    st.markdown(l4["title"])
    st.caption(l4["caption"])
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        appt_date = st.date_input(l4["date_label"], datetime.date.today() + timedelta(days=14))
    with col2:
        appt_time = st.time_input(l4["time_label"], datetime.time(10, 0))

    location = st.text_input(l4["location_label"], l4["location_placeholder"])

    if st.button(l4["btn_generate"], type="primary"):
        dt_start = datetime.datetime.combine(appt_date, appt_time)
        dt_end = dt_start + timedelta(hours=1)

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Medicare Compass//SHIP Appointment//EN
BEGIN:VEVENT
SUMMARY:🩺 SHIP Medicare Official Counseling
DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}
DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}
LOCATION:{location}
DESCRIPTION:📌 Checklist for Counseling:\\n1. Bring your 1-Page Summary from Medicare Compass App.\\n2. Bring all current prescription drug bottles.\\n3. Bring your Medicare Red, White & Blue card.
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:SHIP Counseling tomorrow! Remember to bring your 1-Page Summary and drug bottles.
END:VALARM
END:VEVENT
END:VCALENDAR"""

        st.download_button(
            label=l4["btn_download"],
            data=ics_content,
            file_name="ship_appointment.ics",
            mime="text/calendar",
            use_container_width=True,
        )
        st.success(l4["success_msg"])

# --------------------------------------------------
# 頁面定位控制
# --------------------------------------------------
if app_mode == "MAIN_AI":

    # ① AI 回答完成 → 回到剛剛的提問
    anchor_id = st.session_state.pop("_scroll_to_message", None)

    if anchor_id:
        scroll_to_message(anchor_id)

    # ② 第一次開啟網頁 → 顯示最上方 Medicare Compass
    elif not st.session_state.get("_initial_top_done", False):
        scroll_to_medicare_top()
        st.session_state["_initial_top_done"] = True