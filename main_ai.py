import streamlit as st
import calendar
import datetime
import re
import json
import html
from core.translations import (
    guide_labels, q_caption_map, welcome_guide_map,
    input_placeholder_first_map, input_placeholder_followup_map,
    default_upload_msg_map, spinner_msg_map, timeline_template_map,
    tip_suffix_map, summary_title_map, ui_bottom_map, official_links_map,
    location_tracker_map, journey_buttons_map, ship_import_map,
    end_chat_btn_map
)
from core.ai_engine import generate_clean_response, extract_ship_fields
from core.response_cleaner import clean_response

# --- 新增的日期動態解析函數 (Task 4.3) ---
def extract_birth_month_year(text):
    """從自然語言中萃取生日的月份與年份"""
    import re
    # 1. 測試中文格式 (如：1960年8月, 1961年08月12日)
    zh_match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月", text)
    if zh_match:
        return int(zh_match.group(2)), int(zh_match.group(1))

    # 2. 測試英文月份格式 (如：August 1961, Aug 1, 1960)
    en_months_regex = r"(?i)\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b\s*(?:\d{1,2}(?:st|nd|rd|th)?\,?\s*)?(\d{4})\b"
    en_match = re.search(en_months_regex, text)
    if en_match:
        month_str = en_match.group(1).lower()
        year = int(en_match.group(2))
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
            'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
            'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
            'nov': 11, 'november': 11, 'dec': 12, 'december': 12
        }
        return month_map[month_str], year

    # 3. 測試原本的數字斜線格式 (如：08/1960, 8/1/1961)
    slash_match = re.search(r"(\d{1,2})/(?:(?:\d{1,2})/)?(\d{4})", text)
    if slash_match:
        return int(slash_match.group(1)), int(slash_match.group(2))

    return None, None
# ----------------------------------------

# Summary 專用：從整段對話中取得「最新」已知資料，不依賴使用者第幾輪才提供。
US_STATE_NAME_TO_CODE = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI",
    "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC",
}
US_STATE_CODES = set(US_STATE_NAME_TO_CODE.values())


def extract_state_from_text(text):
    """從文字中找州名或兩碼州縮寫；找不到就回傳空字串。"""
    if not text:
        return ""

    lowered = text.lower()

    # 先找完整州名，避免只靠兩碼縮寫造成誤判。
    for state_name in sorted(US_STATE_NAME_TO_CODE, key=len, reverse=True):
        if re.search(rf"\b{re.escape(state_name)}\b", lowered):
            return US_STATE_NAME_TO_CODE[state_name]

    # 再找兩碼州縮寫。
    for token in re.findall(r"\b[A-Z]{2}\b", text):
        code = token.upper()
        if code in US_STATE_CODES:
            return code

    return ""


def find_latest_birth_from_messages(messages):
    """從所有 User 訊息由後往前找最新的生日資訊。"""
    for message in reversed(messages):
        if message.get("role") != "user":
            continue

        month, year = extract_birth_month_year(str(message.get("content", "")))
        if month and year:
            return month, year

    return None, None


def find_latest_state_from_messages(messages):
    """優先使用 Session State；沒有時再從所有 User 訊息中尋找。"""
    saved_state = str(st.session_state.get("user_state", "")).strip()
    if saved_state:
        return saved_state

    for message in reversed(messages):
        if message.get("role") != "user":
            continue

        state = extract_state_from_text(str(message.get("content", "")))
        if state:
            return state

    return ""


def calculate_summary_timeline(month, year):
    """使用目前既有的 IEP 月份算法，產出 Summary 需要的結構化日期。"""
    turn_65_year = year + 65

    start_m = month - 3 if month > 3 else month - 3 + 12
    start_y = turn_65_year if month > 3 else turn_65_year - 1

    end_m = month + 3 if month <= 9 else month + 3 - 12
    end_y = turn_65_year if month <= 9 else turn_65_year + 1
    end_day = calendar.monthrange(end_y, end_m)[1]

    return {
        "birth": f"{month:02d}/{year}",
        "turn_65": f"{month:02d}/{turn_65_year}",
        "iep_start": f"{start_m:02d}/01/{start_y}",
        "iep_end": f"{end_m:02d}/{end_day:02d}/{end_y}",
    }


def build_key_decision_points(text, max_points=6):
    """
    將最後一則 AI 回覆整理成較精簡的條列。
    只做顯示層整理，不重新呼叫 AI，也不改變原本諮詢流程。
    """
    cleaned = clean_response(text or "")
    if not cleaned:
        return []

    points = []

    for raw_line in cleaned.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # 移除 Markdown 分隔線與標題符號，避免 Summary 出現 ### / ***。
        if re.fullmatch(r"[-*_]{3,}", line):
            continue
        if line.startswith("#"):
            continue

        # Summary 不直接搬表格，避免一頁摘要太擁擠。
        if line.startswith("|"):
            continue

        # 去掉 blockquote / bullet / numbered-list 前綴，但保留粗體等 Markdown。
        line = re.sub(r"^>\s*", "", line)
        line = re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", line).strip()
        line = re.sub(r"<[^>]+>", "", line).strip()

        if not line:
            continue

        # 純小標題（例如 "Recommended Next Steps:"）不單獨當成一個 bullet。
        if line.endswith(":") and len(line) < 80:
            continue

        if line not in points:
            points.append(line)

        if len(points) >= max_points:
            break

    # 如果原文完全沒有適合的逐行內容，至少保留一段清理後文字。
    if not points:
        fallback = re.sub(r"\s+", " ", cleaned).strip()
        if fallback:
            points.append(fallback)

    return points



def render_print_button(markdown_text, button_label, document_title):
    """用瀏覽器原生列印視窗列印指定 Markdown，可另存為 PDF。"""
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
            'body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 0; color: #111827; max-width: 800px; margin: auto; }} ' +
            'h1 {{ color: #1e3a8a; text-align: center; font-size: 26px; margin-bottom: 24px; }} ' +
            'h2, h3 {{ color: #1e3a8a; margin-top: 24px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }} ' +
            'p {{ margin: 10px 0 18px; }} ' +
            'ul {{ padding-left: 24px; }} ' +
            'li {{ margin-bottom: 8px; }} ' +
            'table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }} ' +
            'th, td {{ border: 1px solid #111827; padding: 8px; text-align: left; vertical-align: top; }} ' +
            'th {{ background-color: #f8fafc; }} ' +
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


def transfer_conversation_to_ship(current_lang):
    """
    從本次完整 User 對話擷取 SHIP 原生五欄。
    找不到的資料保留空白，不從州別/城市猜 ZIP。
    """
    fields = extract_ship_fields(
        st.session_state.get("messages", []),
        target_lang=current_lang,
        existing_zip=st.session_state.get("user_zip", ""),
    )

    # 保留既有 reset key：ship_auto_notes 現在只是內部傳輸容器，
    # 不再顯示成 SHIP 頁面的第六格 AI Notes。
    st.session_state["ship_auto_notes"] = fields
    st.session_state["ship_auto_zip"] = fields.get("zip_code", "")
    st.session_state["ship_auto_state"] = find_latest_state_from_messages(
        st.session_state.get("messages", [])
    )

    return fields

def scroll_to_medicare_top():
    st.html(
        """
        <script>
        (() => {
            if ("scrollRestoration" in history) { history.scrollRestoration = "manual"; }
            function goTop() {
                const target = document.getElementById("medicare-top");
                if (target) {
                    target.scrollIntoView({ behavior: "auto", block: "start" });
                }
            }
            setTimeout(goTop, 400);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

def scroll_to_message(anchor_id):
    st.html(
        f"""
        <script>
        (() => {{
            const anchorId = "{anchor_id}";
            let lastHeight = -1;
            let stableFrames = 0;
            let attempts = 0;
            function waitUntilStable() {{
                const target = document.getElementById(anchorId);
                const currentHeight = document.documentElement.scrollHeight;
                if (currentHeight === lastHeight) {{
                    stableFrames++;
                }} else {{
                    stableFrames = 0;
                    lastHeight = currentHeight;
                }}
                attempts++;
                if (target && stableFrames >= 45) {{
                    if (document.activeElement) {{ document.activeElement.blur(); }}
                    const y = target.getBoundingClientRect().top + window.scrollY - 90;
                    window.scrollTo({{ top: Math.max(0, y), behavior: "auto" }});
                    return;
                }}
                if (attempts < 300) {{ requestAnimationFrame(waitUntilStable); }}
            }}
            if ("scrollRestoration" in history) {{ history.scrollRestoration = "manual"; }}
            requestAnimationFrame(waitUntilStable);
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )

def render(current_lang, uploaded_file):
    top_container = st.container()

    with top_container:

        # --- 歡迎卡片 (Welcome Banner) 開始 ---
        expander_title = "👋 Welcome / 歡迎 / Bienvenido / 환영합니다"
        
        # 根據側邊欄選定的語言讀取內容，若無則預設英文
        wd = welcome_guide_map.get(current_lang, welcome_guide_map["English"])
        
        with st.expander(expander_title, expanded=True):
            st.markdown(f"""
            <div class="welcome-banner-card">
                <h4>{wd['greeting']}</h4>
                <p><strong>{wd['step1']} → {wd['step2']} → {wd['step3']}</strong></p>
                <p style="margin-bottom: 0;"><em>{wd['hint']}</em></p>
            </div>
            """, unsafe_allow_html=True)
        # --- 歡迎卡片 (Welcome Banner) 結束 ---
     
        # Task 3.3: 3 步驟用戶旅程快捷按鈕 (多語言版)
        jb = journey_buttons_map.get(current_lang, journey_buttons_map["English"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(jb["btn1"], use_container_width=True):
                st.session_state.auto_submit = jb["prompt1"] # <--- 改成 auto_submit
                st.rerun()

        with col2:
            if st.button(jb["btn2"], use_container_width=True):
                st.session_state.auto_submit = jb["prompt2"] # <--- 改成 auto_submit
                st.rerun()

        with col3:
            if st.button(jb["btn3"], use_container_width=True):
                st.session_state.auto_submit = jb["prompt3"] # <--- 改成 auto_submit
                st.rerun()

        g_ui = guide_labels.get(current_lang, guide_labels["English"])
        with st.expander(g_ui["btn_text"], expanded=False):
            st.markdown(g_ui["guide_title"])
            col1, col2 = st.columns(2)
            with col1:
                st.info(g_ui["p_ab"])
                st.warning(g_ui["p_c"])
            with col2:
                st.success(g_ui["p_d"])
                st.error(g_ui["medigap"])
        st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # --- 新增這兩行來記憶地理資訊 ---
    if "user_state" not in st.session_state:
        st.session_state.user_state = ""
    if "user_zip" not in st.session_state:
        st.session_state.user_zip = ""
    if "conversation_finished" not in st.session_state:
        st.session_state.conversation_finished = False
    if "saved_user_input" not in st.session_state:
        st.session_state.saved_user_input = ""

    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div id="message-{i}" class="chat-anchor"></div>', unsafe_allow_html=True)
        with st.chat_message(message["role"]):
            if message["role"] in ["assistant", "model"]:
                st.markdown(clean_response(message["content"]))
            else:
                st.markdown(message["content"])

    if len(st.session_state.messages) == 0:
        st.caption(q_caption_map.get(current_lang, q_caption_map["English"]))

    # --------------------------------------------------
    # 對話輸入區
    # --------------------------------------------------
    prompt = None

    # --------------------------------------------------
    # Sidebar：重新提交上一筆已儲存輸入
    # --------------------------------------------------
    if (
        st.session_state.pop("resubmit_saved_input", False)
        and not st.session_state.conversation_finished
    ):
        prompt = st.session_state.saved_user_input


    # --------------------------------------------------
    # Quick Start 三個快捷按鈕
    # --------------------------------------------------
    elif (
        "auto_submit" in st.session_state
        and not st.session_state.conversation_finished
    ):
        raw_prompt = st.session_state.pop("auto_submit")

        role_prefix = (
            "[Applying for Myself] "
            if st.session_state.get("persona", "self") == "self"
            else "[Helping Someone Else] "
        )

        prompt = role_prefix + raw_prompt
        st.session_state.saved_user_input = prompt


    # 是否已經有聊天紀錄
    has_history = len(st.session_state.get("messages", [])) > 0

    # 是否已經至少有一次 AI 回答
    has_ai_reply = any(
        m.get("role") in ["assistant", "model"]
        for m in st.session_state.get("messages", [])
    )


    # 第一次顯示 Birth Month/Year & State
    # 之後顯示原本設定好的 Follow-up Question
    input_placeholder = (
        input_placeholder_followup_map.get(
            current_lang,
            input_placeholder_followup_map["English"]
        )
        if has_history
        else input_placeholder_first_map.get(
            current_lang,
            input_placeholder_first_map["English"]
        )
    )


    # --------------------------------------------------
    # 顯示已記錄的地理資訊
    # --------------------------------------------------
    current_loc = []

    if st.session_state.get("user_state"):
        current_loc.append(st.session_state.user_state)

    if st.session_state.get("user_zip"):
        current_loc.append(st.session_state.user_zip)

    if current_loc:
        loc_str = ", ".join(current_loc)

        loc_msg_template = location_tracker_map.get(
            current_lang,
            location_tracker_map["English"]
        )

        st.caption(
            loc_msg_template.format(location=loc_str)
        )


    # --------------------------------------------------
    # 對話尚未結束時才顯示輸入框
    # --------------------------------------------------
    input_prompt = None

    if not st.session_state.conversation_finished:

        # 放在 container 裡 → 不再固定黏在網頁最底部
        with st.container():
            input_prompt = st.chat_input(
                input_placeholder,
                key="main_chat_input"
            )

        if input_prompt:
            role_prefix = (
                "[Applying for Myself] "
                if st.session_state.get("persona", "self") == "self"
                else "[Helping Someone Else] "
            )

            prompt = role_prefix + input_prompt
            st.session_state.saved_user_input = prompt


        # 第一次 AI 回答之後，每一輪都顯示結束對話按鈕
        if has_ai_reply:

            end_btn_label = end_chat_btn_map.get(
                current_lang,
                end_chat_btn_map["English"]
            )

            if st.button(
                end_btn_label,
                type="primary",
                use_container_width=True,
                key="finish_conversation_btn"
            ):
                st.session_state.conversation_finished = True
                st.rerun()

    if not st.session_state.conversation_finished and (prompt or uploaded_file):
        user_text = prompt if prompt else default_upload_msg_map.get(current_lang, "Please review this uploaded document.")
        
        if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            user_message_index = len(st.session_state.messages) - 1
            st.session_state["_scroll_to_message"] = f"message-{user_message_index}"

        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant", avatar="👵"):
            sp_msg = spinner_msg_map.get(current_lang, "Analyzing...")
            with st.spinner(sp_msg):
                # 🚀 Task 4.3 實作：呼叫新的動態解析函數，取代原本單調的 Regex
                month, year = extract_birth_month_year(user_text)
                is_first_input = len(st.session_state.messages) <= 2

                # 只要有成功抓到 month 和 year 就觸發計算
                if month and year and is_first_input:
                    try:
                        turn_65_year = year + 65
                        start_m = month - 3 if month > 3 else month - 3 + 12
                        start_y = turn_65_year if month > 3 else turn_65_year - 1
                        end_m = month + 3 if month <= 9 else month + 3 - 12
                        end_y = turn_65_year if month <= 9 else turn_65_year + 1
                        
                        tmpl = timeline_template_map.get(current_lang, timeline_template_map["English"])
                        final_output = tmpl.format(
                            birth_m_name=calendar.month_name[month], turn_65_year=turn_65_year,
                            start_m_name=calendar.month_name[start_m], start_y=start_y,
                            end_m_name=calendar.month_name[end_m], end_y=end_y, end_day=calendar.monthrange(end_y, end_m)[1]
                        )
                    except Exception:
                        final_output = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                else:
                    # 如果不是問生日，就走原本呼叫 AI 聊天的邏輯
                    raw_response = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                    tip_suffix = tip_suffix_map.get(current_lang, tip_suffix_map["English"])
                    final_output = raw_response.strip() + tip_suffix

                st.markdown(final_output)
                st.session_state.messages.append({"role": "model", "content": final_output})
                st.rerun()

    # --------------------------------------------------
    # 對話還沒結束 → 不顯示 Summary / 官方連結 / 匯出功能
    # --------------------------------------------------
    if not st.session_state.conversation_finished:

        # 保留原本頁面自動定位功能
        anchor_id = st.session_state.pop("_scroll_to_message", None)

        if anchor_id:
            scroll_to_message(anchor_id)

        elif not st.session_state.get("_initial_top_done", False):
            scroll_to_medicare_top()
            st.session_state["_initial_top_done"] = True

        return


    # ==================================================
    # 使用者按下「結束對話」後才會執行下面內容
    # ==================================================

    st.markdown("---")


    # 官方申辦入口 / 免費中立輔導
    links_html = official_links_map.get(
        current_lang,
        official_links_map["English"]
    )

    st.markdown(
        links_html,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # Summary 標題與多語系 UI
    s_title = summary_title_map.get(
        current_lang,
        "📋 Your Medicare 1-Page Summary"
    )

    uib = ui_bottom_map.get(
        current_lang,
        ui_bottom_map["English"]
    )

    st.markdown(
        f'<h2 style="text-align: center; color: #1E3A8A;">{s_title}</h2>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------
    # 整理聊天內容
    # --------------------------------------------------
    ai_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") in ["assistant", "model"]
    ]

    # --------------------------------------------------
    # 1-Page Summary：從整段對話中抓已知資料
    # 不再假設生日一定出現在第一輪。
    # --------------------------------------------------
    birth_month, birth_year = find_latest_birth_from_messages(
        st.session_state.messages
    )

    timeline_data = None
    if birth_month and birth_year:
        try:
            timeline_data = calculate_summary_timeline(
                birth_month,
                birth_year
            )
        except Exception:
            timeline_data = None

    applicant_value = (
        uib["applicant_self"]
        if st.session_state.get("persona", "self") == "self"
        else uib["applicant_family"]
    )

    state_value = find_latest_state_from_messages(
        st.session_state.messages
    )

    # Badge / Key-Value 頂部資料
    badge_items = [
        (uib["applicant_label"], applicant_value)
    ]

    if timeline_data:
        badge_items.append(
            (uib["birth_label"], timeline_data["birth"])
        )

    if state_value:
        badge_items.append(
            (uib["state_label"], state_value)
        )

    badge_html = "<div class='summary-badges'>"
    for key, value in badge_items:
        badge_html += (
            "<div class='summary-badge'>"
            f"<span class='summary-badge-key'>{html.escape(str(key))}:</span>"
            f"<span class='summary-badge-value'>{html.escape(str(value))}</span>"
            "</div>"
        )
    badge_html += "</div>"

    # Key Decisions：取最後一則 AI 回覆，但只在顯示層整理成精簡 bullets。
    decision_points = (
        build_key_decision_points(ai_msgs[-1])
        if ai_msgs
        else []
    )

    # --------------------------------------------------
    # 建立 TXT / Print 共用的 Markdown Summary
    # 畫面與列印使用同一份資料，避免內容不同步。
    # --------------------------------------------------
    summary_lines = [
        f"# {s_title}",
        "",
        " | ".join(
            f"**{key}:** {value}"
            for key, value in badge_items
        ),
        ""
    ]

    if timeline_data:
        summary_lines.extend([
            f"## {uib['timeline_title']}",
            f"- **{uib['timeline_turn65']}:** {timeline_data['turn_65']}",
            f"- **{uib['timeline_iep_start']}:** {timeline_data['iep_start']}",
            f"- **{uib['timeline_iep_end']}:** {timeline_data['iep_end']}",
            ""
        ])

    if decision_points:
        summary_lines.append(
            f"## {uib['decisions_title']}"
        )
        summary_lines.extend(
            f"- {point}"
            for point in decision_points
        )
        summary_lines.append("")

    short_summary_text = "\n".join(summary_lines).strip() + "\n"

    # --------------------------------------------------
    # 完整對話：TXT 與 PDF 各自使用適合的格式
    # --------------------------------------------------
    full_log_text = f"【{uib['full_log_title']}】\n\n"
    full_log_markdown_lines = [
        f"# {uib['full_log_title']}",
        ""
    ]

    for message in st.session_state.messages:
        is_advisor = message.get("role") in ["assistant", "model"]
        role_title = (
            uib["advisor_role_label"]
            if is_advisor
            else uib["user_role_label"]
        )

        content = str(message.get("content", ""))
        printable_content = clean_response(content) if is_advisor else content

        full_log_text += (
            f"[{role_title}]:\n{printable_content}\n\n"
            + "-" * 40
            + "\n\n"
        )

        full_log_markdown_lines.extend([
            f"## {role_title}",
            "",
            printable_content,
            "",
            "---",
            ""
        ])

    full_log_markdown = "\n".join(full_log_markdown_lines).strip() + "\n"

    tab1, tab2 = st.tabs(
        [uib["tab1"], uib["tab2"]]
    )

    ship_map = ship_import_map.get(
        current_lang,
        ship_import_map["English"]
    )

    # ==================================================
    # Tab 1：1-Page Summary
    # ==================================================
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)

        # 用 Streamlit 原生 container 放 Summary，
        # Markdown 內容交給 st.markdown 正常解析，不再用 replace("\\n", "<br>")。
        with st.container(border=True):
            st.markdown(
                badge_html,
                unsafe_allow_html=True
            )

            if timeline_data:
                st.markdown(
                    f"#### {uib['timeline_title']}"
                )
                st.markdown(
                    "\n".join([
                        f"- **{uib['timeline_turn65']}:** {timeline_data['turn_65']}",
                        f"- **{uib['timeline_iep_start']}:** {timeline_data['iep_start']}",
                        f"- **{uib['timeline_iep_end']}:** {timeline_data['iep_end']}",
                    ])
                )

            if decision_points:
                st.markdown(
                    f"#### {uib['decisions_title']}"
                )
                st.markdown(
                    "\n".join(
                        f"- {point}"
                        for point in decision_points
                    )
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # 第一排：TXT 與 PDF 各佔一半
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                uib["dl_txt"],
                data=short_summary_text,
                file_name="medicare_summary.txt",
                use_container_width=True,
                key="summary_download_txt",
            )

        with col2:
            render_print_button(
                short_summary_text,
                uib.get("btn_pdf", "🖨️ Print / Save as PDF"),
                s_title,
            )

        # 第二排：SHIP 說明文字
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(ship_map["help"])

        # 第三排：SHIP 按鈕獨佔整行
        summary_ship_clicked = st.button(
            ship_map["btn"],
            type="primary",
            use_container_width=True,
            key="summary_ship_import",
        )

        if summary_ship_clicked:
            with st.spinner(ship_map["extracting"]):
                transfer_conversation_to_ship(current_lang)
            st.success(ship_map["success"])

    # ==================================================
    # Tab 2：Full Conversation Log
    # ==================================================
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)

        # 改用 Streamlit 原生聊天氣泡呈現，不再使用灰色 Text Area。
        for message in st.session_state.messages:
            role = message.get("role", "user")
            content = str(message.get("content", ""))

            if role in ["assistant", "model"]:
                with st.chat_message(
                    "assistant",
                    avatar="👵"
                ):
                    st.markdown(
                        clean_response(content)
                    )
            else:
                with st.chat_message("user"):
                    st.markdown(content)

        st.markdown("<br>", unsafe_allow_html=True)

        # 第一排：TXT 與 PDF 各佔一半
        log_col1, log_col2 = st.columns(2)

        with log_col1:
            st.download_button(
                uib["dl_log"],
                data=full_log_text,
                file_name="medicare_full_log.txt",
                use_container_width=True,
                key="full_log_download_txt",
            )

        with log_col2:
            render_print_button(
                full_log_markdown,
                uib.get("btn_pdf", "🖨️ Print / Save as PDF"),
                uib["full_log_title"],
            )

        # 第二排：SHIP 說明文字
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(ship_map["help"])

        # 第三排：SHIP 按鈕獨佔整行
        full_ship_clicked = st.button(
            ship_map["btn"],
            type="primary",
            use_container_width=True,
            key="full_log_ship_import",
        )

        if full_ship_clicked:
            with st.spinner(ship_map["extracting"]):
                transfer_conversation_to_ship(current_lang)
            st.success(ship_map["success"])

    # 頁面定位控制
    anchor_id = st.session_state.pop("_scroll_to_message", None)
    if anchor_id:
        scroll_to_message(anchor_id)
    elif not st.session_state.get("_initial_top_done", False):
        scroll_to_medicare_top()
        st.session_state["_initial_top_done"] = True