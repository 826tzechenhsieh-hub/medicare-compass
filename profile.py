import streamlit as st

from core.translations import (
    profile_labels,
    profile_coverage_labels,
    profile_priority_labels,
)


# ==================================================
# 詢問單資料基本設定（內部仍沿用 profile 命名，避免破壞既有 state key）
# ==================================================

DEFAULT_PROFILE_DATA = {
    "coverage_code": "original_medicare",
    "monthly_premium": 0,
    "priority_code": "lower_premium",
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

    if "profile_step" not in st.session_state:
        st.session_state.profile_step = 1

    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False


def get_language(current_lang):
    if current_lang in profile_labels:
        return current_lang

    return "English"


def get_target_noun(ui):
    persona = st.session_state.get("persona", "self")

    if persona == "helping_others":
        return ui["target_other"]

    return ui["target_self"]


# ==================================================
# Step 1
# ==================================================

def render_step_1(lang, ui):
    data = st.session_state.profile_data
    target = get_target_noun(ui)

    st.markdown(ui["step1_title"])
    st.caption(
        ui["step1_caption"].format(target=target)
    )

    coverage_codes = list(profile_coverage_labels[lang].keys())

    current_coverage = data.get("coverage_code", "original_medicare")

    if current_coverage not in coverage_codes:
        current_coverage = coverage_codes[0]

    selected_coverage = st.selectbox(
        ui["coverage_label"],
        coverage_codes,
        index=coverage_codes.index(current_coverage),
        format_func=lambda code: profile_coverage_labels[lang][code],
        key="profile_coverage_select",
    )

    data["coverage_code"] = selected_coverage

    premium = st.number_input(
        ui["premium_label"],
        min_value=0,
        max_value=5000,
        value=int(data.get("monthly_premium", 0)),
        step=10,
        key="profile_monthly_premium",
    )

    data["monthly_premium"] = premium

    st.markdown(f"**{ui['coverage_check_title']}**")

    data["has_part_ab"] = st.checkbox(
        ui["has_part_ab"],
        value=data.get("has_part_ab", False),
        key="profile_has_part_ab",
    )

    data["has_commercial"] = st.checkbox(
        ui["has_commercial"],
        value=data.get("has_commercial", False),
        key="profile_has_commercial",
    )

    data["has_low_income"] = st.checkbox(
        ui["has_low_income"],
        value=data.get("has_low_income", False),
        key="profile_has_low_income",
    )

    st.write("")

    if st.button(
        ui["next"],
        type="primary",
        use_container_width=True,
        key="profile_step1_next",
    ):
        st.session_state.profile_step = 2
        st.rerun()


# ==================================================
# Step 2
# ==================================================

def render_step_2(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step2_title"])

    priority_codes = list(profile_priority_labels[lang].keys())

    current_priority = data.get("priority_code", "lower_premium")

    if current_priority not in priority_codes:
        current_priority = priority_codes[0]

    selected_priority = st.selectbox(
        ui["priority_label"],
        priority_codes,
        index=priority_codes.index(current_priority),
        format_func=lambda code: profile_priority_labels[lang][code],
        key="profile_priority_select",
    )

    data["priority_code"] = selected_priority

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
            use_container_width=True,
            key="profile_step2_back",
        ):
            st.session_state.profile_step = 1
            st.rerun()

    with col2:
        if st.button(
            ui["next"],
            type="primary",
            use_container_width=True,
            key="profile_step2_next",
        ):
            st.session_state.profile_step = 3
            st.rerun()


# ==================================================
# Step 3
# ==================================================

def render_step_3(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step3_title"])

    zip_code = st.text_input(
        ui["zip_label"],
        value=data.get("zip_code", ""),
        placeholder=ui["zip_placeholder"],
        max_chars=5,
        key="profile_zip",
    )

    data["zip_code"] = zip_code

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
            use_container_width=True,
            key="profile_step3_back",
        ):
            st.session_state.profile_step = 2
            st.rerun()

    with col2:
        if st.button(
            ui["next"],
            type="primary",
            use_container_width=True,
            key="profile_step3_next",
        ):
            st.session_state.profile_step = 4
            st.rerun()


# ==================================================
# Step 4 — Review
# ==================================================

def render_step_4(lang, ui):
    data = st.session_state.profile_data

    st.markdown(ui["step4_title"])

    persona = st.session_state.get("persona", "self")

    persona_display = (
        ui["persona_other"]
        if persona == "helping_others"
        else ui["persona_self"]
    )

    coverage_display = profile_coverage_labels[lang].get(
        data.get("coverage_code"),
        "—",
    )

    priority_display = profile_priority_labels[lang].get(
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

    additional_display = (
        "、".join(additional_items)
        if lang == "繁體中文" and additional_items
        else ", ".join(additional_items)
    )

    if not additional_display:
        additional_display = ui["none_selected"]

    with st.container(border=True):
        st.markdown(
            f"**{ui['persona_label']}：** {persona_display}"
        )
        st.markdown(
            f"**{ui['coverage_summary']}：** {coverage_display}"
        )
        st.markdown(
            f"**{ui['premium_summary']}：** "
            f"${data.get('monthly_premium', 0)}"
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
            f"**{ui['zip_summary']}：** "
            f"{data.get('zip_code') or '—'}"
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
            use_container_width=True,
            key="profile_review_back",
        ):
            st.session_state.profile_completed = False
            st.session_state.profile_step = 3
            st.rerun()

    with col2:
        if st.button(
            ui["save_btn"],
            type="primary",
            use_container_width=True,
            key="profile_save",
        ):
            st.session_state.profile_completed = True
            st.rerun()


# ==================================================
# Questionnaire Module Entry
# ==================================================

def render(current_lang):
    init_profile_state()

    lang = get_language(current_lang)
    ui = profile_labels[lang]

    st.markdown(ui["title"])
    st.caption(ui["caption"])
    st.markdown("---")

    total_steps = 4
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

    if current_step == 1:
        render_step_1(lang, ui)

    elif current_step == 2:
        render_step_2(lang, ui)

    elif current_step == 3:
        render_step_3(lang, ui)

    elif current_step == 4:
        render_step_4(lang, ui)