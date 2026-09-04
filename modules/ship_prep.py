import html
import streamlit as st
from core.translations import (
    m3_labels,
    profile_priority_labels,
    ship_flow_map,
)


def _safe_html_text(value):
    """將表單文字安全轉成可放進 HTML 卡片的內容。"""
    return html.escape(str(value or "")).replace("\n", "<br>")

def _get_profile_ship_payload(current_lang):
    """
    從已完成的詢問單取得 SHIP 可直接使用的確認資料。
    詢問單未完成時全部回傳空白。
    """

    empty_payload = {
        "zip_code": "",
        "current_plan": "",
        "monthly_premium": "",
        "primary_concern": "",
        "medications": "",
    }

    if not st.session_state.get("profile_completed", False):
        return empty_payload

    data = st.session_state.get("profile_data", {})

    if not isinstance(data, dict):
        return empty_payload

    # -----------------------------
    # Monthly Premium
    # None = 未提供
    # 0 = 已確認 $0
    # -----------------------------
    premium = data.get("monthly_premium")

    if premium is None or premium == "":
        premium_text = ""
    elif isinstance(premium, float) and premium.is_integer():
        premium_text = str(int(premium))
    else:
        premium_text = str(premium)

    # -----------------------------
    # Primary Concern
    # 固定選項使用翻譯文字
    # Other 使用使用者自行輸入內容
    # -----------------------------
    priority_code = data.get("priority_code", "")

    if priority_code == "other":
        priority_text = str(
            data.get("priority_other", "")
        ).strip()
    else:
        priority_labels = profile_priority_labels.get(
            current_lang,
            profile_priority_labels["English"],
        )

        priority_text = priority_labels.get(
            priority_code,
            "",
        )

    health_notes = str(
        data.get("health_notes", "")
    ).strip()

    concern_parts = []

    if priority_text:
        concern_parts.append(priority_text)

    if health_notes:
        concern_parts.append(health_notes)

    profile_concern = "\n".join(concern_parts)

    return {
        "zip_code": str(data.get("zip_code", "")).strip(),

        # Questionnaire 目前只有 coverage type，
        # 沒有 Aetna / Humana 這種真正的 plan name，
        # 所以不能塞進 Current Plan Name。
        "current_plan": "",

        "monthly_premium": premium_text,
        "primary_concern": profile_concern,
        "medications": str(
            data.get("medications", "")
        ).strip(),
    }


def _merge_unique_text(primary_text, secondary_text):
    """
    Profile 是主要資料；
    Main AI 對話可以補充內容，但避免完全相同的文字重複。
    """

    primary_text = str(primary_text or "").strip()
    secondary_text = str(secondary_text or "").strip()

    if not primary_text:
        return secondary_text

    if not secondary_text:
        return primary_text

    if secondary_text.lower() in primary_text.lower():
        return primary_text

    if primary_text.lower() in secondary_text.lower():
        return secondary_text

    return f"{primary_text}\n{secondary_text}"


def _merge_ship_payload(profile_payload, conversation_payload):
    """
    合併原則：
    Questionnaire = 已確認資料，優先
    Main AI conversation = 補詢問單沒有的資料
    """

    conversation_payload = (
        conversation_payload
        if isinstance(conversation_payload, dict)
        else {}
    )

    profile_premium = profile_payload.get(
        "monthly_premium",
        "",
    )

    return {
        "zip_code":
            profile_payload.get("zip_code")
            or conversation_payload.get("zip_code", "")
            or "",

        # Questionnaire 沒有真正的 Plan Name，
        # 因此這欄仍由 Main AI 對話擷取。
        "current_plan":
            conversation_payload.get("current_plan", "")
            or "",

        # 這裡不能用 `or`！
        # 因為已確認的 $0 也是有效資料。
        "monthly_premium":
            profile_premium
            if profile_premium != ""
            else conversation_payload.get(
                "monthly_premium",
                "",
            ),

        "primary_concern":
            _merge_unique_text(
                profile_payload.get(
                    "primary_concern",
                    "",
                ),
                conversation_payload.get(
                    "primary_concern",
                    "",
                ),
            ),

        "medications":
            profile_payload.get("medications")
            or conversation_payload.get(
                "medications",
                "",
            )
            or "",
    }

def render(current_lang):
    l3 = m3_labels.get(current_lang, m3_labels["English"])

    ship_flow = ship_flow_map.get(
        current_lang,
        ship_flow_map["English"],
    )

    st.markdown(l3["title"])
    st.caption(l3["caption"])
    st.markdown("---")

    # --------------------------------------------------
    # 從 Main AI 的 SHIP 按鈕帶入資料
    # --------------------------------------------------
    # 為了相容 app.py 原本的 reset key，仍沿用 ship_auto_notes 當作
    # 「內部傳輸容器」，但它不再顯示成第六個 AI Notes 欄位。
    # --------------------------------------------------
    # Questionnaire + Main AI → SHIP
    # --------------------------------------------------

    # 1. 已確認的詢問單資料
    profile_payload = _get_profile_ship_payload(
        current_lang
    )

    # 2. Main AI 對話擷取資料
    conversation_payload = st.session_state.get(
        "ship_auto_notes",
        {},
    )

    if not isinstance(conversation_payload, dict):
        conversation_payload = {}

    # 3. 合併
    # Questionnaire 優先，conversation 補缺少資訊
    auto_payload = _merge_ship_payload(
        profile_payload,
        conversation_payload,
    )

    auto_zip = (
        auto_payload.get("zip_code")
        or st.session_state.get(
            "ship_auto_zip",
            "",
        )
        or ""
    )

    auto_plan = (
        auto_payload.get("current_plan", "")
        or ""
    )

    auto_premium = auto_payload.get(
        "monthly_premium",
        "",
    )

    auto_concern = (
        auto_payload.get("primary_concern", "")
        or ""
    )

    auto_meds = (
        auto_payload.get("medications", "")
        or ""
    )

    auto_state = (
        st.session_state.get("ship_auto_state", "")
        or ""
    )

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

    # --------------------------------------------------
    # SHIP Official Website + Appointment Reminder
    # --------------------------------------------------
    st.write("")

    col_ship, col_calendar = st.columns(2)

    with col_ship:
        st.link_button(
            ship_flow["official_btn"],
            "https://www.shiphelp.org/",
            use_container_width=True,
        )

    with col_calendar:
        if st.button(
            ship_flow["calendar_btn"],
            use_container_width=True,
            key="ship_to_calendar",
        ):
            st.session_state["_pending_app_mode"] = "CALENDAR_ICS"
            st.rerun()

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
