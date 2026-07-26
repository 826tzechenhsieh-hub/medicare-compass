import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 頁面標題與配置設定
st.set_page_config(page_title="Medicare Compass 醫保指南針", page_icon="🧭", layout="centered")

st.title("🧭 Medicare Compass 醫保指南針")
st.caption("您的美國醫療保險隨身顧問 | 協助您避開罰款、清楚掌握申辦步驟")

# 2. 抓取 API Key (優先讀取 Secrets，若無則顯示輸入框)
api_key = st.secrets.get("GEMINI_API_KEY", None)

# 3. 側邊欄（Sidebar）導航、防詐警示與語言說明
with st.sidebar:
    st.header("🗺️ 申辦三大階段導航")
    st.markdown("""
    * **第一步：方案探索** *(Traditional Medicare vs. Advantage，該怎麼選？)*
    * **第二步：申辦流程** *(何時申辦？去哪裡申辦？如何避開罰款？)*
    * **第三步：保費與繳費處理** *(Part B 保費、Deductible 與 IRMAA 調整)*
    """)
    st.markdown("---")
    
    st.header("🌐 語言支援 / Languages")
    st.info("💬 本系統支援 **中文、English** 及多國語言，您可用習慣的語言直接發問或講話！")
    
    st.markdown("---")
    # 亮點功能：官方防詐提醒卡
    st.warning("""
    ⚠️ **官方防詐與權益提醒**：  
    Medicare 官方人員**絕不會**主動打電話索取您的 Social Security Number 或銀行帳戶。請認準官方網站 Medicare.gov 或諮詢 SHIP 官方輔導專線 (1-800-252-8966)。
    """)
    
    if not api_key:
        api_key = st.text_input("請輸入您的 Gemini API Key：", type="password")
    else:
        st.success("✅ 系統服務已就緒！")

# 4. 系統指令 (System Instruction) 藍圖
SYSTEM_INSTRUCTION = """
你是一位極具耐心、溫暖且精通美國醫療保險體系的「Medicare 智慧導覽顧問（Medicare Compass）」。
你的使命是幫助剛滿 65 歲的退休族群、離職退休者、第一代移民，以及想從 Medicare Advantage 轉回 Traditional Medicare 的長者與家屬，用最白話、最無痛的方式找到最適方案並避開陷阱。

【你的溝通原則】
1. 語氣溫和、鼓勵且極具安全感，像熟知美國保險的親切朋友。
2. 絕不堆砌專業術語。遇到專有名詞時，必須用生活化的比喻解釋（例如：Deductible 是「每年看病自己要先墊付的額度」）。
3. 破除「政府全包」迷思：第一時間明確告知用戶，Original Medicare (Part B) 政府只包 80%，剩下的 20% 沒有最高上限，這就是為什麼需要 Medigap（補充保險）來蓋住無底洞！
4. 考慮長者的閱讀與視力需求，回答結構要清晰、短句為主、重點加粗，適合文字轉語音（TTS）朗讀。
5. 多語言能力：若使用者用英文詢問，請以英文親切回答；若用中文詢問，請以中文回答。若使用者上傳照片（保單或 SSA 信件），請為其閱讀並摘要關鍵日期與應辦事項。

【開場白設定】
你的第一句開場白必須是：
「您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱，找到最適合您與家人的方案。

請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？」
"""

# 5. 對話歷史紀錄初始化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "您好！我是您的 Medicare 智慧導覽助手。無論您是即將滿 65 歲準備第一次申請、仍在工作中準備退休，或是想了解如何轉方案，我都會一步步帶您避開時間與罰款陷阱，找到最適合您與家人的方案。\n\n請問您目前居住在哪一個州（或 Zip Code）？以及您的出生年月是什麼時候呢？"}
    ]

# 6. 顯示過往對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. 亮點功能：常用快捷問題按鈕（點擊自動代入問題）
st.write("💡 **熱門快速詢問（點擊可直接提問）：**")
col1, col2, col3 = st.columns(3)
quick_prompt = None

with col1:
    if st.button("❓ 什麼是 Medigap？"):
        quick_prompt = "請用最白話的方式告訴我，什麼是 Medigap？為什麼只買 Medicare Original 還不夠？"
with col2:
    if st.button("💼 65歲還在工作要辦 Part B 嗎？"):
        quick_prompt = "我今年 65 歲但還在公司全職工作，公司有提供醫療保險，我需要現在申請 Part B 嗎？會不會有罰款？"
with col3:
    if st.button("📝 什麼是 IRMAA 附加費？"):
        quick_prompt = "請解釋什麼是 IRMAA 保費附加費？如果我退休後收入變少，可以申請調降嗎？"

# 8. 圖片上傳區塊（照片辨識）
uploaded_file = st.file_uploader("📸 拍照或上傳 Medicare 保單 / SSA 官方信件照片（選填）：", type=["jpg", "jpeg", "png"])
img_data = None
if uploaded_file:
    img_data = Image.open(uploaded_file)
    st.image(img_data, caption="已讀取您上傳的照片", use_column_width=True)

# 9. 使用者輸入對話框（提示可用語音輸入）
input_prompt = st.chat_input("請輸入或使用手機鍵盤麥克風 🎙️ 語音輸入您的回答...")

# 判斷輸入來源（快捷按鈕、圖片上傳或鍵盤輸入）
prompt = quick_prompt if quick_prompt else input_prompt

if prompt or uploaded_file:
    if not api_key:
        st.error("請先在左側邊欄設定 API Key 才能開始對話喔！")
    else:
        try:
            clean_key = str(api_key).strip().strip('"').strip("'")
            genai.configure(api_key=clean_key)
            model = genai.GenerativeModel(
                model_name="gemini-3.6-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            user_content = prompt if prompt else "請幫我閱讀分析我剛才上傳的這張 Medicare / SSA 信件照片。"
            
            st.session_state.messages.append({"role": "user", "content": user_content})
            with st.chat_message("user"):
                st.markdown(user_content)

            with st.chat_message("assistant"):
                with st.spinner("Medicare Compass 正在為您分析思考中..."):
                    if img_data:
                        # 處理圖片+文字情境
                        response = model.generate_content([user_content, img_data])
                    else:
                        # 處理純對話情境
                        chat = model.start_chat(history=[
                            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                            for m in st.session_state.messages[:-1]
                        ])
                        response = chat.send_message(user_content)
                    
                    st.markdown(response.text)
                    
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun() # 重新整理頁面以更新按鈕狀態與對話顯示
        except Exception as e:
            st.error(f"連線發生錯誤，請檢查設定。詳細訊息: {e}")

# 10. 亮點功能：一鍵下載/備份對話清單
if len(st.session_state.messages) > 1:
    st.markdown("---")
    chat_history_text = "【Medicare Compass 醫保指南針 - 諮詢對話與導航清單】\n\n"
    for m in st.session_state.messages:
        role_title = "顧問" if m["role"] == "assistant" else "您"
        chat_history_text += f"[{role_title}]:\n{m['content']}\n\n------------------------\n\n"
    
    st.download_button(
        label="📥 下載本次諮詢紀錄與申辦清單 (TXT)",
        data=chat_history_text,
        file_name="Medicare_Compass_Consultation.txt",
        mime="text/plain"
    )
