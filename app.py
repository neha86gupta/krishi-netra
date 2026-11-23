"""Krishi Netra - AI crop leaf disease detection.   Run: streamlit run app.py
Modern unified web application with sticky top navbar matching the website design.
Sidebar is hidden; navigation runs horizontally across the top bar.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Krishi Netra — AI Crop Leaf Disease Detection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from html import escape as esc  # noqa: E402

from krishi import auth  # noqa: E402
from krishi import config as C  # noqa: E402
from krishi.i18n import t  # noqa: E402
from krishi.ui import (
    page_about,
    page_auth,
    page_contact,
    page_diagnose,
    page_history,
    page_how,
    page_info,
    page_insights,
    page_labs,
    page_perf,
    theme,
)  # noqa: E402

# Available navigation pages: Unified web application with website content & auth
PAGES = {
    "diagnose": page_diagnose,
    "about": page_about,
    "how": page_how,
    "labs": page_labs,
    "history": page_history,
    "perf": page_perf,
    "info": page_info,
    "contact": page_contact,
    "auth": page_auth,
}

# The 8 navigation items matching the user's uploaded image exactly:
NAV_KEYS = ["diagnose", "about", "how", "labs", "history", "perf", "info", "contact"]
NAV_LABELS = {
    "en": {
        "diagnose": "Home",
        "about": "About",
        "how": "How It Works",
        "labs": "Features",
        "history": "Technology",
        "perf": "Performance",
        "info": "Datasets",
        "contact": "Contact",
        "auth": "Account",
    },
    "hi": {
        "diagnose": "गृह (जाँच)",
        "about": "परिचय",
        "how": "कार्यप्रणाली",
        "labs": "सुविधाएँ",
        "history": "तकनीक",
        "perf": "प्रदर्शन",
        "info": "डेटासेट",
        "contact": "संपर्क",
        "auth": "खाता",
    },
}

theme.inject()

# Language session state
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
    try:
        q_lang = str(st.query_params.get("lang", "")).lower()
        if q_lang in ("hi", "hindi"):
            st.session_state["lang"] = "hi"
    except Exception:
        pass

active_lang = st.session_state.get("lang", "en")
st.session_state["lang_label"] = "हिन्दी" if active_lang == "hi" else "English"

# Active page session state (defaults to 'diagnose' / 'Home')
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "diagnose"

curr_page = st.session_state["current_page"]
curr_idx = NAV_KEYS.index(curr_page) if curr_page in NAV_KEYS else 0

# ==============================================================================
# TOP STICKY NAVBAR - EXACT REPLICATION OF WEBSITE IMAGE
# ==============================================================================
st.markdown('<div class="site-top-bar">', unsafe_allow_html=True)
top_col1, top_col2, top_col3 = st.columns([0.22, 0.62, 0.16], vertical_alignment="center")

with top_col1:
    st.markdown(
        """
        <div class="site-brand-wrap">
            <div class="site-brand-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path>
                    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path>
                </svg>
            </div>
            <span class="site-brand-name">Krishi Netra</span>
            <span class="site-brand-tag">PROTOTYPE</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_col2:
    st.markdown('<div class="top-nav-radio-wrap">', unsafe_allow_html=True)
    selected_nav = st.radio(
        "Top Navigation",
        options=NAV_KEYS,
        index=curr_idx,
        horizontal=True,
        label_visibility="collapsed",
        format_func=lambda k: NAV_LABELS[active_lang].get(k, k.capitalize()),
        key="top_nav_radio",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if selected_nav != st.session_state.get("current_page"):
        st.session_state["current_page"] = selected_nav
        st.rerun()

with top_col3:
    act_c1, act_c2 = st.columns([0.48, 0.52], vertical_alignment="center")
    with act_c1:
        lang_target = "hi" if active_lang == "en" else "en"
        lang_btn_text = "🇮🇳 हिन्दी" if active_lang == "en" else "🇬🇧 English"
        if st.button(lang_btn_text, key="top_lang_toggle_btn", use_container_width=True):
            st.session_state["lang"] = lang_target
            st.rerun()

    with act_c2:
        curr_user = auth.get_current_user()
        if curr_user:
            user_label = f"{curr_user.get('icon', '👤')} {curr_user['name'].split()[0]}"
            if st.button(user_label, key="top_auth_profile_btn", use_container_width=True):
                st.session_state["current_page"] = "auth"
                st.rerun()
        else:
            if st.button("👤 Sign In" if active_lang == "en" else "👤 लॉगिन", key="top_auth_login_btn", use_container_width=True):
                st.session_state["current_page"] = "auth"
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# MAIN VIEW RENDERER
# ==============================================================================
active_view = st.session_state.get("current_page", "diagnose")

if C.PROJECT_ERROR:
    st.error(t("project_missing"))
    st.code(C.PROJECT_ERROR)

try:
    if active_view in PAGES:
        PAGES[active_view].render()
    else:
        page_diagnose.render()
except Exception:  # noqa: BLE001 - keep the shell alive; details go to the log
    C.log.exception("Page %s crashed", active_view)
    st.error("Something went wrong on this page. Details were written to the log.")

st.markdown(f'<div class="footer">{esc(t("disclaimer"))} {esc(t("credits"))}</div>', unsafe_allow_html=True)
