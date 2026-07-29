import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
from PIL import Image

# 1. 頁面標題與配置設定
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 2. 抓取 API Key
api_key = st.secrets.get("GEMINI_API_KEY", None)

# 3. 側邊欄（Sidebar）：語言與 3-Step 階段化指南
with st.sidebar:
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
    
    # 問題按鈕與 3-Step Roadmap 結合
    quick_prompt = None
    
    if current_lang == "English":
        st.header("🗺️ 3-Step Roadmap Guide")
        st.caption("Step 1: Plan Exploration")
        if st.button("❓ What is Medigap & Supplement?"):
            quick_prompt = "Can you explain what Medigap is in simple terms and why Original Medicare alone isn't enough?"
            
        st.caption("Step 2: Enrollment & Timeline")
        if st.button("💼 Working past 65 & Part B?"):
            quick_prompt = "I'm turning 65 but still working with employer insurance. Do I need Part B now, and will I face penalties?"
            
        st.caption("Step 3: Premiums & IRMAA")
        if st.button("📝 What is IRMAA surcharge?"):
            quick_prompt = "What is the IRMAA Medicare surcharge, and how can I appeal it if my income dropped after retirement?"
            
        st.warning("⚠️ **Official Warning**: Medicare representatives will NEVER call to ask for your Social Security Number.")

    elif current_lang == "Español":
        st.header("🗺️ Guía de 3 Pasos de Medicare")
        st.caption("Paso 1: Exploración de planes")
        if st.button("❓ ¿Qué es Medigap?"):
            quick_prompt = "¿Puede explicarme qué es Medigap y por qué no basta solo con Medicare Original?"
            
        st.caption("Paso 2: Inscripción y Fechas")
        if st.button("💼 ¿Trabaja a los 65 años?"):
            quick_prompt = "Tengo 65 años pero sigo trabajando con seguro de empleo. ¿Necesito la Parte B ahora?"
            
        st.caption("Paso 3: Primas e IRMAA")
        if st.button("📝 ¿Qué es el recargo IRMAA?"):
            quick_prompt = "¿Qué es el recargo de prima IRMAA y cómo puedo apelarlo?"
            
        st.warning("⚠️ **Advertencia Oficial**: Medicare NUNCA lo llamará para pedirle su Seguro Social por teléfono.")

    elif current_lang == "한국어":
        st.header("🗺️ 메디케어 3단계 안내")
        st.caption("1단계: 플랜 탐색")
        if st.button("❓ 메디갭(Medigap)이란?"):
            quick_prompt = "메디갭(Medigap)이 무엇인지, 왜 오리지널 메디케어만으로는 부족한지 알기 쉽게 설명해 주세요."
            
        st.caption("2단계: 신청 절차 및 기한")
        if st.button("💼 65세 이후에도 일하는 경우?"):
            quick_prompt = "65세가 되었지만 직장 보험에 가입되어 있습니다. 지금 파트 B를 신청해야 하나요? 벌금이 있나요?"
            
        st.caption("3단계: 보험료 및 IRMAA")
        if st.button("📝 IRMAA 추가 비용이란?"):
            quick_prompt = "IRMAA 추가 보험료가 무엇이며, 은퇴 후 소득이 줄어든 경우 어떻게 이의 신청을 할 수 있나요?"
            
        st.warning("⚠️ **사기 예방 경고**: 메디케어 당국은 절대로 전화로 주민등록번호(SSN)를 요구하지 않습니다.")

    elif current_lang == "繁體中文":
        st.header("🗺️ 申辦三大階段指引")
        st.caption("第一步：方案探索")
        if st.button("❓ 什麼是 Medigap 補充保險？"):
            quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
            
        st.caption("第二步：時間軸與申辦")
        if st.button("💼 65歲還在工作要辦 Part B 嗎？"):
            quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
            
        st.caption("第三步：保費與調降")
        if st.button("📝 什麼是 IRMAA 附加費？"):
            quick_prompt = "請解釋什麼是 IRMAA 保費附加費？如果我退休後收入變少，可以申請調降嗎？"
            
        st.warning("⚠️ **官方防詐提醒**：Medicare 官方人員**絕不會**主動打電話索取您的 Social Security Number 或銀行帳戶。")

    else: # 简体中文
        st.header("🗺️ 申办三大阶段指引")
        st.caption("第一步：方案探索")
        if st.button("❓ 什么是 Medigap 补充保险？"):
            quick_prompt = "请用最通俗的方式告诉我，什么是 Medigap？为什么只买 Medicare Original 还不够？"
            
        st.caption("第二步：时间轴与申办")
        if st.button("💼 65岁还在工作要办 Part B 吗？"):
            quick_prompt = "我今年 65 岁但还在公司全职工作，公司有提供医疗保险，我需要现在申请 Part B 吗？会不会有罚款？"
            
        st.caption("第三步：保费与调降")
        if st.button("📝 什么是 IRMAA 附加费？"):
            quick_prompt = "请解释什么是 IRMAA 保费附加费？如果我退休后收入变少，可以申请调降吗？"
            
        st.warning("⚠️ **官方防诈提醒**：Medicare 官方人员**绝不会**主动打电话索取您的 Social Security Number 或银行账户。")

    if not api_key:
        api_key = st.text_input("Gemini API Key:", type="password")
    else:
        st.success("✅ Service Ready!" if current_lang in ["English", "Español", "한국어"] else "✅ 系統服務已就緒！")

# 4. 主畫面標題
if current_lang == "English":
    st.title("🧭 Medicare Compass")
    st.caption("Your trusted US Medicare advisor | Step-by-step guidance without penalties.")
elif current_lang == "Español":
    st.title("🧭 Medicare Compass")
    st.caption("Su asesor de confianza para Medicare | Guía paso a paso sin sanciones.")
elif current_lang == "한국어":
    st.title("🧭 Medicare Compass")
    st.caption("신뢰할 수 있는 메디케어 가이드 | 벌금 없이 단계별로 안내해 드립니다.")
elif current_lang == "繁體中文":
    st.title("🧭 Medicare Compass 醫保指南針")
    st.caption("您的美國醫療保險隨身顧問 | 陪伴您三步驟輕鬆了解申辦流程")
else:
    st.title("🧭 Medicare Compass 医保指南针")
    st.caption("您的美国医疗保险随身顾问 | 陪伴您三步骤轻松了解申办流程")

# 5. 系統指令 (System Instruction)
SYSTEM_INSTRUCTION = """
You are a warm, highly patient, and empathetic expert Medicare guide named "Medicare Compass".
Your mission is to guide first-time applicants, turning 65 seniors, and families through US Medicare smoothly.

【Core Framework - 3-Step Roadmap Integration】
Whenever answering a user for the first time or giving a guidance summary, ALWAYS structure your response around these 3 clear steps:
1. Step 1: Plan Exploration (Traditional Medicare vs. Advantage & Medigap supplement)
2. Step 2: Timeline & Enrollment (Key IEP dates & penalty avoidance)
3. Step 3: Premiums & Financial Adjustments (Part B costs, Deductibles, IRMAA)

【Core Principles】
1. Be encouraging, clear, and reassuring. Avoid dense jargon; use simple everyday analogies.
2. Demystify the 80/20 myth early: Clarify that Original Medicare only covers 80% with NO out-of-pocket maximum.
3. Active Next-Step Guidance: At the end of every response, suggest 2 clear next questions/options to keep the momentum going effortlessly.
4. Language Matching: Respond fluently in the selected language (English, Spanish, Korean, Traditional Chinese, Simplified Chinese).
"""

# 6. 開場白對話紀錄與動態多語言語音變數（徹底修復語言錯置問題）
if current_lang == "English":
    welcome_msg = "Hello and welcome! I am your Medicare Compass guide. Navigating Medicare for the first time can feel overwhelming, but don't worry—I will take you through it step-by-step across 3 clear phases:\n\n• **Step 1**: Find the best plan fit.\n• **Step 2**: Calculate your timeline & avoid late penalties.\n• **Step 3**: Manage premiums & payments.\n\nTo begin Step 1, which state do you live in, and what is your birth month and year?"
    voice_msg_text = "Hello and welcome! I am your Medicare Compass guide. I will take you through Medicare step by step across three phases: Step 1, find the best plan fit. Step 2, calculate your timeline and avoid penalties. Step 3, manage premiums and payments. To begin, which state do you live in, and what is your birth month and year?"
    voice_lang = "en-US"
    button_label = "🔊 Listen to Welcome Message"
    playing_label = "▶️ Reading in English..."
elif current_lang == "Español":
    welcome_msg = "¡Hola y bienvenido! Soy su guía de Medicare Compass. Entender Medicare por primera vez puede ser confuso, pero lo guiaré en 3 sencillos pasos:\n\n• **Paso 1**: Elegir el mejor plan.\n• **Paso 2**: Calcular su calendario y evitar multas.\n• **Paso 3**: Manejar primas y pagos.\n\nPara comenzar el Paso 1, ¿en qué estado vive y cuál es su mes y año de nacimiento?"
    voice_msg_text = "¡Hola y bienvenido! Soy su guía de Medicare Compass. Lo guiaré en 3 sencillos pasos: Paso 1, elegir el mejor plan. Paso 2, calcular su calendario y evitar multas. Paso 3, manejar primas y pagos. Para comenzar, ¿en qué estado vive y cuál es su mes y año de nacimiento?"
    voice_lang = "es-ES"
    button_label = "🔊 Escuchar mensaje de bienvenida"
    playing_label = "▶️ Leyendo en español..."
elif current_lang == "한국어":
    welcome_msg = "안녕하세요! 당신의 메디케어 나침반 가이드입니다. 메디케어를 처음 접하시면 복잡하게 느껴지실 수 있지만, 3단계에 걸쳐 쉽게 안내해 드리겠습니다:\n\n• **1단계**: 나에게 맞는 플랜 찾기\n• **2단계**: 신청 기한 확인 및 벌금 예방\n• **3단계**: 보험료 및 납부 관리\n\n1단계를 시작하기 위해, 현재 거주하시는 주와 생년월일을 알려주시겠어요?"
    voice_msg_text = "안녕하세요! 당신의 메디케어 나침반 가이드입니다. 메디케어를 3단계에 걸쳐 쉽게 안내해 드리겠습니다. 1단계 나에게 맞는 플랜 찾기, 2단계 신청 기한 확인 및 벌금 예방, 3단계 보험료 및 납부 관리. 먼저 현재 거주하시는 주와 생년월일을 알려주시겠어요?"
    voice_lang = "ko-KR"
    button_label = "🔊 환영 메시지 듣기"
    playing_label = "▶️ 한국어로 읽는 중..."
elif current_lang == "繁體中文":
    welcome_msg = "您好！我是您的 Medicare 智慧導覽助手。第一次接觸 Medicare 覺得複雜很正常，請放心，我會分三個步驟帶您一步步了解：\n\n• **第一步**：評估 Traditional Medicare 與 Advantage 哪種適合您。\n• **第二步**：算出您的黃金申辦時間軸，避開遲辦罰款。\n• **第三步**：教您處理保費與 Deductible 繳費。\n\n我們就從第一步開始！請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？"
    voice_msg_text = "您好！我是您的 Medicare 智慧導覽助手。第一次接觸 Medicare 覺得複雜很正常，請放心，我會分三個步驟帶您一步步了解：第一步，評估哪種方案適合您。第二步，算出黃金申辦時間軸避開罰款。第三步，教您處理保費與繳費。我們就從第一步開始！請問您目前居住在哪一個州？以及您的出生年月是什麼時候呢？"
    voice_lang = "zh-TW"
    button_label = "🔊 點擊收聽親切語音導覽"
    playing_label = "▶️ 正在朗讀中..."
else:
    welcome_msg = "您好！我是您的 Medicare 智慧导览助手。第一次接触 Medicare 觉得复杂很正常，请放心，我会分三个步骤带您一步步了解：\n\n• **第一步**：评估 Traditional Medicare 与 Advantage 哪种适合您。\n• **第二步**：算出您的黄金申办时间轴，避开迟办罚款。\n• **第三步**：教您处理保费与 Deductible 缴费。\n\n我们就从第一步开始！请问您目前居住在哪一个州（或 Zip Code）？以及您的出生年月是什么时候呢？"
    voice_msg_text = "您好！我是您的 Medicare 智慧导览助手。第一次接触 Medicare 觉得复杂很正常，请放心，我会分三个步骤带您一步步了解：第一步，评估哪种方案适合您。第二步，算出黄金申办时间轴避开罚款。第三步，教您处理保费与缴费。我们就从第一步开始！请问您目前居住在哪一个州？以及您的出生年月是什么时候呢？"
    voice_lang = "zh-CN"
    button_label = "🔊 点击收聽亲切语音导览"
    playing_label = "▶️ 正在朗读中..."

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]

# 7. 顯示過往對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. 徹底解決語言錯置：動態帶入該語言的專屬文字與語音腳本
tts_html = f"""
<div style="margin-bottom: 15px;">
    <button id="speak-btn" onclick="playSpeech()" style="
        background-color: #2E7D32;
        color: white;
        border: none;
        padding: 12px 20px;
        font-size: 15px;
        font-weight: bold;
        border-radius: 8px;
        cursor: pointer;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        display: inline-flex;
        align-items: center;
        gap: 8px;
    ">
        {button_label}
    </button>
</div>

<script>
function playSpeech() {{
    if ('speechSynthesis' in window) {{
        window.speechSynthesis.cancel();
        var text = "{voice_msg_text}";
        var utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "{voice_lang}";
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        
        var btn = document.getElementById('speak-btn');
        btn.innerText = "{playing_label}";
        btn.style.backgroundColor = "#1565C0";
        
        utterance.onend = function() {{
            btn.innerText = "{button_label}";
            btn.style.backgroundColor = "#2E7D32";
        }};
        
        utterance.onerror = function() {{
            btn.innerText = "{button_label}";
            btn.style.backgroundColor = "#2E7D32";
        }};

        window.speechSynthesis.speak(utterance);
    }} else {{
        alert("Speech synthesis is not supported in this browser.");
    }}
}}
</script>
"""
components.html(tts_html, height=70)

# 9. 圖片上傳區塊
if current_lang == "English":
    upload_label = "📸 Upload photo of Medicare card, policy, or SSA letter (optional):"
elif current_lang == "Español":
    upload_label = "📸 Subir foto de tarjeta de Medicare o carta de SSA (opcional):"
elif current_lang == "한국어":
    upload_label = "📸 메디케어 카드, 편지, 또는 서류 사진 업로드 (선택 사항):"
elif current_lang == "繁體中文":
    upload_label = "📸 拍照或上傳 Medicare 保單 / SSA 官方信件照片（選填）："
else:
    upload_label = "📸 拍照或上传 Medicare 保单 / SSA 官方信件照片（选填）："

uploaded_file = st.file_uploader(upload_label, type=["jpg", "jpeg", "png"])
img_data = None
if uploaded_file:
    img_data = Image.open(uploaded_file)
    st.image(img_data, caption="Loaded", use_column_width=True)

# 10. 對話輸入框
if current_lang == "English":
    input_placeholder = "Type your state/birthdate or reply here..."
elif current_lang == "Español":
    input_placeholder = "Escriba su estado/fecha de nacimiento aquí..."
elif current_lang == "한국어":
    input_placeholder = "거주 주 및 생년월일을 입력해 주세요..."
elif current_lang == "繁體中文":
    input_placeholder = "請輸入您的居住州與出生年月，或點選手機麥克風 🎙️..."
else:
    input_placeholder = "请输入您的居住州与出生年月，或点击手机麦克风 🎙️..."

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

# 11. 下載紀錄
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
