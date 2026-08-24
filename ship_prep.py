import streamlit as st
from core.translations import m3_labels

def render(current_lang):
    l3 = m3_labels.get(current_lang, m3_labels["English"])
    st.markdown(l3["title"])
    st.caption(l3["caption"])
    st.markdown("---")

    # 抓取從 AI 模組「一鍵匯入」傳過來的地理與總結資料
    auto_zip = st.session_state.get("ship_auto_zip", "")
    default_zip = auto_zip if auto_zip else "90210"
    auto_notes = st.session_state.get("ship_auto_notes", "")

    with st.form("ship_prep_form"):
        col1, col2 = st.columns(2)
        with col1:
            zip_code = st.text_input(l3["zip_label"], value=default_zip)
            current_plan = st.text_input(l3["plan_label"], value=l3["plan_placeholder"])
        with col2:
            monthly_cost = st.text_input(l3["cost_label"], value="0")
            primary_concern = st.text_input(l3["concern_label"], value=l3["concern_default"])

        # ✅ 修正：讓藥物欄位回歸乾淨，只顯示預設的藥物提示字
        meds = st.text_area(l3["meds_label"], value=l3["meds_default"])
        
        # ✅ 新增：把 AI 的對話總結放在獨立的專屬欄位，不干擾原本的表單
        ai_summary_label = "🤖 AI 諮詢重點 (從聊天室自動匯入)" if current_lang != "English" else "🤖 AI Consultation Notes (Auto-imported)"
        if auto_notes:
            ai_notes = st.text_area(ai_summary_label, value=auto_notes, height=200)
        else:
            ai_notes = ""
            
        submitted = st.form_submit_button(l3["btn_label"])

    if submitted:
        st.markdown("---")
        
        # 如果有 AI 總結，就在最後的卡片加上去
        notes_html = ""
        if ai_notes:
            notes_html = f"<hr><p><b>🤖 AI Notes:</b><br>{ai_notes.replace(chr(10), '<br>')}</p>"

        st.markdown(
            f"""
            <div class="card-box" style="border: 2px solid #2563eb; background-color: #ffffff;">
                <h3 style="text-align:center; color:#1e3a8a; margin-top:0;">🩺 Medicare Compass - SHIP Counseling Summary</h3>
                <hr>
                <p><b>📍 ZIP Code:</b> {zip_code} | <b>Current Plan:</b> {current_plan} (${monthly_cost}/mo)</p>
                <p><b>❓ Primary Concern:</b> {primary_concern}</p>
                <p><b>💊 Medication List:</b><br>{meds.replace(chr(10), '<br>')}</p>
                {notes_html}
                <hr>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom:0;">{l3['footer_note']}</p>
            </div>
            """, unsafe_allow_html=True
        )