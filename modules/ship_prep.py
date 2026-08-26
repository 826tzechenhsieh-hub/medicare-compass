import html
import streamlit as st
from core.translations import m3_labels


def _safe_html_text(value):
    """將表單文字安全轉成可放進 HTML 卡片的內容。"""
    return html.escape(str(value or "")).replace("\n", "<br>")


def render(current_lang):
    l3 = m3_labels.get(current_lang, m3_labels["English"])

    st.markdown(l3["title"])
    st.caption(l3["caption"])
    st.markdown("---")

    # --------------------------------------------------
    # 從 Main AI 的 SHIP 按鈕帶入資料
    # --------------------------------------------------
    # 為了相容 app.py 原本的 reset key，仍沿用 ship_auto_notes 當作
    # 「內部傳輸容器」，但它不再顯示成第六個 AI Notes 欄位。
    auto_payload = st.session_state.get("ship_auto_notes", {})
    if not isinstance(auto_payload, dict):
        auto_payload = {}

    auto_zip = (
        auto_payload.get("zip_code")
        or st.session_state.get("ship_auto_zip", "")
        or ""
    )
    auto_plan = auto_payload.get("current_plan", "") or ""
    auto_premium = auto_payload.get("monthly_premium", "") or ""
    auto_concern = auto_payload.get("primary_concern", "") or ""
    auto_meds = auto_payload.get("medications", "") or ""
    auto_state = st.session_state.get("ship_auto_state", "") or ""

    if any([auto_zip, auto_plan, auto_premium, auto_concern, auto_meds]):
        st.info(l3["auto_fill_note"])
    elif auto_state:
        st.info(l3["state_detected_note"].format(state=auto_state))

    # --------------------------------------------------
    # SHIP 原生五欄
    # 1. ZIP + Monthly Premium 同一層
    # 2. Current Plan Name 一整層
    # 3. Primary Concern / Question 一整層（大欄）
    # 4. Current Medications 一整層（大欄）
    # --------------------------------------------------
    with st.form("ship_prep_form"):
        col1, col2 = st.columns(2)

        with col1:
            zip_code = st.text_input(
                l3["zip_label"],
                value=auto_zip,
                placeholder=l3.get("zip_placeholder", ""),
            )

        with col2:
            monthly_cost = st.text_input(
                l3["cost_label"],
                value=auto_premium,
                placeholder=l3.get("cost_placeholder", ""),
            )

        current_plan = st.text_input(
            l3["plan_label"],
            value=auto_plan,
            placeholder=l3["plan_placeholder"],
        )

        primary_concern = st.text_area(
            l3["concern_label"],
            value=auto_concern,
            placeholder=l3["concern_placeholder"],
            height=150,
        )

        meds = st.text_area(
            l3["meds_label"],
            value=auto_meds,
            placeholder=l3["meds_placeholder"],
            height=170,
        )

        submitted = st.form_submit_button(
            l3["btn_label"],
            use_container_width=True,
        )

    if submitted:
        st.markdown("---")

        safe_zip = _safe_html_text(zip_code) or "—"
        safe_plan = _safe_html_text(current_plan) or "—"
        safe_cost = _safe_html_text(monthly_cost) or "—"
        safe_concern = _safe_html_text(primary_concern) or "—"
        safe_meds = _safe_html_text(meds) or "—"

        st.markdown(
            f"""
            <div class="card-box ship-summary-card" style="border: 2px solid #2563eb; background-color: #ffffff;">
                <h3 style="text-align:center; color:#1e3a8a; margin-top:0;">🩺 Medicare Compass - SHIP Counseling Summary</h3>
                <hr>
                <p><b>📍 {html.escape(l3['zip_label'])}:</b> {safe_zip}</p>
                <p><b>💵 {html.escape(l3['cost_label'])}:</b> {safe_cost}</p>
                <p><b>🪪 {html.escape(l3['plan_label'])}:</b> {safe_plan}</p>
                <p><b>❓ {html.escape(l3['concern_label'])}:</b><br>{safe_concern}</p>
                <p><b>💊 {html.escape(l3['meds_label'])}:</b><br>{safe_meds}</p>
                <hr>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom:0;">{html.escape(l3['footer_note'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
