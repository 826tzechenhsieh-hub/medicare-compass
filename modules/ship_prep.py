import streamlit as st
from core.translations import m3_labels

def render(current_lang):
    l3 = m3_labels.get(current_lang, m3_labels["English"])
    st.markdown(l3["title"])
    st.caption(l3["caption"])
    st.markdown("---")

    with st.form("ship_prep_form"):
        col1, col2 = st.columns(2)
        with col1:
            zip_code = st.text_input(l3["zip_label"], "90210")
            current_plan = st.text_input(l3["plan_label"], l3["plan_placeholder"])
        with col2:
            monthly_cost = st.text_input(l3["cost_label"], "0")
            primary_concern = st.text_input(l3["concern_label"], l3["concern_default"])

        meds = st.text_area(l3["meds_label"], l3["meds_default"])
        submitted = st.form_submit_button(l3["btn_label"])

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
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom:0;">{l3['footer_note']}</p>
            </div>
            """, unsafe_allow_html=True
        )