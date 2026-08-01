import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import urllib.parse
import re
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

# Typography & Styles (极致清爽 UI 样式)
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
        /* 隐藏 Streamlit 默认的 Header anchor 图标，保持通透 */
        .css-1544g2n {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Get API Keys
primary_key = st.secrets.get("GEMINI_API_KEY", None)
secondary_key = st.secrets.get("GEMINI_API_KEY_SECONDARY", None)

# 外科手術式文本清洗器
def sanitize_ai_output(raw_text, target_lang="English"):
    if not raw_text:
        return raw_text
    
    if target_lang in ["繁體中文", "簡體中文", "한국어", "Español"]:
        markers = ["您好", "你好", "안녕하세요", "¡Hola", "我們現在正式開始", "我们现在正式开始", "為了確保", "为了确保"]
        for marker in markers:
            if marker in raw_text:
                idx = raw_text.rfind(marker)
                clean_part = raw_text[idx:].strip()
                clean_part = re.sub(r'\s*\([^)]*\)\??\s*Yes\.', '', clean_part)
                clean_part = re.sub(r'\s*\(Explanation of IEP\)', '', clean_part)
                clean_part = re.sub(r'\s*\(The question\)', '', clean_part)
                clean_part = re.sub(r'\s*\(Closing/Process reminder\)', '', clean_part)
                clean_part = clean_part.strip().strip('"').strip('」')
                if len(clean_part) > 10:
                    return clean_part

    lines = raw_text.split('\n')
    clean_lines = []
    for line in lines:
        if not any(bad in line for bad in ["User:", "Status:", "Persona:", "Constraint", "Language requirement:", "Process rule:", "Goal of Step", "Warm tone?", "Calculates IEP"]):
            clean_lines.append(line)
    
    return "\n".join(clean_lines).strip()

def generate_clean_response(user_input, target_lang="English", img_data=None):
    keys_to_try = [k for k in [primary_key, secondary_key] if k]
    if not keys_to_try:
        raise ValueError("NO_API_KEY")

    last_exception = None

    lang_instruction_map = {
        "English": "Respond purely in English.",
        "Español": "Respond purely in Spanish.",
        "繁體中文": "請完全使用『繁體中文』回答，嚴禁使用簡體字與英文思考標註。",
        "簡體中文": "请完全使用『简体中文』回答，严禁使用繁体字与英文思考标签。",
        "한국어": "Respond purely in Korean."
    }
    lang_rule = lang_instruction_map.get(target_lang, "Respond in the target language.")

    # 官方标准的系统指令（独立隔离，绝不打印在界面上）
    system_instruction_text = f"""You are Medicare Compass, a warm, highly empathetic, human Medicare advisor. {lang_rule}
CRITICAL TIME ANCHOR: The CURRENT YEAR IS 2026.

STRICT OUTPUT RULE:
- NEVER print your internal thought process, scenario checklists, chain-of-thought, or analysis.
- Output ONLY the final conversational message directly to the user.

SUPPORTED USER SCENARIOS (Adapt dynamically based on user response):
1. Turning 65 in 2026 (Born 1961): Currently in Initial Enrollment Period (IEP).
2. Applying for Parents/Family: Ask for the family member's birth year/month with high empathy.
3. Early Planners (<65 years old): Explain IEP rules briefly and welcome early preparation.
4. Past 65 / Plan Switchers (>65 years old): Address Open Enrollment Period (AEP / Oct 15 - Dec 7) or Special Enrollment Periods (SEP).

EXPERT KNOWLEDGE TO EMBED NATIVELY WHEN RELEVANT:
- Traditional Medicare vs. Part C Advantage in Rehab / SNF: Warn that Advantage plans require Prior Authorization and commercial insurers often DENY coverage after 20-30 days in Rehab, forcing out-of-pocket costs or discharge.
- Durable Medical Equipment (DME - Walkers, Hospital Beds, Wheelchairs): NEVER buy privately first! Doctors must write a prescription, and hospital social workers must order via Medicare suppliers before discharge.
- ER & Ambulance: Medicare Part B covers 80% of medically necessary ambulances. Private taxis/rides are NOT covered.
- Travel & Overseas: Traditional Medicare + Medigap covers nationwide US doctors (great for snowbirds/travel). Advantage (Part C) has strict local network limits outside home state. Original Medicare has 0 coverage overseas; Medigap Plan G/N offers up to $50,000 lifetime emergency travel coverage."""

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
                    # 使用 1.5/2.5 官方原生 system_instruction 参数
                    model = genai.GenerativeModel(
                        model_name=m_name,
                        system_instruction=system_instruction_text
                    )
                    
                    # 组装纯粹的用户与模型对话历史
                    formatted_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        formatted_history.append({"role": role, "parts": [m["content"]]})
                        
                    chat = model.start_chat(history=formatted_history)
                    
                    if img_data:
                        response = model.generate_content([user_input, img_data])
                        raw_output = response.text
                    else:
                        response = chat.send_message(user_input)
                        raw_output = response.text
                        
                    return sanitize_ai_output(raw_output, target_lang=target_lang)
                except Exception as inner_e:
                    last_exception = inner_e
                    continue
        except Exception as outer_e:
            last_exception = outer_e
            continue

    if last_exception:
        raise last_exception

# -------------------------------------------------------------------
# 3. Sidebar Setup (极致瘦身与折叠收纳)
# -------------------------------------------------------------------
with st.sidebar:
    # 唯一的品牌 Logo Header
    st.markdown("# 🧭 Medicare Compass™")
    st.caption("##### *powered by Care Compass™*")
    
    user_lang = st.session_state.get("selected_language", "English")

    st.markdown("---")

    # 1. 语言设定
    st.markdown("### 🌐 Language / 語言設定")
    current_lang = st.radio(
        "Select Language / 選擇語言:",
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        index=0,
        key="selected_language"
    )

    st.markdown("---")

    # 2. 附件上传
    if current_lang == "English":
        upload_label = "📎 Upload Notice or Plan Photo (Optional):"
    elif current_lang == "Español":
        upload_label = "📎 Cargar documento / foto (Opcional):"
    elif current_lang == "한국어":
        upload_label = "📎 서류 / 사진 업로드 (선택 사항):"
    elif current_lang == "簡體中文":
        upload_label = "📎 上传信件或保单照片（选填）："
    else:
        upload_label = "📎 上傳信件或保單照片（選填）："

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

    # 3. 法律与隐私条款收纳折叠抽屉（Modal / Expander）
    legal_title_map = {
        "English": "⚖️ Legal, Privacy & Notices",
        "Español": "⚖️ Avisos Legales y Privacidad",
        "한국어": "⚖️ 법적 고지 및 개인정보 보호",
        "簡體中文": "⚖️ 法律声明、隐私与非官方提示",
        "繁體中文": "⚖️ 法律聲明、隱私與非官方提示"
    }
    
    with st.expander(legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False):
        if current_lang == "English":
            st.caption("""
🔒 **Zero-Data Retention Privacy**:
We DO NOT store or track any of your personal inputs or photos. All data is permanently cleared immediately when you close or reset the app.

⚠️ **Official Fraud Warning**:
Medicare will NEVER call or text to ask for your Social Security Number or banking info.

ℹ️ **Disclaimer**:
Educational guidance only. Regulations change; users MUST verify final choices with [Medicare.gov](https://www.medicare.gov) or SSA.

🏛️ **Independent Tool**:
Medicare Compass™ is not affiliated with the US Government, CMS, or SSA.
            """)
        elif current_lang == "Español":
            st.caption("""
🔒 **Compromiso de Privacidad**:
NO almacenamos sus datos personales. Todo se borra permanentemente al cerrar o reiniciar.

⚠️ **Aviso Anti-Fraude**:
Medicare NUNCA lo llamará para pedirle su Número de Seguro Social.

ℹ️ **Aviso Legal**:
Guía educativa únicamente. Verifique siempre con [Medicare.gov](https://www.medicare.gov).

🏛️ **Entidad Independiente**:
No afiliada al Gobierno de EE. UU. o SSA.
            """)
        elif current_lang == "한국어":
            st.caption("""
🔒 **개인정보 보호**:
귀하의 개인 정보를 저장하지 않습니다. 브라우저를 닫으면 모든 데이터가 삭제됩니다.

⚠️ **사기 예방 경고**:
메디케어는 절대로 사회보장번호를 전화로 요구하지 않습니다.

ℹ️ **면책 조항**:
교육용 안내입니다. 최종 사항은 [Medicare.gov](https://www.medicare.gov)에서 확인하세요.

🏛️ **독립 도구**:
미국 정부 기관과 관련이 없습니다.
            """)
        elif current_lang == "簡體中文":
            st.caption("""
🔒 **零数据留存隐私承诺**：
本工具完全不储存任何个人输入资料或照片。页面关闭或重置后即刻永久清除。

⚠️ **防诈骗官方警示**：
Medicare 绝不会打电话或发短信向您索取社安号 (SSN) 或银行卡号。

ℹ️ **免责声明**：
本工具仅供教育与导航参考，政策每年调整，请务必于 [Medicare.gov](https://www.medicare.gov) 核对。

🏛️ **非官方独立声明**：
Medicare Compass™ 为独立辅助工具，不代表美国政府或 SSA 官方机构。
            """)
        else:
            st.caption("""
🔒 **零數據留存隱私承諾**：
本工具完全不儲存任何個人輸入資料或照片。頁面關閉或重置後即刻永久清除。

⚠️ **防詐騙官方警示**：
Medicare 絕不會打電話或發簡訊向您索取社安號 (SSN) 或銀行帳號。

ℹ️ **免責聲明**：
本工具僅供教育與導航參考，政策每年動態調整，請務必至 [Medicare.gov](https://www.medicare.gov) 核對。

🏛️ **非官方獨立聲明**：
Medicare Compass™ 為獨立輔助工具，不代表美國政府或 SSA 官方機構。
            """)

    st.markdown("---")

    # 4. 总结与重置按钮
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
# 4. Main Header & 1-Minute Medicare Map (主界面极简清爽化)
# -------------------------------------------------------------------
top_container = st.container()

with top_container:
    # 顶部 3 步骤导航卡片
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

    # 1分钟医保地图与避坑指南折叠卡片
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
* **🚨 Ambulance & Emergency**: Part B covers 80% for medically necessary emergencies; private taxis/rides are NOT covered.
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
* **🚨 구급차**: 의료상 긴급한 경우에만 80% 보장.
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
    q_caption_map = {
        "English": "💡 Quick start options:",
        "Español": "💡 Opciones de inicio rápido:",
        "한국어": "💡 빠른 시작 옵션:",
        "簡體中文": "💡 您可以点选以下身份快速开始：",
        "繁體中文": "💡 您可以點選以下身分快速開始："
    }
    st.caption(q_caption_map.get(current_lang, "💡 Quick start options:"))
    
    col_start1, col_start2 = st.columns(2)
    with col_start1:
        btn1_map = {
            "English": "👴 I'm applying for myself",
            "Español": "👴 Estoy solicitando para mí",
            "한국어": "👴 본인 신청 (1단계 시작)",
            "簡體中文": "👴 我是长者本人（开始 Step 1 导览）",
            "繁體中文": "👴 我是長者本人（開始 Step 1 導覽）"
        }
        if st.button(btn1_map.get(current_lang, "👴 Apply for myself")):
            p1_map = {
                "English": "Hello! I am applying for myself and would like to start Step 1.",
                "Español": "¡Hola! Estoy solicitando para mí y me gustaría comenzar el Paso 1.",
                "한국어": "안녕하세요! 본인 신청입니다. 1단계를 시작합니다.",
                "簡體中文": "您好！我是长者本人，准备开始 Step 1。",
                "繁體中文": "您好！我是長者本人，準備開始 Step 1。"
            }
            quick_prompt = p1_map.get(current_lang)

    with col_start2:
        btn2_map = {
            "English": "👨‍👩‍👧 I'm helping my parents",
            "Español": "👨‍👩‍👧 Estoy ayudando a mis padres",
            "한국어": "👨‍👩‍👧 부모님 도와드리기 (1단계 시작)",
            "簡體中文": "👨‍👩‍👧 我是帮父母查询的子女（开始 Step 1）",
            "繁體中文": "👨‍👩‍👧 我是幫父母查詢的子女（開始 Step 1）"
        }
        if st.button(btn2_map.get(current_lang, "👨‍👩‍👧 Help parents")):
            p2_map = {
                "English": "Hello! I am helping my family member start Step 1.",
                "Español": "¡Hola! Estoy ayudando a mi familiar a comenzar el Paso 1.",
                "한국어": "안녕하세요! 가족 메디케어 신청을 위해 1단계를 시작합니다.",
                "簡體中文": "您好！我是帮家人查询的，准备开始 Step 1。",
                "繁體中文": "您好！我是幫家人查詢的，準備開始 Step 1。"
            }
            quick_prompt = p2_map.get(current_lang)

has_user_replied = len(st.session_state.messages) > 0
if current_lang == "English":
    input_placeholder = "🎙️ Type birth month/year and state here..." if not has_user_replied else "🎙️ Type your reply here..."
elif current_lang == "Español":
    input_placeholder = "🎙️ Escriba su mes/año de nacimiento y estado aquí..."
elif current_lang == "한국어":
    input_placeholder = "🎙️ 여기에 출생 월/년 및 거주 주를 입력하세요..."
elif current_lang == "簡體中文":
    input_placeholder = "🎙️ 请输入居住州与出生年月..."
else:
    input_placeholder = "🎙️ 請輸入居住州與出生年月..."

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

    with st.chat_message("assistant"):
        with st.spinner("Medicare Compass is analyzing..."):
            try:
                clean_text = generate_clean_response(user_text, target_lang=current_lang, img_data=img_data)
                st.markdown(clean_text)
                st.session_state.messages.append({"role": "assistant", "content": clean_text})
                st.rerun()
            except Exception as e:
                st.error(f"Notice: {e}")

# -------------------------------------------------------------------
# 7. Consultation Summary & Official Portals
# -------------------------------------------------------------------
if st.session_state.show_summary and len(st.session_state.messages) >= 2:
    st.markdown("---")
    st.header("📋 Consultation Summary & Official Portals")

    # 官方申请直通入口卡片
    st.info("🏛️ **Official Application Portals / 官方申请快速通道**: \n\n"
            "• **Social Security Administration (SSA)**: [Apply for Medicare Part A & B Online](https://www.ssa.gov/medicare) \n"
            "• **Official Medicare Portal**: [Create / Sign in to Medicare.gov](https://www.medicare.gov)")

    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    for m in st.session_state.messages:
        role_title = "Compass Advisor" if m["role"] in ["assistant", "model"] else "User"
        full_log_text += f"[{role_title}]:\n{m['content']}\n\n" + "-"*40 + "\n\n"

    short_summary_text = "【Medicare Compass - Summary】\n\n"
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

    tab1, tab2 = st.tabs(["⚡ 1-Page Summary", "📄 Full Log"])

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
