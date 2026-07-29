import streamlit as st
import google.generativeai as genai
import urllib.parse
from PIL import Image

# 1. 頁面標題與配置設定
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 🔠 1. 長者友善大字體與高對比 CSS 樣式
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 19px !important;
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

# 2. 抓取 API Key
api_key = st.secrets.get("GEMINI_API_KEY", None)

# 3. 側邊欄（Sidebar）：清爽化，只保留 3-Step 核心問題與 Reset / 上傳
with st.sidebar:
    # 🔄 Reset 按鈕
    if st.button("🔄 " + ("Reset Conversation" if "English" in st.session_state.get("selected_language", "English") else "重新開始諮詢 (Reset)"), use_container_width=True):
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

    st.markdown("---")
    st.header("🌐 Language / 語言設定")
    
    current_lang = st.radio(
        "Select Language / 選擇語言:", 
        ["English", "Español", "繁體中文", "简体中文", "한국어"], 
        index=0,
        key="selected_language"
    )
    
    # 切換語言時自動重置歷史對話
    if "previous_language" not in st.session_state:
        st.session_state.previous_language = current_lang
    elif st.session_state.previous_language != current_lang:
        st.session_state.previous_language = current_lang
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

    st.markdown("---")
    
    # 📍 3-Step 階段精華問題（簡化左側，不放混淆按鈕）
    quick_prompt = None
    
    if current_lang == "English":
        st.header("🗺️ 3-Step Quick Questions")
        
        st.subheader("📍 Step 1: Plan Exploration")
        if st.button("❓ What is Medigap & why need it?"):
            quick_prompt = "Can you explain what Medigap is in simple terms and why Original Medicare alone isn't enough?"
        if st.button("🩺 Are my doctors covered?"):
            quick_prompt = "How do I check if my current doctors and prescriptions are covered under Part D or Advantage?"

        st.subheader("📍 Step 2: Timeline & Penalties")
        if st.button("💼 Working past 65 & Part B?"):
            quick_prompt = "I'm turning 65 but still working with employer insurance. Do I need Part B now, and will I face penalties?"
        if st.button("📅 What is my IEP timeline?"):
            quick_prompt = "When is my Initial Enrollment Period (IEP), and what happens if I miss it?"

        st.subheader("📍 Step 3: Premiums & Financials")
        if st.button("💵 Part B Cost & Payment?"):
            quick_prompt = "How much is Part B premium and deductible, and how do I set up payments?"
        if st.button("📝 What is IRMAA surcharge?"):
            quick_prompt = "What is the IRMAA Medicare surcharge, and how can I appeal it if my income dropped after retirement?"

    elif current_lang == "繁體中文":
        st.header("🗺️ 申辦三步驟核心問題")
        
        st.subheader("📍 第一步：方案探索")
        if st.button("❓ 什麼是 Medigap？為什麼只買紅藍卡不夠？"):
            quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
        if st.button("🩺 常看的醫生與慢性病藥物有給付嗎？"):
            quick_prompt = "如何確認我平時看診的醫生以及在吃的慢性病藥物有沒有在 Medicare 的給付範圍內？"

        st.subheader("📍 第二步：時間軸與避開罰款")
        if st.button("💼 65歲還在工作有公司保險，要辦 Part B 嗎？"):
            quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
        if st.button("📅 我的黃金申辦期 (IEP) 是什麼時候？"):
            quick_prompt = "請幫我算算我的 Initial Enrollment Period (IEP) 黃金申辦期是哪幾個月？錯過會有罰款嗎？"

        st.subheader("📍 第三步：保費與費用調降")
        if st.button("💵 Part B 保費多少？如何繳費？"):
            quick_prompt = "Part B 的每月保費與每年 Deductible (自付額) 是多少？該如何設定自動繳費？"
        if st.button("📝 什麼是 IRMAA 附加費？如何申請調降？"):
            quick_prompt = "請解釋什麼是 IRMAA 保費附加費？如果我退休後收入變少，可以申請調降嗎？"

    else:
        st.header("🗺️ 3-Step Navigation")
        st.subheader("📍 Step 1")
        if st.button("❓ What is Medigap?"):
            quick_prompt = "Can you explain Medigap simply?"
        st.subheader("📍 Step 2")
        if st.button("💼 Working past 65 & Part B?"):
            quick_prompt = "I'm turning 65 but still working. Do I need Part B?"
        st.subheader("📍 Step 3")
        if st.button("📝 What is IRMAA surcharge?"):
            quick_prompt = "What is the IRMAA surcharge?"

    st.markdown("---")
    
    # 照片上傳解惑區
    st.header("📸 " + ("Document Assistant" if current_lang in ["English", "Español", "한국어"] else "看不懂英文信件/保單？"))
    
    with st.expander("ℹ️ " + ("Why upload photo?" if current_lang in ["English", "Español", "한국어"] else "為什麼要拍照上傳？")):
        st.caption("If you receive letters from Social Security or Medicare that are confusing, simply snap a photo! AI will read and explain it in plain text. Your privacy is safe and documents are not stored.")
    
    upload_label = "Upload photo (Optional) / 拍照上傳（選填）:"
    uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
    img_data = None
    if uploaded_file:
        img_data = Image.open(uploaded_file)
        st.image(img_data, caption="Loaded", use_column_width=True)

    st.markdown("---")
    st.warning("⚠️ **Official Warning**: Medicare will NEVER call to ask for your Social Security Number.")

    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("✅ Service Ready!" if current_lang in ["English", "Español", "한국어"] else "✅ 系統服務已就緒！")

# 4. 主畫面標題與固定式宣導橫幅
if current_lang == "English":
    st.title("🧭 Medicare Compass")
    st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps, avoiding late penalties and demystifying confusing letters.")
elif current_lang == "繁體中文":
    st.title("🧭 Medicare Compass 醫保指南針")
    st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款，並協助翻譯看不懂的英文官方信件。")
else:
    st.title("🧭 Medicare Compass")
    st.info("📢 Designed to help seniors navigate US Medicare smoothly across 3 clear steps.")

# 5. 系統指令 (System Instruction)
SYSTEM_INSTRUCTION = """
You are a warm, highly patient, and empathetic expert Medicare guide named "Medicare Compass".
Your mission is to guide first-time applicants, turning 65 seniors, and families through US Medicare smoothly.

【Core Principles】
1. Keep responses CONCISE and short (2-3 brief paragraphs maximum). Use bold keywords for easy scanning.
2. Phase Transition Check: At the end of answering Phase 1 or Phase 2 topics, ALWAYS ask: 
   "Do you have any more questions about this step? If you feel ready, ask your next question or pick from the left sidebar!"
3. Demystify the 80/20 myth early: Clarify that Original Medicare only covers 80% with NO out-of-pocket maximum.
4. Language Matching: Respond fluently in the selected language.
"""

# 6. 開場白初始化 (直接在主畫面提供身分對話選擇)
if current_lang == "English":
    welcome_msg = "Hello and welcome! I am your Medicare Compass guide. We will guide you step-by-step through Medicare.\n\nTo begin **Step 1: Plan Exploration**, please tell me: **Which state do you live in, and what is your birth month and year?**"
elif current_lang == "繁體中文":
    welcome_msg = "您好！我是您的 Medicare 智慧導覽助手。我們會陪伴您分三步驟輕鬆了解 Medicare。\n\n為了幫您展開 **第一步：方案探索**，請告訴我：**您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？**"
else:
    welcome_msg = "Hello! I am your Medicare Compass guide. Which state do you live in, and what is your birth month and year?"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 7. 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 💡 主畫面快速啟動按鈕 (一進來就呈現在右邊對話框下方，不再迷路)
if len(st.session_state.messages) == 1:
    st.caption("💡 " + ("Quick start options:" if current_lang in ["English", "Español", "한국어"] else "您也可以直接點選以下身分快速開始："))
    col_start1, col_start2 = st.columns(2)
    with col_start1:
        if st.button("👴 " + ("I'm applying for myself" if current_lang == "English" else "我是長者本人（開始 3 步驟導覽）")):
            quick_prompt = "您好！我是長者本人，準備開始了解 Medicare 申辦流程。我住在紐約州，今年剛滿 65 歲。"
    with col_start2:
        if st.button("👨‍👩‍👧 " + ("I'm helping my parents" if current_lang == "English" else "我是幫父母查詢的子女（查看快速對照清單）")):
            quick_prompt = "我是幫家中長輩查詢 Medicare 的子女。請給我一份清晰、結構化的清單，告訴我幫父母申辦時最需要注意的核心選項與時間軸限制！"

# 💊 對話進行中的「發問小卡」
if len(st.session_state.messages) > 1:
    st.caption("💡 " + ("Quick Questions (Click to ask):" if current_lang in ["English", "Español", "한국어"] else "點擊下方小卡直接發問："))
    col_pill1, col_pill2 = st.columns(2)
    with col_pill1:
        if st.button("💡 " + ("Tell me about Part B costs" if current_lang == "English" else "了解 Part B 保費細節")):
            quick_prompt = "請詳細告訴我 Part B 的保費與 Deductible 是多少？"
    with col_pill2:
        if st.button("💡 " + ("How to avoid penalties?" if current_lang == "English" else "如何完全避開遲辦罰款？")):
            quick_prompt = "請告訴我最關鍵的黃金申辦期限，我該如何確保完全不被罰款？"

# 🎙️ 醒目的麥克風語音輸入提示
has_user_replied = len(st.session_state.messages) > 1

if current_lang == "English":
    input_placeholder = "🎙️ Speak or type your question here..." if has_user_replied else "🎙️ Speak or type your state/birthdate here..."
elif current_lang == "繁體中文":
    input_placeholder = "🎙️ 點擊麥克風用語音講，或直接打字發問..." if has_user_replied else "🎙️ 點擊麥克風說出您的居住州與出生年月，或打字回覆..."
else:
    input_placeholder = "🎙️ Speak or type your reply here..."

input_prompt = st.chat_input(input_placeholder)
prompt = quick_prompt if quick_prompt else input_prompt

if prompt or uploaded_file:
    if not api_key:
        st.error("Please set API Key in sidebar.")
    else:
        try:
            clean_key = str(api_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            
            # ✨ 使用官方 100% 穩定支援的 gemini-1.5-flash，解決 404 錯誤
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
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
                    if img_data:
                        response = model.generate_content([user_content, img_data], stream=True)
                    else:
                        chat = model.start_chat(history=[
                            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                            for m in st.session_state.messages[:-1]
                        ])
                        response = chat.send_message(user_content, stream=True)
                    
                    full_text = st.write_stream(stream_text_generator(response))
                    
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# 9. 結案打包工具箱：雙版本 + 一鍵寄至 Email
if len(st.session_state.messages) > 1:
    st.markdown("---")
    st.header("📋 " + ("Consultation Summary & Sharing" if current_lang in ["English", "Español", "한국어"] else "諮詢紀錄打包與分享"))
    
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
        st.caption("适合发给子女或 Line/WeChat 微信快速查看 (Great for family sharing)")
        st.text_area("Preview (內容預覽):", value=short_summary_text, height=150)
        
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
                        📧 Send to My Email (寄給自己/家人)
                    </button>
                </a>
            ''', unsafe_allow_html=True)

    with tab2:
        st.caption("包含今天所有詳細對話問答紀錄 (Complete Q&A History)")
        st.download_button(
            label="📥 Download Full Log (TXT)",
            data=full_log_text,
            file_name="Medicare_Full_Consultation.txt",
            mime="text/plain"
        )
