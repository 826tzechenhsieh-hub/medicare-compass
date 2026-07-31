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

    if user_lang == "English":
        st.markdown("# 🧭 Medicare Compass™")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    elif user_lang == "Español":
        st.markdown("# 🧭 Medicare Compass™")
        st.caption("##### *desarrollado por Care Compass™*")
        st.info("📢 **Propósito de la aplicación**: ¡Diseñada para personas mayores que cumplen 65 años y sus familias para navegar por Medicare en 3 pasas claros!")
    elif user_lang == "한국어":
        st.markdown("# 🧭 Medicare Compass™ 메디케어 나침반")
        st.caption("##### *powered by Care Compass™*")
        st.info("📢 **앱 목적**: 65세가 되는 어르신과 가족이 3단계로 미국 메디케어를 쉽게 이해할 수 있도록 돕습니다!")
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

    if current_lang == "English":
        upload_label = "📎 Upload Document / Photo (Optional):"
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
            st.success("File attached successfully!")
        except Exception:
            st.warning("File uploaded.")

    st.markdown("---")

    if current_lang == "English":
        st.caption("""
🔒 **Privacy Commitment & Zero Retention**:
We DO NOT save or store any of your personal inputs or logs. All data is permanently cleared immediately upon closing your browser or clicking Reset.

ℹ️ **Disclaimer & Notice**:
Information provided is strictly for educational guidance. Regulations change continuously; users MUST always double-check and confirm final details with [Medicare.gov](https://www.medicare.gov) or SSA.

🏛️ **Non-Governmental Entity Notice**:
Medicare Compass™ is an independent educational tool, not affiliated with the US Government, CMS, or SSA.
        """)
    elif current_lang == "Español":
        st.caption("""
🔒 **Compromiso de Privacidad**:
NO guardamos ni almacenamos ninguno de sus datos personales. Todos los datos se borran de forma permanente al cerrar el navegador o hacer clic en Reiniciar.

ℹ️ **Aviso Legal**:
La información se proporciona estrictamente con fines educativos. Las regulaciones cambian continuamente; los usuarios SIEMPRE deben verificar los detalles finales con [Medicare.gov](https://www.medicare.gov).

🏛️ **Entidad No Gubernamental**:
Medicare Compass™ es una herramienta educativa independiente y no está afiliada al Gobierno de EE. UU., CMS o SSA.
        """)
    elif current_lang == "한국어":
        st.caption("""
🔒 **개인정보 보호 약속**:
귀하의 개인 정보나 대화 기록을 저장하지 않습니다. 브라우저를 닫거나 재설정을 누르면 모든 데이터가 즉시 영구 삭제됩니다.

ℹ️ **면책 조항**:
제공되는 정보는 교육 안내용입니다. 규정은 지속적으로 변경되므로 사용자는 항상 [Medicare.gov](https://www.medicare.gov)에서 최종 세부 정보를 확인해야 합니다.

🏛️ **비정부 기관 안내**:
Medicare Compass™는 독립적인 교육 도구이며 미국 정부, CMS 또는 SSA와 관련이 없습니다.
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
    if current_lang == "English":
        st.markdown("# 🧭 Medicare Compass™")
        st.info("📢 **App Purpose**: Designed for seniors turning 65 and families to navigate US Medicare smoothly across 3 clear steps!")
    elif current_lang == "Español":
        st.markdown("# 🧭 Medicare Compass™")
        st.info("📢 **Propósito de la aplicación**: ¡Diseñada para personas mayores que cumplen 65 años y sus familias para navegar por Medicare en 3 pasos claros!")
    elif current_lang == "한국어":
        st.markdown("# 🧭 Medicare Compass™ 메디케어 나침반")
        st.info("📢 **앱 목적**: 65세가 되는 어르신과 가족이 3단계로 미국 메디케어를 쉽게 이해할 수 있도록 돕습니다!")
    elif current_lang == "簡體中文":
        st.markdown("# 🧭 Medicare Compass™ 医保指南针")
        st.info("📢 **本工具宗旨**：专为即将满 65 岁长者与退休家庭设计！陪伴您分三步骤轻松了解申办流程、避开终身迟办罚款。")
    else:
        st.markdown("# 🧭 Medicare Compass™ 醫保指南針")
        st.info("📢 **本工具宗旨**：專為即將滿 65 歲長者與退休家庭設計！陪伴您分三步驟輕鬆了解申辦流程、避開終身遲辦罰款。")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    if current_lang == "English":
        with col1:
            st.markdown("### 1️⃣ Step 1: When")
            st.caption("IEP Timing, Date of Birth & State.")
        with col2:
            st.markdown("### 2️⃣ Step 2: What")
            st.caption("Needs, Coverage & Plan Comparison.")
        with col3:
            st.markdown("### 3️⃣ Step 3: How")
            st.caption("Step-by-step Application & Payment.")
    elif current_lang == "Español":
        with col1:
            st.markdown("### 1️⃣ Paso 1: Cuándo")
            st.caption("Fechas clave de IEP, fecha de nacimiento y estado.")
        with col2:
            st.markdown("### 2️⃣ Paso 2: Qué")
            st.caption("Necesidades, cobertura y comparación de planes.")
        with col3:
            st.markdown("### 3️⃣ Paso 3: Cómo")
            st.caption("Solicitud paso a paso y pago.")
    elif current_lang == "한국어":
        with col1:
            st.markdown("### 1️⃣ 1단계: 언제")
            st.caption("IEP 가입 기간, 생년월일 및 거주 주.")
        with col2:
            st.markdown("### 2️⃣ 2단계: 무엇을")
            st.caption("보장 필요성 및 플랜 비교.")
        with col3:
            st.markdown("### 3️⃣ 3단계: 어떻게")
            st.caption("단계별 신청 방법 및 납부 설정.")
    elif current_lang == "簡體中文":
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

    # 1-Minute Medicare Map
    expander_title_map = {
        "English": "🗺️ **1-Minute Medicare Map**",
        "Español": "🗺️ **Mapa de Medicare de 1 Minuto**",
        "한국어": "🗺️ **1분 메디케어 한눈에 보기**",
        "簡體中文": "🗺️ **1分钟医保地图对照**",
        "繁體中文": "🗺️ **1分鐘醫保地圖對照**"
    }
    
    with st.expander(expander_title_map.get(current_lang, "🗺️ **1-Minute Medicare Map**"), expanded=True):
        if current_lang == "English":
            st.markdown("""
* **Original Medicare (Government)**: Part A (Hospital) + Part B (Medical - 80% coverage, 20% gap).
* **Part C (Medicare Advantage)**: Private all-in-one plans (A + B + usually D).
* **Part D (Prescription Drugs)**: Standalone drug coverage.
* **Medigap (Supplement)**: Private plans to cover Part B's 20% gap.
            """)
        elif current_lang == "Español":
            st.markdown("""
* **Original Medicare (Gobierno)**: Parte A (Hospital) + Parte B (Médica - 80% de cobertura, ¡20% de brecha!).
* **Parte C (Medicare Advantage)**: Planes privados todo en uno (A + B + D).
* **Parte D (Medicamentos)**: Cobertura de medicamentos.
* **Medigap (Suplemento)**: Planes privados para cubrir la brecha del 20% de la Parte B.
            """)
        elif current_lang == "한국어":
            st.markdown("""
* **Original Medicare (정부 메디케어)**: Part A (병원) + Part B (의료 - 80% 보장, 20% 본인 부담).
* **Part C (Medicare Advantage)**: 민간 통합 플랜 (A + B + D).
* **Part D (처방약)**: 약품 보장.
* **Medigap (보충 보험)**: Part B의 20% 본인 부담금을 메워주는 민간 보험.
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
    q_caption_map = {
        "English": "💡 Quick start options:",
        "Español": "💡 Opciones de inicio rápido:",
        "한국어": "💡 빠른 시작 옵션:",
        "簡體中文": "💡 您也可以直接点选以下身份快速开始：",
        "繁體中文": "💡 您也可以直接點選以下身分快速開始："
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
                "English": "Hello! I am applying for myself and would like to start Step 1: When. Please calculate my enrollment deadlines.",
                "Español": "¡Hola! Estoy solicitando para mí y me gustaría comenzar el Paso 1: Cuándo. Por favor calcule mis fechas límite.",
                "한국어": "안녕하세요! 본인 신청입니다. 1단계를 시작하고 내 가입 마감일을 계산해 주세요.",
                "簡體中文": "您好！我是长者本人，准备开始 Step 1，请帮我计算申办期限！",
                "繁體中文": "您好！我是長者本人，準備開始 Step 1，請幫我計算申辦期限！"
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
                "English": "Hello! I am helping my parents start Step 1: When. What information do you need?",
                "Español": "¡Hola! Estoy ayudando a mis padres a comenzar el Paso 1. ¿Qué información necesita?",
                "한국어": "안녕하세요! 부모님 메디케어 신청을 돕고 있습니다. 1단계를 시작해 주세요.",
                "簡體中文": "您好！我是帮长辈查询的子女，请引导我们开始 Step 1！",
                "繁體中文": "您好！我是幫長輩查詢的子女，請引導我們開始 Step 1！"
            }
            quick_prompt = p2_map.get(current_lang)

has_user_replied = len(st.session_state.messages) > 0
if current_lang == "English":
    input_placeholder = "🎙️ Type your birth month/year and state here..." if not has_user_replied else "🎙️ Speak or type your reply here..."
elif current_lang == "Español":
    input_placeholder = "🎙️ Escriba su mes/año de nacimiento y estado aquí..."
elif current_lang == "한국어":
    input_placeholder = "🎙️ 여기에 출생 월/년 및 거주 주를 입력하세요..."
elif current_lang == "簡體中文":
    input_placeholder = "🎙️ 请输入您的居住州与出生年月..."
else:
    input_placeholder = "🎙️ 請輸入您的居住州與出生年月..."

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
