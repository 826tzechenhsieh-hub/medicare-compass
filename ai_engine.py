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

def generate_clean_response(user_input, target_lang="English", img_data=None):
    """呼叫 Gemini 模型並強制以目標語言輸出乾淨的結果"""
    preferred_models = [
        "gemini-3.6-flash", "gemini-3.5-flash", 
        "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-flash"
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

    # 🔥 準備動態地理資訊字串 (Context Injection)
    location_context = ""
    if st.session_state.get("user_zip") or st.session_state.get("user_state"):
        locs = []
        if st.session_state.get("user_state"): locs.append(f"State: {st.session_state.user_state}")
        if st.session_state.get("user_zip"): locs.append(f"Zip: {st.session_state.user_zip}")
        location_context = f"\n\nUSER LOCATION CONTEXT: {', '.join(locs)}. You MUST tailor your Medicare advice (like Advantage plans and Medigap rules) to this specific location."

    # 將 location_context 動態塞入系統提示詞
    strict_system_instruction = (
        f"You are Medicare Compass, an expert assistant.\n"
        f"CRITICAL RULE: You MUST respond ENTIRELY in {target_lang}. "
        f"All headings, table headers, bullet points, advice, and tips MUST be accurately translated into {target_lang}.\n"
        f"{location_context}\n\n" # <--- 注入在這裡
        "Task: Present Medicare choices concisely.\n\n"
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