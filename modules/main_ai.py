import streamlit as st
import calendar
import datetime
import re
import json
import urllib.parse
from core.translations import (
    guide_labels, q_caption_map, btn1_map, btn2_map, welcome_guide_map,
    input_placeholder_first_map, input_placeholder_followup_map,
    default_upload_msg_map, spinner_msg_map, timeline_template_map,
    tip_suffix_map, summary_title_map, ui_bottom_map, official_links_map,
    location_tracker_map, journey_buttons_map, ship_import_map,
    end_chat_btn_map
)
from core.ai_engine import generate_clean_response
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
        st.markdown("""
            <div id="medicare-top" class="header-box">
                <span class="main-title">🧭 Medicare Compass</span>
                <div class="sub-title">Powered by CareCompass™</div>
            </div>
        """, unsafe_allow_html=True)
        st.divider()

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

    if "user_role_type" not in st.session_state:
        st.session_state.user_role_type = "self"
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
        col_start1, col_start2 = st.columns(2)
        with col_start1:
            btn1_label = btn1_map.get(current_lang, btn1_map["English"])
            btn_type1 = "primary" if st.session_state.user_role_type == "self" else "secondary"
            if st.button(btn1_label, use_container_width=True, type=btn_type1):
                st.session_state.user_role_type = "self"
                st.rerun()
        with col_start2:
            btn2_label = btn2_map.get(current_lang, btn2_map["English"])
            btn_type2 = "primary" if st.session_state.user_role_type == "family" else "secondary"
            if st.button(btn2_label, use_container_width=True, type=btn_type2):
                st.session_state.user_role_type = "family"
                st.rerun()

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
            if st.session_state.get("user_role_type") == "self"
            else "[Helping Family/Parents] "
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
                if st.session_state.get("user_role_type") == "self"
                else "[Helping Family/Parents] "
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


    # Summary 標題
    s_title = summary_title_map.get(
        current_lang,
        "📋 Your Medicare Quick Summary"
    )

    st.markdown(
        f'<h2 style="text-align: center; color: #1E3A8A;">{s_title}</h2>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)


    # 整理聊天內容
    user_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") == "user"
    ]

    ai_msgs = [
        m["content"]
        for m in st.session_state.messages
        if m.get("role") in ["assistant", "model"]
    ]


    uib = ui_bottom_map.get(
        current_lang,
        ui_bottom_map["English"]
    )
    pretty_summary_html = "<div class='summary-box' style='background-color: #F8FAFC; border: 1px solid #CBD5E1; padding: 25px; border-radius: 12px; font-size: 19px; line-height: 1.8;'>"

    if user_msgs:
        pretty_summary_html += f"<h4 style='color: #0F172A; margin-top:0; font-size: 20px;'>{uib['bg_title']}</h4><ul>"
        for u in user_msgs: pretty_summary_html += f"<li style='margin-bottom: 8px;'>{u}</li>"
        pretty_summary_html += "</ul><hr style='border: none; border-top: 1px solid #CBD5E1; margin: 20px 0;'>"

    if ai_msgs:
        pretty_summary_html += f"<h4 style='color: #0F172A; font-size: 20px;'>{uib['adv_title']}</h4>"
        formatted_last_ai = ai_msgs[-1].replace("\n", "<br>")
        pretty_summary_html += f"<div style='background-color: #FFFFFF; color: #111827 !important; padding: 20px; border-radius: 8px; border: 1px solid #E2E8F0;'>{formatted_last_ai}</div>"

    pretty_summary_html += "</div>"

    short_summary_text = "【Medicare Compass - Summary】\n\n"
    if user_msgs:
        short_summary_text += "📌 KEY USER INPUTS:\n"
        for u in user_msgs: short_summary_text += f"- {u}\n"
        short_summary_text += "\n"
    if ai_msgs:
        short_summary_text += f"💡 LATEST ADVICE:\n{ai_msgs[-1]}\n"

    full_log_text = "【Medicare Compass - Complete Consultation Log】\n\n"
    for m in st.session_state.messages:
        role_title = "Compass Advisor" if m["role"] in ["assistant", "model"] else "User"
        full_log_text += f"[{role_title}]:\n{m['content']}\n\n" + "-" * 40 + "\n\n"

    email_subject = urllib.parse.quote("My Medicare Compass Summary")
    email_body = urllib.parse.quote(short_summary_text)
    mailto_url = f"mailto:?subject={email_subject}&body={email_body}"

    tab1, tab2 = st.tabs([uib["tab1"], uib["tab2"]])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(pretty_summary_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        # Task 4.2: 將按鈕改為 3 欄，加入 Print/PDF 按鈕
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(uib["dl_txt"], data=short_summary_text, file_name="medicare_summary.txt", use_container_width=True)
        with col3:
            st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="width:100%; height:46px; border-radius:8px; background-color:#2563EB; color:white; border:none; cursor:pointer; font-size:17px; font-weight:bold;">{uib["email_btn"]}</button></a>', unsafe_allow_html=True)
        with col2:
            # 終極完美方案：直接拿 txt 的乾淨內容，轉成 Word 般的排版列印
            # 將 Python 裡的純文字總結安全地轉成 JavaScript 可以讀取的格式
            safe_md = json.dumps(short_summary_text)
            pdf_label = uib.get("btn_pdf", "🖨️ Print / Save PDF")
            
            # 注入帶有 markdown 解析器的安全區塊
            html_snippet = f"""
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <body style="margin: 0; padding: 0;">
                <button onclick="printClean()" style="width:100%; height:46px; border-radius:8px; background-color:#16A34A; color:white; border:none; cursor:pointer; font-size:17px; font-weight:bold; font-family: sans-serif;">
                    {pdf_label}
                </button>
            </body>
            <script>
            function printClean() {{
                // 1. 抓取最乾淨的純文字內容
                const markdownText = {safe_md};
                
                // 2. 轉換為標準 HTML
                const htmlContent = marked.parse(markdownText);
                
                // 3. 開啟一個全新的隱形乾淨視窗
                const printWindow = window.open('', '', 'width=800,height=600');
                
                // 4. 寫入類似 Word 的乾淨排版與表格樣式
                printWindow.document.write(
                    '<html><head><title>Medicare Summary</title>' +
                    '<style>' +
                    'body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 40px; color: black; max-width: 800px; margin: auto; }} ' +
                    'h1, h2, h3 {{ color: #1e3a8a; margin-top: 20px; }} ' +
                    'table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }} ' +
                    'th, td {{ border: 1px solid #000; padding: 10px; text-align: left; }} ' +
                    'th {{ background-color: #f0f7ff; font-weight: bold; }} ' +
                    'hr {{ border: 1px solid #1e3a8a; margin-bottom: 20px; }} ' +
                    'li {{ margin-bottom: 8px; }} ' +
                    '</style>' +
                    '</head><body>' +
                    '<h2 style="text-align:center;">🩺 Medicare Compass - Personal Summary</h2>' +
                    '<hr>' +
                    htmlContent +
                    '</body></html>'
                );
                printWindow.document.close();
                
                // 5. 等待瞬間排版完成後，直接呼叫列印
                setTimeout(function() {{
                    printWindow.focus();
                    printWindow.print();
                }}, 500);
            }}
            </script>
            """
            st.components.v1.html(html_snippet, height=55)
                    
        # Task 4.1: 一鍵匯入至 SHIP 準備單 
        st.markdown("<br>", unsafe_allow_html=True)
        ship_map = ship_import_map.get(current_lang, ship_import_map["English"])
        
        if st.button(ship_map["btn"], type="primary", use_container_width=True):
            # 1. 儲存地理資訊給模組 3
            st.session_state["ship_auto_zip"] = st.session_state.get("user_zip", "")
            st.session_state["ship_auto_state"] = st.session_state.get("user_state", "")
            
            # 2. 將使用者的對話與 AI 的精華總結，打包為備註傳給模組 3
            st.session_state["ship_auto_notes"] = short_summary_text
            
            # 3. 顯示成功訊息引導長輩
            st.success(ship_map["success"])

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.text_area(uib["log_label"], value=full_log_text, height=300, key="full_log_area")
        st.download_button(uib["dl_log"], data=full_log_text, file_name="medicare_full_log.txt", use_container_width=True)

    # 頁面定位控制
    anchor_id = st.session_state.pop("_scroll_to_message", None)
    if anchor_id:
        scroll_to_message(anchor_id)
    elif not st.session_state.get("_initial_top_done", False):
        scroll_to_medicare_top()
        st.session_state["_initial_top_done"] = True