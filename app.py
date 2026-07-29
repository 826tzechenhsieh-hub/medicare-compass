import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 頁面標題與配置設定
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 2. 抓取 API Key
api_key = st.secrets.get("GEMINI_API_KEY", None)

# 3. 側邊欄（Sidebar）：語系選單（以美國在地族群為優先順序）
with st.sidebar:
    st.header("🌐 Language / 語言設定")
    
    # 預設 English 為第一順位，其次為 Español, 繁體中文, 简体中文, 한국어
    current_lang = st.radio(
        "Select Language / 選擇語言:", 
        ["English", "Español", "繁體中文", "简体中文", "한국어"], 
        index=0,
        key="selected_language"
    )
    
    # 切換語言時自動重置歷史對話以同步開場白
    if "previous_language" not in st.session_state:
        st.session_state.previous_language = current_lang
    elif st.session_state.previous_language != current_lang:
        st.session_state.previous_language = current_lang
        if "messages" in st.session_state:
            del st.session_state["messages"]
        st.rerun()

    st.markdown("---")
    
    # 快捷問題按鈕（收納於左側）
    quick_prompt = None
    st.header("💡 " + (
        "Quick Questions" if current_lang == "English" else
        "Preguntas Frecuentes" if current_lang == "Español" else
        "자주 묻는 질문" if current_lang == "한국어" else
        "快捷發問小助手" if current_lang == "繁體中文" else "快捷发问小助手"
    ))
    
    if current_lang == "English":
        if st.button("❓ What is Medigap?"):
            quick_prompt = "Can you explain what Medigap is in simple terms and why Original Medicare alone isn't enough?"
        if st.button("💼 Working past 65 & Part B?"):
            quick_prompt = "I'm turning 65 but still working with employer insurance. Do I need Part B now, and will I face penalties?"
        if st.button("📝 What is IRMAA surcharge?"):
            quick_prompt = "What is the IRMAA Medicare surcharge, and how can I appeal it if my income dropped after retirement?"
    elif current_lang == "Español":
        if st.button("❓ ¿Qué es Medigap?"):
            quick_prompt = "¿Puede explicarme qué es Medigap y por qué no basta solo con Medicare Original?"
        if st.button("💼 ¿Trabaja a los 65 años?"):
            quick_prompt = "Tengo 65 años pero sigo trabajando con seguro de empleo. ¿Necesito la Parte B ahora?"
        if st.button("📝 ¿Qué es el recargo IRMAA?"):
            quick_prompt = "¿Qué es el recargo de prima IRMAA y cómo puedo apelarlo?"
    elif current_lang == "한국어":
        if st.button("❓ 메디갭(Medigap)이란?"):
            quick_prompt = "메디갭(Medigap)이 무엇인지, 왜 오리지널 메디케어만으로는 부족한지 알기 쉽게 설명해 주세요."
        if st.button("💼 65세 이후에도 일하는 경우?"):
            quick_prompt = "65세가 되었지만 직장 보험에 가입되어 있습니다. 지금 파트 B를 신청해야 하나요? 벌금이 있나요?"
        if st.button("📝 IRMAA 추가 비용이란?"):
            quick_prompt = "IRMAA 추가 보험료가 무엇이며, 은퇴 후 소득이 줄어든 경우 어떻게 이의 신청을 할 수 있나요?"
    elif current_lang == "繁體中文":
        if st.button("❓ 什麼是 Medigap？"):
            quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
        if st.button("💼 65歲還在工作要辦 Part B 嗎？"):
            quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
        if st.button("📝 什麼是 IRMAA 附加費？"):
            quick_prompt = "請解釋什麼是 IRMAA 保費附加費？如果我退休後收入變少，可以申請調降嗎？"
    else:  # 简体中文
        if st.button("❓ 什么是 Medigap？"):
            quick_prompt = "请用最通俗的方式告诉我，什么是 Medigap？为什么只买 Medicare Original 还不够？"
        if st.button("💼 65岁还在工作要办 Part B 吗？"):
            quick_prompt = "我今年 65 岁但还在公司全职工作，公司有提供医疗保险，我需要现在申请 Part B 吗？会不会有罚款？"
        if st.button("📝 什么是 IRMAA 附加费？"):
            quick_prompt = "请解释什么是 IRMAA 保费附加费？如果我退休后收入变少，可以申请调降吗？"

    st.markdown("---")
    
    # 側邊欄三大階段導航與防詐警示
    if current_lang == "English":
        st.header("🗺️ 3-Step Roadmap")
        st.markdown("""
        * **Step 1: Plan Exploration** *(Traditional vs. Advantage)*
        * **Step 2: Enrollment Process** *(Deadlines & Penalty Avoidance)*
        * **Step 3: Premiums & Payments** *(Part B & IRMAA)*
        """)
        st.warning("⚠️ **Official Warning**: Medicare will NEVER call to request your Social Security Number or bank account info.")
    elif current_lang == "Español":
        st.header("🗺️ Guía de 3 Pasos")
        st.markdown("""
        * **Paso 1: Exploración de planes** *(Original vs. Advantage)*
        * **Paso 2: Inscripción** *(Fechas límite y evitar multas)*
        * **Paso 3: Primas y Pagos** *(Parte B e IRMAA)*
        """)
        st.warning("⚠️ **Advertencia Oficial**: Medicare NUNCA lo llamará para pedirle su Seguro Social o cuenta bancaria.")
    elif current_lang == "한국어":
        st.header("🗺️ 메디케어 3단계 가이드")
        st.markdown("""
        * **1단계: 플랜 탐색** *(오리지널 vs. 어드밴티지)*
        * **2단계: 신청 절차** *(신청 기한 및 벌금 방지)*
        * **3단계: 보험료 및 납부** *(파트 B 및 IRMAA)*
        """)
        st.warning("⚠️ **사기 예방 경고**: 메디케어 당국은 절대로 전화로 주민등록번호(SSN)나 은행 계좌 정보를 요구하지 않습니다.")
    elif current_lang == "繁體中文":
        st.header("🗺️ 申辦三大階段導航")
        st.markdown("""
        * **第一步：方案探索** *(Traditional Medicare vs. Advantage)*
        * **第二步：申辦流程** *(時間軸與避開罰款)*
        * **第三步：保費與繳費** *(Part B 保費與 IRMAA 調整)*
        """)
        st.warning("⚠️ **官方防詐提醒**：Medicare 官方人員**絕不會**主動打電話索取您的 Social Security Number 或銀行帳戶。")
    else:  # 简体中文
        st.header("🗺️ 申办三大阶段导航")
        st.markdown("""
        * **第一步：方案探索** *(Traditional Medicare vs. Advantage)*
        * **第二步：申办流程** *(时间轴与避开罚款)*
        * **第三步：保费与缴费** *(Part B 保费与 IRMAA 调整)*
        """)
        st.warning("⚠️ **官方防诈提醒**：Medicare 官方人员**绝不会**主动打电话索取您的 Social Security Number 或银行账户。")

    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("✅ Service Ready!" if current_lang in ["English", "Español"] else "✅ 系統服務已就緒！")

# 4. 主畫面標題與說明
if current_lang == "English":
    st.title("🧭 Medicare Compass")
    st.caption("Your trusted US Medicare advisor | Avoid late penalties & navigate options with confidence.")
elif current_lang == "Español":
    st.title("🧭 Medicare Compass")
    st.caption("Su asesor de confianza para Medicare | Evite sanciones y elija su plan con confianza.")
elif current_lang == "한국어":
    st.title("🧭 Medicare Compass")
    st.caption("신뢰할 수 있는 미국 메디케어 가이드 | 벌금을 방지하고 나에게 맞는 플랜을 선택하세요.")
elif current_lang == "繁體中文":
    st.title("🧭 Medicare Compass 醫保指南針")
    st.caption("您的美國醫療保險隨身顧問 | 協助您避開罰款、清楚掌握申辦步驟")
else:  # 简体中文
    st.title("🧭 Medicare Compass 医保指南针")
    st.caption("您的美国医疗保险随身顾问 | 协助您避开罚款、清楚掌握申办步骤")

# 5. 系統指令 (System Instruction)
SYSTEM_INSTRUCTION = """
You are a warm, highly patient, and empathetic expert Medicare guide named "Medicare Compass".
Your mission is to help seniors turning 65, retirees, green card immigrants, and families navigating US Medicare.

【Core Principles】
1. Be encouraging, clear, and reassuring. Avoid overly dense legal/insurance jargon.
2. Always explain key terms with simple everyday analogies.
3. Demystify the "Full Government Coverage" myth: Clarify early that Original Medicare (Part B) only covers 80%, leaving 20% with NO out-of-pocket maximum—which is why Medigap/Supplements exist!
4. Active Guidance (CRITICAL): At the end of every response, ALWAYS suggest 2 clear, logical follow-up questions or options that the user can ask next to guide them step-by-step through the process.
5. Strict Character & Language Matching: Respond fluently in the exact language selected (English, Spanish, Korean, Traditional Chinese, Simplified Chinese).
"""

# 6. 開場白對話紀錄初始化（當地最親切溫和的問候語）
if current_lang == "English":
    welcome_msg = "Hello! I am your Medicare Compass guide. Whether you are turning 65 soon, planning retirement, or reviewing your current plan, I'm here to walk you through every step warm and simple, while avoiding late penalties.\n\nTo get started, which state (or Zip Code) do you live in, and what is your birth month and year?"
elif current_lang == "Español":
    welcome_msg = "¡Hola! Soy su guía de Medicare Compass. Ya sea que esté cumpliendo 65 años, planificando su jubilación o revisando sus opciones, estoy aquí para guiarlo paso a paso sin complicaciones ni multas.\n\nPara comenzar, ¿en qué estado (o código postal) vive y cuál es su mes y año de nacimiento?"
elif current_lang == "한국어":
    welcome_msg = "안녕하세요! 당신의 메디케어 나침반 가이드입니다. 곧 65세가 되시거나, 은퇴를 준비 중이시거나, 현재 플랜을 검토 중이시더라도 벌금 없이 가장 알맞은 플랜을 찾으실 수 있도록 따뜻하고 쉽게 안내해 드리겠습니다.\n\n먼저, 현재 거주하시는 주(또는 우편번호)와 생년월일(년/월)을 알려주실 수 있나요?"
elif current_lang == "繁體中文":
    welcome_msg = "您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱。\n\n請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？"
else:  # 简体中文
    welcome_msg = "您好！我是您的 Medicare 智慧导览助手。无论您是即将满 65 岁准备第一次申请、仍在工作中准备退休，或是想了解如何转方案，我都会一步步带您避开时间与罚款陷阱。\n\n请问您目前居住在哪一个州（或 Zip Code）？以及您的出生年月是什么时候呢？"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 7. 顯示過往對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. 圖片上傳區塊
if current_lang == "English":
    upload_label = "📸 Upload photo of Medicare card, policy, or SSA letter (optional):"
elif current_lang == "Español":
    upload_label = "📸 Subir foto de tarjeta de Medicare o carta de SSA (opcional):"
elif current_lang == "한국어":
    upload_label = "📸 메디케어 카드, 편지, 또는 서류 사진 업로드 (선택 사항):"
elif current_lang == "繁體中文":
    upload_label = "📸 拍照或上傳 Medicare 保單 / SSA 官方信件照片（選填）："
else:  # 简体中文
    upload_label = "📸 拍照或上传 Medicare 保单 / SSA 官方信件照片（选填）："

uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
img_data = None
if uploaded_file:
    img_data = Image.open(uploaded_file)
    st.image(img_data, caption="Loaded", use_column_width=True)

# 9. 對話輸入框（含語音輸入提示）
if current_lang == "English":
    input_placeholder = "Type your reply or use microphone 🎙️..."
elif current_lang == "Español":
    input_placeholder = "Escriba su respuesta o use el micrófono 🎙️..."
elif current_lang == "한국어":
    input_placeholder = "답변을 입력하거나 마이크 🎙️로 말씀하세요..."
elif current_lang == "繁體中文":
    input_placeholder = "請輸入您的回答，或點選手機麥克風 🎙️ 語音輸入..."
else:  # 简体中文
    input_placeholder = "请输入您的回答，或点击手机麦克风 🎙️ 语音输入..."

input_prompt = st.chat_input(input_placeholder)
prompt = quick_prompt if quick_prompt else input_prompt

if prompt or uploaded_file:
    if not api_key:
        st.error("Please set API Key in sidebar.")
    else:
        try:
            clean_key = str(api_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            user_content = prompt if prompt else "Please analyze this uploaded document."
            
            st.session_state.messages.append({"role": "user", "content": user_content})
            with st.chat_message("user"):
                st.markdown(user_content)

            with st.chat_message("assistant"):
                spinner_text = "Medicare Compass is analyzing..." if current_lang in ["English", "Español", "한국어"] else "Medicare Compass 正在為您分析思考中..."
                with st.spinner(spinner_text):
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
            st.error(f"Error: {e}")

# 10. 下載紀錄
if len(st.session_state.messages) > 1:
    st.markdown("---")
    chat_history_text = "【Medicare Compass - Consultation Summary】\n\n"
    for m in st.session_state.messages:
        role_title = "Advisor" if m["role"] == "assistant" else "User"
        chat_history_text += f"[{role_title}]:\n{m['content']}\n\n------------------------\n\n"
    
    download_label = "📥 Export Summary (TXT)" if current_lang in ["English", "Español", "한국어"] else "📥 下載本次諮詢紀錄與申辦清單 (TXT)"
    st.download_button(
        label=download_label,
        data=chat_history_text,
        file_name="Medicare_Compass_Summary.txt",
        mime="text/plain"
    )
