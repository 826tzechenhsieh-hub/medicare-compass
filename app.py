import re
import urllib.parse
import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# 1. 定義 AI 回應清洗函式
def clean_response(text: str) -> str:
    if not text:
        return ""

    # 移除 <think>...</think> 或 <thought>...</thought> 標籤及其內容
    text = re.sub(r"<(think|thought)>.*?</\1>", "", text, flags=re.DOTALL)

    # 移除殘留的 Draft 關鍵字行與 Metadata
    metadata_patterns = [
        r"^\s*[\*•\-]\s*(User|Constraint|Role|Salutation|NJ Context|Closing|Greeting|Persona|Context|Check|Did I|Follow-up):.*$\n?",
        r"^\s*[\*•\-]\s*(Concise bullet points|No wall of text|Expert knowledge|Current date|Ensure tone|Wait, did I).*$\n?",
        r"^\s*(User Goal|Context|Persona|Check against rules|\(Self-Correction\)|Final Content Plan|User wants to know|Constraint \d+:|Ensure tone is).*$\n?",
    ]

    for pattern in metadata_patterns:
        text = re.sub(pattern, "", text, flags=re.MULTILINE | re.IGNORECASE)

    return text.strip()


# --------------------------------------------------
# 下方接你原本的 st.set_page_config(...)
# --------------------------------------------------
# --------------------------------------------------
# 2. 下方接著是你原本的 Streamlit 主程式 (st.set_page_config 等)
# --------------------------------------------------

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
            padding-top: 1.0rem !important;
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
            line-height: 1.7 !important;
        }
        .stButton>button {
            font-size: 18px !important;
            padding: 10px 20px !important;
            border-radius: 8px !important;
        }
        .stChatInput input {
            font-size: 19px !important;
        }
        .css-1544g2n {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Get API Keys
primary_key = st.secrets.get("GEMINI_API_KEY", None)
secondary_key = st.secrets.get("GEMINI_API_KEY_SECONDARY", None)

# 超強力外科手術截斷函數
def sanitize_ai_output(raw_text, target_lang="English"):
    if not raw_text:
        return raw_text
    
    content_anchors = [
        "Hello!", "In New Jersey", "In California", "In Virginia",
        "Path 1:", "Path 2:", "Option 1:", "Option 2:", 
        "Actionable Steps", "How to Apply:", "Where to Apply:",
        "To give you the most accurate", "Which state do you live in?",
        "您好", "你好", "¡Hola", "안녕하세요"
    ]
    
    for anchor in content_anchors:
        if anchor in raw_text:
            idx = raw_text.rfind(anchor)
            candidate = raw_text[idx:].strip()
            if len(candidate) > 15 and not any(bad in candidate for bad in ["*Review against rules:*", "*Final Polish:*", "*Correction on", "*Final Content Construction:*"]):
                return candidate

    lines = raw_text.split('\n')
    clean_lines = []
    bad_keywords = [
        "*Review against rules:*", "*Final Polish:*", "*Correction on", "*Final Content Construction:*",
        "*Ready.*", "*One more check:*", "*Constraint Check:*", "*Final check on rules:*",
        "User's goal:", "Constraint:", "Instruction:", "Concise bullet points?", "No drafts"
    ]
    
    for line in lines:
        stripped = line.strip()
        if any(bad.lower() in stripped.lower() for bad in bad_keywords):
            continue
        clean_lines.append(line)
        
    final_text = "\n".join(clean_lines).strip()
    return final_text if final_text else raw_text.strip()

def generate_clean_response(user_input, target_lang="English", img_data=None):
    valid_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                valid_models.append(m.name)
    except Exception:
        pass

    if not valid_models:
        valid_models = ["gemini-1.5-flash", "models/gemini-1.5-flash"]

    # 嚴格的系統指令
    strict_system_instruction = (
        f"You are Medicare Compass, an expert assistant.\n"
        f"Language: {target_lang}.\n"
        f"Task: Directly print the user's Medicare timeline in clear Markdown bullets.\n"
        f"DO NOT reflect, re-state user input, check formatting, or include any 'Yes/No' evaluations."
    )

    last_exception = None
    for m_name in valid_models:
        try:
            model = genai.GenerativeModel(
                model_name=m_name, 
                system_instruction=strict_system_instruction
            )

            formatted_history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [str(m["content"])]})

            chat = model.start_chat(history=formatted_history)

            if img_data:
                response = model.generate_content([user_input, img_data])
            else:
                response = chat.send_message(user_input)

            raw_text = response.text
            clean_text = sanitize_ai_output(clean_response(raw_text), target_lang=target_lang)
            return clean_text

        except Exception as inner_e:
            last_exception = inner_e
            continue

    if last_exception:
        raise last_exception

# -------------------------------------------------------------------
# 3. Sidebar Setup
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🧭 Medicare Compass™")
    st.caption("##### *powered by Care Compass™*")
    
    st.markdown("---")

    st.markdown("### 🌐 Language / 語言設定")
    current_lang = st.radio(
        "Select Language / 選擇語言:",
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        index=0,
        key="selected_language"
    )

    st.markdown("---")

    if "saved_user_input" in st.session_state and st.session_state.saved_user_input:
        st.markdown(f"💾 **本地設備記憶 (Local Memory)**:\n`{st.session_state.saved_user_input}`")
        if st.button("🗑️ 清除本地記憶 (Clear Memory)", use_container_width=True):
            st.session_state.saved_user_input = ""
            st.rerun()
        st.markdown("---")

    if current_lang == "English":
        upload_label = "📎 Take Photo or Upload Notice/Plan (Optional):"
    elif current_lang == "Español":
        upload_label = "📎 Tomar foto o cargar documento (Opcional):"
    elif current_lang == "한국어":
        upload_label = "📎 사진 촬영 또는 서류 업로드 (선택 사항):"
    elif current_lang == "簡體中文":
        upload_label = "📎 拍照或上传信件/保单照片（选填）："
    else:
        upload_label = "📎 拍照或上傳信件/保單照片（選填）："

    uploaded_file = st.file_uploader(upload_label, type=["png", "jpg", "jpeg", "pdf"])
    img_data = None
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            st.success("File attached!")
        except Exception:
            st.warning("File uploaded.")

    if not primary_key:
        primary_key = st.text_input("Gemini API Key:", type="password")

    st.markdown("---")

    legal_title_map = {
        "English": "⚖️ Legal, Privacy & Notices",
        "Español": "⚖️ Avisos Legales y Privacidad",
        "한국어": "⚖️ 법적 고지 및 개인정보 보호",
        "簡體中文": "⚖️ 法律声明、隐私与非官方提示",
        "繁體中文": "⚖️ 法律聲明、隱私與非官方提示"
    }
    
    with st.expander(legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False):
        st.caption("""
🔒 **Zero-Server-Data Privacy**:
We DO NOT store or track any of your inputs on our servers. Any remembered input is stored ONLY on your local browser device.

⚠️ **Anti-Fraud Notice**: Medicare will NEVER call/text asking for SSN or banking details.
ℹ️ **Disclaimer**: Educational guidance only; verify final choices with [Medicare.gov](https://www.medicare.gov).
🏛️ **Independent Tool**: Not affiliated with the US Government, CMS, or SSA.
        """)

    st.markdown("---")

    if current_lang == "English":
        summary_btn_label = "📋 Generate / Update Summary"
        reset_label = "🔄 Reset Conversation"
    elif current_lang == "Español":
        summary_btn_label = "📋 Generar / Actualizar Resumen"
        reset_label = "🔄 Reiniciar Conversación"
    elif current_lang == "한국어":
        summary_btn_label = "📋 요약 생성 / 업데이트"
        reset_label = "🔄 대화 재설정"
    elif current_lang == "簡體中文":
        summary_btn_label = "📋 生成 / 更新咨询总结"
        reset_label = "🔄 重新开始咨询"
    else:
        summary_btn_label = "📋 生成 / 更新諮詢總結"
        reset_label = "🔄 重新開始諮詢"

    if st.button(summary_btn_label, use_container_width=True, type="primary"):
        st.session_state.show_summary = True

    if st.button(reset_label, use_container_width=True):
        st.session_state.messages = []
        st.session_state.show_summary = False
        st.rerun()

# -------------------------------------------------------------------
# 4. Main Header & 1-Minute Medicare Map
# -------------------------------------------------------------------
top_container = st.container()

with top_container:
    col1, col2, col3 = st.columns(3)
    if current_lang == "English":
        with col1:
            st.markdown("### 1️⃣ Step 1: When")
            st.caption("IEP Timing, Date of Birth & State.")
        with col2:
            st.markdown("### 2️⃣ Step 2: What")
            st.caption("Needs, Coverage & Plan Options.")
        with col3:
            st.markdown("### 3️⃣ Step 3: How")
            st.caption("Application & Official Channels.")
    elif current_lang == "Español":
        with col1:
            st.markdown("### 1️⃣ Paso 1: Cuándo")
            st.caption("Fechas clave, fecha de nacimiento y estado.")
        with col2:
            st.markdown("### 2️⃣ Paso 2: Qué")
            st.caption("Necesidades y comparación de planes.")
        with col3:
            st.markdown("### 3️⃣ Paso 3: Cómo")
            st.caption("Solicitud paso a paso.")
    elif current_lang == "한국어":
        with col1:
            st.markdown("### 1️⃣ 1단계: 언제")
            st.caption("IEP 기간, 생년월일 및 거주 주.")
        with col2:
            st.markdown("### 2️⃣ 2단계: 무엇을")
            st.caption("보장 필요성 및 플랜 비교.")
        with col3:
            st.markdown("### 3️⃣ 3단계: 어떻게")
            st.caption("신청 방법 및 수속.")
    elif current_lang == "簡體中文":
        with col1:
            st.markdown("### 1️⃣ 第一步：WHEN 参保时机")
            st.caption("出生年月、居住州与黄金期限。")
        with col2:
            st.markdown("### 2️⃣ 第二步：WHAT 方案比对")
            st.caption("医疗需求与两大路径解析。")
        with col3:
            st.markdown("### 3️⃣ 第三步：HOW 申办执行")
            st.caption("官方申请流程与快速通道。")
    else:
        with col1:
            st.markdown("### 1️⃣ 第一步：WHEN 參保時機")
            st.caption("出生年月、居住州與黃金期限。")
        with col2:
            st.markdown("### 2️⃣ 第二步：WHAT 方案比對")
            st.caption("醫療需求與兩大路徑解析。")
        with col3:
            st.markdown("### 3️⃣ 第三步：HOW 申辦執行")
            st.caption("官方申請流程與快速通道。")

    st.markdown("---")

    expander_title_map = {
        "English": "🗺️ **1-Minute Medicare Map & Real-Life Pitfall Guide**",
        "Español": "🗺️ **Mapa de Medicare de 1 Minuto y Guía Práctica**",
        "한국어": "🗺️ **1분 메디케어 한눈에 보기 및 핵심 주의사항**",
        "簡體中文": "🗺️ **1分钟医保地图与真实场景避坑指南**",
        "繁體中文": "🗺️ **1分鐘醫保地圖與真實場景避坑指南**"
    }
    
    with st.expander(expander_title_map.get(current_lang, "🗺️ **1-Minute Medicare Map**"), expanded=True):
        if current_lang == "English":
            st.markdown("""
* **Original Medicare (Gov)**: Part A (Hospital) + Part B (Medical - 80% paid, 20% gap NO limit).
* **Part C (Medicare Advantage)**: Private all-in-one plans. *⚠️ Note: Insurers require Prior Auth and may DENY rehab coverage midway after 20-30 days.*
* **Medigap (Supplement)**: Covers Part B's 20% gap with nationwide doctor access (Ideal for travel/snowbirds).
* **🏠 Discharge Devices (DME - Walker/Bed)**: *Do NOT buy privately!* Must have a doctor's prescription before discharge to get reimbursed.
* **🚨 Ambulance & Emergency**: Part B covers 80% for medically necessary emergencies only; private taxis/rides are NOT covered.
            """)
        elif current_lang == "Español":
            st.markdown("""
* **Original Medicare (Gobierno)**: Parte A (Hospital) + Parte B (Médica - 80% cubierto, 20% sin límite).
* **Parte C (Medicare Advantage)**: Planes privados. *⚠️ Requiere autorización previa y puede denegar la rehabilitación.*
* **Medigap (Suplemento)**: Cubre el 20% de la Parte B con acceso médico nacional (Ideal para viajes).
* **🏠 Equipos del hogar (DME)**: Requiere receta médica antes del alta hospitalaria.
* **🚨 Ambulancias**: Cubre el 80% solo para emergencias médicas reales.
            """)
        elif current_lang == "한국어":
            st.markdown("""
* **Original Medicare (정부)**: Part A (병원) + Part B (의료 - 80% 보장, 20% 본인 부담).
* **Part C (Medicare Advantage)**: 민간 통합 플랜. *⚠️ 재활 입원 중 보험사의 사전 승인거절 위험 주의.*
* **Medigap (보충 보험)**: Part B 20% 부담금 보장 및 전국 병원 이용 가능.
* **🏠 퇴원 후 가정용 의료기기 (DME)**: 퇴원 전 의사 처방전 필수.
            """)
        elif current_lang == "簡體中文":
            st.markdown("""
* **Original Medicare (传统红蓝卡)**：Part A (住院) + Part B (门诊，政府给付 80%，自付 20% 无上限)。
* **Part C (Medicare Advantage 优惠套餐)**：私人保险包办。*⚠️ 警告：需 Prior Authorization，康复中心 (Rehab) 30天后极易遭保险公司拒付 (Deny) 逼迫自费。*
* **Medigap (补充保险)**：填补 20% 缺口，全美看诊无网络限制（适合跨州居住/频繁旅行）。
* **🏠 出院居家设备 (DME - 病床/助行器)**：*切勿自行购买！* 必须由医生开处方并由社工预订方可报销。
* **🚨 急诊与救护车**：Part B 仅报销“医疗紧急且必要”的救护车 80%；私人叫车或非紧急不可报销。
            """)
        else:
            st.markdown("""
* **Original Medicare (傳統紅藍卡)**：Part A (住院) + Part B (門診，政府給付 80%，自付 20% 無上限)。
* **Part C (Medicare Advantage 優惠套餐)**：私人保險包辦。*⚠️ 警告：需 Prior Authorization，康復中心 (Rehab) 30天後極易遭保險公司拒付 (Deny) 逼迫自費。*
* **Medigap (補充保險)**：填補 20% 缺口，全美看診無網絡限制（適合跨州居住/頻繁旅行）。
* **🏠 出院居家設備 (DME - 病床/助行器)**：*切勿自行購買！* 必須由醫生開處方並由社工預訂方可報銷。
* **🚨 急診與救護車**：Part B 僅報銷「醫療緊急且必要」的救護車 80%；私人叫車或非緊急不可報銷。
            """)

    st.markdown("---")

# -------------------------------------------------------------------
# 5. Message History & Local Memory Integration
# -------------------------------------------------------------------
if "user_role_type" not in st.session_state:
    st.session_state.user_role_type = "self"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "saved_user_input" not in st.session_state:
    st.session_state.saved_user_input = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

has_user_replied = len(st.session_state.messages) > 0

if len(st.session_state.messages) == 0:
    q_caption_map = {
        "English": "💡 **Step 1 Quick Start**: Choose who you are inquiring for, then enter details below:",
        "Español": "💡 **Paso 1 Inicio rápido**: Elija para quién consulta e ingrese los datos abajo:",
        "한국어": "💡 **1단계 빠른 시작**: 신청 대상을 선택한 후, 아래에 정보를 입력하세요:",
        "簡體中文": "💡 **Step 1 快速开始**：请先选择查询身份，并在下方输入**出生年月与居住州**：",
        "繁體中文": "💡 **Step 1 快速開始**：請先選擇查詢身分，並在下方輸入**出生年月與居住州**："
    }
    st.caption(q_caption_map.get(current_lang, "💡 Quick Start:"))
    
    col_start1, col_start2 = st.columns(2)
    with col_start1:
        btn1_label = "👴 " + ("Applying for Myself" if current_lang == "English" else "我是长者本人" if current_lang == "簡體中文" else "我是長者本人" if current_lang == "繁體中文" else "Solicitando para mí" if current_lang == "Español" else "본인 신청")
        btn_type1 = "primary" if st.session_state.user_role_type == "self" else "secondary"
        if st.button(btn1_label, use_container_width=True, type=btn_type1):
            st.session_state.user_role_type = "self"
            st.rerun()

    with col_start2:
        btn2_label = "👨‍👩‍👧 " + ("Helping Family / Parents" if current_lang == "English" else "我是帮家人/父母" if current_lang == "簡體中文" else "我是幫家人/父母" if current_lang == "繁體中文" else "Ayudando a mi familia" if current_lang == "Español" else "가족 도와드리기")
        btn_type2 = "primary" if st.session_state.user_role_type == "family" else "secondary"
        if st.button(btn2_label, use_container_width=True, type=btn_type2):
            st.session_state.user_role_type = "family"
            st.rerun()

    # 1. 安全初始化，防範 NameError
    prompt = None

    # 2. 本地記憶按鈕
    if st.session_state.get("saved_user_input"):
        st.markdown("<br>", unsafe_allow_html=True)
        quick_btn_label = f"⚡ 點擊直接使用上次記憶提交: {st.session_state.saved_user_input}"
        if st.button(quick_btn_label, type="primary", use_container_width=True):
            prompt = st.session_state.saved_user_input

    # 3. 輸入框 Placeholder
    # 動態 Placeholder: 根據選擇的語言與狀態顯示提示
    has_user_replied = len(st.session_state.get("messages", [])) > 0 or bool(st.session_state.get("saved_user_input"))
    if not has_user_replied:
        if current_lang == "繁體中文":
            input_placeholder = "✍️ 請輸入出生年月與居住州 (例如: 8/26/1961, NJ) ..."
        elif current_lang == "簡體中文":
            input_placeholder = "✍️ 请输入出生年月与居住州 (例如: 8/26/1961, NJ) ..."
        elif current_lang == "Español":
            input_placeholder = "✍️ Ingrese su fecha de nacimiento y estado (p. ej. 8/26/1961, NJ) ..."
        elif current_lang == "한국어":
            input_placeholder = "✍️ 생년월일과 주를 입력하세요 (예: 8/26/1961, NJ) ..."
        else:
            input_placeholder = "✍️ Please enter Date of Birth & State (e.g. 8/26/1961, NJ) ..."
    else:
        if current_lang == "繁體中文":
            input_placeholder = "💬 請輸入您想諮詢的 Medicare 問題..."
        elif current_lang == "簡體中文":
            input_placeholder = "💬 请输入您想咨询的 Medicare 问题..."
        elif current_lang == "Español":
            input_placeholder = "💬 Escriba su pregunta sobre Medicare..."
        elif current_lang == "한국어":
            input_placeholder = "💬 Medicare에 대해 질문을 입력하세요..."
        else:
            input_placeholder = "💬 Ask any follow-up question about Medicare..."

    input_prompt = st.chat_input(input_placeholder)

    if input_prompt:
        role_prefix = "[Applying for Myself] " if st.session_state.get("user_role_type") == "self" else "[Helping Family/Parents] "
        prompt = role_prefix + input_prompt
        st.session_state.saved_user_input = prompt

  # 4. 執行對話與呼叫 AI (第一階段極簡化 + 客製頭像，解決 Stuck 與頭像 M 問題)
    if prompt or uploaded_file:
        user_text = prompt if prompt else "Please review this uploaded document."
        
        if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})

        with st.chat_message("user"):
            st.markdown(user_text)

        # 使用自訂的 🧭 圖示取代預設的灰底 M
        with st.chat_message("assistant", avatar="🧭"):
            with st.spinner("Analyzing..."):
                import re
                import calendar

                date_match = re.search(r'(\d{1,2})/(?:(\d{1,2})/)?(\d{4})', user_text)
                
                # 初次輸入：只專注在「時間軸」與「Step 1 / Step 2」，不放多餘 Tip 與容易卡住的提問
                if date_match and len(st.session_state.messages) <= 2:
                    try:
                        month = int(date_match.group(1))
                        year = int(date_match.group(3))
                        turn_65_year = year + 65
                        
                        start_m = month - 3 if month > 3 else month - 3 + 12
                        start_y = turn_65_year if month > 3 else turn_65_year - 1

                        end_m = month + 3 if month <= 9 else month + 3 - 12
                        end_y = turn_65_year if month <= 9 else turn_65_year + 1

                        start_m_name = calendar.month_name[start_m]
                        end_m_name = calendar.month_name[end_m]
                        birth_m_name = calendar.month_name[month]
                        end_day = calendar.monthrange(end_y, end_m)[1]

                        # 將 Tip 移走，留到 Step 2 解答完畢後才出現
                        final_output = (
                            f"### 🗓️ Your Personalized Medicare Timeline\n\n"
                            f"**Key Milestones:**\n"
                            f"* **Turning 65**: {birth_m_name} {turn_65_year}\n"
                            f"* **Initial Enrollment Period (IEP)**: **{start_m_name} 1, {start_y} – {end_m_name} {end_day}, {end_y}** (7-Month Window)\n\n"
                            f"**Recommended Next Steps:**\n"
                            f"* **Step 1**: Check active employer coverage (if still working) to see if you can delay Part B.\n"
                            f"* **Step 2**: Compare **Original Medicare (+ Medigap)** vs. **Medicare Advantage** based on your doctor and drug needs."
                        )
                    except Exception:
                        final_output = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                else:
                    # 後續對話：正常的 AI 諮詢（在此階段的回答結尾會自動加上溫馨 Tip）
                    raw_response = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                    
                    # 只有在回答第二階段問題時，才把 Tip 附在最下方
                    tip_suffix = "\n\n💡 *Tip: Once you've chosen your preferred pathway, submit your official enrollment online at [SSA.gov](https://www.ssa.gov).*"
                    final_output = raw_response.strip() + tip_suffix

                st.markdown(final_output)
                st.session_state.messages.append({"role": "model", "content": final_output})
# -------------------------------------------------------------------
# 7. Consultation Summary & SHIP Official Portals
# -------------------------------------------------------------------
if st.session_state.show_summary and len(st.session_state.messages) >= 2:
    st.markdown("---")
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📋 您的 Medicare 評估總結與官方通道</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ 官方申辦入口與免費中立輔導</h4>
            <ul style='line-height: 1.9; font-size: 18px;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>線上申請 Medicare Part A & B 官方通道</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov 官網帳號與選 Plan 入口</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>尋找您所在州的 SHIP 1對1 免費中立輔導 (ShipHelp.org)</a></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    user_msgs = [m['content'] for m in st.session_state.messages if m.get('role') == 'user']
    ai_msgs = [m['content'] for m in st.session_state.messages if m.get('role') in ['assistant', 'model']]

    pretty_summary_html = "<div style='background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 25px; border-radius: 12px; font-size: 19px; line-height: 1.8;'>"
    
    if user_msgs:
        pretty_summary_html += "<h4 style='color: #0F172A; margin-top:0; font-size: 20px;'>📌 您的核心背景與需求：</h4><ul>"
        for u in user_msgs:
            pretty_summary_html += f"<li style='margin-bottom: 8px;'>{u}</li>"
        pretty_summary_html += "</ul><hr style='border: none; border-top: 1px solid #CBD5E1; margin: 20px 0;'>"

    if ai_msgs:
        pretty_summary_html += "<h4 style='color: #0F172A; font-size: 20px;'>💡 Advisor 避坑建議與方案總結：</h4>"
        formatted_last_ai = ai_msgs[-1].replace('\n', '<br>')
        pretty_summary_html += f"<div style='background-color: #FFFFFF; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0;'>{formatted_last_ai}</div>"
    
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
        full_log_text += f"[{role_title}]:\n{m['content']}\n\n" + "-"*40 + "\n\n"

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs(["⚡ 1-Page Summary (精簡卡片)", "📄 Full Conversation Log (完整記錄)"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(pretty_summary_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 下載 1頁精簡總結 (TXT)", data=short_summary_text, file_name="medicare_summary.txt", use_container_width=True)
        with col2:
            st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="width:100%; height:46px; border-radius:8px; background-color:#2563EB; color:white; border:none; cursor:pointer; font-size:17px; font-weight:bold;">✉️ 發送到我的郵箱</button></a>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area("完整對話記錄 (Full Log):", value=full_log_text, height=300, key="full_log_area")
        st.download_button("📥 下載完整對話記錄 (TXT)", data=full_log_text, file_name="medicare_full_log.txt", use_container_width=True)

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
