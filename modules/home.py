"""Welcome content and the two-stage entry flow."""
import streamlit as st
from core.flow_translations import flow_labels, persona_options
from core.navigation import choose_persona, start_route
from core.translations import welcome_guide_map, guide_labels


def render_welcome(language):
    wd = welcome_guide_map.get(language, welcome_guide_map["English"])
    with st.expander("👋 Welcome / 歡迎 / Bienvenido / 환영합니다", expanded=True):
        st.markdown(f"""
        <div class="welcome-banner-card">
            <h4>{wd['greeting']}</h4>
            <p><strong>{wd['step1']} → {wd['step2']} → {wd['step3']}</strong></p>
            <p><em>{wd['hint']}</em></p>
        </div>
        """, unsafe_allow_html=True)
    guide = guide_labels.get(language, guide_labels["English"])
    with st.expander(guide["btn_text"]):
        st.markdown(guide["guide_title"])
        left, right = st.columns(2)
        with left:
            st.info(guide["p_ab"])
            st.warning(guide["p_c"])
        with right:
            st.success(guide["p_d"])
            st.error(guide["medigap"])


def render(language):
    ui = flow_labels(language)
    personas = persona_options(language)
    if st.session_state["entry_stage"] == "welcome":
        render_welcome(language)
        persona = st.selectbox(ui["who"], list(personas), index=None,
                               format_func=personas.__getitem__, key="entry_persona")
        if persona is not None:
            choose_persona(persona)
            st.rerun()
    else:
        st.subheader(ui["today"])
        st.caption(personas[st.session_state["persona"]])
        for route in ("guided", "switch", "direct", "unsure"):
            if st.button(ui[route], key=f"entry_{route}", width="stretch",
                         type="primary" if route == "guided" else "secondary"):
                start_route(route)
                st.rerun()
        if st.button(ui["back"], key="entry_back"):
            st.session_state["entry_stage"] = "welcome"
            st.rerun()
