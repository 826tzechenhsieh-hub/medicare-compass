import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import urllib.parse
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 強制頁面保持在頂端，防止 Streamlit 自動向下捲動
components.html(
    """
    <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
    """,
    height=0,
)
# Senior-friendly typography & Smooth auto-scroll prevention
st.markdown("""
    <style>
        /* 清除 Streamlit 頂部預設巨大空白 */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        html, body, [class*="css"] {
            font-size: 19px !important;
        }
        /* 徹底禁止 Streamlit 自動往下捲動，強制停留在頂部 */
        .main {
            overflow-anchor: none !important;
        }
        [data-testid="stChatMessageContainer"] {
            scroll-margin-top: 0px !important;
        }
        /* 保留您原本的 Chat/Button/Input 字型大小設定 */
        .stChatMessage {
            font-size: 20px !important;
            line-height: 1.6 !important;
        }
        .stButton>button {
            font-size: 18px !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
        }
        .stChatInput input {
            font-size: 19px !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Get Dual API Keys for Automatic Failover / Rotation
primary_key = st.secrets.get("GEMINI_API_KEY", None)
secondary_key = st.secrets.get("GEMINI_API_KEY_SECONDARY", None)

# Helper function to try generating content with dual-key failover
def generate_response_with_fallback(prompt_input, image_data=None, system_instruction=""):
    keys_to_try = [k for k in [primary_key, secondary_key] if k]
    
    if not keys_to_try:
        raise ValueError("NO_API_KEY")

    last_exception = None
    
    for current_key in keys_to_try:
        try:
            clean_key = str(current_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            
            # Smart Model Detection (Filters out unsupported prefixes)
            working_model_name = "gemini-2.0-flash"
            try:
                for m in genai.list_models():
                    name_clean = m.name.replace("models/", "")
                    if 'generateContent' in m.supported_generation_methods and "flash" in name_clean:
                        working_model_name = name_clean
                        break
            except Exception:
                pass

            model = genai.GenerativeModel(working_model_name, system_instruction=system_instruction)
            
            if image_data:
                response = model.generate_content([prompt_input, image_data], stream=True)
            else:
                chat = model.start_chat(history=[
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ])
                response = chat.send_message(prompt_input, stream=True)
                
            return response # Successfully obtained response stream
        except Exception as e:
            last_exception = e
            # If 429 or quota limit hit, loop automatically tries the next key in list!
            continue
            
    raise last_exception

# -------------------------------------------------------------------
# 3. Sidebar Setup
# -------------------------------------------------------------------
with st.sidebar:
    # 預先獲取當前語言 setting (避免 NameError)
    user_lang = st.session_state.get("selected_language", "English")

    # 1. 置頂品牌大標題 (方案 A) 與宗旨 Banner
    if user_lang in ["English", "Español", "한국어"]:
        st.markdown("# 🧭 Medicare Compass™")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    else:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款。")

    st.markdown("---")

    # 2. 語言選擇器
    st.header("🌐 Language / 語言設定")
    current_lang = st.radio(
        "Select Language / 選擇語言:",
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        index=0,
        key="selected_language"
    )

    st.markdown("---")

    # 3. 安全警示與 API 密碼
    st.markdown("⚠️ **Official Warning**: Medicare will NEVER call to ask for your Social Security Number.")
    
    if not primary_key:
        primary_key = st.text_input("Gemini API Key:", type="password")

    st.markdown("---")

    # 4. 隱私承諾、免責聲明與非官方聲明
    if current_lang in ["English", "Español", "한국어"]:
        st.caption("""
🔒 **Data Privacy**: No personal input, uploaded documents, or chat histories are saved or stored. All data is permanently cleared upon session reset or browser closure.

ℹ️ **Disclaimer**: Information provided is for educational and guidance reference only. Policy rates and terms change over time. Please verify final plan details with [Medicare.gov](https://www.medicare.gov).

🏛️ **Non-Governmental**: Medicare Compass™ (powered by Care Compass™) is an independent educational tool and is not affiliated with, endorsed by, or connected to the US Government or Social Security Administration.
        """)
    else:
        st.caption("""
🔒 **隱私承諾**：本工具**完全不儲存**任何您的個人資料、對話紀錄或上傳文件，視窗關閉或重置後即刻永久清除。

ℹ️ **免責聲明**：資訊僅供教育與評估參考。醫保政策與費用每年調整，最終細節請務必至 [Medicare.gov](https://www.medicare.gov) 官方核對。

🏛️ **非官方聲明**：Medicare Compass™（powered by Care Compass™）為獨立輔助導航應用，不代表美國政府或社會安全局 (SSA) 官方機構。
        """)

    st.markdown("---")

    # 5. 最底部：重置對話按鈕
    reset_label = "🔄 Reset Conversation" if current_lang in ["English", "Español", "한국어"] else "🔄 重新開始諮詢"
    if st.button(reset_label, use_container_width=True):
        st.session_state.messages = []
        st.rerun()
# -------------------------------------------------------------------
# 4. Main Header & Announcement Banner (Pinned Top Container)
# -------------------------------------------------------------------
top_container = st.container()

with top_container:
    if current_lang in ["English", "Español", "한국어"]:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    else:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款。")

    st.markdown("---")

    # 5. 導航三步驟小卡片 (3 Steps Navigation)
    if current_lang in ["English", "Español", "한국어"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ Step 1: When")
            st.caption("Initial Enrollment Period (IEP) timing & key deadlines.")
        with col2:
            st.markdown("### 2️⃣ Step 2: What")
            st.caption("Compare Part A, B, C (Advantage), and Part D.")
        with col3:
            st.markdown("### 3️⃣ Step 3: How")
            st.caption("Avoid lifetime penalties & apply step-by-step.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ 第一步：參保時機")
            st.caption("掌握滿 65 歲前後 7 個月的黃金申辦期 (IEP)。")
        with col2:
            st.markdown("### 2️⃣ 第二步：方案比對")
            st.caption("釐清 Part A、B、C (紅藍卡/優質卡) 與 D 藥費保障。")
        with col3:
            st.markdown("### 3️⃣ 第三步：避罰申辦")
            st.caption("了解遲辦罰款規則與一步步官方申辦途徑。")

    st.markdown("---")
# 5. System Instructions (AI 提示詞大腦 - 完全保留)
SYSTEM_INSTRUCTION = """
You are a warm, highly patient, and empathetic expert Medicare guide named "Medicare Compass".
Your mission is to guide first-time applicants, turning 65 seniors, and families through US Medicare smoothly.

【Core Principles & Conceptual Map】
1. Always ground the user first: Ensure they understand the basic 2 pathways if asked:
   - Pathway 1: Original Medicare (Part A Hospital + Part B Medical) + Part D (Drugs) + Medigap (Supplement)
   - Pathway 2: Medicare Advantage (Part C All-in-one private plan)
2. Demystify early: Original Medicare Part B only covers 80% with NO out-of-pocket maximum limit.
3. Concise Responses: Keep answers short, structured, and bullet-pointed (2-3 brief paragraphs max). Use bold keywords.
4. Phase Transition Check: Always end Phase 1/2 with a friendly check-in on whether they want to proceed to the next step.
5. Language Matching: Respond fluently in the selected language.
---
"""


# 6. Greeting Initialization (Cleaned Welcome Messages)
if current_lang == "English":
    welcome_msg = """Hello and welcome! Before we dive in, here is your **1-Minute Medicare Map**:

* 🔴 **Original Medicare (Government)**: 
  * **Part A (Hospital)**: Mostly free if you worked 10 years.
  * **Part B (Medical)**: Monthly premium required, covers **80%** (20% gap!).
* 🟡 **Part C (Medicare Advantage)**: Private all-in-one plans (A + B + usually D).
* 🔵 **Part D (Prescription Drugs)**: Standalone drug coverage.
* 🟣 **Medigap (Supplement)**: Private plans to cover the **20% gap** of Part B.

---
To begin **Step 1: Plan Exploration**, please tell me: **Which state do you live in, and what is your birth month and year?**"""

elif current_lang in ["繁體中文", "简体中文"]:
    welcome_msg = """您好！在開始前，先為您奉上 **1分鐘 Medicare 快速地圖**：

* 🔴 **Original Medicare (傳統紅藍卡 / 政府發行)**：
  * **Part A (住院保險)**：工作滿 10 年者多數免費。
  * **Part B (門診保險)**：需繳月保費，政府給付 **80%**（**自付 20% 無上限！**）。
* 🟡 **Part C (Advantage 優惠套餐)**：私人保險公司包辦 (A + B + 通常含 D)。
* 🔵 **Part D (處方藥專案)**：單純補充藥物給付。
* 🟣 **Medigap (補充保險)**：填補 Part B 那 **20% 自付額無底洞**。

---
為了幫您展開 **第一步：方案探索**，請告訴我：**您目前居住在哪一個州？以及您的出生年月是什麼時候呢？**"""

elif current_lang == "Español":
    welcome_msg = """¡Hola y bienvenido! Aquí está su **Mapa de Medicare de 1 Minuto**:

* 🔴 **Original Medicare (Gobierno)**:
  * **Parte A (Hospital)**: Mayormente gratuita si trabajó 10 años.
  * **Parte B (Médica)**: Requiere prima mensual, cubre el **80%** (¡20% de brecha!).
* 🟡 **Parte C (Medicare Advantage)**: Planes privados todo en uno (A + B + D).
* 🔵 **Parte D (Medicamentos)**: Cobertura de medicamentos.
* 🟣 **Medigap (Suplemento)**: Planes privados para cubrir la **brecha del 20%** de la Parte B.

---
Para comenzar el **Paso 1: Exploración de Planes**, por favor dígame: **¿En qué estado vive y cuál es su mes y año de nacimiento?**"""

elif current_lang == "한국어":
    welcome_msg = """안녕하세요! **1분 메디케어 한눈에 보기**:

* 🔴 **Original Medicare (정부 메디케어)**:
  * **Part A (병원)**: 10년 이상 일한 경우 대부분 무료.
  * **Part B (의료)**: 월 보험료 발생, **80%** 보장 (20% 본인 부담!).
* 🟡 **Part C (Medicare Advantage)**: 민간 통합 플랜 (A + B + D).
* 🔵 **Part D (처방약)**: 약품 보장.
* 🟣 **Medigap (보충 보험)**: Part B의 **20% 본인 부담금**을 메워주는 민간 보험.

---
**1단계: 플랜 탐색**을 시작하려면: **현재 거주하는 주(State)와 출생 월/년을 알려주세요!**"""

else:
    welcome_msg = "Hello! Which state do you live in, and what is your birth month and year?"

# 7. Display Chat History
if "messages" not in st.session_state:
    if "welcome_msg" not in locals(): welcome_msg = "# 🧭 Medicare Compass"
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Universal Quick Start Options
if len(st.session_state.messages) == 1:
    st.caption("💡 " + ("Quick start options:" if current_lang in ["English", "Español", "한국어"] else "您也可以直接點選以下身分快速開始："))
    col_start1, col_start2 = st.columns(2)
    with col_start1:
        if st.button("👴 " + ("I'm applying for myself" if current_lang == "English" else "我是長者本人（開始 3 步驟導覽）")):
            quick_prompt = "Hello! I am applying for myself and would like to start Step 1: Plan Exploration. Please guide me on what details you need!" if current_lang == "English" else "您好！我是長者本人，準備開始了解 Medicare 申辦流程。請引導我展開第一步！"
    with col_start2:
        if st.button("👨‍👩‍👧 " + ("I'm helping my parents" if current_lang == "English" else "我是幫父母查詢的子女（查看快速對照清單）")):
            quick_prompt = "Hello! I am helping my parents explore Medicare options. Please provide a clear breakdown of where we should begin." if current_lang == "English" else "您好！我是幫家中長輩查詢 Medicare 的子女，請告訴我幫父母申辦時最需要注意的第一步！"

# Quick Cards during conversation
if len(st.session_state.messages) > 1:
    st.caption("💡 " + ("Quick Questions (Click to ask):" if current_lang in ["English", "Español", "한국어"] else "點擊下方小卡直接發問："))
    col_pill1, col_pill2 = st.columns(2)
    with col_pill1:
        if st.button("💡 " + ("Tell me about Part B costs" if current_lang == "English" else "了解 Part B 保費細節")):
            quick_prompt = "Please tell me about Part B premium and deductible." if current_lang == "English" else "請詳細告訴我 Part B 的保費與 Deductible 是多少？"
    with col_pill2:
        if st.button("💡 " + ("How to avoid penalties?" if current_lang == "English" else "如何完全避開遲辦罰款？")):
            quick_prompt = "How can I avoid all Medicare late penalties?" if current_lang == "English" else "請告訴我最關鍵的黃金申辦期限，我該如何確保完全不被罰款？"

# Input Bar
has_user_replied = len(st.session_state.messages) > 1

if current_lang == "English":
    input_placeholder = "🎙️ Speak or type your question here..." if has_user_replied else "🎙️ Speak or type your state/birthdate here..."
elif current_lang == "繁體中文":
    input_placeholder = "🎙️ 點擊麥克風用語音講，或直接打字發問..." if has_user_replied else "🎙️ 點擊麥克風說出您的居住州與出生年月，或打字回覆..."
else:
    input_placeholder = "🎙️ Speak or type your reply here..."

# 先給 quick_prompt 一個安全預設值 (避免 NameError)
if 'quick_prompt' not in locals():
    quick_prompt = None

if 'uploaded_file' not in locals():
    uploaded_file = None
input_prompt = st.chat_input(input_placeholder)
prompt = quick_prompt if quick_prompt else input_prompt

# 8. Execution Logic with Dual-Key Fallback & Warm Error Interception
if prompt or uploaded_file:
    if not primary_key:
        st.error("Please set API Key in sidebar.")
    else:
        user_content = prompt if prompt else "Please analyze this uploaded document."
        st.session_state.messages.append({"role": "user", "content": user_content})
        with st.chat_message("user"):
            st.markdown(user_content)

        def stream_text_generator(response_stream):
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        with st.chat_message("assistant"):
            spinner_text = "Medicare Compass is analyzing..."
            with st.spinner(spinner_text):
                try:
                    response = generate_response_with_fallback(user_content, img_data, SYSTEM_INSTRUCTION)
                    full_text = st.write_stream(stream_text_generator(response))
                    st.session_state.messages.append({"role": "assistant", "content": full_text})
                    st.rerun()
                except Exception as e:
                    err_msg = str(e)
                    # Warm, Friendly Interception for 429 Quota Exceeded Errors
                    if "429" in err_msg or "quota" in err_msg.lower():
                        warm_card = "☕ **Medicare Compass 正在為您整理資料中...**\n\n系統目前整理流量較大，請喝口水稍微等待 10 秒鐘後再發問，我們馬上為您解答喔！" if current_lang == "繁體中文" else "☕ **Medicare Compass is organizing your information...**\n\nSystem traffic is currently high. Please take a quick 10-second break and ask again. We will be right back with you!"
                        st.info(warm_card)
                    else:
                        st.error(f"Notice: {e}")

# 9. Summary Section (Only shows after 3+ turns)
if len(st.session_state.messages) >= 3:
    st.markdown("---")
    st.header("📋 " + ("Consultation Summary & Sharing" if current_lang in ["English", "Español", "한국어"] else "諮詢紀錄打包與分享"))

    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    for m in st.session_state.messages:
        role_title = "Compass Advisor" if m["role"] == "assistant" else "User"
        full_log_text += f"[{role_title}]:\n{m['content']}\n\n------------------------\n\n"

    short_summary_text = "【Medicare Compass - 1-Page Key Takeaways / 1頁重點摘要】\n\n"
    assistant_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "assistant"]
    if len(assistant_msgs) > 1:
        short_summary_text += "💡 KEY RECOMMENDATIONS & TIMELINE:\n\n" + assistant_msgs[-1]
    else:
        short_summary_text += "💡 INITIAL ADVICE:\n\n" + assistant_msgs[0]

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs(["⚡ 1-Page Summary (1頁精簡版)", "📄 Full Log (完整紀錄版)"])
    
    with tab1:
        st.caption("Great for sending to family via Email or WeChat")
        st.text_area("Preview:", value=short_summary_text, height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download 1-Page Summary (TXT)",
                data=short_summary_text,
                file_name="Medicare_1Page_Summary.txt",
                mime="text/plain"
            )
        with col2:
            st.markdown(f'''
                <a href="{mailto_url}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #0288D1;
                        color: white;
                        border: none;
                        padding: 7px 15px;
                        font-size: 14px;
                        border-radius: 5px;
                        cursor: pointer;
                        width: 100%;
                    ">
                        📧 Send to My Email
                    </button>
                </a>
            ''', unsafe_allow_html=True)

    with tab2:
        st.caption("Complete Q&A History")
        st.download_button(
            label="📥 Download Full Log (TXT)",
            data=full_log_text,
            file_name="Medicare_Full_Consultation.txt",
            mime="text/plain"
        )
# 10. Force Scroll to Top on Initial Load / Reboot (Universal Fix)
st.markdown("""
    <script>
        function scrollToTop() {
            // 1. 針對 Streamlit 的核心滾動容器
            var mainContainer = window.parent.document.querySelector(".main");
            if (mainContainer) mainContainer.scrollTop = 0;
            
            var blockContainer = window.parent.document.querySelector(".block-container");
            if (blockContainer) blockContainer.scrollTop = 0;

            // 2. 針對全域瀏覽器視窗
            window.parent.scrollTo(0, 0);
            window.scrollTo(0, 0);
        }
        
        // 立即執行一次
        scrollToTop();
        
        // 延遲 200 毫秒等 Streamlit DOM 渲染完成後再執行一次（雙重保險）
        setTimeout(scrollToTop, 200);
    </script>
""", unsafe_allow_html=True)
