# translations.py

sidebar_labels = {
    "English": {"header": "### 🌐 Language Settings", "select": "Select Language:"},
    "Español": {"header": "### 🌐 Configuración de Idioma", "select": "Seleccionar idioma:"},
    "繁體中文": {"header": "### 🌐 語言設定", "select": "請選擇語言："},
    "簡體中文": {"header": "### 🌐 语言设置", "select": "请选择语言："},
    "한국어": {"header": "### 🌐 언어 설정", "select": "언어 선택:"}
}

guide_labels = {
    "English": {
        "btn_text": "📖 Click to view: 1-Minute Medicare Guide",
        "guide_title": "### 🗺️ Major Pathways Guide",
        "p_ab": "🟦 **Part A & B (Original Medicare)**\n\nBasic hospital & medical coverage provided by the federal government.",
        "p_c": "🟨 **Part C (Medicare Advantage)**\n\nAll-in-one bundled plans provided by private insurers, often including Dental/Vision.",
        "p_d": "🟩 **Part D (Prescription Drug)**\n\nStandalone coverage specifically for prescription medications.",
        "medigap": "🟥 **Medigap (Medicare Supplement)**\n\nSupplemental plans that help pay Part A/B out-of-pocket costs."
    },
    "繁體中文": {
        "btn_text": "📖 點擊查看：1 分鐘 Medicare 快速指南",
        "guide_title": "### 🗺️ 主要方案指南",
        "p_ab": "🟦 **Part A & B (原始 Medicare)**\n\n由聯邦政府提供的基礎住院與醫療保障。",
        "p_c": "🟨 **Part C (Medicare Advantage/聯邦醫療保險優勢計畫)**\n\n由私人保險公司提供的全方位綜合計畫，通常包含牙科與視力福利。",
        "p_d": "🟩 **Part D (處方藥物)**\n\n專門針對處方藥物提供的獨立保險。",
        "medigap": "🟥 **Medigap (聯邦醫療補充保險)**\n\n協助支付 Part A/B 原始 Medicare 未涵蓋之自付費用的補充計畫。"
    },
    "簡體中文": {
        "btn_text": "📖 点击查看：1 分钟 Medicare 快速指南",
        "guide_title": "### 🗺️ 主要方案指南",
        "p_ab": "🟦 **Part A & B (原始 Medicare)**\n\n由联邦政府提供的基础住院与医疗保障。",
        "p_c": "🟨 **Part C (Medicare Advantage/联邦医疗保险优势计划)**\n\n由私人保险公司提供的全方位综合计划，通常包含牙科与视力福利。",
        "p_d": "🟩 **Part D (处方药物)**\n\n专门针对处方药物提供的独立保险。",
        "medigap": "🟥 **Medigap (联邦医疗补充保险)**\n\n协助支付 Part A/B 原始 Medicare 未涵盖之自付费用的补充计划。"
    },
    "Español": {
        "btn_text": "📖 Haga clic para ver: Guía rápida de Medicare de 1 minuto",
        "guide_title": "### 🗺️ Guía de Vías Principales",
        "p_ab": "🟦 **Parte A y B (Medicare Original)**\n\nCobertura médica y hospitalaria básica proporcionada por el gobierno federal.",
        "p_c": "🟨 **Parte C (Medicare Advantage)**\n\nPlanes combinados 'todo en uno' ofrecidos por aseguradoras privadas, a menudo incluyen cobertura dental/visual.",
        "p_d": "🟩 **Parte D (Medicamentos Recetados)**\n\nCobertura independiente específicamente para medicamentos recetados.",
        "medigap": "🟥 **Medigap (Seguro Suplementario de Medicare)**\n\nPlanes suplementarios que ayudan a pagar los costos de bolsillo de la Parte A/B."
    },
    "한국어": {
        "btn_text": "📖 클릭하여 보기: 1분 Medicare 가이드",
        "guide_title": "### 🗺️ 주요 플랜 가이드",
        "p_ab": "🟦 **Part A & B (오리지널 Medicare)**\n\n연방 정부에서 제공하는 기본 병원 및 의료 보장.",
        "p_c": "🟨 **Part C (Medicare Advantage)**\n\n민간 보험사에서 제공하는 올인원 통합 플랜, 보통 치과/안과 혜택 포함.",
        "p_d": "🟩 **Part D (처방약)**\n\n처방약에 특화된 단독 보장 플랜.",
        "medigap": "🟥 **Medigap (Medicare 보충 보험)**\n\nPart A/B의 본인 부담금을 지불하는 데 도움이 되는 보충 플랜."
    }
}

m2_labels = {
    "English": {
        "title": "## 🔄 Medicare Plan Switching Assistant",
        "caption": "Neutral & Objective Guidance: Evaluate Why, When, and How to change your Medicare Plan.",
        "step1_title": "Step 1: 🔍 WHY - What is your primary reason for switching?",
        "step1_label": "Select the option that best describes your situation:",
        "reasons": [
            "--- Select a Reason ---",
            "💰 Higher Costs (Premium, Copay, or Deductible increased)",
            "🩺 Doctor/Hospital Out of Network (Primary doctor no longer accepted)",
            "🏠 Life Change/Relocation (Moved to new ZIP Code, retired, or lost employer insurance)",
            "💊 Drug Coverage Change (Need new specialty medication not covered)",
            "🤷 Rate Shopping (Looking for better value/coverage)"
        ],
        "step2_title": "Step 2: ⏰ WHEN - Time Window & Eligibility Check",
        "move_question": "Have you moved, changed residence, or lost employer coverage in the last 60 days?",
        "yes_no": ["No", "Yes"],
        "sep_alert": "<div class='warning-card'><strong>💡 Qualification Detected: You qualify for a SEP (Special Enrollment Period)!</strong><br>Because of your recent life event, you can switch plans for free within <b>60 days</b> of the change—no need to wait for the Fall Open Enrollment!</div>",
        "standard_windows": "📅 **Standard Time Windows:**\n* **AEP (Annual Enrollment Period: Oct 15 – Dec 7)**: Open to everyone to switch Part C/D plans.\n* **OEP (Advantage Open Enrollment: Jan 1 – Mar 31)**: Open to current Medicare Advantage members.",
        "step3_title": "Step 3: 🚀 HOW - Action Plan & Crucial Warnings",
        "warnings_box": "<div class='card-box'><h4>📋 Crucial Warnings Before Switching</h4><ul><li><b>⚠️ Medical Underwriting Risk:</b> Switching from Medicare Advantage back to Original Medicare + Medigap may require health screening in most states, which could lead to denial or higher rates based on pre-existing conditions.</li><li><b>💊 Formulary Check:</b> Always verify that your current medications are covered on the new plan's Formulary at Medicare.gov.</li></ul></div>",
        "next_step_tip": "💡 Next Step: Select '📋 1-Page SHIP Prep Summary' in the sidebar to export a 1-Page Summary for a local SHIP counselor!"
    },
    "繁體中文": {
        "title": "## 🔄 Medicare Plan 轉換決策助理",
        "caption": "中立且客觀的指引：評估為什麼 (Why)、何時 (When) 以及如何 (How) 更換您的 Medicare 計畫。",
        "step1_title": "步驟 1：🔍 WHY - 您想更換計畫的主要原因是什麼？",
        "step1_label": "請選擇最符合您目前狀況的選項：",
        "reasons": [
            "--- 請選擇原因 ---",
            "💰 費用調漲（保費、自付額或 Copay 上漲）",
            "🩺 醫師/醫院不在網路內（常用主治醫師不再合作）",
            "🏠 個人生活變更/搬家（搬到新郵遞區號區域、退休或失去雇主保險）",
            "💊 處方藥物保障變更（需要的新特效藥未涵蓋）",
            "🤷 比價與尋找更好保障（希望尋找性價比更高的方案）"
        ],
        "step2_title": "步驟 2：⏰ WHEN - 轉換時間窗口與資格確認",
        "move_question": "您是否在過去 60 天內搬家、變更居住地或失去了雇主團體保險？",
        "yes_no": ["否", "是"],
        "sep_alert": "<div class='warning-card'><strong>💡 符合特殊資格：您符合特殊登記期 (SEP)！</strong><br>由於您近期有重大生活變更，您可在事件發生的 <b>60 天內</b> 免費更換計畫，無需等待秋季年度公開登記期！</div>",
        "standard_windows": "📅 **標準轉換時間窗口：**\n* **AEP (年度公開登記期: 10月15日 – 12月7日)**：所有人皆可更換 C/D 部分計畫。\n* **OEP (Medicare Advantage 開放登記期: 1月1日 – 3月31日)**：僅限現有 Medicare Advantage 會員更換方案。",
        "step3_title": "步驟 3：🚀 HOW - 行動指南與重要風險提示",
        "warnings_box": "<div class='card-box'><h4>📋 更換計畫前的重要風險提示</h4><ul><li><b>⚠️ 健康審查風險 (Medical Underwriting)：</b> 若從 Medicare Advantage 換回 原始 Medicare + Medigap，在多數州需要通過健康核保，可能因既往病史被拒保或提高保費。</li><li><b>💊 處方藥物清單核對 (Formulary Check)：</b> 務必先至 Medicare.gov 官網確認您的常用藥物是否包含在新計畫的處方藥清單中。</li></ul></div>",
        "next_step_tip": "💡 下一步：點擊左側邊欄選單中的「📋 1-Page SHIP 諮詢準備單」，產出諮詢總結帶去給免費 SHIP 顧問！"
    },
    "簡體中文": {
        "title": "## 🔄 Medicare Plan 转换决策助理",
        "caption": "中立且客观的指引：评估为什么 (Why)、何时 (When) 以及如何 (How) 更换您的 Medicare 计划。",
        "step1_title": "步骤 1：🔍 WHY - 您想更换计划的主要原因是什么？",
        "step1_label": "请选择最符合您目前状况的选项：",
        "reasons": [
            "--- 请选择原因 ---",
            "💰 费用调涨（保费、自付款或 Copay 上涨）",
            "🩺 医生/医院不在网络内（常用主治医生不再合作）",
            "🏠 搬家/个人生活变更（搬到新邮编区域、退休或失去雇主保险）",
            "💊 处方药物保障变更（需要的新特效药未涵盖）",
            "🤷 比价与寻找更好保障（希望寻找性价比更高的方案）"
        ],
        "step2_title": "步骤 2：⏰ WHEN - 转换时间窗口与资格确认",
        "move_question": "您是否在过去 60 天内搬家、变更居住地或失去了雇主团体保险？",
        "yes_no": ["否", "是"],
        "sep_alert": "<div class='warning-card'><strong>💡 符合特殊资格：您符合特殊注册期 (SEP)！</strong><br>由于您近期有重大生活变更，您可在事件发生的 <b>60 天内</b> 免费更换计划，无需等待秋季年度公开注册期！</div>",
        "standard_windows": "📅 **标准转换时间窗口：**\n* **AEP (年度公开注册期: 10月15日 – 12月7日)**：所有人皆可更换 C/D 部分计划。\n* **OEP (Medicare Advantage 开放注册期: 1月1日 – 3月31日)**：仅限现有 Medicare Advantage 会员更换方案。",
        "step3_title": "步骤 3：🚀 HOW - 行动指南与重要风险提示",
        "warnings_box": "<div class='card-box'><h4>📋 更换计划前的重要风险提示</h4><ul><li><b>⚠️ 健康审查风险 (Medical Underwriting)：</b> 若从 Medicare Advantage 换回 原始 Medicare + Medigap，在多数州需要通过健康核保，可能因既往病史被拒保或提高保费。</li><li><b>💊 处方药物清单核对 (Formulary Check)：</b> 务必先至 Medicare.gov 官网确认您的常用药物是否包含在新计划的处方药清单中。</li></ul></div>",
        "next_step_tip": "💡 下一步：点击左侧边栏菜单中的“📋 1-Page SHIP 咨询准备单”，生成咨询总结带给免费 SHIP 顾问！"
    },
    "Español": {
        "title": "## 🔄 Asistente de Cambio de Plan de Medicare",
        "caption": "Guía neutral y objetiva: evalúe por qué, cuándo y cómo cambiar su plan de Medicare.",
        "step1_title": "Paso 1: 🔍 WHY - ¿Cuál es su razón principal para cambiar?",
        "step1_label": "Seleccione la opción que mejor describa su situación:",
        "reasons": [
            "--- Seleccione una razón ---",
            "💰 Costos más altos (Aumento de prima, copago o deducible)",
            "🩺 Médico/Hospital fuera de la red (Su médico ya no es aceptado)",
            "🏠 Cambio de vida/Mudanza (Se mudó de ZIP Code, se retiró o perdió seguro de empleo)",
            "💊 Cambio en cobertura de medicamentos (Necesita un nuevo medicamento no cubierto)",
            "🤷 Comparación de tarifas (Buscando mejor valor o cobertura)"
        ],
        "step2_title": "Paso 2: ⏰ WHEN - Ventana de tiempo y elegibilidad",
        "move_question": "¿Se ha mudado, cambiado de residencia o perdido la cobertura del empleador en los últimos 60 días?",
        "yes_no": ["No", "Sí"],
        "sep_alert": "<div class='warning-card'><strong>💡 ¡Calificación detectada: Califica para un SEP (Período de Inscripción Especial)!</strong><br>Debido a su evento reciente, puede cambiar de plan gratis dentro de los <b>60 días</b> posteriores al cambio.</div>",
        "standard_windows": "📅 **Ventanas de tiempo estándar:**\n* **AEP (Período de Inscripción Anual: 15 de oct – 7 de dic)**: Abierto a todos para cambiar planes Parte C/D.\n* **OEP (Inscripción Abierta de Advantage: 1 de ene – 31 de mar)**: Abierto a miembros actuales de Medicare Advantage.",
        "step3_title": "Paso 3: 🚀 HOW - Plan de acción y advertencias cruciales",
        "warnings_box": "<div class='card-box'><h4>📋 Advertencias cruciales antes de cambiar</h4><ul><li><b>⚠️ Riesgo de suscripción médica:</b> Cambiar de Medicare Advantage a Medicare Original + Medigap puede requerir evaluación médica en la mayoría de los estados.</li><li><b>💊 Verificación de formulario:</b> Verifique que sus medicamentos estén cubiertos en Medicare.gov.</li></ul></div>",
        "next_step_tip": "💡 Siguiente paso: Seleccione '📋 Resumen de Preparación SHIP' en la barra lateral."
    },
    "한국어": {
        "title": "## 🔄 Medicare 플랜 변경 의사결정 도우미",
        "caption": "중립적이고 객관적인 안내: Medicare 플랜을 변경하는 이유, 시기 및 방법을 평가합니다.",
        "step1_title": "1단계: 🔍 WHY - 플랜을 변경하려는 주요 이유는 무엇입니까?",
        "step1_label": "귀하의 상황에 가장 잘 맞는 옵션을 선택하십시오:",
        "reasons": [
            "--- 이유 선택 ---",
            "💰 비용 인상 (보험료, 디덕터블 또는 코페이 증가)",
            "🩺 의사/병원 네트워크 이탈 (주치의가 더 이상 플랜을 받지 않음)",
            "🏠 거주지 변경/이사 (새 ZIP 코드 이사, 은퇴 또는 직장 보험 상실)",
            "💊 처방약 보장 변경 (보장되지 않는 새로운 특수 약물 필요)",
            "🤷 더 나은 보장 비교 (비용 대비 더 나은 혜택 탐색)"
        ],
        "step2_title": "2단계: ⏰ WHEN - 변경 가능 기간 및 자격 확인",
        "move_question": "지난 60일 이내에 이사하셨거나 직장 보험을 상실하셨습니까?",
        "yes_no": ["아니오", "예"],
        "sep_alert": "<div class='warning-card'><strong>💡 자격 감지: 특별 등록 기간(SEP) 자격이 있습니다!</strong><br>최근의 신상 변화로 인해 이벤트 발생 <b>60일 이내</b>에 연례 정기 등록 기간을 기다리지 않고 무료로 플랜을 변경할 수 있습니다.</div>",
        "standard_windows": "📅 **표준 변경 기간:**\n* **AEP (연례 정기 등록 기간: 10월 15일 – 12월 7일)**: 모든 가입자가 Part C/D 플랜 변경 가능.\n* **OEP (Advantage 오픈 등록 기간: 1월 1일 – 3월 31일)**: 현재 Medicare Advantage 가입자 대상.",
        "step3_title": "3단계: 🚀 HOW - 실행 계획 및 주요 주의사항",
        "warnings_box": "<div class='card-box'><h4>📋 플랜 변경 전 필수 주의사항</h4><ul><li><b>⚠️ 건강 심사 위험 (Medical Underwriting):</b> Medicare Advantage에서 Original Medicare + Medigap으로 전환 시 대부분의 주에서 건강 심사가 필요할 수 있습니다.</li><li><b>💊 처방약 목록 확인 (Formulary Check):</b> Medicare.gov에서 복용 중인 약물이 새 플랜의 보장 목록에 있는지 확인하십시오.</li></ul></div>",
        "next_step_tip": "💡 다음 단계: 사이드바에서 '📋 1페이지 SHIP 상담 준비표'를 선택하여 요약본을 출력하세요!"
    }
}

m3_labels = {
    "English": {
        "title": "## 📋 1-Page SHIP Counseling Prep Form",
        "caption": "Review the information already mentioned in your Medicare Compass conversation, complete any missing fields, and prepare it for a local SHIP counselor.",
        "auto_fill_note": "✅ Information found in your conversation has been prefilled below. Please review it and complete anything that is missing.",
        "state_detected_note": "📍 State detected: {state}. Please enter your ZIP Code so SHIP resources can be matched locally.",
        "zip_label": "ZIP Code",
        "zip_placeholder": "e.g. 07030",
        "plan_label": "Current Plan Name",
        "plan_placeholder": "e.g. Aetna Medicare Advantage",
        "cost_label": "Monthly Premium ($)",
        "cost_placeholder": "e.g. 120",
        "concern_label": "Primary Concern / Question",
        "concern_placeholder": "Describe the main question or concern you want to discuss with a SHIP counselor.",
        "meds_label": "Current Medications (Name / Dosage / Frequency)",
        "meds_placeholder": "e.g. Eliquis 5mg — twice daily",
        "btn_label": "Generate 1-Page Summary",
        "footer_note": "Privacy-first output. Review the information for accuracy, then print or screenshot this page for your SHIP appointment."
    },
    "繁體中文": {
        "title": "## 📋 1-Page SHIP 諮詢準備單",
        "caption": "檢查 Medicare Compass 對話中已經提過的資訊，補齊缺少欄位後，整理成可帶給當地 SHIP 顧問的一頁準備單。",
        "auto_fill_note": "✅ 已將對話中能辨識的資訊自動帶入下方欄位，請確認內容並補上尚未提供的資料。",
        "state_detected_note": "📍 已辨識州別：{state}。請再輸入 ZIP Code，才能對應當地 SHIP 資源。",
        "zip_label": "居住地郵遞區號 (ZIP Code)",
        "zip_placeholder": "例如：07030",
        "plan_label": "目前投保的計畫名稱",
        "plan_placeholder": "例如：Aetna Medicare Advantage",
        "cost_label": "每月保費 ($)",
        "cost_placeholder": "例如：120",
        "concern_label": "您最想諮詢的核心問題 / 痛點",
        "concern_placeholder": "請描述您最希望與 SHIP 顧問確認的問題或疑慮。",
        "meds_label": "目前平時服用的處方藥物 (名稱 / 劑量 / 頻率)",
        "meds_placeholder": "例如：Eliquis 5mg — 每日兩次",
        "btn_label": "生成 1 頁精簡諮詢單",
        "footer_note": "隱私優先。請先確認資料正確，再列印或截圖此頁面，於 SHIP 預約時提供給顧問。"
    },
    "簡體中文": {
        "title": "## 📋 1-Page SHIP 咨询准备单",
        "caption": "检查 Medicare Compass 对话中已经提过的信息，补齐缺少字段后，整理成可提供给当地 SHIP 顾问的一页准备单。",
        "auto_fill_note": "✅ 已将对话中能够识别的信息自动带入下方字段，请确认内容并补充尚未提供的资料。",
        "state_detected_note": "📍 已识别州别：{state}。请再输入 ZIP Code，以便对应当地 SHIP 资源。",
        "zip_label": "居住地邮政编码 (ZIP Code)",
        "zip_placeholder": "例如：07030",
        "plan_label": "目前投保的计划名称",
        "plan_placeholder": "例如：Aetna Medicare Advantage",
        "cost_label": "每月保费 ($)",
        "cost_placeholder": "例如：120",
        "concern_label": "您最想咨询的核心问题 / 痛点",
        "concern_placeholder": "请描述您最希望与 SHIP 顾问确认的问题或疑虑。",
        "meds_label": "目前常规服用的处方药物 (名称 / 剂量 / 频率)",
        "meds_placeholder": "例如：Eliquis 5mg — 每日两次",
        "btn_label": "生成 1 页精简咨询单",
        "footer_note": "隐私优先。请先确认资料正确，再打印或截图此页面，于 SHIP 预约时提供给顾问。"
    },
    "Español": {
        "title": "## 📋 Resumen de Preparación para Asesoría SHIP",
        "caption": "Revise la información ya mencionada en su conversación de Medicare Compass, complete los campos faltantes y prepárela para un asesor local de SHIP.",
        "auto_fill_note": "✅ La información encontrada en su conversación se ha completado automáticamente. Revísela y complete cualquier dato faltante.",
        "state_detected_note": "📍 Estado detectado: {state}. Ingrese su código ZIP para identificar los recursos locales de SHIP.",
        "zip_label": "Código Postal (ZIP)",
        "zip_placeholder": "p. ej. 07030",
        "plan_label": "Nombre del Plan Actual",
        "plan_placeholder": "p. ej. Aetna Medicare Advantage",
        "cost_label": "Prima Mensual ($)",
        "cost_placeholder": "p. ej. 120",
        "concern_label": "Preocupación / Pregunta Principal",
        "concern_placeholder": "Describa la pregunta o preocupación principal que desea consultar con SHIP.",
        "meds_label": "Medicamentos Actuales (Nombre / Dosis / Frecuencia)",
        "meds_placeholder": "p. ej. Eliquis 5mg — dos veces al día",
        "btn_label": "Generar Resumen de 1 Página",
        "footer_note": "Privacidad primero. Revise la información antes de imprimir o guardar una captura para su cita con SHIP."
    },
    "한국어": {
        "title": "## 📋 1페이지 SHIP 상담 준비표",
        "caption": "Medicare Compass 대화에서 이미 언급한 정보를 확인하고, 빠진 항목을 보완해 지역 SHIP 상담사에게 보여줄 준비표를 만드세요.",
        "auto_fill_note": "✅ 대화에서 확인된 정보를 아래 항목에 자동으로 채웠습니다. 내용을 확인하고 빠진 정보를 추가해 주세요.",
        "state_detected_note": "📍 확인된 주: {state}. 지역 SHIP 자원을 찾으려면 ZIP Code를 입력해 주세요.",
        "zip_label": "우편번호 (ZIP Code)",
        "zip_placeholder": "예: 07030",
        "plan_label": "현재 가입된 플랜명",
        "plan_placeholder": "예: Aetna Medicare Advantage",
        "cost_label": "월 보험료 ($)",
        "cost_placeholder": "예: 120",
        "concern_label": "주요 문의 사항 / 우려점",
        "concern_placeholder": "SHIP 상담사에게 가장 확인하고 싶은 질문이나 우려점을 적어 주세요.",
        "meds_label": "현재 복용 중인 처방약 (약품명 / 용량 / 복용 빈도)",
        "meds_placeholder": "예: Eliquis 5mg — 하루 2회",
        "btn_label": "1페이지 요약표 생성",
        "footer_note": "개인정보 보호를 우선합니다. 내용을 확인한 후 SHIP 상담을 위해 인쇄하거나 화면을 저장하세요."
    }
}

m4_labels = {
    "English": {
        "title": "## 📅 SHIP Appointment Calendar Reminder (.ics)",
        "caption": "Never forget your SHIP appointment! Add it directly to your Google or Apple Calendar with built-in prep notes.",
        "date_label": "Appointment Date",
        "time_label": "Appointment Time",
        "location_label": "Location / Method",
        "location_placeholder": "e.g. Phone Call / Local Community Center",
        "btn_generate": "📅 Generate Calendar File (.ics)",
        "btn_download": "💾 Download .ics File (Click to Add to Calendar)",
        "success_msg": "Calendar file created! Click above to download and open on your phone or computer."
    },
    "繁體中文": {
        "title": "## 📅 SHIP 預約行事曆提醒 (.ics)",
        "caption": "絕不遺忘您的 SHIP 諮詢預約！將預約時間直接同步至您的 Google 或 Apple 行事曆，並內建備忘提示。",
        "date_label": "預約日期",
        "time_label": "預約時間",
        "location_label": "預約地點 / 方式",
        "location_placeholder": "例如: 電話諮詢 / 當地社區中心",
        "btn_generate": "📅 生成行事曆檔案 (.ics)",
        "btn_download": "💾 下載 .ics 行事曆檔案 (點擊即可加入行事曆)",
        "success_msg": "行事曆檔案已成功生成！請點擊上方按鈕下載並於手機或電腦開啟。"
    },
    "簡體中文": {
        "title": "## 📅 SHIP 预约日历提醒 (.ics)",
        "caption": "绝不遗忘您的 SHIP 咨询预约！将预约时间直接同步至您的 Google 或 Apple 日历，并内建备忘提示。",
        "date_label": "预约日期",
        "time_label": "预约时间",
        "location_label": "预约地点 / 方式",
        "location_placeholder": "例如: 电话咨询 / 当地社区中心",
        "btn_generate": "📅 生成日历文件 (.ics)",
        "btn_download": "💾 下载 .ics 日历文件 (点击即可加入日历)",
        "success_msg": "日历文件已成功生成！请点击上方按钮下载并在手机或电脑打开。"
    },
    "Español": {
        "title": "## 📅 Recordatorio de Cita SHIP (.ics)",
        "caption": "¡Nunca olvide su cita de SHIP! Agréguela a su Google o Apple Calendar.",
        "date_label": "Fecha de Cita",
        "time_label": "Hora de Cita",
        "location_label": "Ubicación / Método",
        "location_placeholder": "ej. Llamada / Centro Comunitario Local",
        "btn_generate": "📅 Generar Archivo de Calendario (.ics)",
        "btn_download": "💾 Descargar Archivo .ics",
        "success_msg": "¡Archivo creado! Haga clic arriba para descargar."
    },
    "한국어": {
        "title": "## 📅 SHIP 예약 일정 알림 (.ics)",
        "caption": "SHIP 예약 일정을 잊지 마세요! Google 또는 Apple 캘린더에 사전 준비 사항과 함께 직접 추가하세요.",
        "date_label": "예약 날짜",
        "time_label": "예약 시간",
        "location_label": "장소 / 상담 방식",
        "location_placeholder": "예: 전화 상담 / 지역 커뮤니티 센터",
        "btn_generate": "📅 캘린더 파일 생성 (.ics)",
        "btn_download": "💾 .ics 파일 다운로드 (클릭하여 캘린더에 추가)",
        "success_msg": "캘린더 파일이 생성되었습니다! 위 버튼을 클릭하여 다운로드 후 열어보세요."
    }
}
# --------------------------------------------------
# 側邊欄 (Sidebar) 語言字典
# --------------------------------------------------

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
}

m2_text = {
    "English": "🔄 Plan Switching Assistant (Why-When-How)",
    "Español": "🔄 Asistente de Cambio de Plan",
    "한국어": "🔄 플랜 변경 의사결정 도우미",
    "簡體中文": "🔄 Plan 转换决策助理 (Why-When-How)",
    "繁體中文": "🔄 Plan 轉換決策助理 (Why-When-How)",
}

m3_text = {
    "English": "📋 1-Page SHIP Prep Summary",
    "Español": "📋 Resumen de Preparación SHIP",
    "한국어": "📋 1페이지 SHIP 상담 준비표",
    "簡體中文": "📋 1-Page SHIP 咨询准备单",
    "繁體中文": "📋 1-Page SHIP 諮詢準備單",
}

m4_text = {
    "English": "📅 SHIP Appointment Reminder",
    "Español": "📅 Recordatorio de Cita SHIP",
    "한국어": "📅 SHIP 예약 일정 알림",
    "簡體中文": "📅 SHIP 预约行事历提醒",
    "繁體中文": "📅 SHIP 預約行事曆提醒",
}

font_size_map = {
    "English": {
        "title": "#### 🔠 Font Size",
        "label": "Adjust font size"
    },
    "Español": {
        "title": "#### 🔠 Tamaño de fuente",
        "label": "Ajustar tamaño de fuente"
    },
    "繁體中文": {
        "title": "#### 🔠 字體大小",
        "label": "調整字體大小"
    },
    "簡體中文": {
        "title": "#### 🔠 字体大小",
        "label": "调整字体大小"
    },
    "한국어": {
        "title": "#### 🔠 글자 크기",
        "label": "글자 크기 조정"
    }
}

upload_label_map = {
    "English": "📷 Take Photo or Upload Notice/Plan (Optional):",
    "Español": "📷 Tomar foto o cargar documento (Opcional):",
    "한국어": "📷 사진 촬영 또는 서류 업로드 (선택 사항):",
    "簡體中文": "📷 拍照或上传信件/保单照片 (选填):",
    "繁體中文": "📷 拍照或上傳信件/保單照片 (選填):",
}

legal_title_map = {
    "English": "⚖️ Legal, Privacy & Notices",
    "Español": "⚖️ Avisos Legales y Privacidad",
    "한국어": "⚖️ 법적 고지 및 개인정보 보호",
    "簡體中文": "⚖️ 法律声明、隐私与非官方提示",
    "繁體中文": "⚖️ 法律聲明、隱私與非官方提示",
}

legal_caption_map = {
    "English": "🔒 **Zero-Server-Data Privacy**:\nWe DO NOT store or track any of your inputs on our servers. Any remembered input is stored ONLY on your local browser device.\n\n⚠️ **Anti-Fraud Notice**: Medicare will NEVER call/text asking for SSN or banking details.\nℹ️ **Disclaimer**: Educational guidance only; verify final choices with [Medicare.gov](https://www.medicare.gov).\n🏛️ **Independent Tool**: Not affiliated with the US Government, CMS, or SSA.",
    "繁體中文": "🔒 **零伺服器資料隱私**:\n我們不會在伺服器上儲存或追蹤您的任何輸入。任何記憶的輸入僅儲存於您的本機瀏覽器裝置中。\n\n⚠️ **防詐騙提示**: Medicare 絕對不會打電話/傳簡訊要求提供社會安全碼 (SSN) 或銀行資料。\nℹ️ **免責聲明**: 僅供教育指引；最終選擇請至 [Medicare.gov](https://www.medicare.gov) 官方網站確認。\n🏛️ **獨立工具**: 本工具與美國政府、CMS 或 SSA 無關。",
    "簡體中文": "🔒 **零服务器数据隐私**:\n我们不会在服务器上存储或追踪您的任何输入。任何记忆的输入仅存储于您的本地浏览器设备中。\n\n⚠️ **防诈骗提示**: Medicare 绝对不会打电话/发短信要求提供社会安全码 (SSN) 或银行信息。\nℹ️ **免责声明**: 仅供教育指引；最终选择请至 [Medicare.gov](https://www.medicare.gov) 官方网站确认。\n🏛️ **独立工具**: 本工具与美国政府、CMS 或 SSA 无关。",
    "Español": "🔒 **Privacidad de datos cero en el servidor**:\nNO almacenamos ni rastreamos ninguna de sus entradas en nuestros servidores. Cualquier entrada recordada se almacena SOLO en su dispositivo de navegador local.\n\n⚠️ **Aviso contra el fraude**: Medicare NUNCA llamará/enviará mensajes de texto pidiendo el SSN o detalles bancarios.\nℹ️ **Descargo de responsabilidad**: Solo orientación educativa; verifique opciones finales en [Medicare.gov](https://www.medicare.gov).\n🏛️ **Herramienta independiente**: No afiliada al Gobierno de EE. UU., CMS o SSA.",
    "한국어": "🔒 **서버 데이터 제로 개인정보 보호**:\n당사는 귀하의 어떠한 입력 내용도 서버에 저장하거나 추적하지 않습니다. 기억된 입력 내용은 로컬 브라우저 기기에만 저장됩니다.\n\n⚠️ **사기 방지 안내**: Medicare는 결코 SSN이나 은행 정보를 묻는 전화/문자를 하지 않습니다.\nℹ️ **면책 조항**: 교육적 목적의 안내일 뿐이며, 최종 선택은 [Medicare.gov](https://www.medicare.gov)에서 확인하십시오.\n🏛️ **독립적인 도구**: 미국 정부, CMS 또는 SSA와 제휴하지 않았습니다."
}

reset_btn_map = {
    "English": "🔄 Reset Conversation",
    "Español": "🔄 Reiniciar",
    "한국어": "🔄 대화 재설정",
    "簡體中文": "🔄 重新开始咨询",
    "繁體中文": "🔄 重新開始諮詢",
}
# --------------------------------------------------
# 模組 1 (MAIN_AI) 語言字典
# --------------------------------------------------
q_caption_map = {
    "English": "💡 **Quick Start**: Select identity, then enter **Birth Month/Year & State** below:",
    "Español": "💡 **Inicio rápido**: Elija su rol e ingrese **Mes/Año de nacimiento y Estado**:",
    "한국어": "💡 **빠른 시작**: 신분을 선택하고 아래에 **생년월일 및 거주 주**를 입력하세요:",
    "簡體中文": "💡 **快速开始**: 请选择身份，并在下方输入**出生年月与居住州**：",
    "繁體中文": "💡 **快速開始**: 請選擇身份，並在下方輸入**出生年月與居住州**：",
}

btn1_map = {
    "English": "👨‍⚕️ Applying for Myself",
    "Español": "👨‍⚕️ Aplicando para mí mismo",
    "한국어": "👨‍⚕️ 본인 신청",
    "簡體中文": "👨‍⚕️ 我是长者本人",
    "繁體中文": "👨‍⚕️ 我是長者本人",
}

btn2_map = {
    "English": "👨‍👩‍👧 Helping Family/Parents",
    "Español": "👨‍👩‍👧 Ayudando a mi familia/padres",
    "한국어": "👨‍👩‍👧 가족 도와드리기",
    "簡體中文": "👨‍👩‍👧 我是子女/家属",
    "繁體中文": "👨‍👩‍👧 我是子女/家屬",
}

quick_btn_map = {
    "English": "⚡ Submit saved input",
    "Español": "⚡ Enviar entrada guardada",
    "한국어": "⚡ 저장된 입력 제출 클릭",
    "簡體中文": "⚡ 直接使用上次记忆提交",
    "繁體中文": "⚡ 重新提交已儲存內容"
}

input_placeholder_first_map = {
    "English": "✍️ Please enter Birth Month/Year & State (e.g. 08/1961, NJ) ...",
    "Español": "✍️ Ingrese su mes/año de nacimiento y estado (p. ej. 08/1961, NJ) ...",
    "한국어": "✍️ 생년월과 주를 입력하세요 (예: 08/1961, NJ) ...",
    "簡體中文": "✍️ 请输入出生年月与居住州 (例如: 1961年08月, 新泽西州) ...",
    "繁體中文": "✍️ 請輸入出生年月與居住州 (例如: 1961年8月, 新澤西州) ...",
}

input_placeholder_followup_map = {
    "English": "💬 Ask any follow-up question about Medicare...",
    "Español": "💬 Escriba su pregunta sobre Medicare...",
    "한국어": "💬 Medicare에 대해 질문을 입력하세요...",
    "簡體中文": "💬 请输入您想咨询的 Medicare 问题...",
    "繁體中文": "💬 請輸入您想諮詢的 Medicare 問題...",
}

end_chat_btn_map = {
    "English": "✅ I got the information I need — End Conversation",
    "Español": "✅ Ya obtuve la información que necesitaba — Finalizar conversación",
    "한국어": "✅ 필요한 정보를 얻었습니다 — 상담 종료",
    "簡體中文": "✅ 已得到想要的信息，结束对话",
    "繁體中文": "✅ 已得到想要資訊，結束對話",
}

default_upload_msg_map = {
    "English": "Please review this uploaded document.",
    "Español": "Por favor, revise este documento subido.",
    "한국어": "업로드된 문서를 검토해 주세요.",
    "簡體中文": "请查看这份上传的文件。",
    "繁體中文": "請查看這份上傳的文件。"
}

spinner_msg_map = {
    "English": "Analyzing...",
    "Español": "Analizando...",
    "한국어": "분석 중...",
    "簡體中文": "分析中...",
    "繁體中文": "分析中..."
}

timeline_template_map = {
    "English": "### 🗓️ Your Personalized Medicare Timeline\n\n**Key Milestones:**\n* **Turning 65:** {birth_m_name} {turn_65_year}\n* **Initial Enrollment Period (IEP):** **{start_m_name} 1, {start_y} – {end_m_name} {end_day}, {end_y}** (7-Month Window)\n\n**Recommended Next Steps:**\n* **Step 1:** Check active employer coverage (if still working) to see if you can delay Part B.\n* **Step 2:** Compare **Pathway A: Total Freedom to See Any Doctor** (Original Medicare + Medigap) vs. **Pathway B: All-in-One Medicare Advantage**.",
    "繁體中文": "### 🗓️ 您的專屬 Medicare 時間軸\n\n**關鍵里程碑:**\n* **年滿 65 歲:** {birth_m_name} {turn_65_year} 年\n* **首次登記期 (IEP):** **{start_y} 年 {start_m_name} 1 日 – {end_y} 年 {end_m_name} {end_day} 日** (7個月窗口期)\n\n**建議下一步:**\n* **步驟 1:** 如果您仍在工作，請確認雇主保險是否符合延遲 Part B 的資格。\n* **步驟 2:** 比較 **方案 A: 看診完全自由** (Original Medicare + Medigap) 與 **方案 B: 全包式計畫** (Medicare Advantage)。",
    "簡體中文": "### 🗓️ 您的专属 Medicare 时间轴\n\n**关键里程碑:**\n* **年满 65 岁:** {birth_m_name} {turn_65_year} 年\n* **首次注册期 (IEP):** **{start_y} 年 {start_m_name} 1 日 – {end_y} 年 {end_m_name} {end_day} 日** (7个月窗口期)\n\n**建议下一步:**\n* **步骤 1:** 如果您仍在工作，请确认雇主保险是否符合延迟 Part B 的资格。\n* **步骤 2:** 比较 **方案 A: 看病完全自由** (Original Medicare + Medigap) 与 **方案 B: 全包式计划** (Medicare Advantage)。",
    "Español": "### 🗓️ Su Cronograma Personalizado de Medicare\n\n**Hitos Clave:**\n* **Cumple 65:** {birth_m_name} {turn_65_year}\n* **Período de Inscripción Inicial (IEP):** **1 de {start_m_name}, {start_y} – {end_day} de {end_m_name}, {end_y}** (Ventana de 7 Meses)\n\n**Próximos Pasos Recomendados:**\n* **Paso 1:** Verifique su cobertura actual de empleador (si sigue trabajando) para ver si puede retrasar la Parte B.\n* **Paso 2:** Compare **Vía A: Libertad Total de Médicos** (Medicare Original + Medigap) vs. **Vía B: Todo en Uno** (Medicare Advantage).",
    "한국어": "### 🗓️ 귀하의 맞춤형 Medicare 일정\n\n**주요 마일스톤:**\n* **65세 도달:** {turn_65_year}년 {birth_m_name}\n* **최초 가입 기간 (IEP):** **{start_y}년 {start_m_name} 1일 – {end_y}년 {end_m_name} {end_day}일** (7개월 기간)\n\n**권장 다음 단계:**\n* **1단계:** 계속 근무 중인 경우 현재 직장 보험을 확인하여 Part B 가입을 연기할 수 있는지 확인하세요.\n* **2단계:** **플랜 A: 자유로운 병원 선택** (오리지널 Medicare + Medigap) 대 **플랜 B: 올인원 플랜** (Medicare Advantage) 비교."
}

tip_suffix_map = {
    "English": "\n\n💡 *Tip: Once you've chosen your preferred pathway, submit your official enrollment online at [SSA.gov](https://www.ssa.gov).* ",
    "Español": "\n\n💡 *Consejo: Una vez que elija su vía preferida, envíe su inscripción oficial en línea en [SSA.gov](https://www.ssa.gov).* ",
    "한국어": "\n\n💡 *팁: 선호하는 플랜을 선택한 후 [SSA.gov](https://www.ssa.gov)에서 온라인으로 공식 가입을 제출하세요.* ",
    "簡體中文": "\n\n💡 *提示: 确认您的首选方案后，请前往官方网站 [SSA.gov](https://www.ssa.gov) 提交在线申请。* ",
    "繁體中文": "\n\n💡 *提示: 確認您的首選方案後，請前往官方網站 [SSA.gov](https://www.ssa.gov) 提交線上申請。* "
}

summary_title_map = {
    "English": "📋 Your Medicare 1-Page Summary",
    "Español": "📋 Su Resumen de Medicare de 1 Página",
    "한국어": "📋 Medicare 1페이지 요약",
    "簡體中文": "📋 您的 Medicare 1页总结",
    "繁體中文": "📋 您的 Medicare 1頁總結"
}

ui_bottom_map = {
    "English": {
        "tab1": "⚡ 1-Page Summary",
        "tab2": "📄 Full Conversation Log",
        "applicant_label": "Applicant",
        "applicant_self": "Self",
        "applicant_family": "Family / Parent",
        "birth_label": "Birth",
        "state_label": "State",
        "timeline_title": "🗓️ Personal Timeline",
        "timeline_turn65": "Turns 65",
        "timeline_iep_start": "IEP starts",
        "timeline_iep_end": "IEP ends",
        "decisions_title": "💡 Key Decisions & Plan Summary",
        "dl_txt": "📥 Download 1-Page Summary (TXT)",
        "btn_pdf": "🖨️ Print / Save as PDF",
        "dl_log": "📥 Download Full Log (TXT)",
        "full_log_title": "Medicare Compass - Full Conversation Log",
        "user_role_label": "User",
        "advisor_role_label": "Compass Advisor"
    },
    "繁體中文": {
        "tab1": "⚡ 1-Page Summary (精簡卡片)",
        "tab2": "📄 Full Conversation Log (完整記錄)",
        "applicant_label": "申請對象",
        "applicant_self": "本人",
        "applicant_family": "家人 / 父母",
        "birth_label": "出生年月",
        "state_label": "州別",
        "timeline_title": "🗓️ 個人 Medicare 時間軸",
        "timeline_turn65": "年滿 65 歲",
        "timeline_iep_start": "IEP 開始",
        "timeline_iep_end": "IEP 結束",
        "decisions_title": "💡 關鍵決策與方案總結",
        "dl_txt": "📥 下載 1頁精簡總結 (TXT)",
        "btn_pdf": "🖨️ 列印 / 存為 PDF",
        "dl_log": "📥 下載完整對話記錄 (TXT)",
        "full_log_title": "Medicare Compass - 完整對話記錄",
        "user_role_label": "使用者",
        "advisor_role_label": "Compass 顧問"
    },
    "簡體中文": {
        "tab1": "⚡ 1-Page Summary (精简卡片)",
        "tab2": "📄 Full Conversation Log (完整记录)",
        "applicant_label": "申请对象",
        "applicant_self": "本人",
        "applicant_family": "家人 / 父母",
        "birth_label": "出生年月",
        "state_label": "州别",
        "timeline_title": "🗓️ 个人 Medicare 时间轴",
        "timeline_turn65": "年满 65 岁",
        "timeline_iep_start": "IEP 开始",
        "timeline_iep_end": "IEP 结束",
        "decisions_title": "💡 关键决策与方案总结",
        "dl_txt": "📥 下载 1页精简总结 (TXT)",
        "btn_pdf": "🖨️ 打印 / 存为 PDF",
        "dl_log": "📥 下载完整对话记录 (TXT)",
        "full_log_title": "Medicare Compass - 完整对话记录",
        "user_role_label": "用户",
        "advisor_role_label": "Compass 顾问"
    },
    "Español": {
        "tab1": "⚡ Resumen de 1 página",
        "tab2": "📄 Registro completo",
        "applicant_label": "Solicitante",
        "applicant_self": "Yo",
        "applicant_family": "Familiar / Padre o Madre",
        "birth_label": "Nacimiento",
        "state_label": "Estado",
        "timeline_title": "🗓️ Cronología Personal",
        "timeline_turn65": "Cumple 65 años",
        "timeline_iep_start": "Inicio del IEP",
        "timeline_iep_end": "Fin del IEP",
        "decisions_title": "💡 Decisiones Clave y Resumen del Plan",
        "dl_txt": "📥 Descargar resumen (TXT)",
        "btn_pdf": "🖨️ Imprimir / Guardar PDF",
        "dl_log": "📥 Descargar registro (TXT)",
        "full_log_title": "Medicare Compass - Registro Completo de Conversación",
        "user_role_label": "Usuario",
        "advisor_role_label": "Asesor Compass"
    },
    "한국어": {
        "tab1": "⚡ 1페이지 요약",
        "tab2": "📄 전체 대화 기록",
        "applicant_label": "신청 대상",
        "applicant_self": "본인",
        "applicant_family": "가족 / 부모",
        "birth_label": "출생 월/연도",
        "state_label": "주",
        "timeline_title": "🗓️ 개인 Medicare 일정",
        "timeline_turn65": "65세 도달",
        "timeline_iep_start": "IEP 시작",
        "timeline_iep_end": "IEP 종료",
        "decisions_title": "💡 주요 결정 및 플랜 요약",
        "dl_txt": "📥 1페이지 요약 다운로드 (TXT)",
        "btn_pdf": "🖨️ 인쇄 / PDF로 저장",
        "dl_log": "📥 전체 기록 다운로드 (TXT)",
        "full_log_title": "Medicare Compass - 전체 대화 기록",
        "user_role_label": "사용자",
        "advisor_role_label": "Compass 상담자"
    }
}

official_links_map = {
    "English": """
        <div class='official-links-box' style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ Official Portals & Free Counseling</h4>
            <ul style='line-height: 1.9; font-size: 18px; color: #111827 !important;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>Apply for Medicare Part A & B Online</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov - Compare & Choose Plans</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>Find your local SHIP counselor (ShipHelp.org)</a></li>
            </ul>
        </div>
    """,
    "繁體中文": """
        <div class='official-links-box' style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ 官方申辦入口與免費中立輔導</h4>
            <ul style='line-height: 1.9; font-size: 18px; color: #111827 !important;'>            
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>線上申請 Medicare Part A & B 官方通道</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov 官網帳號與選 Plan 入口</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>尋找您所在州的 SHIP 1對1 免費中立輔導 (ShipHelp.org)</a></li>
            </ul>
        </div>
    """,
    "簡體中文": """
        <div class='official-links-box' style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ 官方申办入口与免费中立辅导</h4>
            <ul style='line-height: 1.9; font-size: 18px; color: #111827 !important;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>在线申请 Medicare Part A & B 官方通道</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov 官网账号与选 Plan 入口</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>寻找您所在州的 SHIP 1对1 免费中立辅导 (ShipHelp.org)</a></li>
            </ul>
        </div>
    """,
    "Español": """
        <div class='official-links-box' style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ Portales Oficiales y Asesoría Gratuita</h4>
            <ul style='line-height: 1.9; font-size: 18px; color: #111827 !important;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>Solicitar Medicare Parte A y B</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov - Comparar Planes</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>Encuentre asesoría local (ShipHelp.org)</a></li>
            </ul>
        </div>
    """,
    "한국어": """
        <div class='official-links-box' style='background-color: #EFF6FF; border-left: 5px solid #2563EB; padding: 22px; border-radius: 10px; margin-bottom: 25px;'>
            <h4 style='margin-top:0; color: #1E40AF; font-size: 21px;'>🏛️ 공식 포털 및 무료 상담</h4>
            <ul style='line-height: 1.9; font-size: 18px; color: #111827 !important;'>
                <li><b>Social Security Administration (SSA)</b>: <a href='https://www.ssa.gov/medicare' target='_blank'>온라인으로 Medicare 파트 A 및 B 신청</a></li>
                <li><b>Official Medicare Portal</b>: <a href='https://www.medicare.gov' target='_blank'>Medicare.gov - 플랜 비교 및 선택</a></li>
                <li><b>Free Local Counseling (SHIP)</b>: <a href='https://www.shiphelp.org' target='_blank'>해당 지역 SHIP 무료 상담 찾기 (ShipHelp.org)</a></li>
            </ul>
        </div>
    """
}

welcome_guide_map = {
    "English": {
        "greeting": "Welcome! Let's get your Medicare sorted in 3 easy steps:",
        "step1": "1. Find Your Timing",
        "step2": "2. Choose a Plan",
        "step3": "3. Get Your Checklist",
        "hint": "💡 Hint: You can switch languages or enlarge the text in the left menu."
    },
    "繁體中文": {
        "greeting": "您好！讓我們用 3 個簡單步驟搞定 Medicare：",
        "step1": "1. 算準申請時間",
        "step2": "2. 選擇適合方案",
        "step3": "3. 取得待辦清單",
        "hint": "💡 提示：您可以在左側選單切換語言或調大字體。"
    },
    "簡體中文": {
        "greeting": "您好！让我们用 3 个简单步骤搞定 Medicare：",
        "step1": "1. 算准申请时间",
        "step2": "2. 选择适合方案",
        "step3": "3. 获取待办清单",
        "hint": "💡 提示：您可以在左侧菜单切换语言或调大字体。"
    },
    "Español": {
        "greeting": "¡Bienvenido! Resolvamos su Medicare en 3 sencillos pasos:",
        "step1": "1. Calcule su tiempo",
        "step2": "2. Elija un plan",
        "step3": "3. Obtenga su lista",
        "hint": "💡 Consejo: Puede cambiar el idioma o ampliar el texto en el menú de la izquierda."
    },
    "한국어": {
        "greeting": "환영합니다! 3가지 간단한 단계로 메디케어를 해결하세요:",
        "step1": "1. 신청 시기 확인",
        "step2": "2. 플랜 선택",
        "step3": "3. 체크리스트 받기",
        "hint": "💡 힌트: 왼쪽 메뉴에서 언어를 변경하거나 글씨를 크게 할 수 있습니다."
    }
}

location_tracker_map = {
    "English": "📍 The system is currently analyzing based on **{location}** regulations. Please let me know if you need to change this.",
    "繁體中文": "📍 系統目前將依據 **{location}** 的法規為您分析。若需更改，請直接告訴我。",
    "簡體中文": "📍 系统目前将依据 **{location}** 的法规为您分析。若需更改，请直接告诉我。",
    "Español": "📍 El sistema está analizando actualmente según las regulaciones de **{location}**. Por favor, avíseme si necesita cambiar esto.",
    "한국어": "📍 시스템은 현재 **{location}** 규정을 바탕으로 분석 중입니다. 변경이 필요하시면 말씀해 주세요."
}

journey_buttons_map = {
    "English": {
        "btn1": "📅 Step 1\nWhen to Apply?",
        "prompt1": "When can I start applying for Medicare? Please explain the IEP (Initial Enrollment Period) window and eligibility.",
        "btn2": "⚖️ Step 2\nWhich Path?",
        "prompt2": "Please compare the pros and cons of Original Medicare vs. Medicare Advantage.",
        "btn3": "🏢 Step 3\nWhere to Apply?",
        "prompt3": "I have decided on my plan. Where is the official website to apply, and how do I pay?"
    },
    "繁體中文": {
        "btn1": "📅 Step 1\n什麼時候申請？",
        "prompt1": "請問我什麼時候可以開始申請 Medicare？請告訴我 IEP 黃金窗口的規定與資格。",
        "btn2": "⚖️ Step 2\n決定哪種方式？",
        "prompt2": "請幫我比較 Original Medicare (傳統聯邦醫療保險) 和 Medicare Advantage (優勢計畫) 的優缺點。",
        "btn3": "🏢 Step 3\n去哪裡申請？",
        "prompt3": "我決定好方案了，請問具體應該去哪個官方網站申請？需要怎麼付費？"
    },
    "簡體中文": {
        "btn1": "📅 Step 1\n什么时候申请？",
        "prompt1": "请问我什么时候可以开始申请 Medicare？请告诉我 IEP 黄金窗口的规定与资格。",
        "btn2": "⚖️ Step 2\n决定哪种方式？",
        "prompt2": "请帮我比较 Original Medicare (传统联邦医疗保险) 和 Medicare Advantage (优势计划) 的优缺点。",
        "btn3": "🏢 Step 3\n去哪里申请？",
        "prompt3": "我决定好方案了，请问具体应该去哪个官方网站申请？需要怎么付费？"
    },
    "Español": {
        "btn1": "📅 Paso 1\n¿Cuándo aplicar?",
        "prompt1": "¿Cuándo puedo comenzar a solicitar Medicare? Explique la ventana del IEP (Período de Inscripción Inicial) y la elegibilidad.",
        "btn2": "⚖️ Paso 2\n¿Qué plan elegir?",
        "prompt2": "Por favor, compare los pros y los contras de Original Medicare frente a Medicare Advantage.",
        "btn3": "🏢 Paso 3\n¿Dónde aplicar?",
        "prompt3": "He decidido mi plan. ¿Cuál es el sitio web oficial para presentar la solicitud y cómo pago?"
    },
    "한국어": {
        "btn1": "📅 1단계\n언제 신청하나요?",
        "prompt1": "메디케어 신청은 언제부터 할 수 있나요? IEP(최초 가입 기간)와 자격 요건에 대해 설명해 주세요.",
        "btn2": "⚖️ 2단계\n어떤 플랜을 선택?",
        "prompt2": "오리지널 메디케어와 메디케어 어드밴티지의 장단점을 비교해 주세요.",
        "btn3": "🏢 3단계\n어디서 신청하나요?",
        "prompt3": "플랜을 결정했습니다. 신청할 수 있는 공식 웹사이트는 어디이며, 결제는 어떻게 하나요?"
    }
}

ship_import_map = {
    "English": {
        "help": "Need free local help? Auto-fill the SHIP Prep form with details already mentioned in this conversation. Missing information will stay blank for you to review.",
        "btn": "📋 Auto-fill SHIP Prep",
        "extracting": "Preparing your SHIP fields from this conversation...",
        "success": "✅ SHIP Prep is ready. Open the 'SHIP Prep' module in the left menu to review or complete the fields."
    },
    "繁體中文": {
        "help": "需要免費在地協助嗎？系統會把這次對話中已經提過的資訊自動帶入 SHIP 準備單；沒有提到的欄位會保留空白，讓您自行確認補充。",
        "btn": "📋 自動帶入 SHIP 準備單",
        "extracting": "正在從本次對話整理 SHIP 所需欄位...",
        "success": "✅ SHIP 準備單已整理完成。請點擊左側「SHIP 準備單」模組確認或補齊欄位。"
    },
    "簡體中文": {
        "help": "需要免费的当地协助吗？系统会把本次对话中已经提过的信息自动带入 SHIP 准备单；未提及的字段会保留空白，供您确认补充。",
        "btn": "📋 自动带入 SHIP 准备单",
        "extracting": "正在从本次对话整理 SHIP 所需字段...",
        "success": "✅ SHIP 准备单已整理完成。请点击左侧“SHIP 准备单”模块确认或补充字段。"
    },
    "Español": {
        "help": "¿Necesita ayuda local gratuita? Complete automáticamente el formulario SHIP Prep con la información ya mencionada en esta conversación. Los datos faltantes quedarán en blanco para que los revise.",
        "btn": "📋 Autocompletar SHIP Prep",
        "extracting": "Preparando los campos de SHIP a partir de esta conversación...",
        "success": "✅ SHIP Prep está listo. Abra el módulo 'SHIP Prep' en el menú de la izquierda para revisar o completar los campos."
    },
    "한국어": {
        "help": "무료 지역 상담이 필요하신가요? 이번 대화에서 이미 언급한 정보를 SHIP 준비표에 자동으로 채웁니다. 확인되지 않은 항목은 비워 두므로 직접 확인해 주세요.",
        "btn": "📋 SHIP 준비표 자동 채우기",
        "extracting": "이번 대화에서 SHIP 항목을 정리하고 있습니다...",
        "success": "✅ SHIP 준비표가 준비되었습니다. 왼쪽 메뉴의 'SHIP Prep' 모듈에서 내용을 확인하거나 빠진 항목을 입력해 주세요."
    }
}

