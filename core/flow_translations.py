"""Entry-flow labels, separate from existing Medicare advice."""
FLOW_LABELS = {
    "English": {
        "who": "Who are you exploring for?", "self": "For myself", "other": "Helping parents / spouse",
        "today": "What would you like to explore today?", "guided": "1. Step by step — explore suitable directions",
        "switch": "2. Plan switch", "direct": "3. Ask AI directly", "unsure": "4. I don't know where to start",
        "back": "Back", "change": "Choose another topic", "trust": "About & Trust",
        "ai_notice": "This tool uses AI to organize Medicare information and support your exploration. AI may make mistakes. Confirm decisions with Medicare, Social Security, or a SHIP counselor.",
        "month": "Birth month", "year": "Birth year", "birth": "Birth month / year",
        "birth_required": "Please enter the applicant's birth month and year before continuing.",
        "initial": "Enter your question and background, such as application timing and ZIP code.", "followup": "Ask more related questions",
        "start": "Based on my confirmed questionnaire, help me explore suitable Medicare directions and compare Original Medicare with Medicare Advantage.",
        "ship": "Continue to SHIP preparation", "move": "Recent move or coverage change",
        "questionnaire": "Complete the steps, review your answers, then explore your Medicare directions with AI.",
    },
    "繁體中文": {
        "who": "您正在為誰了解 Medicare？", "self": "為我自己", "other": "協助父母／配偶",
        "today": "今天想了解什麼？", "guided": "1. Step by step — 探索適合方向",
        "switch": "2. Plan switch — 更換計畫", "direct": "3. 直接詢問 AI", "unsure": "4. 不知道從哪開始",
        "back": "返回", "change": "選擇其他主題", "trust": "About & Trust／關於與信任",
        "ai_notice": "本工具使用 AI 技術整理 Medicare 資訊，協助您探索選擇。AI 可能出錯；實際決定請向 Medicare、Social Security 或 SHIP 輔導員確認。",
        "month": "出生月份", "year": "出生年份", "birth": "出生年月",
        "birth_required": "請先填寫申請人的出生月份與年份，再繼續下一步。",
        "initial": "請輸入想詢問的問題與基本條件，例如申請時間、ZIP code。", "followup": "詢問更多相關問題",
        "start": "請根據我已確認的詢問單資料，協助探索適合的 Medicare 方向，並比較 Original Medicare 與 Medicare Advantage。",
        "ship": "繼續填寫 SHIP 準備單", "move": "近期搬家或保險變動",
        "questionnaire": "依步驟填寫並確認資料，再由 AI 協助探索適合的 Medicare 方向。",
    },
    "簡體中文": {
        "who": "您正在为谁了解 Medicare？", "self": "为我自己", "other": "协助父母／配偶",
        "today": "今天想了解什么？", "guided": "1. Step by step — 探索适合方向",
        "switch": "2. Plan switch — 更换计划", "direct": "3. 直接询问 AI", "unsure": "4. 不知道从哪开始",
        "back": "返回", "change": "选择其他主题", "trust": "About & Trust／关于与信任",
        "ai_notice": "本工具使用 AI 技术整理 Medicare 信息，协助您探索选择。AI 可能出错；实际决定请向 Medicare、Social Security 或 SHIP 辅导员确认。",
        "month": "出生月份", "year": "出生年份", "birth": "出生年月",
        "birth_required": "请先填写申请人的出生月份与年份，再继续下一步。",
        "initial": "请输入想询问的问题与基本条件，例如申请时间、ZIP code。", "followup": "询问更多相关问题",
        "start": "请根据我已确认的询问单资料，协助探索适合的 Medicare 方向，并比较 Original Medicare 与 Medicare Advantage。",
        "ship": "继续填写 SHIP 准备单", "move": "近期搬家或保险变动",
        "questionnaire": "按步骤填写并确认资料，再由 AI 协助探索适合的 Medicare 方向。",
    },
    "Español": {
        "who": "¿Para quién está explorando Medicare?", "self": "Para mí", "other": "Ayudando a mis padres / cónyuge",
        "today": "¿Qué le gustaría explorar hoy?", "guided": "1. Paso a paso — explorar opciones adecuadas",
        "switch": "2. Cambiar de plan", "direct": "3. Preguntar directamente a la IA", "unsure": "4. No sé por dónde empezar",
        "back": "Volver", "change": "Elegir otro tema", "trust": "Acerca de y confianza",
        "ai_notice": "Esta herramienta usa IA para organizar información de Medicare y ayudarle a explorar opciones. La IA puede cometer errores. Confirme sus decisiones con Medicare, Social Security o un asesor SHIP.",
        "month": "Mes de nacimiento", "year": "Año de nacimiento", "birth": "Mes / año de nacimiento",
        "birth_required": "Ingrese el mes y año de nacimiento del solicitante antes de continuar.",
        "initial": "Ingrese su pregunta y datos básicos, como fechas de solicitud y código postal.", "followup": "Hacer más preguntas relacionadas",
        "start": "Según mi cuestionario confirmado, ayúdeme a explorar opciones de Medicare y comparar Medicare Original con Medicare Advantage.",
        "ship": "Continuar a la preparación SHIP", "move": "Mudanza reciente o cambio de cobertura",
        "questionnaire": "Complete los pasos, revise sus respuestas y explore sus opciones de Medicare con IA.",
    },
    "한국어": {
        "who": "누구를 위해 Medicare를 알아보고 계신가요?", "self": "본인", "other": "부모님 / 배우자 돕기",
        "today": "오늘 무엇을 알아보고 싶으신가요?", "guided": "1. 단계별로 적합한 방향 알아보기",
        "switch": "2. 플랜 변경", "direct": "3. AI에게 직접 질문", "unsure": "4. 어디서 시작할지 모르겠어요",
        "back": "뒤로", "change": "다른 주제 선택", "trust": "소개 및 신뢰",
        "ai_notice": "이 도구는 AI 기술로 Medicare 정보를 정리하고 선택을 돕습니다. AI는 실수할 수 있습니다. 결정은 Medicare, Social Security 또는 SHIP 상담사에게 확인하세요.",
        "month": "출생 월", "year": "출생 연도", "birth": "출생 월 / 연도",
        "birth_required": "계속하려면 신청자의 출생 월과 연도를 입력하세요.",
        "initial": "신청 시기, 우편번호 등 기본 정보와 질문을 입력하세요.", "followup": "관련 질문 더 하기",
        "start": "확인한 설문 정보를 바탕으로 적합한 Medicare 방향을 탐색하고 Original Medicare와 Medicare Advantage를 비교해 주세요.",
        "ship": "SHIP 준비표로 계속", "move": "최근 이사 또는 보험 변경",
        "questionnaire": "단계별로 작성하고 답변을 확인한 후 AI와 함께 Medicare 방향을 알아보세요.",
    },
}


for language, labels in {
    "English": ("Continue where you left off", "Back to SHIP preparation", "Back to plan switching", "Back to conversation", "Retry bilingual version"),
    "繁體中文": ("繼續剛才的進度", "返回 SHIP 準備單", "返回更換計畫", "返回對話", "重新產生雙語版本"),
    "簡體中文": ("继续刚才的进度", "返回 SHIP 准备单", "返回更换计划", "返回对话", "重新生成双语版本"),
    "Español": ("Continuar donde lo dejó", "Volver a la preparación SHIP", "Volver al cambio de plan", "Volver a la conversación", "Reintentar versión bilingüe"),
    "한국어": ("이전 진행 내용 계속", "SHIP 준비표로 돌아가기", "플랜 변경으로 돌아가기", "대화로 돌아가기", "이중 언어 버전 다시 생성"),
}.items():
    FLOW_LABELS[language].update(dict(zip(
        ("resume", "back_ship", "back_switch", "back_chat", "retry_bilingual"), labels,
    )))


def flow_labels(language):
    return FLOW_LABELS.get(language, FLOW_LABELS["English"])


SWITCH_NEXT = {
    "English": "Continue below to prepare your SHIP summary. Your selected switching reason will be filled in; you can review and complete the remaining information.",
    "繁體中文": "接著按下方按鈕填寫 SHIP 準備單。您選擇的更換原因會帶入痛點欄位，其餘資料請自行填寫並確認。",
    "簡體中文": "接着按下方按钮填写 SHIP 准备单。您选择的更换原因会填入痛点字段，其余资料请自行填写并确认。",
    "Español": "Continúe abajo para preparar su resumen SHIP. Se incluirá el motivo seleccionado; revise y complete los demás datos.",
    "한국어": "아래 버튼으로 SHIP 준비표를 작성하세요. 선택한 변경 이유가 입력되며 나머지 정보는 직접 작성하고 확인하세요.",
}


UNSURE_LABELS = {
    "English": {
        "title": "Not sure where to start?",
        "body": "This short questionnaire helps you understand what information you may need to explore Medicare. Choose ‘Not sure’ where available, or leave fields blank and continue. **Please fill in your birth month and year; these are the only required fields.**",
        "continue": "Start questionnaire",
        "unknown": "Not sure",
    },
    "繁體中文": {
        "title": "不知道從哪開始？",
        "body": "這份詢問單可以幫助您了解，探索 Medicare 時需要準備哪些資料。不確定的選項可以選「不確定」，其他欄位也可以留空，直接按下一步。**只有出生月份與年份需要填寫。**",
        "continue": "開始填寫詢問單",
        "unknown": "不確定",
    },
    "簡體中文": {
        "title": "不知道从哪开始？",
        "body": "这份询问单可以帮助您了解，探索 Medicare 时需要准备哪些资料。不确定的选项可以选「不确定」，其他字段也可以留空，直接按下一步。**只有出生月份与年份需要填写。**",
        "continue": "开始填写询问单",
        "unknown": "不确定",
    },
    "Español": {
        "title": "¿No sabe por dónde empezar?",
        "body": "Este breve cuestionario le ayuda a conocer la información que puede necesitar para explorar Medicare. Puede elegir ‘No estoy seguro/a’ o dejar los campos en blanco y continuar. **Solo son obligatorios el mes y el año de nacimiento.**",
        "continue": "Comenzar cuestionario",
        "unknown": "No estoy seguro/a",
    },
    "한국어": {
        "title": "어디서 시작할지 모르겠나요?",
        "body": "이 설문은 Medicare를 알아볼 때 어떤 정보가 필요한지 이해하는 데 도움이 됩니다. 확실하지 않으면 ‘잘 모르겠어요’를 선택하거나 비워 두고 다음 단계로 넘어가세요. **출생 월과 연도만 필수입니다.**",
        "continue": "설문 시작하기",
        "unknown": "잘 모르겠어요",
    },
}
