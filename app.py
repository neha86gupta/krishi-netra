"""Krishi Netra - AI crop leaf disease detection.   Run: streamlit run app.py

Thin entry point: page routing, language switch and shell only. Logic lives in krishi/.
"""
import streamlit as st

st.set_page_config(page_title="Krishi Netra", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

from html import escape as esc  # noqa: E402

from krishi import config as C  # noqa: E402
from krishi.i18n import t  # noqa: E402
from krishi.ui import page_diagnose, page_history, page_info, page_insights, page_labs, page_perf, theme  # noqa: E402

# Available navigation pages (Demo & testing page removed per requirement)
PAGES = {
    "diagnose": page_diagnose,
    "info": page_info,
    "perf": page_perf,
    "history": page_history,
    "insights": page_insights,
    "labs": page_labs,
}
ICONS = {
    "diagnose": "🔍",
    "info": "📚",
    "perf": "📊",
    "history": "🕘",
    "insights": "🌱",
    "labs": "🧪",
}

theme.inject()

# Pre-select Hindi if ?lang=hi query parameter is passed from website
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
    try:
        q_lang = str(st.query_params.get("lang", "")).lower()
        if q_lang in ("hi", "hindi"):
            st.session_state["lang"] = "hi"
    except Exception:
        pass

LANG_CHOICES = ["🇬🇧 English", "🇮🇳 हिन्दी (Hindi)"]
current_lang = st.session_state.get("lang", "en")
default_idx = 1 if current_lang == "hi" else 0

with st.sidebar:
    st.markdown('<div class="brand">🌿 Krishi Netra</div>', unsafe_allow_html=True)
    
    # Clearly show both English and Hindi options side by side
    selected_lang_str = st.radio(
        "Language / भाषा",
        LANG_CHOICES,
        index=default_idx,
        horizontal=True,
        key="lang_radio_selector",
        help="Switch entire app interface between English and Hindi"
    )
    active_lang = "hi" if "हिन्दी" in selected_lang_str else "en"
    st.session_state["lang"] = active_lang
    st.session_state["lang_label"] = "हिन्दी" if active_lang == "hi" else "English"

    st.markdown(
        '<div style="margin: 0.9rem 0 0.35rem 0; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.85;">'
        + ("नेविगेशन / Navigation" if active_lang == "hi" else "Navigation / नेविगेशन")
        + '</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "nav",
        list(PAGES),
        key="nav",
        label_visibility="collapsed",
        format_func=lambda k, _L=active_lang: f"{ICONS[k]} {t('nav_' + k, _L)}",
    )

if C.PROJECT_ERROR:
    st.error(t("project_missing"))
    st.code(C.PROJECT_ERROR)

try:
    PAGES[page].render()
except Exception:  # noqa: BLE001 - keep the shell alive; details go to the log
    C.log.exception("Page %s crashed", page)
    st.error("Something went wrong on this page. Details were written to the log.")

st.markdown(f'<div class="footer">{esc(t("disclaimer"))} {esc(t("credits"))}</div>', unsafe_allow_html=True)
