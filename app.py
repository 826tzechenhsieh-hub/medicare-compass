import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import urllib.parse
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 強制頁面保持在頂端
components.html(
    """
    <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
    """,
    height=0,
)

# Typography & Styles
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
        html, body, [class*="css"] {
            font-size: 19px !important;
        }
        .main {
            overflow-anchor: none !important;
        }
        [data-testid="stChatMessageContainer"] {
            scroll-margin-top: 0px !important;
        }
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

# 2. Get API Keys
primary_key = st.secrets.get("GEMINI_API_KEY", None)
secondary_key = st.secrets.get("GEMINI_API_KEY_SECONDARY", None)

def generate_clean_response(user_input, target_lang="English", img_data=None):
    keys_to_try = [k for k in [primary_key, secondary_key] if k]
    if not keys_to_try:
        raise ValueError("NO_API_KEY")

    last_exception = None

    # 對齊 AI 語言指令
    lang_instruction_map = {
        "English": "Respond purely in English.",
        "Español": "Respond purely in Spanish (Español).",
        "繁體中文": "請務必完全使用『繁體中文 (Traditional Chinese, zh-TW)』回答，嚴禁使用簡體字。",
        "簡體中文": "请务必完全使用『简体中文 (Simplified Chinese, zh-CN)』回答，严禁使用繁体字。",
        "한국어": "Respond purely in Korean (한국어)."
    }
    lang_rule = lang_instruction_map.get(target_lang, "Respond in the target language.")

    for current_key in keys_to_try:
        try:
            clean_key = str(current_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            
            valid_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        valid_models.append(m.name)
            except Exception:
                pass

            if not valid_models:
                valid_models = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-2.5-flash"]

            for m_name in valid_models:
                try:
                    model = genai.GenerativeModel(m_name)
                    
                    system_context = [
                        {"role": "user", "parts": [f"""You are Medicare Compass, a warm, concise Medicare advisor.
Speak directly to the senior. Never output thinking process, goals, or constraints.
LANGUAGE REQUIREMENT: {lang_rule}

[CRITICAL IEP CALCULATION RULES]
1. Initial Enrollment Period (IEP) ALWAYS lasts for exactly 7 MONTHS (3 months BEFORE birth month, birth month, and 3 months AFTER birth month when turning 65).
2. Calculate turning 65 year correctly: Birth Year + 65. (e.g. Born Aug 1961 -> Turns 65 in Aug 2026 -> IEP: May 1, 2026 to Nov 30, 2026).
3. If birth year provided is in the future or recent years (e.g. 2026), kindly ask user to clarify their actual birth year (e.g. 1961).

[STRICT STEP 1 TRANSITION GATE]
After calculating the IEP window, STOP IMMEDIATELY and ask ONLY if they have questions about their timing before Step 2.
DO NOT jump into Step 2 plan comparison until user confirms!"""]},
                        {"role": "model", "parts": ["Understood. I will strictly follow language requirements, calculate IEP as a 7-month window, and stop for confirmation before Step 2."]}
                    ]
                    
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        system_context.append({"role": role, "parts": [m["content"]]})
                        
                    chat = model.start_chat(history=system_context)
                    
                    if img_data:
                        response = model.generate_content([user_input, img_data], stream=True)
                    else:
                        response = chat.send_message(user_input, stream=True)
                    return response
                except Exception as inner_e:
                    last_exception = inner_e
                    continue
        except Exception as outer_e:
            last_exception = outer_e
            continue

    if last_exception:
        raise last_exception

# -------------------------------------------------------------------
# 3. Sidebar Setup
# -------------------------------------------------------------------
with st.sidebar:
    user_lang = st.session_state.get("selected_language", "English")

    if user_lang in ["English", "Español", "한국어"]:
        st.markdown("# 🧭 Medicare Compass™")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    elif user_lang == "簡體中文":
        st.markdown("# 🧭 Medicare Compass™ 医保指南针")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **本工具宗旨**：专为即将满 65 岁长者与退休家庭设计！陪伴您分三步骤轻松了解申办流程、避开终身迟办罚款。")
    else:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款。")

    st.markdown("---")

    st.header("🌐 Language / 語言設定")
    current_lang = st.radio(
        "Select Language / 選擇語言:",
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        index=0,
        key="selected_language"
    )

    st.markdown("---")

    st.markdown("⚠️ **Official Warning**: Medicare will NEVER call to ask for your Social Security Number.")
    if not primary_key:
        primary_key = st.text_input("Gemini API Key:", type="password")

    st.markdown("---")

    upload_label = "📎 Upload Document / Photo (Optional):" if current_lang in ["English", "Español", "한국어"] else ("📎 上传信件或保单照片（选填）：" if current_lang == "簡體中文" else "📎 上傳信件或保單照片（選填）：")
    uploaded_file = st.file_uploader(upload_label, type=["png", "jpg", "jpeg", "pdf"])
    img_data = None
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            st.success("File attached successfully!")
        except Exception:
            st.warning("File uploaded.")

    st.markdown("---")

    if current_lang in ["English", "Español", "한국어"]:
        st.caption("""
🔒 **Privacy Commitment & Zero Retention**:
We DO NOT save or store any of your personal inputs or logs. All data is permanently cleared immediately upon closing your browser or clicking Reset.

ℹ️ **Disclaimer & Notice**:
Information provided is strictly for educational guidance. Regulations change continuously; users MUST always double-check and confirm final details with [Medicare.gov](https://www.medicare.gov) or SSA.

🏛️ **Non-Governmental Entity Notice**:
Medicare Compass™ is an independent educational tool, not affiliated with the US Government, CMS, or SSA.
        """)
    elif current_lang == "簡體中文":
        st.caption("""
🔒 **隐私承诺与零数据留存**：
本平台**完全不储存、不保留**您的任何个人输入资料、上传文件或对话纪录。视窗关闭或重置后即刻永久清除。

ℹ️ **免责声明与资讯时效提醒**：
本工具资讯仅供教育评估与导航参考。医保政策每年动态调整，使用者于决策前，**务必至官方网站 [Medicare.gov](https://www.medicare.gov) 或社会安全局 (SSA) 进行最终核对**。

🏛️ **非官方独立声明**：
Medicare Compass™ 为独立辅助导航工具，不代表美国政府、联邦医疗照顾局 (CMS) 或社会安全局 (SSA) 官方机构。
        """)
    else:
        st.caption("""
🔒 **隱私承諾與零數據留存**：
本平台與應用程式**完全不儲存、不安裝且不保留**您的任何個人輸入資料、上傳的文件照片或對話紀錄。所有數據僅供當次即時運算，視窗關閉或重置後即刻永久清除。

ℹ️ **免責聲明與資訊時效提醒**：
本工具資訊僅供教育評估與導航參考。我們雖致力於提供最新資訊，但醫保政策、保費與條款每年且動態調整，無法保證毫秒級實時同步。使用者於決策前，**務必至官方網站 [Medicare.gov](https://www.medicare.gov) 或社會安全局 (SSA) 進行最終核對與確認**。

🏛️ **非官方獨立聲明**：
Medicare Compass™（powered by Care Compass™）為獨立輔助導航工具，不代表美國政府、聯邦醫療照顧局 (CMS) 或社會安全局 (SSA) 官方機構。
        """)

    st.markdown("---")

    summary_btn_label = "📋 Generate / Update Summary" if current_lang in ["English", "Español", "한국어"] else ("📋 生成 / 更新咨询总结" if current_lang == "簡體中文" else "📋 生成 / 更新諮詢總結")
    if st.button(summary_btn_label, use_container_width=True, type="primary"):
        st.session_state.show_summary = True

    reset_label = "🔄 Reset Conversation" if current_lang in ["English", "Español", "한국어"] else ("🔄 重新开始咨询" if current_lang == "簡體中文" else "🔄 重新開始諮詢")
    if st.button(reset_label, use_container_width=True):
        st.session_state.messages = []
        st.session_state.show_summary = False
        st.rerun()

# -------------------------------------------------------------------
# 4. Main Header & 1-Minute Medicare Map
# -------------------------------------------------------------------
top_container = st.container()

with top_container:
    if current_lang in ["English", "Español", "한국어"]:
        st.markdown("# 🧭 Medicare Compass™")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    elif current_lang == "簡體中文":
        st.markdown("# 🧭 Medicare Compass™ 医保指南针")
        st.info("📢 **本工具宗旨**：专为即将满 65 岁长者与退休家庭设计！陪伴您分三步骤轻松了解申办流程、避开终身迟办罚款。")
    else:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款。")

    st.markdown("---")

    if current_lang in ["English", "Español", "한국어"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ Step 1: When")
            st.caption("IEP Timing, Date of Birth & State.")
        with col2:
            st.markdown("### 2️⃣ Step 2: What")
            st.caption("Needs, Coverage & Plan Comparison.")
        with col3:
            st.markdown("### 3️⃣ Step 3: How")
            st.caption("Step-by-step Application & Payment.")
    elif current_lang == "簡體中文":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ 第一步：WHEN 参保时机")
            st.caption("出生年月、居住州与 IEP 黄金期限。")
        with col2:
            st.markdown("### 2️⃣ 第二步：WHAT 方案比对")
            st.caption("医疗需求、两大路径与最适合方案。")
        with col3:
            st.markdown("### 3️⃣ 第三步：HOW 申办执行")
            st.caption("逐步申请流程与保费扣款设定。")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("### 1️⃣ 第一步：WHEN 參保時機")
            st.caption("出生年月、居住州與 IEP 黃金期限。")
        with col2:
            st.markdown("### 2️⃣ 第二步：WHAT 方案比對")
            st.caption("醫療需求、兩大路徑與最適合方案。")
        with col3:
            st.markdown("### 3️⃣ 第三步：HOW 申辦執行")
            st.caption("逐步申請流程與保費扣款設定。")

    st.markdown("---")

    with st.expander("🗺️ **1-Minute Medicare Map (一分鐘醫保地圖對照)**", expanded=True):
        if current_lang == "English":
            st.markdown("""
* **Original Medicare (Government)**: Part A (Hospital) + Part B (Medical - 80% coverage, 20% gap).
* **Part C (Medicare Advantage)**: Private all-in-one plans (A + B + usually D).
* **Part D (Prescription Drugs)**: Standalone drug coverage.
* **Medigap (Supplement)**: Private plans to cover Part B's 20% gap.
            """)
        elif current_lang == "簡體中文":
            st.markdown("""
* **Original Medicare (传统红蓝卡)**：Part A (住院) + Part B (门诊，政府给付 80%，自付 20% 无上限)。
* **Part C (Medicare Advantage 优惠套餐)**：私人保险包办 (A + B + 通常含 D)。
* **Part D (处方药专案)**：独立药物保险。
* **Medigap (补充保险)**：填补 Part B 那 20% 自付额缺口。
            """)
        else:
            st.markdown("""
* **Original Medicare (傳統紅藍卡)**：Part A (住院) + Part B (門診，政府給付 80%，自付 20% 無上限)。
* **Part C (Medicare Advantage 優惠套餐)**：私人保險包辦 (A + B + 通常含 D)。
* **Part D (處方藥專案)**：獨立藥物保險。
* **Medigap (補充保險)**：填補 Part B 那 20% 自付額缺口。
            """)

    st.markdown("---")

# -------------------------------------------------------------------
# 5. Message History Setup
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

quick_prompt = None
if len(st.session_state.messages) == 0:
    st.caption("💡 " + ("Quick start options:" if current_lang in ["English", "Español", "한국어"] else ("您也可以直接点选以下身份快速开始：" if current_lang == "簡體中文" else "您也可以直接點選以下身分快速開始：")))
    col_start1, col_start2 = st.columns(2)
    with col_start1:
        btn1_txt = "👴 " + ("I'm applying for myself" if current_lang == "English" else ("我是长者本人（开始 Step 1 导览）" if current_lang == "簡體中文" else "我是長者本人（開始 Step 1 導覽）"))
        if st.button(btn1_txt):
            quick_prompt = "Hello! I am applying for myself and would like to start Step 1: When. Please calculate my enrollment deadlines." if current_lang == "English" else ("您好！我是长者本人，准备开始 Step 1，请帮我计算申办期限！" if current_lang == "簡體中文" else "您好！我是長者本人，準備開始 Step 1，請幫我計算申辦期限！")
    with col_start2:
        btn2_txt = "👨‍👩‍👧 " + ("I'm helping my parents" if current_lang == "English" else ("我是帮父母查询的子女（开始 Step 1）" if current_lang == "簡體中文" else "我是幫父母查詢的子女（開始 Step 1）"))
        if st.button(btn2_txt):
            quick_prompt = "Hello! I am helping my parents start Step 1: When. What information do you need?" if current_lang == "English" else ("您好！我是帮长辈查询的子女，请引导我们开始 Step 1！" if current_lang == "簡體中文" else "您好！我是幫長輩查詢的子女，請引導我們開始 Step 1！")

has_user_replied = len(st.session_state.messages) > 0
input_placeholder = "🎙️ Type your birth month/year and state here..." if not has_user_replied else "🎙️ Speak or type your reply here..."
input_prompt = st.chat_input(input_placeholder)

prompt = quick_prompt if quick_prompt else input_prompt

# -------------------------------------------------------------------
# 6. Response Execution
# -------------------------------------------------------------------
if prompt or uploaded_file:
    user_text = prompt if prompt else "Please review this uploaded document."
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    def stream_text_generator(response_stream):
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    with st.chat_message("assistant"):
        with st.spinner("Medicare Compass is analyzing..."):
            try:
                response = generate_clean_response(user_text, target_lang=current_lang, img_data=img_data)
                full_text = st.write_stream(stream_text_generator(response))
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                st.rerun()
            except Exception as e:
                st.error(f"Notice: {e}")

# -------------------------------------------------------------------
# 7. Consultation Summary Section
# -------------------------------------------------------------------
if st.session_state.show_summary and len(st.session_state.messages) >= 2:
    st.markdown("---")
    st.header("📋 Consultation Summary & Sharing")

    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    for m in st.session_state.messages:
        role_title = "Compass Advisor" if m["role"] in ["assistant", "model"] else "User"
        full_log_text += f"[{role_title}]:\n{m['content']}\n\n" + "-"*40 + "\n\n"

    short_summary_text = "【Medicare Compass - Summary / 重点摘要】\n\n"
    user_msgs = [m['content'] for m in st.session_state.messages if m.get('role') == 'user']
    ai_msgs = [m['content'] for m in st.session_state.messages if m.get('role') in ['assistant', 'model']]

    if user_msgs:
        short_summary_text += "📌 KEY USER INPUTS:\n"
        for u in user_msgs:
            short_summary_text += f"- {u}\n"
        short_summary_text += "\n"

    if ai_msgs:
        short_summary_text += f"💡 LATEST ADVICE:\n{ai_msgs[-1]}\n"

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs(["⚡ 1-Page Summary (1页精简版)", "📄 Full Log (完整纪录版)"])

    with tab1:
        st.text_area("Preview:", value=short_summary_text, height=200, key="summary_preview_area")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download 1-Page Summary (TXT)", data=short_summary_text, file_name="medicare_summary.txt", use_container_width=True)
        with col2:
            st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="width:100%; height:42px; border-radius:8px; background-color:#0066cc; color:white; border:none; cursor:pointer; font-size:16px;">✉️ Send to My Email</button></a>', unsafe_allow_html=True)

    with tab2:
        st.text_area("Full Conversation Log:", value=full_log_text, height=260, key="full_log_area")
        st.download_button("📥 Download Full Log (TXT)", data=full_log_text, file_name="medicare_full_log.txt", use_container_width=True)

# Auto-scroll control
st.markdown("""
    <script>
        function scrollToTop() {
            var mainContainer = window.parent.document.querySelector(".main");
            if (mainContainer) mainContainer.scrollTop = 0;
            window.parent.scrollTo(0, 0);
        }
        scrollToTop();
        setTimeout(scrollToTop, 200);
    </script>
""", unsafe_allow_html=True)
