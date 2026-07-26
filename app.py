import streamlit as st
import google.generativeai as genai

# 1. 頁面標題與大字體設定
st.set_page_config(page_title="Medicare Compass 醫保指南針", page_icon="🧭", layout="centered")

st.title("🧭 Medicare Compass 醫保指南針")
st.caption("您的美國醫療保險隨身顧問 | 協助您避開罰款、清楚掌握申辦步驟")

# 2. 自動取得後台設定的 API Key（若後台沒設定，則允許手動輸入）
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("⚙️ 系統設定")
    if not api_key:
        api_key = st.text_input("請輸入您的 Gemini API Key：", type="password")
    else:
        st.success("✅ 系統服務已就緒，可直接開始對話！")
    st.markdown("---")
    st.write("💡 **說明**：本工具由 Gemini AI 提供支援，保護您的隱私，不會儲存個人敏感情資。")

# 3. 系統指令 (System Instruction) 藍圖
SYSTEM_INSTRUCTION = """
你是一位極具耐心、溫暖且精通美國醫療保險體系的「Medicare 智慧導覽顧問（Medicare Compass）」。
你的使命是幫助剛滿 65 歲的退休族群、離職退休者、第一代移民，以及想從 Medicare Advantage 轉回 Traditional Medicare 的長者與家屬，用最白話、最無痛的方式找到最適方案並避開陷阱。

【你的溝通原則】
1. 語氣溫和、鼓勵且極具安全感，像熟知美國保險的親切朋友。
2. 絕不堆砌專業術語。遇到專有名詞時，必須用生活化的比喻解釋（例如：Deductible 是「每年看病自己要先墊付的額度」）。
3. 破除「政府全包」迷思：第一時間明確告知用戶，Original Medicare (Part B) 政府只包 80%，剩下的 20% 沒有最高上限，這就是為什麼需要 Medigap（補充保險）來蓋住無底洞！
4. 考慮長者的閱讀與視力需求，回答結構要清晰、短句為主、重點加粗，適合文字轉語音（TTS）朗讀。

【核心問答、時間軸、州別與防詐邏輯引擎】
當使用者開始對話時，請依序引導（一次只問 1~2 個問題）：

Step 1: 基礎定位、工作狀態與破除迷思
- 詢問使用者的居住州（Zip Code）與出生年月。
- 詢問目前工作狀態（在職/退休）。

Step 2: 選擇對應情境與健康/轉換門檻診斷
- 診斷州別特例（如 NY, CT 免健康檢查；CA, OR 生日條款）。

Step 3: Part D 處方藥防坑指南與 IRMAA / Extra Help 解惑
- 說明 Part D 終身罰款風險與基本方案防護。
- 說明 IRMAA 附加費與 SSA-44 表格申訴調降。

Step 4: 醫生 Network 與附加福利 (Dental, Vision, Hearing)

Step 5: 產出白話導航報告、官方信任資源與 30 天後續清單
- 最終摘要必須包含「目前狀態」與「步驟 roadmap」。

【開場白設定】
你的第一句開場白必須是：
「您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱，找到最適合您與家人的方案。

請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？」
"""

# 4. 對話歷史紀錄初始化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱，找到最適合您與家人的方案。\n\n請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？"}
    ]

# 5. 顯示過往對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 使用者輸入對話框
if prompt := st.chat_input("請輸入您的回答或疑問..."):
    if not api_key:
        st.error("請先在左側邊欄輸入您的 Gemini API Key 才能開始對話喔！")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Medicare Compass 正在為您思考中..."):
                chat = model.start_chat(history=[
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.messages[:-1]
                ])
                response = chat.send_message(prompt)
                st.markdown(response.text)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})
