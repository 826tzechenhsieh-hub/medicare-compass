import calendar
import datetime
from datetime import timedelta
import re
import urllib.parse
from PIL import Image
import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components


# --------------------------------------------------
# 1. AI 回應清洗與衛生處理函式 (強效防草稿與思考過程洩漏)
# --------------------------------------------------
def clean_response(text: str) -> str:
    """过滤 AI 内部的思考过程、草稿标签与 Prompt 残留"""
    if not text:
        return ""
    
    text = re.sub(r"<(think|thought)>.*?</\1>", "", text, flags=re.DOTALL)
    
    patterns = [
        r"User Profile:.*?\n",
        r"Key Constraint Checklist:.*?\n",
        r"Personal Medicare Timeline:.*?\n",
        r"Persona/Role:.*?\n",
        r"\(Self-Correction\):.*?\n",
        r"Final Content Plan:.*?\n",
        r"Comparison Table:.*?\n",
        r"Key decision making question:.*?\n",
        r"```json.*?```",
        r"^\s*[\*\-]?\s*Directly print.*$",
        r"^\s*[\*\-]?\s*Markdown bullets\?.*$",
        r"^\s*[\*\-]?\s*Final Polish\..*$",
        r"^\s*[\*\-]?\s*Self-Correction:.*$",
    ]
    
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
    return cleaned.strip()

def sanitize_ai_output(raw_text, target_lang="English"):
  if not raw_text:
    return raw_text

  content_anchors = [
      "Hello!",
      "In New Jersey",
      "In California",
      "In Virginia",
      "Path 1:",
      "Path 2:",
      "Option 1:",
      "Option 2:",
      "Actionable Steps",
      "How to Apply:",
      "Where to Apply:",
      "To give you the most accurate",
      "Which state do you live in?",
      "您好",
      "你好",
      "¡Hola",
      "안녕하세요",
  ]

  for anchor in content_anchors:
    if anchor in raw_text:
      idx = raw_text.rfind(anchor)
      candidate = raw_text[idx:].strip()
      if len(candidate) > 15 and not any(
          bad in candidate
          for bad in [
              "*Review against rules:*",
              "*Final Polish:*",
              "*Correction on",
              "*Final Content Construction:*",
          ]
      ):
        return candidate

  lines = raw_text.split("\n")
  clean_lines = []
  bad_keywords = [
      "*Review against rules:*",
      "*Final Polish:*",
      "*Correction on",
      "*Final Content Construction:*",
      "*Ready.*",
      "*One more check:*",
      "*Constraint Check:*",
      "*Final check on rules:*",
      "User's goal:",
      "Constraint:",
      "Instruction:",
      "Concise bullet points?",
      "No drafts",
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
      if "generateContent" in m.supported_generation_methods:
        valid_models.append(m.name)
  except Exception:
    pass

  if not valid_models:
    valid_models = ["gemini-1.5-flash", "models/gemini-1.5-flash"]

  strict_system_instruction = (
        f"You are Medicare Compass, an expert assistant.\nLanguage: {target_lang}.\n"
        "Task: Present Medicare choices concisely.\n\n"
        "CRITICAL OUTPUT RULES:\n"
        "1. NEVER output internal system logic, user profiles, timeline tags, or checklists (e.g., 'User Profile:', 'Key Constraint Checklist:').\n"
        "2. DO NOT show thinking process or meta details to the user.\n"
        "3. START IMMEDIATELY with direct, warm, and friendly Medicare guidance for the user.\n\n"
        "FINAL OUTPUT FORMAT:\n"
        "1. A Summary Comparison table contrasting Pathway A vs Pathway B.\n"
        "2. 2 Key Decision-Making Questions.\n"
        "3. 1 Official Enrollment Tip."
    )

  last_exception = None
  for m_name in valid_models:
    try:
      model = genai.GenerativeModel(
          model_name=m_name, system_instruction=strict_system_instruction
      )

      formatted_history = []
      if "messages" in st.session_state:
        for m in st.session_state.messages[:-1]:
          role = "user" if m["role"] == "user" else "model"
          formatted_history.append(
              {"role": role, "parts": [str(m["content"])]}
          )

      chat = model.start_chat(history=formatted_history)

      if img_data:
        response = model.generate_content([user_input, img_data])
      else:
        response = chat.send_message(user_input)

      raw_text = response.text
      clean_text = sanitize_ai_output(
          clean_response(raw_text), target_lang=target_lang
      )
      return clean_text

    except Exception as inner_e:
      last_exception = inner_e
      continue

  if last_exception:
    raise last_exception


# --------------------------------------------------
# 2. Page Configuration & Custom CSS (視覺顏色優化)
# --------------------------------------------------
st.set_page_config(page_title="Medicare Compass", page_icon="🧭", layout="centered")

# 強效強制置頂 JavaScript
components.html(
    """
    <script>
        function forceScrollTop() {
            var mainSec = window.parent.document.querySelector('section.main');
            if (mainSec) mainSec.scrollTop = 0;
            window.parent.scrollTo(0, 0);
        }
        forceScrollTop();
        setTimeout(forceScrollTop, 300);
        setTimeout(forceScrollTop, 800);
    </script>
    """,
    height=0,
)

st.markdown(
    """
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
        
        /* 雙色路徑卡片視覺樣式 (無 Tension 柔和色系) */
        .pathway-a-box {
            background-color: #f0f7ff;
            border-left: 6px solid #2563eb;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .pathway-b-box {
            background-color: #f0fdf4;
            border-left: 6px solid #16a34a;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .warning-card {
            background-color: #fffbe2;
            border-left: 5px solid #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .card-box {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# API Keys
primary_key = st.secrets.get("GEMINI_API_KEY", None)
if primary_key:
  genai.configure(api_key=primary_key)

# --------------------------------------------------
# 3. Sidebar Setup & 功能模組選單 (支援多語言同步)
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Language / 語言設定")
    current_lang = st.radio(
        "Select Language / 選擇語言:",
        ["English", "Español", "繁體中文", "簡體中文", "한국어"],
        index=0,
        key="selected_language",
    )

    st.markdown("---")

    nav_title_map = {
        "English": "🧩 Navigation Modules",
        "Español": "🧩 Módulos de Navegación",
        "한국어": "🧩 탐색 모듈",
        "簡體中文": "🧩 功能导航模块",
        "繁體中文": "🧩 功能導航模組",
    }

    nav_label_map = {
        "English": "Select Service / Module:",
        "Español": "Seleccionar módulo:",
        "한국어": "모듈 선택:",
        "簡體中文": "请选择服务功能：",
        "繁體中文": "請選擇服務功能：",
    }

    m1_text = {
        "English": "💬 Main AI Navigator",
        "Español": "💬 Navegador AI Principal",
        "한국어": "💬 메인 AI 내비게이터",
        "簡體中文": "💬 智慧医保咨询 (Main AI)",
        "繁體中文": "💬 智慧醫保諮詢 (Main AI)",
    }[current_lang]

    m2_text = {
        "English": "🔄 Plan Switching Assistant (Why-When-How)",
        "Español": "🔄 Asistente de Cambio de Plan",
        "한국어": "🔄 플랜 변경 의사결정 도우미",
        "簡體中文": "🔄 Plan 转换决策助理 (Why-When-How)",
        "繁體中文": "🔄 Plan 轉換決策助理 (Why-When-How)",
    }[current_lang]

    m3_text = {
        "English": "📋 1-Page SHIP Prep Summary",
        "Español": "📋 Resumen de Preparación SHIP",
        "한국어": "📋 1페이지 SHIP 상담 준비표",
        "簡體中文": "📋 1-Page SHIP 咨询准备单",
        "繁體中文": "📋 1-Page SHIP 諮詢準備單",
    }[current_lang]

    m4_text = {
        "English": "📅 SHIP Appointment Reminder",
        "Español": "📅 Recordatorio de Cita SHIP",
        "한국어": "📅 SHIP 예약 일정 알림",
        "簡體中文": "📅 SHIP 预约行事历提醒",
        "繁體中文": "📅 SHIP 預約行事曆提醒",
    }[current_lang]

    st.markdown(f"### {nav_title_map[current_lang]}")
    selected_module_label = st.radio(
        nav_label_map[current_lang],
        [m1_text, m2_text, m3_text, m4_text],
        index=0,
    )

    if selected_module_label == m1_text:
        app_mode = "MAIN_AI"
    elif selected_module_label == m2_text:
        app_mode = "SWITCH_ASSISTANT"
    elif selected_module_label == m3_text:
        app_mode = "SHIP_PREP"
    else:
        app_mode = "CALENDAR_ICS"

    st.markdown("---")

    if (
        "saved_user_input" in st.session_state
        and st.session_state.saved_user_input
    ):
        st.info("Saved user input found.")
    st.markdown("---")

    upload_label_map = {
        "English": "📷 Take Photo or Upload Notice/Plan (Optional):",
        "Español": "📷 Tomar foto o cargar documento (Opcional):",
        "한국어": "📷 사진 촬영 또는 서류 업로드 (선택 사항):",
        "簡體中文": "📷 拍照或上传信件/保单照片 (选填):",
        "繁體中文": "📷 拍照或上傳信件/保單照片 (選填):",
    }
    uploaded_file = st.file_uploader(
        upload_label_map.get(current_lang, "📷 上傳照片"),
        type=["png", "jpg", "jpeg", "pdf"],
    )
    img_data = None
    if uploaded_file:
        try:
            img_data = Image.open(uploaded_file)
            st.success("File attached!")
        except Exception:
            pass
        st.warning("File uploaded.")

    if not primary_key:
        user_api_key = st.text_input("Gemini API Key:", type="password")
        if user_api_key:
            genai.configure(api_key=user_api_key)

    st.markdown("---")

    legal_title_map = {
        "English": "⚖️ Legal, Privacy & Notices",
        "Español": "⚖️ Avisos Legales y Privacidad",
        "한국어": "⚖️ 법적 고지 및 개인정보 보호",
        "簡體中文": "⚖️ 法律声明、隐私与非官方提示",
        "繁體中文": "⚖️ 法律聲明、隱私與非官方提示",
    }
    with st.expander(
        legal_title_map.get(current_lang, "⚖️ Legal & Privacy"), expanded=False
    ):
        st.caption("""
🔒 **Zero-Server-Data Privacy**:
We DO NOT store or track any of your inputs on our servers. Any remembered input is stored ONLY on your local browser device.

⚠️ **Anti-Fraud Notice**: Medicare will NEVER call/text asking for SSN or banking details.
ℹ️ **Disclaimer**: Educational guidance only; verify final choices with [Medicare.gov](https://www.medicare.gov).
🏛️ **Independent Tool**: Not affiliated with the US Government, CMS, or SSA.
---""")

    st.markdown("---")

    if app_mode == "MAIN_AI":
        summary_btn_map = {
            "English": "📝 Generate / Update Summary",
            "Español": "📝 Generar Resumen",
            "한국어": "📝 요약 생성",
            "簡體中文": "📝 生成/更新咨询总结",
            "繁體中文": "📝 生成/更新諮詢總結",
        }
        summary_btn_label = summary_btn_map.get(current_lang, summary_btn_map["繁體中文"])

        reset_btn_map = {
            "English": "🔄 Reset Conversation",
            "Español": "🔄 Reiniciar",
            "한국어": "🔄 대화 재설정",
            "簡體中文": "🔄 重新开始咨询",
            "繁體中文": "🔄 重新開始諮詢",
        }
        reset_label = reset_btn_map.get(current_lang, reset_btn_map["繁體中文"])

        if st.button(summary_btn_label, use_container_width=True, type="primary"):
            st.session_state.show_summary = True

        if st.button(reset_label, use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# --------------------------------------------------
# 4. 模組分流與執行邏輯
# --------------------------------------------------

# --------------------------------------------------
# 🅰️ 模組 1: 💬 智慧醫保諮詢 (Main AI Navigator)
# --------------------------------------------------
if app_mode == "MAIN_AI":
    top_container = st.container()

    with top_container:
        # 1. 顶部大标题 (大 Logo 居中)
        st.markdown("""
            <style>
            .header-box { text-align: center; padding: 10px 0; }
            .main-title { font-size: 2.3rem !important; font-weight: bold; color: #1E3A8A; }
            .sub-title { font-size: 1.0rem; color: #6B7280; margin-top: -5px; }
            </style>
            <div class="header-box">
                <span class="main-title">🧭 Medicare Compass</span>
                <div class="sub-title">Powered by CareCompass™</div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 2. 纯英文且无冗余的大字号折叠指南
        btn_text = "📖 Click to view: 1-Minute Medicare Guide"
        with st.expander(btn_text, expanded=False):
            st.markdown("### 🗺️ Major Pathways Guide")
            col1, col2 = st.columns(2)
            with col1:
                st.info("🟦 **Part A & B (Original Medicare)**\n\nBasic hospital & medical coverage provided by the federal government.")
                st.warning("🟨 **Part C (Medicare Advantage)**\n\nAll-in-one bundled plans provided by private insurers, often including Dental/Vision.")
            with col2:
                st.success("🟩 **Part D (Prescription Drug)**\n\nStandalone coverage specifically for prescription medications.")
                st.error("🟥 **Medigap (Medicare Supplement)**\n\nSupplemental plans that help pay Part A/B out-of-pocket costs.")

        st.markdown("---")

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
            if message["role"] in ["assistant", "model"]:
                st.markdown(clean_response(message["content"]))
            else:
                st.markdown(message["content"])

    if len(st.session_state.messages) == 0:
        q_caption_map = {
            "English": (
                "💡 **Quick Start**: Select identity, then enter **Birth Month/Year**"
                " & State** below:"
            ),
            "Español": (
                "💡 **Inicio rápido**: Elija su rol e ingrese **Mes/Año de"
                " nacimiento y Estado**:"
            ),
            "한국어": (
                "💡 **빠른 시작**: 신분을 선택하고 아래에 **생년월일 및 거주 주**를"
                " 입력하세요:"
            ),
            "簡體中文": (
                "💡 **快速开始**: 请选择身份，并在下方输入**出生年月与居住州**："
            ),
            "繁體中文": (
                "💡 **快速開始**: 請選擇身份，並在下方輸入**出生年月與居住州**："
            ),
        }
        st.caption(q_caption_map.get(current_lang, "💡 Quick Start:"))

        col_start1, col_start2 = st.columns(2)
    with col_start1:
      btn1_label = "👴 " + (
          "Applying for Myself"
          if current_lang == "English"
          else (
              "我是长者本人"
              if current_lang == "簡體中文"
              else (
                  "我是長者本人"
                  if current_lang == "繁體中文"
                  else (
                      "Solicitando para mí"
                      if current_lang == "Español"
                      else "본인 신청"
                  )
              )
          )
      )
      btn_type1 = (
          "primary"
          if st.session_state.user_role_type == "self"
          else "secondary"
      )
      if st.button(btn1_label, use_container_width=True, type=btn_type1):
        st.session_state.user_role_type = "self"
        st.rerun()

    with col_start2:
      btn2_label = "👨‍👩‍👧 " + (
          "Helping Family / Parents"
          if current_lang == "English"
          else (
              "我是帮家人/父母"
              if current_lang == "簡體中文"
              else (
                  "我是幫家人/父母"
                  if current_lang == "繁體中文"
                  else (
                      "Ayudando a mi familia"
                      if current_lang == "Español"
                      else "가족 도와드리기"
                  )
              )
          )
     )
        btn_type2 = (
            "primary"
            if st.session_state.user_role_type == "family"
            else "secondary"
        )
        if st.button(btn2_label, use_container_width=True, type=btn_type2):
            st.session_state.user_role_type = "family"
            st.rerun()

    prompt = None

    if st.session_state.get("saved_user_input"):
        st.markdown("<br>", unsafe_allow_html=True)
        quick_btn_label = (
            f"⚡ 點擊直接使用上次記憶提交: {st.session_state.saved_user_input}"
        )
        if st.button(
            quick_btn_label, type="primary", use_container_width=True
        ):
            prompt = st.session_state.saved_user_input

    # ------------------------------------------------------------------
    # 修正 1: 輸入框 Placeholder (改為僅 Month/Year, 無固定 Date)
    # ------------------------------------------------------------------
    has_history = len(st.session_state.get("messages", [])) > 0
    if not has_history:
        if current_lang == "繁體中文":
            input_placeholder = (
                "✍️ 請輸入出生年月與居住州 (例如: 08/1961, NJ) ..."
            )
        elif current_lang == "簡體中文":
            input_placeholder = (
                "✍️ 请输入出生年月与居住州 (例如: 08/1961, NJ) ..."
            )
        elif current_lang == "Español":
            input_placeholder = (
                "✍️ Ingrese su mes/año de nacimiento y estado (p. ej. 08/1961, NJ) ..."
            )
        elif current_lang == "한국어":
            input_placeholder = (
                "✍️ 생년월과 주를 입력하세요 (예: 08/1961, NJ) ..."
            )
        else:
            input_placeholder = (
                "✍️ Please enter Birth Month/Year & State (e.g. 08/1961, NJ) ..."
            )
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

    prompt = None
    input_prompt = st.chat_input(input_placeholder)

    if input_prompt:
        role_prefix = (
            "[Applying for Myself] "
            if st.session_state.get("user_role_type") == "self"
            else "[Helping Family/Parents] "
        )
        prompt = role_prefix + input_prompt
        st.session_state.saved_user_input = prompt

    if prompt or uploaded_file:
        user_text = prompt if prompt else "Please review this uploaded document."

        if (
            not st.session_state.messages
            or st.session_state.messages[-1]["content"] != user_text
        ):
            st.session_state.messages.append({"role": "user", "content": user_text})

        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant", avatar="🧭"):
            with st.spinner("Analyzing..."):
                date_match = re.search(r"(\d{1,2})/(?:\d{1,2}/)?(\d{4})", user_text)
                is_first_input = len(st.session_state.messages) <= 2

                if date_match and is_first_input:
                    try:
                        month = int(date_match.group(1))
                        year = int(date_match.group(2))
                        turn_65_year = year + 65

                        start_m = month - 3 if month > 3 else month - 3 + 12
                        start_y = turn_65_year if month > 3 else turn_65_year - 1
            end_m = month + 3 if month <= 9 else month + 3 - 12
            end_y = turn_65_year if month <= 9 else turn_65_year + 1

            start_m_name = calendar.month_name[start_m]
            end_m_name = calendar.month_name[end_m]
            birth_m_name = calendar.month_name[month]
            end_day = calendar.monthrange(end_y, end_m)[1]

            # 🔧 修正 2: Step 2 導引文字白話化 (移除抽象的 Lifestyle)
            final_output = (
                f"### 🗓️ Your Personalized Medicare Timeline\n\n"
                f"**Key Milestones:**\n"
                f"* **Turning 65**: {birth_m_name} {turn_65_year}\n"
                f"* **Initial Enrollment Period (IEP)**: **{start_m_name} 1,"
                f" {start_y} – {end_m_name} {end_day}, {end_y}** (7-Month"
                " Window)\n\n"
                f"**Recommended Next Steps:**\n"
                f"* **Step 1**: Check active employer coverage (if still"
                " working) to see if you can delay Part B.\n"
                f"* **Step 2**: Compare **Pathway 🅰️ Total Freedom to See Any"
                " Doctor (Original Medicare + Medigap)** vs. **Pathway 🅱️"
                " All-in-One Bundled Package (Medicare Advantage)** based on"
                " your need for cross-state doctor choices or prescription"
                " drugs."
            )
          except Exception:
            final_output = generate_clean_response(
                user_text, target_lang=current_lang, img_data=uploaded_file
            )
        else:
          raw_response = generate_clean_response(
              user_text, target_lang=current_lang, img_data=uploaded_file
          )
          tip_suffix = (
              "\n\n💡 *Tip: Once you've chosen your preferred pathway, submit"
              " your official enrollment online at [SSA.gov](https://www.ssa.gov).*"
          )
          final_output = raw_response.strip() + tip_suffix

        st.markdown(final_output)
        st.session_state.messages.append(
            {"role": "model", "content": final_output}
        )
        st.rerun()

  if st.session_state.show_summary and len(st.session_state.messages) >= 2:
    st.markdown("---")
    st.markdown(
        "<h2 style='text-align: center; color: #1E3A8A;'>📋 您的 Medicare"
        " 評估總結與官方通道</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ 官方申辦入口與免費中立輔導</h4>
            <ul style='line-height: 1.9; font-size: 18px;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>線上申請 Medicare Part A & B 官方通道</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov 官網帳號與選 Plan 入口</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>尋找您所在州的 SHIP 1對1 免費中立輔導 (ShipHelp.org)</a></li>
            </ul>
        </div>
    """,
        unsafe_allow_html=True,
    )

    user_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") == "user"
    ]
    ai_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") in ["assistant", "model"]
    ]

    pretty_summary_html = (
        "<div style='background-color: #F8FAFC; border: 1px solid #CBD5E1;"
        " padding: 25px; border-radius: 12px; font-size: 19px; line-height:"
        " 1.8;'>"
    )

    if user_msgs:
      pretty_summary_html += (
          "<h4 style='color: #0F172A; margin-top:0; font-size: 20px;'>📌"
          " 您的核心背景與需求：</h4><ul>"
      )
      for u in user_msgs:
        pretty_summary_html += f"<li style='margin-bottom: 8px;'>{u}</li>"
      pretty_summary_html += (
          "</ul><hr style='border: none; border-top: 1px solid #CBD5E1;"
          " margin: 20px 0;'>"
      )

    if ai_msgs:
      pretty_summary_html += (
          "<h4 style='color: #0F172A; font-size: 20px;'>💡 Advisor"
          " 避坑建議與方案總結：</h4>"
      )
      formatted_last_ai = ai_msgs[-1].replace("\n", "<br>")
      pretty_summary_html += (
          "<div style='background-color: #FFFFFF; padding: 20px; border-radius:"
          f" 8px; border: 1px solid #E2E8F0;'>{formatted_last_ai}</div>"
      )

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
      role_title = (
          "Compass Advisor"
          if m["role"] in ["assistant", "model"]
          else "User"
      )
      full_log_text += (
          f"[{role_title}]:\n{m['content']}\n\n" + "-" * 40 + "\n\n"
      )

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs(
        ["⚡ 1-Page Summary (精簡卡片)", "📄 Full Conversation Log (完整記錄)"]
    )

    with tab1:
      st.markdown("<br>", unsafe_allow_html=True)
      st.markdown(pretty_summary_html, unsafe_allow_html=True)
      st.markdown("<br>", unsafe_allow_html=True)

      col1, col2 = st.columns(2)
      with col1:
        st.download_button(
            "📥 下載 1頁精簡總結 (TXT)",
            data=short_summary_text,
            file_name="medicare_summary.txt",
            use_container_width=True,
        )
      with col2:
        st.markdown(
            f'<a href="{mailto_url}" target="_blank"><button'
            ' style="width:100%; height:46px; border-radius:8px;'
            ' background-color:#2563EB; color:white; border:none;'
            ' cursor:pointer; font-size:17px; font-weight:bold;">✉️'
            " 發送到我的郵箱</button></a>",
            unsafe_allow_html=True,
        )

    with tab2:
      st.markdown("<br>", unsafe_allow_html=True)
      st.text_area(
          "完整對話記錄 (Full Log):",
          value=full_log_text,
          height=300,
          key="full_log_area",
      )
      st.download_button(
          "📥 下載完整對話記錄 (TXT)",
          data=full_log_text,
          file_name="medicare_full_log.txt",
          use_container_width=True,
      )

# --------------------------------------------------
# 🆕 模組 2: 🔄 Plan 轉換決策助理 (Switching Assistant)
# --------------------------------------------------
elif app_mode == "SWITCH_ASSISTANT":
  st.markdown("## 🔄 Medicare Plan Switching Assistant")
  st.caption(
      "Neutral & Objective Guidance: Evaluate Why, When, and How to change your"
      " Medicare Plan."
  )
  st.markdown("---")

  st.subheader("Step 1: 🔍 WHY - What is your primary reason for switching?")
  reason = st.selectbox(
      "Select the option that best describes your situation:",
      [
          "--- Select a Reason ---",
          "💰 Higher Costs (Premium, Copay, or Deductible increased)",
          (
              "🩺 Doctor/Hospital Out of Network (Primary doctor no longer"
              " accepted)"
          ),
          (
              "🏠 Life Change/Relocation (Moved to new ZIP Code, retired, or"
              " lost employer insurance)"
          ),
          (
              "💊 Drug Coverage Change (Need new specialty medication not"
              " covered)"
          ),
          "🤷 Rate Shopping (Looking for better value/coverage)",
      ],
  )

  if reason != "--- Select a Reason ---":
    st.write("---")
    st.subheader("Step 2: ⏰ WHEN - Time Window & Eligibility Check")

    move_recent = st.radio(
        "Have you moved, changed residence, or lost employer coverage in the"
        " last 60 days?",
        ["No", "Yes"],
    )

    if move_recent == "Yes":
      st.markdown(
          """
            <div class="warning-card">
                <strong>💡 Qualification Detected: You qualify for a SEP (Special Enrollment Period)!</strong><br>
                Because of your recent life event, you can switch plans for free within <b>60 days</b> of the change—no need to wait for the Fall Open Enrollment!
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.info("""
            📅 **Standard Time Windows:**
            * **AEP (Annual Enrollment Period: Oct 15 – Dec 7)**: Open to everyone to switch Part C/D plans.
            * **OEP (Advantage Open Enrollment: Jan 1 – Mar 31)**: Open to current Medicare Advantage members.
            """)

    st.write("---")
    st.subheader("Step 3: 🚀 HOW - Action Plan & Crucial Warnings")

    st.markdown(
        """
        <div class="card-box">
            <h4>📋 Crucial Warnings Before Switching</h4>
            <ul>
                <li><b>⚠️ Medical Underwriting Risk:</b> Switching from Medicare Advantage back to Original Medicare + Medigap may require health screening in most states, which could lead to denial or higher rates based on pre-existing conditions.</li>
                <li><b>💊 Formulary Check:</b> Always verify that your current medications are covered on the new plan's Formulary at Medicare.gov.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "💡 Next Step: Select '📋 1-Page SHIP Prep Summary' in the sidebar to"
        " export a 1-Page Summary for a local SHIP counselor!"
    )

# --------------------------------------------------
# 🆕 模組 3: 📋 1-Page SHIP 諮詢準備單 (SHIP Prep)
# --------------------------------------------------
elif app_mode == "SHIP_PREP":
  st.markdown("## 📋 1-Page SHIP Counseling Prep Form")
  st.caption(
      "Fill out this form while waiting for your SHIP appointment to generate a"
      " 1-Page Summary for 3x faster counseling!"
  )
  st.markdown("---")

  with st.form("ship_prep_form"):
    col1, col2 = st.columns(2)
    with col1:
      zip_code = st.text_input("ZIP Code", "90210")
      current_plan = st.text_input(
          "Current Plan Name", "e.g. UnitedHealthcare Medicare Advantage"
      )
    with col2:
      monthly_cost = st.text_input("Monthly Premium ($)", "0")
      primary_concern = st.text_input(
          "Primary Concern / Question",
          "Premium increased and drug copays are too high",
      )

    meds = st.text_area(
        "Current Medications (Name / Dosage / Frequency)",
        "1. Lipitor 20mg (Daily)\n2. Metformin 500mg (Twice daily)",
    )

    submitted = st.form_submit_button("Generate 1-Page Summary")

  if submitted:
    st.markdown("---")
    st.markdown(
        f"""
        <div class="card-box" style="border: 2px solid #2563eb; background-color: #ffffff;">
            <h3 style="text-align:center; color:#1e3a8a; margin-top:0;">🩺 Medicare Compass - SHIP Counseling Summary</h3>
            <hr>
            <p><b>📍 ZIP Code:</b> {zip_code} | <b>Current Plan:</b> {current_plan} (${monthly_cost}/mo)</p>
            <p><b>❓ Primary Concern:</b> {primary_concern}</p>
            <p><b>💊 Medication List:</b><br>{meds.replace(chr(10), '<br>')}</p>
            <hr>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom:0;">Zero-ad, privacy-first algorithm output. Print or screenshot this page for your SHIP appointment.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# 🆕 模組 4: 📅 SHIP 預約行事曆提醒 (Calendar ICS)
# --------------------------------------------------
elif app_mode == "CALENDAR_ICS":
  st.markdown("## 📅 SHIP Appointment Calendar Reminder (.ics)")
  st.caption(
      "Never forget your SHIP appointment! Add it directly to your Google or"
      " Apple Calendar with built-in prep notes."
  )
  st.markdown("---")

  col1, col2 = st.columns(2)
  with col1:
    appt_date = st.date_input(
        "Appointment Date", datetime.date.today() + timedelta(days=14)
    )
  with col2:
    appt_time = st.time_input("Appointment Time", datetime.time(10, 0))

  location = st.text_input(
      "Location / Method", "e.g. Phone Call / Local Community Center"
  )

  if st.button("📅 Generate Calendar File (.ics)", type="primary"):
    dt_start = datetime.datetime.combine(appt_date, appt_time)
    dt_end = dt_start + timedelta(hours=1)

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Medicare Compass//SHIP Appointment//EN
BEGIN:VEVENT
SUMMARY:🩺 SHIP Medicare Official Counseling
DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}
DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}
LOCATION:{location}
DESCRIPTION:📌 Checklist for Counseling:\\n1. Bring your 1-Page Summary from Medicare Compass App.\\n2. Bring all current prescription drug bottles.\\n3. Bring your Medicare Red, White & Blue card.
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:SHIP Counseling tomorrow! Remember to bring your 1-Page Summary and drug bottles.
END:VALARM
END:VEVENT
END:VCALENDAR"""

    st.download_button(
        label="💾 Download .ics File (Click to Add to Calendar)",
        data=ics_content,
        file_name="ship_appointment.ics",
        mime="text/calendar",
        use_container_width=True,
    )
    st.success(
        "Calendar file created! Click above to download and open on your phone"
        " or computer."
    )

# --------------------------------------------------
# 5. 頁面置頂 JavaScript 執行
# --------------------------------------------------
st.markdown(
    """
    <script>
        function forceScrollTop() {
            var mainSec = window.parent.document.querySelector("section.main");
            if (mainSec) mainSec.scrollTop = 0;
            window.parent.scrollTo(0, 0);
        }
        forceScrollTop();
        setTimeout(forceScrollTop, 300);
    </script>
""",
    unsafe_allow_html=True,
)
