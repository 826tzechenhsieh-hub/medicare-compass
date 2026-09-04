import streamlit as st
import google.generativeai as genai
import re # <--- 加上這個用來抓取 Zip Code 和州名
from core.response_cleaner import clean_response, sanitize_ai_output

def configure_gemini(user_api_key=None):
    """初始化並設定 Gemini API Key"""
    if user_api_key:
        genai.configure(api_key=user_api_key)
        return True

    try:
        primary_key = st.secrets["GEMINI_API_KEY"]
        if primary_key:
            genai.configure(api_key=primary_key)
            return True
    except (KeyError, FileNotFoundError):
        pass
    
    return False

def generate_clean_response(
    user_input,
    target_lang="English",
    img_data=None,
    questionnaire_context=""
):
    """呼叫 Gemini 模型並強制以目標語言輸出乾淨的結果"""
    preferred_models = [
        "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", 
        "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"
    ]
    valid_models = []

    try:
        available_models = {}
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                model_id = m.name.replace("models/", "")
                available_models[model_id] = m.name
        valid_models = [available_models[m] for m in preferred_models if m in available_models]
    except Exception:
        pass

    if not valid_models:
        valid_models = [f"models/{m}" for m in preferred_models]

    # 🔥 Task 3.1: 攔截使用者的地理資訊並存入 Session State
    def update_location_memory(text):
        # 1. 抓取 5 碼數字 (Zip Code)
        zip_match = re.search(r'\b\d{5}\b', text)
        if zip_match:
            st.session_state.user_zip = zip_match.group(0)

        # 2. 抓取常見州名 (這裡列出涵蓋率最高的幾州，可依需求擴充)
        states = [
            "California", "CA", "New York", "NY", "Florida", "FL", "Texas", "TX",
            "Illinois", "IL", "Pennsylvania", "PA", "Ohio", "OH", "Georgia", "GA",
            "New Jersey", "NJ", "Virginia", "VA", "Washington", "WA", "Arizona", "AZ"
        ]
        for state in states:
            if re.search(rf'\b{state}\b', text, re.IGNORECASE):
                st.session_state.user_state = state
                break

    # 執行攔截 (抓取這次使用者輸入的文字)
    update_location_memory(user_input)

    if "[Helping Someone Else]" in user_input:
        persona_context = """
CONSULTATION ROLE:
The user is helping another Medicare applicant or acting on that person's behalf.

- Address the helper normally, but refer to the Medicare beneficiary in the third person.
- Use terms such as "the applicant", "the person you are helping", or the equivalent in the selected language.
- Do NOT refer to the applicant's Medicare coverage, medications, eligibility, premiums, or enrollment decisions as if they belong to the helper.
- In Chinese responses, prefer terms such as「申請人」、「對方」or「他／她」when referring to the Medicare beneficiary.
- Do not assume that facts about the helper apply to the applicant unless explicitly stated.
"""
    else:
        persona_context = """
CONSULTATION ROLE:
The user is the Medicare applicant.
Use a direct second-person perspective when referring to their Medicare situation.
"""

    # 🔥 準備動態地理資訊字串 (Context Injection)
    location_context = ""
    if st.session_state.get("user_zip") or st.session_state.get("user_state"):
        locs = []
        if st.session_state.get("user_state"): locs.append(f"State: {st.session_state.user_state}")
        if st.session_state.get("user_zip"): locs.append(f"Zip: {st.session_state.user_zip}")
        location_context = f"\n\nUSER LOCATION CONTEXT: {', '.join(locs)}. You MUST tailor your Medicare advice (like Advantage plans and Medigap rules) to this specific location."

    questionnaire_instruction = ""

    if questionnaire_context:
        questionnaire_instruction = (
            "\n\nCONFIRMED QUESTIONNAIRE CONTEXT:\n"
            f"{questionnaire_context}\n\n"
            "QUESTIONNAIRE CONTEXT RULES:\n"
            "- This information was directly provided and confirmed by the user in the questionnaire.\n"
            "- Use it as background context when it is relevant to the user's question.\n"
            "- Do not ask the user to repeat information that is already clearly provided here.\n"
            "- Do not invent missing questionnaire information.\n"
            "- Do not assume that 'Part A and/or Part B selected' means the user has both Part A and Part B.\n"
            "- If the user's current message explicitly corrects questionnaire information, use the newer explicit information for the current answer.\n"
            "- Do NOT modify or claim to modify the saved questionnaire data.\n"
            "- Do not unnecessarily repeat the full questionnaire in the response.\n"
        )

    # 將 location_context 動態塞入系統提示詞
    strict_system_instruction = (
        f"You are Medicare Compass, an expert assistant.\n"
        f"CRITICAL RULE: You MUST respond ENTIRELY in {target_lang}. "
        f"All headings, table headers, bullet points, advice, and tips MUST be accurately translated into {target_lang}.\n"
        f"{location_context}\n\n" 
        f"{persona_context}\n\n"
        f"{questionnaire_instruction}\n\n"

        "Task: Present Medicare choices concisely.\n\n"

        "MEDICARE ELIGIBILITY SAFETY RULES:\n"
        "1. PART B AND EMPLOYER COVERAGE:\n"
        "   - IMPORTANT: Employer size determines which coverage generally pays first; employer size alone does NOT determine Part B Special Enrollment Period eligibility. A qualifying group health plan based on current employment may still provide a Part B SEP even when the employer has fewer than 20 employees.\n"
        "   - Only treat employer coverage as a reason to delay Part B when it is group health coverage based on the CURRENT employment of the user or the user's spouse.\n"
        "   - If the user clearly states that the current employer has 20 or more employees, explain that Part B can generally be delayed while qualifying current-employment group coverage continues, with a Special Enrollment Period available later. Do NOT automatically tell the user to enroll in Part B immediately solely because they are turning 65.\n"
        "   - If the employer has fewer than 20 employees, Medicare generally pays first. Explain that the user should confirm coordination with the employer plan and generally should not assume Part B can be safely delayed.\n"
        "   - COBRA and retiree coverage are NOT the same as current-employment group health coverage for the Part B Special Enrollment Period.\n"
        "   - If employer coverage type or employer size is unknown, do NOT guess. Clearly state what information still needs to be confirmed.\n\n"

        "2. PART A WORK CREDITS AND SPOUSE ELIGIBILITY:\n"
        "   - NEVER convert or reinterpret a user's statement that someone 'paid Social Security taxes' into proof of Medicare-covered employment or sufficient Medicare work credits. Treat Medicare-covered work history as UNKNOWN unless the user explicitly states it or it is otherwise confirmed.\n"
        "   - If the spouse's age or Medicare-covered work history is unknown, use wording such as 'may qualify' or 'may be eligible.' Do NOT say 'likely qualifies,' 'will qualify,' or 'will not have to pay a Part A premium.'\n"
        "   - Do not imply that a spouse receiving Social Security retirement benefits allows the user to receive age-based Medicare Part A before age 65. Age-based Medicare eligibility generally begins at 65 unless another qualifying condition applies.\n"
        "   - Premium-free Part A is generally available when the user has worked and paid Medicare taxes long enough, typically about 10 years / 40 quarters.\n"
        "   - If the user clearly states they do NOT have enough work credits, do NOT immediately conclude that they must pay a Part A premium. First consider whether they may qualify through a current or former spouse's work record.\n"
        "   - A current spouse may generally need to meet Social Security relationship requirements, including the usual one-year duration-of-marriage rule, but exceptions may apply.\n"
        "   - If neither the user's own work record nor a qualifying spouse-based record is established, explain only that a Part A premium MAY apply and recommend confirmation with Social Security.\n"
        "   - If work-credit or spouse information is unknown, do NOT invent it and do NOT make a definitive premium-free Part A determination.\n\n"

        "3. UNCERTAINTY, SAFETY, AND VERIFICATION:\n"
        "   - Do not provide Medicare premium, deductible, penalty, or cost amounts unless they are known to be current for the applicable year. If the current-year amount is not reliably available, describe the cost qualitatively and direct the user to Medicare.gov or Social Security for the current amount.\n"
        "   - Never reuse or assume a prior-year Medicare cost amount. If mentioning a dollar amount, clearly identify the applicable year and ensure it is current.\n"
        "   - Medicare eligibility, enrollment timing, premiums, penalties, and coordination of benefits can depend on facts that may not be fully available in the conversation. Do NOT present an eligibility or cost determination as guaranteed unless all required facts are clearly established.\n"
        "   - Prefer calibrated wording such as 'generally,' 'typically,' 'may qualify,' 'may be eligible,' 'based on the information provided,' and 'should confirm' when appropriate.\n"
        "   - Avoid overly absolute wording such as 'definitely,' 'guaranteed,' 'always,' 'never,' 'you will qualify,' or 'you will not have to pay' unless the conclusion is directly supported by confirmed facts and an applicable Medicare or Social Security rule.\n"
        "   - Clearly distinguish between a general Medicare rule and a final determination of the user's individual eligibility.\n"
        "   - When important information is missing, state exactly what still needs to be confirmed instead of guessing or filling in the missing fact.\n"
        "   - For decisions involving enrollment timing, late-enrollment penalties, premium-free Part A eligibility, Special Enrollment Periods, or employer coverage coordination, recommend final verification with the appropriate official source such as Social Security, Medicare, the employer's benefits administrator, or a SHIP counselor.\n"
        "   - Keep verification reminders concise. Do not overwhelm the user with repeated disclaimers or make the response sound alarmist.\n\n"

        "CRITICAL OUTPUT RULES:\n"
        "1. NO INTERNAL MONOLOGUE: Do not generate `<think>` tags, drafts, self-corrections, or reasoning steps.\n"
        "2. NO META-DATA: Never output system logic, user profiles, timeline tags, or checklists (e.g., 'User Profile:', 'Key Constraint Checklist:').\n"
        "3. START IMMEDIATELY: Begin your response directly with warm, friendly Medicare guidance.\n\n"

        "FINAL OUTPUT FORMAT:\n"
        "1. A Summary Comparison table contrasting Pathway A (Original Medicare) vs Pathway B (Medicare Advantage).\n"
        "2. 2 Key Decision-Making Questions.\n"
        "3. 1 Official Enrollment Tip."
    )
    
    # ... 後面的 safe_fallback 與模型呼叫維持原樣 ...
    
    # 🚨 Task 1.3: 準備各語言的安全備援回覆 (Safe Fallback)
    safe_fallback = {
        "English": "I've organized the Medicare suggestions for you. Please check the summary below, or ask me any specific questions!",
        "繁體中文": "系統已為您整理好 Medicare 的建議，請參考下方的重點摘要，或直接詢問我任何問題喔！",
        "簡體中文": "系统已为您整理好 Medicare 的建议，请参考下方的重点摘要，或直接询问我任何问题哦！",
        "Español": "He organizado las sugerencias de Medicare para usted. ¡Consulte el resumen a continuación o hágame cualquier pregunta específica!",
        "한국어": "메디케어 제안을 정리해 드렸습니다. 아래 요약을 확인하시거나 궁금한 점을 질문해 주세요!"
    }

    # 🚨 Task 1.1: 透過 GenerationConfig 設定 API 參數阻斷思考過程
    # stop_sequences 是強力的防線，只要碰到這些字串就強制停止輸出
    safe_config = genai.types.GenerationConfig(
        temperature=0.3, # 降低隨機性，讓輸出更穩定
        stop_sequences=["<think>", "User Profile:", "Constraint Check:"]
    )
    
    last_exception = None
    for m_name in valid_models:
        try:
            model = genai.GenerativeModel(
                model_name=m_name, 
                system_instruction=strict_system_instruction,
                generation_config=safe_config  # 套用安全設定
            )
            formatted_history = []
            if "messages" in st.session_state:
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
            
            # 🚨 Task 1.3 實作：如果清出來的字太短或為空，絕對不輸出 raw_text，改回傳安全備援句
            if not clean_text or len(clean_text) < 15:
                return safe_fallback.get(target_lang, safe_fallback["English"])
                
            return clean_text
            
        except Exception as inner_e:
            last_exception = inner_e
            continue

    if last_exception:
        # 如果模型全數崩潰，也回傳安全的預設語句，避免畫面當掉 (Task 3.2 的一部分)
        return safe_fallback.get(target_lang, safe_fallback["English"])

def _normalize_ship_value(value):
    """SHIP 欄位統一轉成乾淨字串；未知值一律視為空白。"""
    if value is None:
        return ""

    if isinstance(value, list):
        value = "\n".join(str(item).strip() for item in value if str(item).strip())
    else:
        value = str(value).strip()

    if value.lower() in {"unknown", "not provided", "not mentioned", "n/a", "na", "none", "null", "-"}:
        return ""

    return value


def _fallback_extract_ship_fields(user_text, existing_zip=""):
    """當 Gemini 無法完成結構化擷取時，使用保守 Regex 做基本 fallback。"""
    result = {
        "zip_code": existing_zip or "",
        "current_plan": "",
        "monthly_premium": "",
        "primary_concern": "",
        "medications": "",
    }

    if not user_text:
        return result

    clean_text = re.sub(
        r"\[(?:Applying for Myself|Helping Family/Parents)\]\s*",
        "",
        user_text,
        flags=re.IGNORECASE,
    )

    if not result["zip_code"]:
        zip_match = re.search(r"\b(\d{5})(?:-\d{4})?\b", clean_text)
        if zip_match:
            result["zip_code"] = zip_match.group(1)

    plan_patterns = [
        r"(?:my|current)\s+plan\s+(?:is|:)\s*([^\n.!?]{2,120})",
        r"(?:i\s*(?:am|'m)\s+(?:on|enrolled\s+in|covered\s+by))\s+([^\n.!?]{2,120})",
    ]
    for pattern in plan_patterns:
        match = re.search(pattern, clean_text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip(" .,:;-")
            if candidate:
                result["current_plan"] = candidate
                break

    premium_patterns = [
        r"(?:monthly\s+premium|premium)\s*(?:is|:|of)?\s*\$?\s*(\d+(?:\.\d{1,2})?)",
        r"(?:i\s+pay|paying)\s*\$?\s*(\d+(?:\.\d{1,2})?)\s*(?:a|per)?\s*month",
        r"\$\s*(\d+(?:\.\d{1,2})?)\s*(?:a|per)\s*month",
    ]
    for pattern in premium_patterns:
        match = re.search(pattern, clean_text, flags=re.IGNORECASE)
        if match:
            result["monthly_premium"] = match.group(1)
            break

    medication_lines = []
    medication_patterns = [
        r"(?:i\s+take|i\s*(?:am|'m)\s+taking)\s+([^\n.!?]+)",
        r"(?:my\s+medications?(?:\s+include)?|medications?)\s*(?:are|include|:)?\s*([^\n.!?]+)",
    ]
    for pattern in medication_patterns:
        for match in re.finditer(pattern, clean_text, flags=re.IGNORECASE):
            candidate = match.group(1).strip(" .,:;-")
            if candidate and candidate not in medication_lines:
                medication_lines.append(candidate)

    if medication_lines:
        result["medications"] = "\n".join(medication_lines)

    concern_candidates = []
    for raw_line in clean_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lowered = line.lower()
        if (
            "?" in line
            or "worried" in lowered
            or "concern" in lowered
            or "want to know" in lowered
            or "should i" in lowered
            or "can i" in lowered
            or "do i need" in lowered
        ):
            if line not in concern_candidates:
                concern_candidates.append(line)

        if len(concern_candidates) >= 3:
            break

    if concern_candidates:
        result["primary_concern"] = " ".join(concern_candidates)

    return result


def extract_ship_fields(messages, target_lang="English", existing_zip=""):
    """
    從目前對話中擷取 SHIP Prep 原生五欄需要的資料。

    原則：
    - 只使用使用者明確提供的資訊，不猜測。
    - 州/城市不能推導 ZIP；沒有 ZIP 就留空。
    - Primary Concern 可根據使用者實際提問做簡短整理，但不可新增未提及事實。
    - 如果 Gemini 擷取失敗，退回保守 Regex fallback。
    """
    user_messages = []

    for message in messages or []:
        if message.get("role") != "user":
            continue

        content = str(message.get("content", "")).strip()
        content = re.sub(
            r"\[(?:Applying for Myself|Helping Family/Parents)\]\s*",
            "",
            content,
            flags=re.IGNORECASE,
        ).strip()

        if content:
            user_messages.append(content)

    transcript = "\n\n".join(
        f"USER {idx + 1}: {text}"
        for idx, text in enumerate(user_messages)
    )

    fallback = _fallback_extract_ship_fields(
        transcript,
        existing_zip=existing_zip,
    )

    if not transcript:
        return fallback

    preferred_models = [
        "gemini-3.5-flash-lite", "gemini-3.1-flash-lite",
        "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"
    ]
    valid_models = []

    try:
        available_models = {}
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                model_id = m.name.replace("models/", "")
                available_models[model_id] = m.name
        valid_models = [available_models[m] for m in preferred_models if m in available_models]
    except Exception:
        pass

    if not valid_models:
        valid_models = [f"models/{m}" for m in preferred_models]

    extraction_prompt = f"""
You are a strict data-extraction component for Medicare Compass.
Read ONLY the USER messages below and extract data for an existing SHIP consultation form.

Return ONLY one valid JSON object with exactly these keys:
{{
  "zip_code": "",
  "current_plan": "",
  "monthly_premium": "",
  "primary_concern": "",
  "medications": ""
}}

Rules:
1. Use only facts explicitly stated by the user. Never guess or invent missing information.
2. Do NOT infer a ZIP Code from a state, city, county, neighborhood, or plan. If the user only says New York / NY / New Jersey / NJ, zip_code must remain empty.
3. current_plan is the user's CURRENT insurance/Medicare plan name only when clearly stated.
4. monthly_premium is the monthly premium for the CURRENT plan only. Do not confuse copays, deductibles, drug costs, Part B premium, or annual costs with the current-plan premium.
5. primary_concern may summarize the user's actual questions/concerns in 1-3 concise sentences, but may not add facts. Write this field in {target_lang}.
6. medications should list only current regular prescription medications explicitly stated by the user. Preserve name/dosage/frequency when provided. Separate multiple medications with newline characters.
7. If a field is unknown, uncertain, or not stated, return an empty string.
8. Do not include explanations, Markdown, code fences, or extra keys.

Known explicit ZIP captured earlier from user input (may be empty): {existing_zip}

USER MESSAGES:
---
{transcript}
---
""".strip()

    import json

    for m_name in valid_models:
        try:
            extraction_config = genai.types.GenerationConfig(
                temperature=0.0,
            )

            model = genai.GenerativeModel(
                model_name=m_name,
                generation_config=extraction_config,
            )

            response = model.generate_content(extraction_prompt)
            raw_text = str(response.text or "").strip()
            raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.IGNORECASE)

            json_match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
            if not json_match:
                continue

            parsed = json.loads(json_match.group(0))

            result = {
                "zip_code": _normalize_ship_value(parsed.get("zip_code", "")),
                "current_plan": _normalize_ship_value(parsed.get("current_plan", "")),
                "monthly_premium": _normalize_ship_value(parsed.get("monthly_premium", "")),
                "primary_concern": _normalize_ship_value(parsed.get("primary_concern", "")),
                "medications": _normalize_ship_value(parsed.get("medications", "")),
            }

            # 已經由既有 Regex 明確抓到的 ZIP 優先，避免模型修改。
            if existing_zip:
                result["zip_code"] = existing_zip

            # AI 沒抓到的欄位才用保守 fallback 補上。
            for key in result:
                if not result[key] and fallback.get(key):
                    result[key] = fallback[key]

            return result

        except Exception:
            continue

    return fallback
