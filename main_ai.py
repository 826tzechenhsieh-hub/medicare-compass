import streamlit as st
import calendar
import datetime
import re
import urllib.parse
from core.translations import (
    guide_labels, q_caption_map, btn1_map, btn2_map, quick_btn_map, welcome_guide_map,
    input_placeholder_first_map, input_placeholder_followup_map,
    default_upload_msg_map, spinner_msg_map, timeline_template_map,
    tip_suffix_map, summary_title_map, ui_bottom_map, official_links_map,
    location_tracker_map, journey_buttons_map
)
from core.ai_engine import generate_clean_response
from core.response_cleaner import clean_response

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

        # ✨✨✨ 請將「歡迎卡片」貼在這裡 ✨✨✨
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
        # ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

        # ✨✨✨ Task 3.3: 3 步驟用戶旅程快捷按鈕 (多語言版) ✨✨✨
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
        # ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

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
    if "show_summary" not in st.session_state:
        st.session_state.show_summary = False
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

    prompt = None

    # 🚀 1. 如果偵測到「自動送出」指令，直接打包發送，不顯示紅色按鈕
    if "auto_submit" in st.session_state:
        raw_prompt = st.session_state.pop("auto_submit") # 取出並立刻清除狀態
        # 幫按鈕的對話自動加上身分前綴，讓 AI 更精準
        role_prefix = "[Applying for Myself] " if st.session_state.get("user_role_type") == "self" else "[Helping Family/Parents] "
        prompt = role_prefix + raw_prompt
        st.session_state.saved_user_input = prompt # 同步存一份，以防切換標籤時遺失

    # 🛑 2. 如果不是自動送出，才去跑原本的紅色確認按鈕邏輯
    else:
        if st.session_state.get("saved_user_input"):
            st.markdown("<br>", unsafe_allow_html=True)
            q_btn = quick_btn_map.get(current_lang, quick_btn_map["English"])
            quick_btn_label = q_btn.format(input=st.session_state.saved_user_input)
            if st.button(quick_btn_label, type="primary", use_container_width=True):
                prompt = st.session_state.saved_user_input

    # ... 下面接著是你原本的 ha
    has_history = len(st.session_state.get("messages", [])) > 0
    input_placeholder = input_placeholder_followup_map.get(current_lang, input_placeholder_followup_map["English"]) if has_history else input_placeholder_first_map.get(current_lang, input_placeholder_first_map["English"])

    # ✨✨✨ 透明定位標籤 ✨✨✨
    current_loc = []
    if st.session_state.get("user_state"): current_loc.append(st.session_state.user_state)
    if st.session_state.get("user_zip"): current_loc.append(st.session_state.user_zip)

    if current_loc:
        loc_str = ", ".join(current_loc)
        # 根據側邊欄語言動態抓取提示文字
        loc_msg_template = location_tracker_map.get(current_lang, location_tracker_map["English"])
        st.caption(loc_msg_template.format(location=loc_str))
    # ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

    # 下面是你原本就有的聊天輸入框 👇
    input_prompt = st.chat_input(input_placeholder)

    if input_prompt:
        role_prefix = "[Applying for Myself] " if st.session_state.get("user_role_type") == "self" else "[Helping Family/Parents] "
        prompt = role_prefix + input_prompt
        st.session_state.saved_user_input = prompt

    if prompt or uploaded_file:
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
                date_match = re.search(r"(\d{1,2})/(?:(?:\d{1,2})/)?(\d{4})", user_text)
                is_first_input = len(st.session_state.messages) <= 2

                if date_match and is_first_input:
                    try:
                        month, year = int(date_match.group(1)), int(date_match.group(2))
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
                    raw_response = generate_clean_response(user_text, target_lang=current_lang, img_data=uploaded_file)
                    tip_suffix = tip_suffix_map.get(current_lang, tip_suffix_map["English"])
                    final_output = raw_response.strip() + tip_suffix

                st.markdown(final_output)
                st.session_state.messages.append({"role": "model", "content": final_output})
                st.rerun()

    if st.session_state.show_summary and len(st.session_state.messages) >= 2:
        st.markdown("---")
        s_title = summary_title_map.get(current_lang, "📋 Your Medicare Quick Summary")
        st.markdown(f'<h2 style="text-align: center; color: #1E3A8A;">{s_title}</h2>', unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)

    user_msgs = [m["content"] for m in st.session_state.messages if m.get("role") == "user"]
    ai_msgs = [m["content"] for m in st.session_state.messages if m.get("role") in ["assistant", "model"]]

    if len(ai_msgs) >= 2:
        links_html = official_links_map.get(current_lang, official_links_map["English"])
        st.markdown(links_html, unsafe_allow_html=True)

    uib = ui_bottom_map.get(current_lang, ui_bottom_map["English"])
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
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(uib["dl_txt"], data=short_summary_text, file_name="medicare_summary.txt", use_container_width=True)
        with col2:
            st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="width:100%; height:46px; border-radius:8px; background-color:#2563EB; color:white; border:none; cursor:pointer; font-size:17px; font-weight:bold;">{uib["email_btn"]}</button></a>', unsafe_allow_html=True)

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