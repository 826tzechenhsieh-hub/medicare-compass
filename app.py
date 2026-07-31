import streamlit as st
import google.generativeai as genai
import urllib.parse
from PIL import Image

# 1. Page Config
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# Senior-friendly typography & Smooth auto-scroll prevention
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

# 3. Sidebar
with st.sidebar:
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
    
    if "previous_language" not in st.session_state:
        st.session_state.previous_language = current_lang
    elif st.session_state.previous_language != current_lang:
        st.session_state.previous_language = current_lang
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

    st.markdown("---")
    
    quick_prompt = None
    
    if current_lang == "English":
        st.header("🗺️ 3-Step Quick Questions")
        
        st.subheader("📍 Step 0: General Overview")
        if st.button("🗺️ Traditional Medicare vs Advantage?"):
            quick_prompt = "Can you explain the basic framework of Medicare (Parts A, B, C, D, and Medigap) in simple terms?"

        st.subheader("📍 Step 1: Plan Exploration")
        if st.button("❓ What is Medigap & why need it?"):
            quick_prompt = "Can you explain what Medigap is in simple terms and why Original Medicare alone isn't enough?"
        if st.button("🩺 Are my doctors in-network & prescriptions covered?"):
            quick_prompt = "How do I check if my current doctors are in-network and if my prescriptions are covered under Part D or Advantage?"

        st.subheader("📍 Step 2: Timeline & Penalties")
        if st.button("💼 Working past 65 with employer coverage?"):
            quick_prompt = "I'm turning 65 but still working with employer insurance. Do I need Part B now, and will I face penalties?"
        if st.button("📅 When is my 7-Month Enrollment Window (IEP)?"):
            quick_prompt = "Can you explain my 7-month Initial Enrollment Period (IEP) timeline and what happens if I miss it?"

        st.subheader("📍 Step 3: Premiums & Financials")
        if st.button("💵 Part B Cost & Automatic Payment?"):
            quick_prompt = "How much is the Part B premium and deductible, and how do I set up automatic payments?"
        if st.button("📝 High Income Premium Surcharge (IRMAA)?"):
            quick_prompt = "What is the IRMAA high-income Medicare surcharge, and how can I appeal it if my income dropped after retirement?"

    elif current_lang == "繁體中文":
        st.header("🗺️ 申辦核心指南")
        
        st.subheader("📍 零：基礎地圖總覽")
        if st.button("🗺️ 傳統紅藍卡 (A/B) vs 優惠套餐 (C)？"):
            quick_prompt = "請用白話說明 Medicare 的整體架構：傳統紅藍卡 Part A/B、Part C 優惠套餐、Part D 處方藥與 Medigap 補充保險有何不同？"

        st.subheader("📍 第一步：方案探索")
        if st.button("❓ 什麼是 Medigap？為什麼只買紅藍卡不夠？"):
            quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
        if st.button("🩺 常看的診所（網絡內）與藥物有給付嗎？"):
            quick_prompt = "如何確認我平時看診的醫生（是否在網絡內 In-network）以及在吃的慢性病藥物有沒有在給付範圍內？"

        st.subheader("📍 第二步：時間軸與避開罰款")
        if st.button("💼 65歲還在工作有公司保險，要辦 Part B 嗎？"):
            quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
        if st.button("📅 什麼是 7 個月黃金申辦期 (IEP)？"):
            quick_prompt = "請幫我解釋 Initial Enrollment Period (IEP) 7 個月申辦黃金期是什麼時候？錯過會有罰款嗎？"

        st.subheader("📍 第三步：保費與費用調降")
        if st.button("💵 Part B 保費多少？如何設定自動繳費？"):
            quick_prompt = "Part B 的每月保費與每年 Deductible (自付額) 是多少？該如何設定自動繳費？"
        if st.button("📝 什麼是高收入附加費 (IRMAA)？如何調降？"):
            quick_prompt = "請解釋什麼是 IRMAA 高收入保費附加費？如果我退休後收入變少，可以申請調降嗎？"

    else:
        st.header("🗺️ 3-Step Navigation")
        st.subheader("📍 General Overview")
        if st.button("🗺️ Medicare Basics (A/B/C/D)"):
            quick_prompt = "Can you explain Medicare Parts A, B, C, D simply?"

    st.markdown("---")
    
    st.header("📸 " + ("Document Assistant" if current_lang in ["English", "Español", "한국어"] else "看不懂英文信件/保單？"))
    
    upload_label = "Upload photo (Optional) / 拍照上傳（選填）:"
    uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
    img_data = None
    if uploaded_file:
        img_data = Image.open(uploaded_file)
        st.image(img_data, caption="Loaded", use_column_width=True)

    st.markdown("---")
    st.warning("⚠️ **Official Warning**: Medicare will NEVER call to ask for your Social Security Number.")

    if not primary_key:
        primary_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("✅ Service Ready!" if current_lang in ["English", "Español", "한국어"] else "✅ 系統服務已就緒！")

# 4. Main Header & Announcement Banner
if current_lang == "English":
    st.title("🧭 Medicare Compass")
    st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps, avoiding late penalties and demystifying confusing letters.")
elif current_lang == "繁體中文":
    st.title("🧭 Medicare Compass 醫保指南針")
    st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款，並協助翻譯看不懂的英文官方信件。")
else:
    st.title("🧭 Medicare Compass")
    st.info("📢 Designed to help seniors navigate US Medicare smoothly across 3 clear steps.")

# 5. System Instructions
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
"""

# 6. Greeting Initialization (With Clear Overview Map)
if current_lang == "English":
    welcome_msg = """Hello and welcome! I am your **Medicare Compass** guide. 

Before we dive in, here is your **1-Minute Medicare Map**:
* 🔴 **Original Medicare (Government)**: 
  * **Part A (Hospital)**: Mostly free if you worked 10 years.
  * **Part B (Medical)**: Monthly premium required, covers **80%** (20% gap!).
* 🟡 **Part C (Medicare Advantage)**: Private all-in-one plans (A + B + usually D).
* 🔵 **Part D (Prescription Drugs)**: Standalone drug coverage.
* 🟣 **Medigap (Supplement)**: Private plans to cover the **20% gap** of Part B.

---
To begin **Step 1: Plan Exploration**, please tell me: **Which state do you live in, and what is your birth month and year?**"""
elif current_lang == "繁體中文":
    welcome_msg = """您好！我是您的 **Medicare 智慧導覽助手**。

在開始前，先為您奉上 **1分鐘 Medicare 快速地圖**：
* 🔴 **Original Medicare (傳統紅藍卡 / 政府發行)**：
  * **Part A (住院保險)**：工作滿 10 年者多數免費。
  * **Part B (門診保險)**：需繳月保費，政府給付 **80%**（**自付 20% 無上限！**）。
* 🟡 **Part C (Advantage 優惠套餐)**：私人保險公司包辦 (A + B + 通常含 D)。
* 🔵 **Part D (處方藥專案)**：單純補充藥物給付。
* 🟣 **Medigap (補充保險)**：填補 Part B 那 **20% 自付額無底洞**。

---
為了幫您展開 **第一步：方案探索**，請告訴我：**您目前居住在哪一個州？以及您的出生年月是什麼時候呢？**"""
else:
    welcome_msg = "Hello! I am your Medicare Compass guide. Which state do you live in, and what is your birth month and year?"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 7. Display Chat History
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
    st.header("📋 " + ("Consultation Summary & Sharing" if current_lang in ["English", "Español", "한국어"] else "諮諮紀錄打包與分享"))
    
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
# 10. Force Scroll to Top on Initial Load / Reboot
st.markdown("""
    <script>
        var body = window.parent.document.querySelector(".main");
        if (body) {
            body.scrollTop = 0;
        }
    </script>
""", unsafe_allow_html=True)
