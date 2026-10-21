"""Language, accessible text sizes, trust notice, and information base only."""
import streamlit as st
from core.config import MEDICARE_INFO_YEAR
from core.flow_translations import flow_labels
from core.translations import legal_caption_map, header_labels

TEXT_SIZES = ((19, "A Standard"), (22, "A+ Large"), (26, "A++ Extra"))


def render():
    with st.sidebar:
        st.selectbox("Language", ["English", "Español", "繁體中文", "簡體中文", "한국어"],
                     key="selected_language")
        language = st.session_state["selected_language"]
        ui = flow_labels(language)
        st.divider()
        st.markdown("### Text size")
        for size, label in TEXT_SIZES:
            st.button(label, key=f"text_size_{size}", width="stretch",
                      type="primary" if st.session_state["font_size"] == size else "secondary",
                      on_click=set_text_size, args=(size,))
        st.divider()
        with st.expander(ui["trust"]):
            st.caption(legal_caption_map.get(language, legal_caption_map["English"]))
            st.caption(ui["ai_notice"])
        st.divider()
        header = header_labels.get(language, header_labels["English"])
        st.markdown(f"""
        <div class="info-base-badge">
            <div>{header['info_base'].format(year=MEDICARE_INFO_YEAR)}</div>
            <div class="info-base-reviewed">{header['last_reviewed']}</div>
        </div>
        """, unsafe_allow_html=True)
    apply_text_size(st.session_state["font_size"])
    return language


def set_text_size(size):
    st.session_state["font_size"] = size


def apply_text_size(size):
    # Explicitly requested accessibility scaling, including controls and tables.
    st.markdown(f"""
    <style>
    html {{ font-size: {size}px !important; }}
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th,
    [data-testid="stWidgetLabel"] p,
    [data-baseweb="select"], input, textarea {{ font-size: {size}px !important; }}
    .stButton > button, .stLinkButton > a, .stDownloadButton > button {{
        font-size: {size}px !important; min-height: {round(size * 2.5)}px;
        padding: {round(size * .5)}px {size}px !important;
    }}
    .stButton > button p, .stChatInput textarea {{ font-size: {size}px !important; }}
    .stChatMessage {{ font-size: {size}px !important; line-height: 1.7; }}
    </style>
    """, unsafe_allow_html=True)
