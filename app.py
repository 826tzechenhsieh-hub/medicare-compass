import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 頁面標題與配置設定
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 2. 抓取 API Key (優先讀取 Secrets，若無則顯示輸入框)
api_key = st.secrets.get("GEMINI_API_KEY", None)

# 3. 側邊欄（Sidebar）：語言切換開關 (含繁、簡、英、西)
with st.sidebar:
    st.header("🌐 Language / 語言設定")
    lang = st.radio(
        "Choose Interface Language / 選擇介面語言:", 
        ["繁體中文", "简体中文", "English", "Español"], 
        index=0
    )
    st.markdown("---")
    
    if lang == "繁體中文":
        st.header("🗺️ 申辦三大階段導航")
        st.markdown("""
        * **第一步：方案探索** *(Traditional Medicare vs. Advantage，該怎麼選？)*
        * **第二步：申辦流程** *(何時申辦？去哪裡申辦？如何避開罰款？)*
        * **第三步：保費與繳費處理** *(Part B 保費、Deductible 與 IRMAA 調整)*
        """)
        st.markdown("---")
        st.warning("""
        ⚠️ **官方防詐與權益提醒**：  
        Medicare 官方人員**絕不會**主動打電話索取您的 Social Security Number 或銀行帳戶。請認準官方網站 Medicare.gov 或諮詢 SHIP 官方輔導專線 (1-800-252-8966)。
        """)
    elif lang == "简体中文":
        st.header("🗺️ 申办三大阶段导航")
        st.markdown("""
        * **第一步：方案探索** *(Traditional Medicare vs. Advantage，该怎么选？)*
        * **第二步：申办流程** *(何时申办？去哪里申办？如何避开罚款？)*
        * **第三步：保费与缴费处理** *(Part B 保费、Deductible 与 IRMAA 调整)*
        """)
        st.markdown("---")
        st.warning("""
        ⚠️ **官方防诈与权益提醒**：  
        Medicare 官方人员**绝不会**主动打电话索取您的 Social Security Number 或银行账户。请认准官方网站 Medicare.gov 或咨询 SHIP 官方辅导专线 (1-800-252-8966)。
        """)
    elif lang == "Español":
        st.header("🗺️ Guía de 3 Pasos de Medicare")
        st.markdown("""
        * **Paso 1: Exploración de planes** *(Medicare Original vs. Advantage)*
        * **Paso 2: Proceso de inscripción** *(¿Cuándo y cómo solicitarlo sin multas?)*
        * **Paso 3: Prima y pagos** *(Primas de Parte B, deducibles y ajustes de IRMAA)*
        """)
        st.markdown("---")
        st.warning("""
        ⚠️ **Advertencia Oficial de Fraude**:  
        Los representantes de Medicare **NUNCA** lo llamarán para pedirle su Número de Seguro Social o cuenta bancaria.
        """)
    else:  # English
        st.header("🗺️ 3-Step Medicare Roadmap")
        st.markdown("""
        * **Step 1: Plan Exploration** *(Traditional Medicare vs. Advantage: Which fits you best?)*
        * **Step 2: Enrollment Process** *(When & where to apply? How to avoid penalties?)*
        * **Step 3: Premium & Payments** *(Part B premiums, deductibles, and IRMAA adjustments)*
        """)
        st.markdown("---")
        st.warning("""
        ⚠️ **Official Fraud Warning**:  
        Medicare representatives will **NEVER** call to request your Social Security Number or bank account info.
        """)

    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("✅ Service Ready!" if lang in ["English", "Español"] else "✅ 系統服務已就緒！")

# 4. 主畫面動態標題與說明
if lang == "繁體中文":
    st.title("🧭 Medicare Compass 醫保指南針")
    st.caption("您的美國醫療保險隨身顧問 | 協助您避開罰款、清楚掌握申辦步驟")
elif lang == "简体中文":
    st.title("🧭 Medicare Compass 医保指南针")
    st.caption("您的美国医疗保险随身顾问 | 协助您避开罚款、清楚掌握申办步骤")
elif lang == "Español":
    st.title("🧭 Medicare Compass")
    st.caption("Su asesor de confianza para Medicare | Evite sanciones y elija con confianza.")
else:
    st.title("🧭 Medicare Compass")
    st.caption("Your trusted US Medicare advisor | Avoid late penalties & navigate options with confidence.")

# 5. 系統指令 (System Instruction) 藍圖
SYSTEM_INSTRUCTION = """
You are a warm, highly patient, and empathetic expert Medicare guide named "Medicare Compass".
Your mission is to help seniors turning 65, retirees, green card immigrants, and families transitioning between Medicare Advantage and Traditional Medicare.

【Core Principles】
1. Be encouraging, clear, and reassuring. Avoid overly dense legal/insurance jargon.
2. Always explain key terms with simple everyday analogies (e.g., Deductible = "the out-of-pocket amount you pay each year before coverage kicks in").
3. Demystify the "Full Government Coverage" myth: Clarify early that Original Medicare (Part B) only covers 80%, leaving 20% with NO out-of-pocket maximum—which is why Medigap/Supplements exist!
4. Format response cleanly with bolding and short paragraphs for effortless reading or Text-to-Speech (TTS).
5. Strict Character & Language Matching: 
   - If the user uses Traditional Chinese (繁體中文), ALWAYS respond in Traditional Chinese with Taiwanese/HK insurance terminology preferences.
   - If the user uses Simplified Chinese (简体中文), ALWAYS respond in Simplified Chinese.
   - Match the exact language of input (English, Spanish, Korean, Vietnamese, etc.).
"""

# 6. 開場白對話紀錄初始化
if lang == "繁體中文":
    welcome_msg = "您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱。\n\n請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？"
elif lang == "简体中文":
    welcome_msg = "您好！我是您的 Medicare 智慧导览助手。无论您是即将满 65 岁准备第一次申请、仍在工作中准备退休，或是想了解如何转方案，我都会一步步带您避开时间与罚款陷阱。\n\n请问您目前居住在哪一个州（或 Zip Code）？以及您的出生年月是什么时候呢？"
elif lang == "Español":
    welcome_msg = "¡Hola! Soy su guía de Medicare Compass. Ya sea que esté cumpliendo 65 años o planificando su jubilación, estoy aquí para guiarlo paso a paso.\n\nPara comenzar, ¿en qué estado vive y cuál es su mes y año de nacimiento?"
else:
    welcome_msg = "Hello! I am your Medicare Compass guide. Whether you're turning 65 or planning retirement, I'm here to walk you through every step.\n\nTo get started, which state do you reside in, and what is your birth month and year?"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 7. 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. 動態快捷問題按鈕
quick_prompt = None

if lang == "繁體中文":
    st.write("💡 **熱門快速詢問（點擊可直接提問）：**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❓ 什麼是 Medigap？"):
            quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
    with col2:
        if st.button("💼 65歲還在工作要辦 Part B 嗎？"):
            quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
    with col3:
        if st.button("📝 什麼是 IRMAA 附加費？"):
            quick_prompt = "請解釋什麼是 IRMAA 保費附加費？如果我退休後收入變少，可以申請調降嗎？"
elif lang == "简体中文":
    st.write("💡 **热门快速询问（点击可直接提问）：**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❓ 什么是 Medigap？"):
            quick_prompt = "请用最通俗的方式告诉我，什么是 Medigap？为什么只买 Medicare Original 还不够？"
    with col2:
        if st.button("💼 65岁还在工作要办 Part B 吗？"):
            quick_prompt = "我今年 65 岁但还在公司全职工作，公司有提供医疗保险，我需要现在申请 Part B 吗？会不会有罚款？"
    with col3:
        if st.button("📝 什么是 IRMAA 附加费？"):
            quick_prompt = "请解释什么是 IRMAA 保费附加费？如果我退休后收入变少，可以申请调降吗？"
else:
    st.write("💡 **Frequently Asked Questions:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❓ What is Medigap?"):
            quick_prompt = "Can you explain what Medigap is in simple terms and why Original Medicare alone isn't enough?"
    with col2:
        if st.button("💼 Working past 65 & Part B?"):
            quick_prompt = "I'm turning 65 but still working with employer insurance. Do I need Part B now, and will I face penalties?"
    with col3:
        if st.button("📝 What is IRMAA surcharge?"):
            quick_prompt = "What is the IRMAA Medicare surcharge, and how can I appeal it if my income dropped after retirement?"

# 9. 圖片上傳區塊
if lang == "繁體中文":
    upload_label = "📸 拍照或上傳 Medicare 保單 / SSA 官方信件照片（選填）："
elif lang == "简体中文":
    upload_label = "📸 拍照或上传 Medicare 保单 / SSA 官方信件照片（选填）："
else:
    upload_label = "📸 Upload photo of Medicare card, policy, or SSA letter (optional):"

uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
img_data = None
if uploaded_file:
    img_data = Image.open(uploaded_file)
    st.image(img_data, caption="Photo loaded", use_column_width=True)

# 10. 對話輸入框
if lang == "繁體中文":
    input_placeholder = "請輸入或使用手機鍵盤麥克風 🎙️ 語音輸入..."
elif lang == "简体中文":
    input_placeholder = "请输入或使用手机键盘麦克风 🎙️ 语音输入..."
else:
    input_placeholder = "Type your reply or use microphone 🎙️..."

input_prompt = st.chat_input(input_placeholder)
prompt = quick_prompt if quick_prompt else input_prompt

if prompt or uploaded_file:
    if not api_key:
        st.error("Please set your Gemini API Key in sidebar.")
    else:
        try:
            clean_key = str(api_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            fallback_img_prompt = "Please analyze this uploaded Medicare document photo."
            user_content = prompt if prompt else fallback_img_prompt
            
            st.session_state.messages.append({"role": "user", "content": user_content})
            with st.chat_message("user"):
                st.markdown(user_content)

            with st.chat_message("assistant"):
                with st.spinner("Medicare Compass is analyzing..."):
                    if img_data:
                        response = model.generate_content([user_content, img_data])
                    else:
                        chat = model.start_chat(history=[
                            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                            for m in st.session_state.messages[:-1]
                        ])
                        response = chat.send_message(user_content)
                    
                    st.markdown(response.text)
                    
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"Error connecting to service: {e}")

# 11. 一鍵匯出諮詢紀錄
if len(st.session_state.messages) > 1:
    st.markdown("---")
    chat_history_text = "【Medicare Compass - Consultation Summary】\n\n"
    for m in st.session_state.messages:
        role_title = "Advisor" if m["role"] == "assistant" else "User"
        chat_history_text += f"[{role_title}]:\n{m['content']}\n\n------------------------\n\n"
    
    download_label = "📥 Export Consultation Record (TXT) / 下載諮詢紀錄"
    st.download_button(
        label=download_label,
        data=chat_history_text,
        file_name="Medicare_Compass_Summary.txt",
        mime="text/plain"
    )
