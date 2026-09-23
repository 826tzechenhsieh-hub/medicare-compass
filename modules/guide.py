"""Public V1.5 journey; reuses profile state, response engine and export/feedback tools."""

import html
import json
import hashlib
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError

from core.ai_engine import generate_clean_response
from core.config import SHIP_URL
from core.guide_state import clear_person, clear_result, parse_guidance, valid_zip
from core.guide_text import text
from core.feedback_translations import get_feedback_ui
from core.feedback_ui import draft, field, submit
from modules import profile


def go(route):
    st.session_state["selected_app_mode"] = route
    st.session_state["_scroll_to_top"] = True
    st.rerun()


def choose_person(persona):
    if st.session_state.get("persona") != persona:
        clear_person(st.session_state)
    st.session_state["persona"] = persona
    st.session_state["persona_selector"] = persona
    st.session_state["guide_home_step"] = "intent"
    go(None)


def home(language):
    ui = text(language)
    stage = st.session_state.get("guide_home_step", "who")
    if stage == "who":
        st.subheader(ui["who"])
        for code, label in (("self", "self"), ("helping_others", "family")):
            if st.button(ui[label], key=f"person_{code}", use_container_width=True):
                choose_person(code)
        return
    st.caption(ui["self"] if st.session_state.get("persona") == "self" else ui["family"])
    st.subheader(ui["intent"] if stage == "intent" else ui["journey"])
    if stage == "intent":
        for code in ("explore", "question", "start_unsure"):
            if st.button(ui[code], key=f"intent_{code}", use_container_width=True):
                st.session_state["guide_intent"] = code
                if code == "question":
                    st.session_state["main_presentation"] = "question"
                    st.session_state["_question_start_index"] = len(st.session_state.get("messages", []))
                    st.session_state["conversation_finished"] = False
                    go("MAIN_AI")
                st.session_state["guide_home_step"] = "journey"
                st.rerun()
    else:
        for code in ("first", "review", "unknown"):
            if st.button(ui[code], key=f"journey_{code}", use_container_width=True):
                if st.session_state.get("guide_journey") != code:
                    clear_result(st.session_state)
                st.session_state["guide_journey"] = code
                st.session_state["profile_step"] = 1
                go("PROFILE")
    if st.button(ui["back"], key="home_back"):
        st.session_state["guide_home_step"] = "who" if stage == "intent" else "intent"
        st.rerun()


def profile_field(name, widget, label, **kwargs):
    """Restore durable values before widgets are recreated by navigation/language."""
    data = st.session_state.profile_data
    key = f"_guide_profile_{name}"
    st.session_state[key] = data.get(name, "")

    def remember():
        value = st.session_state[key]
        if data.get(name) != value:
            clear_result(st.session_state)
            st.session_state["profile_completed"] = False
        data[name] = value

    return widget(label, key=key, on_change=remember, **kwargs)


def guided(language):
    ui = text(language)
    new_profile = "profile_data" not in st.session_state
    profile.init_profile_state()
    data = st.session_state.profile_data
    # Retire the temporary state selector without carrying its old answer forward.
    if "state_code" in data:
        data.pop("state_code")
        clear_result(st.session_state)
    st.session_state.pop("_guide_profile_state_code", None)
    if new_profile:
        data.update(coverage_code="unknown", priority_code="unknown",
                    has_part_ab=None, has_commercial=None, has_low_income=None)
    step = st.session_state.profile_step
    st.caption(ui["self"] if st.session_state.get("persona") == "self" else ui["family"])
    st.progress(step / 5, text=ui["progress"].format(step=step, total=5))
    if step == 1:
        st.caption(ui["intro"])
        profile_field("coverage_code", st.radio, ui["coverage"],
                      options=["unknown", "not_enrolled", "original_medicare", "medicare_advantage", "employer_coverage"],
                      format_func=lambda code: ui.get(code, ui["unknown"]))
    elif step == 2:
        options = ["timing", "lower_premium", "broad_network", "drug_cost", "lower_risk", "unknown"]
        if st.session_state.get("guide_journey") == "review":
            options = ["lower_premium", "broad_network", "drug_cost", "lower_risk", "timing", "unknown"]
        profile_field("priority_code", st.radio, ui["priority"], options=options,
                      format_func=lambda code: ui.get(code, ui["unknown"]))
    elif step == 3:
        st.subheader(ui["details"])
        profile_field("health_notes", st.text_area, ui["notes"], height=140, max_chars=2000)
    elif step == 4:
        st.subheader(ui["location"])
        profile_field("zip_code", st.text_input, ui["zip"], max_chars=5)
        st.markdown(
            '<a href="https://tools.usps.com/zip-code-lookup.htm" '
            'target="_blank" rel="noopener noreferrer">'
            f'{html.escape(ui["zip_lookup"])}</a>', unsafe_allow_html=True,
        )
        st.caption(ui["new_tab"])
    else:
        st.subheader(ui["check"])
        with st.container(border=True):
            st.write(f"**{ui['coverage']}**  \n{ui.get(data['coverage_code'], ui['unknown'])}")
            st.write(f"**{ui['priority']}**  \n{ui.get(data['priority_code'], ui['unknown'])}")
            st.write(f"**{ui['details']}**")
            st.write(data.get("health_notes") or ui["unknown"])
            st.write(f"**{ui['zip']}**  \n{data.get('zip_code') or ui['unknown']}")
    back, forward = st.columns(2)
    with back:
        if st.button(ui["back"], key="guide_back", use_container_width=True):
            if step == 1:
                st.session_state["guide_home_step"] = "journey"
                go(None)
            st.session_state.profile_step -= 1
            st.rerun()
    with forward:
        if st.button(ui["next"] if step < 5 else ui["generate"], key="guide_next",
                     type="primary", use_container_width=True):
            if step == 4 and not valid_zip(data.get("zip_code", "")):
                st.warning(ui["zip_error"])
            elif step < 5:
                st.session_state.profile_step += 1
                st.rerun()
            else:
                st.session_state.profile_completed = True
                st.session_state["main_presentation"] = "full"
                # Feed the established conversation renderer instead of replacing it.
                snapshot = {"profile": dict(data), "journey": st.session_state.get("guide_journey"),
                            "persona": st.session_state.get("persona")}
                if (st.session_state.get("_main_guided_input") != snapshot
                        or not st.session_state.get("messages")):
                    clear_result(st.session_state)
                    st.session_state["_main_guided_input"] = snapshot
                    st.session_state["auto_submit"] = ui["guided_prompt"]
                go("MAIN_AI")
    if st.session_state.get("guide_error"):
        st.warning(ui["failure"])
        ship(language)


def prepare(language, origin, question="", attachment=None):
    """One existing generation operation. Rerenders and language changes never call AI."""
    ui = text(language)
    from modules.main_ai import build_questionnaire_context
    payload = {
        "language": language, "origin": origin, "question": question,
        "persona": st.session_state.get("persona"),
        "journey": st.session_state.get("guide_journey", "unknown") if origin == "guided" else None,
        "profile": dict(st.session_state.get("profile_data", {})) if origin == "guided" else None,
        "attachment": hashlib.sha256(attachment["data"]).hexdigest() if attachment is not None else None,
    }
    if st.session_state.get("guide_result_input") == payload:
        return True
    clear_result(st.session_state)
    role = "[Helping Someone Else]" if payload["persona"] == "helping_others" else "[Applying for Myself]"
    request = question or "Please explain directions to explore based on the provided facts."
    if origin == "guided":
        request += f"\nJourney: {payload['journey']}. Priority: {payload['profile'].get('priority_code', 'unknown')}."
    context = build_questionnaire_context() if origin == "guided" else ""
    try:
        with st.spinner(ui["waiting"]):
            response = generate_clean_response(f"{role} {request}", target_lang=language,
                                              img_data=attachment, questionnaire_context=context,
                                              guidance_mode=True)
            sections = parse_guidance(response)
    except Exception:
        st.session_state["guide_error"] = True
        return False
    st.session_state.pop("guide_error", None)
    st.session_state["guide_result"] = sections
    st.session_state["guide_result_language"] = language
    st.session_state["guide_result_origin"] = origin
    st.session_state["guide_result_input"] = payload
    return True


def question(language):
    ui = text(language)
    st.subheader(ui["ask"])
    st.caption(ui["ask_hint"])
    st.session_state["_guide_question"] = st.session_state.get("saved_user_input", "")

    def save_question():
        st.session_state["saved_user_input"] = st.session_state["_guide_question"]

    value = st.text_area(ui["question"], key="_guide_question", height=120,
                         on_change=save_question, max_chars=2000)
    attachment = st.session_state.get("guide_attachment")
    with st.expander(ui["upload"]):
        upload = st.file_uploader(ui["upload"], type=["png", "jpg", "jpeg", "pdf"], key="guide_upload")
        if upload is not None:
            try:
                raw = upload.getvalue()
                if upload.type == "application/pdf":
                    if not raw.startswith(b"%PDF-"):
                        raise OSError("Invalid PDF")
                    attachment = {"mime_type": "application/pdf", "data": raw}
                else:
                    picture = Image.open(BytesIO(raw)).convert("RGB")
                    output = BytesIO()
                    picture.save(output, format="PNG")
                    attachment = {"mime_type": "image/png", "data": output.getvalue()}
                st.session_state["guide_attachment"] = attachment
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                st.warning(ui["failure"])
                attachment = None
                st.session_state.pop("guide_attachment", None)
        if attachment is not None:
            if attachment["mime_type"] == "image/png":
                st.image(attachment["data"], width=180)
            else:
                st.caption("PDF ✓")
            if st.button("×", key="remove_attachment", help=ui["upload"]):
                st.session_state.pop("guide_attachment", None)
                st.session_state.pop("guide_upload", None)
                st.rerun()
    back, forward = st.columns(2)
    with back:
        if st.button(ui["back"], key="question_back", use_container_width=True):
            st.session_state["guide_home_step"] = "intent"
            go(None)
    with forward:
        if st.button(ui["send"], type="primary", key="question_send", use_container_width=True):
            if not value.strip() and attachment is None:
                st.warning(ui["empty"])
            elif prepare(language, "question", value.strip(), attachment):
                go("GUIDE_RESULT")
    if st.session_state.get("guide_error"):
        st.warning(ui["failure"])
        ship(language)


def main_attachment(language):
    """Keep uploads secondary and submit only after an explicit user action."""
    ui = text(language)
    with st.expander(ui["upload"]):
        upload = st.file_uploader(ui["upload"], type=["png", "jpg", "jpeg", "pdf"], key="main_upload")
        if upload is not None:
            raw = upload.getvalue()
            if st.button(ui["send"], key="main_attachment_send"):
                st.session_state["_main_attachment_submit"] = True
                st.session_state["conversation_finished"] = False
            return {"mime_type": upload.type, "data": raw}
    return None


def copy_summary(value, ui):
    """Copy only on an explicit click; keep a visible select-text fallback."""
    safe = json.dumps(value, ensure_ascii=True).replace("<", "\\u003c")
    copied = json.dumps(ui["copied"], ensure_ascii=True)
    fallback = json.dumps(ui["copy_fallback"], ensure_ascii=True)
    size = int(st.session_state.get("font_size", 20))
    components.html(f'''<!doctype html><html><head><style>
    #status:not(:empty) {{ background:#f8fafc; padding:8px; border-radius:8px; }}
    </style></head><body style="margin:0;font: {size}px sans-serif">
    <button id="copy" style="width:100%;min-height:52px;padding:12px;background:#164a76;color:white;border:0;border-radius:8px;font:inherit;cursor:pointer">{html.escape(ui['copy'])}</button>
    <div id="status" role="status" aria-live="polite" style="margin-top:8px;color:#18334a"></div>
    <script>
    document.getElementById('copy').onclick = async () => {{
      const value = {safe}; let ok = false;
      try {{ await navigator.clipboard.writeText(value); ok = true; }} catch(e) {{
        const area = document.createElement('textarea'); area.value = value;
        document.body.appendChild(area); area.select();
        try {{ ok = document.execCommand('copy'); }} catch(e) {{}} area.remove();
      }}
      document.getElementById('status').textContent = ok ? {copied} : {fallback};
    }};
    </script></body></html>''', height=145 if size == 24 else 125)


def feedback(language):
    ui = text(language)
    shared = get_feedback_ui(language)
    state = "product_feedback_state"
    with st.container(border=True):
        if draft(state).get("saved"):
            st.success(shared["saved"])
            return
        rating_labels = {"Very clear": ui["clear"], "Mostly clear": ui["mostly"], "Still confusing": ui["confused"]}
        rating = field(state, "helpfulness", st.radio, ui["feedback"],
                       options=list(rating_labels), initial=None, index=None,
                       format_func=rating_labels.get)
        choices = {"Starting": ui["starting"], "Terms": ui["terms"], "Summary": ui["results"]}
        difficulty = field(state, "confusion", st.radio, ui["difficulty"],
                           options=list(choices), initial=None, index=None, format_func=choices.get)
        st.caption(shared["privacy"])
        if st.button(shared["submit"], key="guide_feedback_submit"):
            if rating is None:
                st.warning(shared["choose_rating"])
            elif submit(state, "Product Feedback", {"helpfulness": rating, "confusion": difficulty or "",
                        "future_request": "", "language": language}, shared):
                st.rerun()


def ship(language):
    ui = text(language)
    st.subheader(ui["ship_title"])
    st.write(ui["ship_note"])
    st.link_button(ui["ship_link"], SHIP_URL, use_container_width=True)


def result(language):
    if "guide_result" not in st.session_state:
        go(None)
    ui = text(language)
    saved_language = st.session_state["guide_result_language"]
    content_ui = text(saved_language)
    sections = st.session_state["guide_result"]
    if saved_language != language:
        st.caption(ui["saved_language"])
    headings = {"WHAT": content_ui["summary"], "WHY": content_ui["why"],
                "WATCH": content_ui["watch"], "NEXT": content_ui["next_steps"]}
    with st.container(border=True):
        st.markdown(sections["SUMMARY"])
        for key, label in headings.items():
            st.subheader(label)
            st.markdown(sections[key])
        st.caption(content_ui["advice"])
    share_text = "Medicare Compass\n\n" + sections["SUMMARY"] + "\n\n"
    share_text += "\n\n".join(f"{label}\n{sections[key]}" for key, label in headings.items())
    share_text += f"\n\n{content_ui['advice']}\n\nSHIP: {SHIP_URL}"
    copy_summary(share_text, ui)
    with st.expander(ui["share"]):
        st.caption(ui["copy_fallback"])
        st.text_area(ui["copy"], value=share_text, height=300, key="guide_copy_text")
        from modules.main_ai import render_print_button
        render_print_button(share_text, ui["print"], "Medicare Compass")
    feedback(language)
    ship(language)
    if st.button(ui["back"], key="result_back"):
        go("PROFILE" if st.session_state["guide_result_origin"] == "guided" else "MAIN_AI")
    with st.expander(ui["more"]):
        if st.button(ui["prep"], key="guide_ship_prep"):
            go("SHIP_PREP")
        if st.button(ui["restart"], key="guide_restart"):
            st.session_state["guide_reset_confirm"] = True
        if st.session_state.get("guide_reset_confirm"):
            st.write(ui["reset_note"])
            if st.button(ui["confirm"], key="guide_confirm_restart"):
                st.session_state["_do_full_reset"] = {
                    "language": st.session_state.get("selected_language", "English"),
                    "font_size": st.session_state.get("font_size", 20),
                }
                st.rerun()
