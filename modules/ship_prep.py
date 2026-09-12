import html
import json

import streamlit as st

from core.translations import (
    m3_labels,
    profile_priority_labels,
    ship_flow_map,
)
from core.bilingual_output import (
    supports_bilingual,
    generate_bilingual_version,
    get_cached_bilingual,
)


def _safe_html_text(value):
    """將表單文字安全轉成可放進 HTML 卡片的內容。"""
    return html.escape(str(value or "")).replace("\n", "<br>")


def _render_print_button(markdown_text, button_label, document_title):
    """用瀏覽器原生列印視窗列印 SHIP 文件，可另存為 PDF。"""
    safe_md = json.dumps(markdown_text, ensure_ascii=False)
    safe_label = html.escape(str(button_label))
    safe_title = html.escape(str(document_title))

    html_snippet = f"""
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <body style="margin:0; padding:0;">
        <button
            onclick="printClean()"
            style="
                width:100%;
                height:46px;
                border-radius:8px;
                background-color:#16A34A;
                color:white;
                border:none;
                cursor:pointer;
                font-size:17px;
                font-weight:bold;
                font-family:sans-serif;
            "
        >
            {safe_label}
        </button>
    </body>

    <script>
    function printClean() {{
        const markdownText = {safe_md};
        const htmlContent = marked.parse(markdownText);
        const printWindow = window.open('', '', 'width=850,height=700');

        if (!printWindow) {{
            alert('Please allow pop-ups to print or save as PDF.');
            return;
        }}

        printWindow.document.write(
            '<html><head><title>{safe_title}</title>' +
            '<style>' +
            '@page {{ size: auto; margin: 16mm; }} ' +
            'body {{ font-family: Arial, sans-serif; line-height: 1.65; padding: 0; color: #111827; max-width: 800px; margin: auto; }} ' +
            'h1 {{ color: #1e3a8a; text-align: center; font-size: 26px; margin-bottom: 24px; }} ' +
            'h2, h3 {{ color: #1e3a8a; margin-top: 24px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }} ' +
            'p {{ margin: 10px 0 18px; }} ' +
            'ul {{ padding-left: 24px; }} ' +
            'li {{ margin-bottom: 8px; }} ' +
            'hr {{ border: 0; border-top: 1px solid #cbd5e1; margin: 20px 0; }} ' +
            '</style>' +
            '</head><body>' +
            htmlContent +
            '</body></html>'
        );

        printWindow.document.close();

        setTimeout(function() {{
            printWindow.focus();
            printWindow.print();
        }}, 500);
    }}
    </script>
    """

    st.components.v1.html(html_snippet, height=55)


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

def _normalize_bilingual_preview(markdown_text):
    """
    只調整螢幕 Preview 的 Markdown 標題大小。
    不影響 TXT / PDF 匯出內容。
    """
    lines = []

    for line in str(markdown_text or "").splitlines():

        if line.startswith("# "):
            line = "### " + line[2:]

        elif line.startswith("## "):
            line = "#### " + line[3:]

        elif line.startswith("### "):
            line = "##### " + line[4:]

        lines.append(line)

    return "\n".join(lines)

def _build_ship_document_markdown(result, l3):
    """建立 SHIP 原語言文件，供預覽、AI 雙語轉換、TXT 與 PDF 共用。"""

    ship_document_title = str(
        l3["title"]
    ).replace("##", "").strip()

    lines = [
        f"# {ship_document_title}",
        "",
        f"**{l3['zip_label']}:** {result.get('zip_code') or '—'}",
        "",
        f"**{l3['cost_label']}:** {result.get('monthly_cost') or '—'}",
        "",
        f"**{l3['plan_label']}:** {result.get('current_plan') or '—'}",
        "",
        f"## {l3['concern_label']}",
        "",
        result.get("primary_concern") or "—",
        "",
        f"## {l3['meds_label']}",
        "",
        result.get("meds") or "—",
        "",
        "---",
        "",
        l3["footer_note"],
    ]

    return "\n".join(lines).strip() + "\n"


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
    # Generate 1-Page Summary
    # --------------------------------------------------
    if submitted:
        result = {
            "zip_code": str(zip_code or "").strip(),
            "monthly_cost": str(monthly_cost or "").strip(),
            "current_plan": str(current_plan or "").strip(),
            "primary_concern": str(primary_concern or "").strip(),
            "meds": str(meds or "").strip(),
        }

        # 先存起來，避免點 Download / Print 後 rerun 讓 Preview 消失
        st.session_state["ship_prep_result"] = result

        # 非 English：按 Generate 後直接產生 Bilingual，不再多一顆按鈕
        if supports_bilingual(current_lang):
            source_markdown = _build_ship_document_markdown(
                result,
                l3,
            )

            # 新的 Summary 要重新對應新的雙語結果，
            # 先清掉 SHIP Prep 自己保存的舊 Preview。
            st.session_state.pop(
                "ship_prep_bilingual_result",
                None,
            )

            try:
                with st.spinner(
                    "Generating bilingual version..."
                ):
                    bilingual_ship = generate_bilingual_version(
                        source_text=source_markdown,
                        current_lang=current_lang,
                        cache_name="ship_prep",
                    )

                # 直接保存 generate_bilingual_version() 的回傳值。
                # 不只依賴 bilingual_output.py 內部 cache，
                # 避免 AI 已經跑完但 Preview 取不到結果。
                st.session_state["ship_prep_bilingual_result"] = {
                    "source": source_markdown,
                    "language": current_lang,
                    "content": bilingual_ship,
                }

            except Exception as e:
                st.error(
                    f"Unable to generate bilingual version: {e}"
                )

    # --------------------------------------------------
    # Preview
    # --------------------------------------------------
    saved_result = st.session_state.get(
        "ship_prep_result",
        None,
    )

    if isinstance(saved_result, dict):

        st.markdown("---")

        ship_document_markdown = _build_ship_document_markdown(
            saved_result,
            l3,
        )

        ship_document_title = str(
            l3["title"]
        ).replace("##", "").strip()

        # --------------------------------------------------
        # 原語言 Summary Card
        # --------------------------------------------------
        safe_zip = _safe_html_text(
            saved_result.get("zip_code")
        ) or "—"

        safe_plan = _safe_html_text(
            saved_result.get("current_plan")
        ) or "—"

        safe_cost = _safe_html_text(
            saved_result.get("monthly_cost")
        ) or "—"

        safe_concern = _safe_html_text(
            saved_result.get("primary_concern")
        ) or "—"

        safe_meds = _safe_html_text(
            saved_result.get("meds")
        ) or "—"

        st.markdown(
            f"""
            <div class="card-box ship-summary-card" style="border: 2px solid #2563eb; background-color: #ffffff;">
                <h3 style="text-align:center; color:#1e3a8a; margin-top:0;">{html.escape(ship_document_title)}</h3>
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

        # --------------------------------------------------
        # 非 English：直接顯示 Bilingual Preview
        # English：直接使用英文原稿
        # --------------------------------------------------
        export_document = ship_document_markdown

        if supports_bilingual(current_lang):
            bilingual_ship = None

            # 先讀 SHIP Prep 直接保存的 AI 回傳結果。
            saved_bilingual = st.session_state.get(
                "ship_prep_bilingual_result",
                {},
            )

            if (
                isinstance(saved_bilingual, dict)
                and saved_bilingual.get("source") == ship_document_markdown
                and saved_bilingual.get("language") == current_lang
            ):
                bilingual_ship = saved_bilingual.get(
                    "content"
                )

            # 若 Session State 沒有，再回頭讀共用 bilingual cache。
            if not bilingual_ship:
                bilingual_ship = get_cached_bilingual(
                    "ship_prep",
                    ship_document_markdown,
                    current_lang,
                )

            if bilingual_ship:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🌐 Bilingual Preview")

                with st.container(border=True):
                    st.markdown(
                        _normalize_bilingual_preview(
                            bilingual_ship
                        )
                    )

                export_document = bilingual_ship

        # --------------------------------------------------
        # 匯出按鈕
        # 非英文時匯出雙語版；English 時匯出英文版
        # --------------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.download_button(
                "📄 TXT",
                data=export_document,
                file_name=(
                    "medicare_ship_prep_bilingual.txt"
                    if supports_bilingual(current_lang)
                    else "medicare_ship_prep.txt"
                ),
                mime="text/plain",
                use_container_width=True,
                key="ship_prep_download_txt",
            )

        with export_col2:
            _render_print_button(
                export_document,
                "🖨️ Print / PDF",
                (
                    f"{ship_document_title} - Bilingual"
                    if supports_bilingual(current_lang)
                    else ship_document_title
                ),
            )

    # --------------------------------------------------
    # SHIP Official Website + Appointment Reminder
    # 放在文件產出之後，流程比較順
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
