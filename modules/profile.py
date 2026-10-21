import streamlit as st
import datetime

from core.flow_translations import flow_labels, UNSURE_LABELS

from core.translations import (
    profile_labels,
    profile_coverage_labels,
    profile_priority_labels,
)


# ==================================================
# 詢問單資料基本設定（內部仍沿用 profile 命名，避免破壞既有 state key）
# ==================================================

DEFAULT_PROFILE_DATA = {
    "birth_month": None,
    "birth_year": None,
    "coverage_code": "original_medicare",
    "monthly_premium": None,
    "priority_code": "lower_premium",
    "priority_other": "",
    "health_notes": "",
    "medications": "",
    "pharmacy": "",
    "zip_code": "",
    "has_part_ab": False,
    "has_commercial": False,
    "has_low_income": False,
}

# ==================================================
# Session State
# ==================================================

def init_profile_state():
    if "profile_data" not in st.session_state:
        st.session_state.profile_data = DEFAULT_PROFILE_DATA.copy()
        if st.session_state.get("entry_route") == "unsure":
            st.session_state.profile_data.update(
                coverage_code="unknown", priority_code="unknown", coverage_uncertain=True,
            )

    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 1

    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False


def get_language(current_lang):
    if current_lang in profile_labels:
        return current_lang

    return "English"


def profile_options(lang, category):
    options = dict((profile_coverage_labels if category == "coverage" else profile_priority_labels)[lang])
    options["unknown"] = UNSURE_LABELS[lang]["unknown"]
    return options


def update_coverage_uncertainty(changed):
    """A known checked situation and the group-level unknown cannot coexist."""
    data = st.session_state.profile_data
    if changed == "coverage_uncertain":
        data[changed] = st.session_state.profile_coverage_uncertain
        if data[changed]:
            for field in ("has_part_ab", "has_commercial", "has_low_income"):
                data[field] = False
                st.session_state[f"profile_{field}"] = False
    elif st.session_state[f"profile_{changed}"]:
        data["coverage_uncertain"] = False
        st.session_state.profile_coverage_uncertain = False


def build_initial_question(lang):
    """Send the confirmed answers as the first question, in the selected language."""
    data = st.session_state.profile_data
    ui = profile_labels[lang]
    flow = flow_labels(lang)
    priority = (data.get("priority_other") if data.get("priority_code") == "other"
                else profile_options(lang, "priority").get(data.get("priority_code"), "—"))
    additional = [ui[label] for key, label in (
        ("has_part_ab", "part_ab_yes"), ("has_commercial", "commercial_yes"),
        ("has_low_income", "low_income_yes"),
    ) if data.get(key)]
    if data.get("coverage_uncertain"):
        additional.append(UNSURE_LABELS[lang]["unknown"])
    premium = data.get("monthly_premium")
    items = [
        (ui["persona_label"], ui["persona_self"] if st.session_state.get("persona") == "self" else ui["persona_other"]),
        (ui["zip_summary"], data.get("zip_code") or "—"),
        (flow["birth"], f"{data['birth_month']:02d}/{data['birth_year']}"),
        (ui["coverage_summary"], profile_options(lang, "coverage").get(data.get("coverage_code"), "—")),
        (ui["premium_summary"], "—" if premium is None else f"${premium}"),
        (ui["additional_summary"], ", ".join(additional) or ui["none_selected"]),
        (ui["priority_summary"], priority or "—"),
        (ui["notes_summary"], data.get("health_notes") or "—"),
        (ui["meds_summary"], data.get("medications") or "—"),
        (ui["pharmacy_summary"], data.get("pharmacy") or "—"),
    ]
    return flow["start"] + "\n\n" + "\n".join(f"- {label}: {value}" for label, value in items)


# ==================================================
# Steps 1–2 — Basic information and coverage
# ==================================================

def render_step_1(lang, ui):
    data = st.session_state.profile_data
    st.markdown(ui["step1_title"])

    zip_code = st.text_input(
        ui["zip_label"],
        value=data.get("zip_code", ""),
        placeholder=ui["zip_placeholder"],
        max_chars=5,
        key="profile_zip",
    )

    data["zip_code"] = zip_code
    st.link_button(
        "Don't know your ZIP code? Look it up at USPS ↗",
        "https://tools.usps.com/zip-code-lookup.htm",
        key="profile_usps_lookup",
        type="tertiary",
    )

    flow = flow_labels(lang)
    data["birth_month"] = st.pills(
        flow["month"], list(range(1, 13)),
        default=data.get("birth_month"),
        selection_mode="single",
        key="profile_birth_month",
        wrap=True,
        width="stretch",
    )
    data["birth_year"] = st.number_input(
        flow["year"], min_value=1900, max_value=datetime.date.today().year,
        value=data.get("birth_year"), step=1, key="profile_birth_year",
    )

    if st.button(ui["next"], type="primary", width="stretch", key="profile_step1_next"):
        if not data.get("birth_month") or not data.get("birth_year"):
            st.warning(flow["birth_required"])
            return
        st.session_state.profile_step = 2
        st.rerun()


def render_step_2(lang, ui):
    data = st.session_state.profile_data
    st.markdown(ui["step2_title"])

    coverage_labels = profile_options(lang, "coverage")
    coverage_codes = list(coverage_labels)

    current_coverage = data.get("coverage_code", "original_medicare")

    if current_coverage not in coverage_codes:
        current_coverage = coverage_codes[0]

    selected_coverage = st.selectbox(
        ui["coverage_label"],
        coverage_codes,
        index=coverage_codes.index(current_coverage),
        format_func=lambda code: coverage_labels[code],
        key="profile_coverage_select",
    )

    data["coverage_code"] = selected_coverage

    premium = st.number_input(
        ui["premium_label"],
        min_value=0,
        max_value=5000,
        value=data.get("monthly_premium"),
        step=10,
        key="profile_monthly_premium",
    )

    data["monthly_premium"] = premium

    st.markdown(f"**{ui['coverage_check_title']}**")

    data["has_part_ab"] = st.checkbox(
        ui["has_part_ab"],
        value=data.get("has_part_ab", False),
        key="profile_has_part_ab",
        on_change=update_coverage_uncertainty,
        args=("has_part_ab",),
    )

    data["has_commercial"] = st.checkbox(
        ui["has_commercial"],
        value=data.get("has_commercial", False),
        key="profile_has_commercial",
        on_change=update_coverage_uncertainty,
        args=("has_commercial",),
    )

    data["has_low_income"] = st.checkbox(
        ui["has_low_income"],
        value=data.get("has_low_income", False),
        key="profile_has_low_income",
        on_change=update_coverage_uncertainty,
        args=("has_low_income",),
    )

    data["coverage_uncertain"] = st.checkbox(
        UNSURE_LABELS[lang]["unknown"],
        value=data.get("coverage_uncertain", False),
        key="profile_coverage_uncertain",
        on_change=update_coverage_uncertainty,
        args=("coverage_uncertain",),
    )

    st.write("")

    back, next_page = st.columns(2)
    with back:
        if st.button(ui["back"], width="stretch", key="profile_step2_back"):
            st.session_state.profile_step = 1
            st.rerun()
    with next_page:
        if st.button(ui["next"], type="primary", width="stretch", key="profile_step2_next"):
            st.session_state.profile_step = 3
            st.rerun()



# ==================================================
# Step 3 — Goals and health notes
# ==================================================

def render_step_3(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step3_title"])

    priority_labels = profile_options(lang, "priority")
    priority_codes = list(priority_labels)

    current_priority = data.get("priority_code", "lower_premium")

    if current_priority not in priority_codes:
        current_priority = priority_codes[0]

    selected_priority = st.selectbox(
        ui["priority_label"],
        priority_codes,
        index=priority_codes.index(current_priority),
        format_func=lambda code: priority_labels[code],
        key="profile_priority_select",
    )

    data["priority_code"] = selected_priority

    if selected_priority == "other":
        priority_other = st.text_area(
            ui["priority_other_label"],
            value=data.get("priority_other", ""),
            placeholder=ui["priority_other_placeholder"],
            height=120,
            key="profile_priority_other",
        )

        data["priority_other"] = priority_other
    else:
        data["priority_other"] = ""

    notes = st.text_area(
        ui["notes_label"],
        value=data.get("health_notes", ""),
        placeholder=ui["notes_placeholder"],
        height=160,
        key="profile_health_notes",
    )

    data["health_notes"] = notes

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            ui["back"],
            width="stretch",
            key="profile_step3_back",
        ):
            st.session_state.profile_step = 2
            st.rerun()

    with col2:
        if st.button(
            ui["next"],
            type="primary",
            width="stretch",
            key="profile_step3_next",
        ):
            st.session_state.profile_step = 4
            st.rerun()


# ==================================================
# Step 4 — Prescriptions
# ==================================================

def render_step_4(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step4_title"])

    meds = st.text_area(
        ui["meds_label"],
        value=data.get("medications", ""),
        placeholder=ui["meds_placeholder"],
        height=170,
        key="profile_medications",
    )

    data["medications"] = meds

    pharmacy = st.text_input(
        ui["pharmacy_label"],
        value=data.get("pharmacy", ""),
        placeholder=ui["pharmacy_placeholder"],
        key="profile_pharmacy",
    )

    data["pharmacy"] = pharmacy

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            ui["back"],
            width="stretch",
            key="profile_step4_back",
        ):
            st.session_state.profile_step = 3
            st.rerun()

    with col2:
        if st.button(
            ui["next"],
            type="primary",
            width="stretch",
            key="profile_step4_next",
        ):
            st.session_state.profile_step = 5
            st.rerun()


# ==================================================
# Step 5 — Review
# ==================================================

def render_step_5(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step5_title"])

    persona = st.session_state.get("persona", "self")

    persona_display = (
        ui["persona_other"]
        if persona == "helping_others"
        else ui["persona_self"]
    )

    coverage_display = profile_options(lang, "coverage").get(
        data.get("coverage_code"),
        "—",
    )

    if data.get("priority_code") == "other":
        priority_display = data.get("priority_other") or "—"
    else:
        priority_display = profile_options(lang, "priority").get(
            data.get("priority_code"),
            "—",
        )

    additional_items = []

    if data.get("has_part_ab"):
        additional_items.append(ui["part_ab_yes"])

    if data.get("has_commercial"):
        additional_items.append(ui["commercial_yes"])

    if data.get("has_low_income"):
        additional_items.append(ui["low_income_yes"])

    if data.get("coverage_uncertain"):
        additional_items.append(UNSURE_LABELS[lang]["unknown"])

    additional_display = (
        "、".join(additional_items)
        if lang == "繁體中文" and additional_items
        else ", ".join(additional_items)
    )

    if not additional_display:
        additional_display = ui["none_selected"]

    premium_value = data.get("monthly_premium")

    premium_display = (
        "—"
        if premium_value is None
        else f"${premium_value}"
    )

    with st.container(border=True):
        st.markdown(
            f"**{ui['persona_label']}：** {persona_display}"
        )
        st.markdown(
            f"**{ui['zip_summary']}：** "
            f"{data.get('zip_code') or '—'}"
        )
        st.markdown(
            f"**{flow_labels(lang)['birth']}：** "
            f"{data.get('birth_month', '—')}/{data.get('birth_year', '—')}"
        )
        st.markdown(
            f"**{ui['coverage_summary']}：** {coverage_display}"
        )
        st.markdown(
            f"**{ui['premium_summary']}：** {premium_display}"
        )
        st.markdown(
            f"**{ui['additional_summary']}：** {additional_display}"
        )
        st.markdown(
            f"**{ui['priority_summary']}：** {priority_display}"
        )
        st.markdown(
            f"**{ui['notes_summary']}：** "
            f"{data.get('health_notes') or '—'}"
        )
        st.markdown(
            f"**{ui['meds_summary']}：** "
            f"{data.get('medications') or '—'}"
        )
        st.markdown(
            f"**{ui['pharmacy_summary']}：** "
            f"{data.get('pharmacy') or '—'}"
        )

    st.write("")

    if st.session_state.profile_completed:
        st.success(ui["saved"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            ui["edit_btn"],
            width="stretch",
            key="profile_review_back",
        ):
            st.session_state.profile_completed = False
            st.session_state.profile_step = 4
            st.rerun()

    with col2:
        if st.button(
            ui["save_btn"],
            type="primary",
            width="stretch",
            key="profile_save",
        ):
            # 標記 Questionnaire 已完成
            st.session_state.profile_completed = True

            # Start once, after explicit review, using the existing AI instructions.
            st.session_state["auto_submit"] = build_initial_question(lang)
            st.session_state["user_zip"] = data.get("zip_code", "")

            # 下一次 rerun 後直接進入 Main AI
            st.session_state["_pending_app_mode"] = "MAIN_AI"

            st.rerun()


# ==================================================
# Questionnaire Module Entry
# ==================================================

def render(current_lang):
    init_profile_state()

    lang = get_language(current_lang)
    ui = profile_labels[lang]

    if st.session_state.get("entry_route") == "unsure" and not st.session_state.get("profile_intro_seen"):
        intro = UNSURE_LABELS[lang]
        st.subheader(intro["title"])
        st.markdown(intro["body"])
        if st.button(intro["continue"], type="primary", width="stretch", key="profile_intro_continue"):
            st.session_state.profile_intro_seen = True
            st.session_state["_scroll_to_top"] = True
            st.rerun()
        return

    st.markdown(ui["title"])
    st.caption(flow_labels(lang)["questionnaire"])
    st.markdown("---")

    total_steps = 5
    current_step = st.session_state.profile_step

    step_name = ui["step_names"][current_step - 1]

    st.progress(
        current_step / total_steps,
        text=ui["progress"].format(
            current=current_step,
            total=total_steps,
            name=step_name,
        ),
    )

    st.caption(ui["autosave"])
    st.write("")

    renderers = (render_step_1, render_step_2, render_step_3, render_step_4, render_step_5)
    renderers[current_step - 1](lang, ui)
