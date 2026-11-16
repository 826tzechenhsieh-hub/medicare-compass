import streamlit as st
import re
from core.translations import m2_labels
from core.flow_translations import flow_labels, SWITCH_NEXT

PLAN_FINDER = "https://www.medicare.gov/plan-compare/"
CARE_COMPARE = "https://www.medicare.gov/care-compare/"
ENROLLMENT = "https://www.medicare.gov/basics/get-started-with-medicare/get-more-coverage/joining-a-plan"
SPECIAL_ENROLLMENT = f"{ENROLLMENT}/special-enrollment-periods"
MEDIGAP = "https://www.medicare.gov/health-drug-plans/medigap/ready-to-buy/when"
REASON_LINKS = ((), (PLAN_FINDER,), (PLAN_FINDER, CARE_COMPARE), (SPECIAL_ENROLLMENT,),
                (PLAN_FINDER,), (PLAN_FINDER,))
CHECKLIST_STEPS = ("formulary", "providers", "medigap", "enroll")


def plain_text(text):
    """Remove Markdown emphasis from option labels and exported guidance."""
    return re.sub(r"[*_`#]", "", str(text)).strip()


def checklist_text(text):
    # Keep official URLs visible in a plain-text download.
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", plain_text(text))


def render(current_lang):
    l2 = m2_labels.get(current_lang, m2_labels["English"])
    st.markdown(l2["title"])
    st.caption(l2["caption"])
    st.markdown("---")

    st.subheader(l2["step1_title"])
    # Store stable option codes so changing the UI language keeps the selection.
    reason_index = st.selectbox(
        l2["step1_label"], list(range(len(l2["reasons"]))),
        format_func=lambda index: l2["reasons"][index], key="switch_reason",
        persist_state="session",
    )
    if reason_index:
        reason = l2["reasons"][reason_index]
        reason_guidance = l2["guidance"][reason_index].format(*REASON_LINKS[reason_index])
        st.info(reason_guidance)
        st.write("---")
        st.subheader(l2["step2_title"])
        move_index = st.radio(
            l2["move_question"], list(range(len(l2["yes_no"]))),
            index=None, format_func=lambda index: l2["yes_no"][index], key="switch_move",
            persist_state="session",
        )
        timing_guidance = ""
        if move_index == 1:
            timing_guidance = l2["sep_alert"].format(SPECIAL_ENROLLMENT)
            st.warning(timing_guidance)
        elif move_index == 0:
            timing_guidance = l2["standard_windows"]
            st.info(timing_guidance)

        st.write("---")
        st.subheader(l2["step3_title"])
        export_lines = [l2["download_checklist"], "", plain_text(reason), checklist_text(reason_guidance)]
        if timing_guidance:
            export_lines.extend(("", l2["step2_title"], l2["move_question"],
                                 l2["yes_no"][move_index], checklist_text(timing_guidance)))
        export_lines.extend(("", l2["step3_title"]))
        for number, (step, (label, guidance), url) in enumerate(zip(
            CHECKLIST_STEPS, l2["checklist"], (PLAN_FINDER, CARE_COMPARE, MEDIGAP, ENROLLMENT),
        ), start=1):
            checked = st.checkbox(label, key=f"switch_check_{step}", persist_state="session")
            guidance = guidance.format(url)
            st.caption(guidance)
            mark = "x" if checked else " "
            export_lines.extend(("", f"{number}. [{mark}] {label}", checklist_text(guidance)))
        st.download_button(
            f"📄 {l2['download_checklist']} (TXT)",
            data="\n".join(export_lines) + "\n", file_name="medicare_plan_switching_checklist.txt",
            mime="text/plain; charset=utf-8", key="switch_download_checklist", on_click="ignore",
        )
        st.success(SWITCH_NEXT.get(current_lang, SWITCH_NEXT["English"]))

        flow = flow_labels(current_lang)
        if st.button(flow["ship"], key="switch_to_ship", type="primary", width="stretch"):
            concern = plain_text(reason)
            previous = st.session_state.get("ship_switch_concern_source", "")
            if (concern != previous
                    or move_index != st.session_state.get("ship_switch_move_answer")):
                st.session_state.pop("ship_prep_result", None)
                st.session_state.pop("ship_prep_bilingual_result", None)
            if concern != previous:
                draft = st.session_state.get("ship_draft_concern", "")
                st.session_state["ship_draft_concern"] = (
                    draft.replace(previous, concern, 1) if previous and previous in draft else concern
                )
            st.session_state["ship_switch_concern_source"] = concern
            st.session_state["ship_switch_move_answer"] = move_index
            st.session_state["ship_auto_notes"] = {
                "primary_concern": concern,
            }
            st.session_state["_pending_app_mode"] = "SHIP_PREP"
            st.rerun()
