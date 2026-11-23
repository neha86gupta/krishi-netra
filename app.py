"""Krishi Netra - AI crop leaf disease detection.   Run: streamlit run app.py

Thin entry point: page routing, language switch and shell only. Logic lives in krishi/.
"""
import streamlit as st

st.set_page_config(page_title="Krishi Netra", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

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
    "how": page_how,
    "about": page_about,
    "perf": page_perf,
    "info": page_info,
    "labs": page_labs,
    "history": page_history,
    "contact": page_contact,
    "auth": page_auth,
}
ICONS = {
    "diagnose": "🩺",
    "how": "🔍",
    "about": "📖",
    "perf": "📊",
    "info": "🌾",
    "labs": "🔬",
    "history": "📜",
    "contact": "📞",
    "auth": "👤",
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
    st.markdown(
        """
        <div class="brand">
            <span class="brand-icon">🌿</span>
            <span>Krishi Netra</span>
            <span class="brand-badge">V2.1</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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

    # User Account Profile / Sign-in Card
    curr_user = auth.get_current_user()
    if curr_user:
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; padding: 0.65rem 0.85rem; margin: 0.8rem 0 0.4rem 0;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 2px;">
                    <span style="font-size:0.75rem; color:#86efac; font-weight:700;">🟢 {"सक्रिय खाता" if active_lang == "hi" else "Signed In"}</span>
                    <span style="font-size:0.72rem; background:rgba(34,197,94,0.22); padding:1px 7px; border-radius:6px; color:#dcfce7; font-weight:600;">{curr_user.get('role_badge', 'Member')}</span>
                </div>
                <div style="font-weight:700; font-size:0.92rem; color:#ffffff;">{curr_user.get('icon', '👤')} {curr_user['name']}</div>
                <div style="font-size:0.74rem; color:#cbd5e1;">📍 {curr_user.get('location', 'India')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); border-radius: 14px; padding: 0.6rem 0.85rem; margin: 0.8rem 0 0.4rem 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.78rem; color:#e2e8f0; font-weight:600;">👤 {"अतिथि मोड" if active_lang == "hi" else "Guest Access"}</span>
                    <span style="font-size:0.72rem; color:#86efac; font-weight:600;">{"1-क्लिक एक्सेस" if active_lang == "hi" else "1-Click Demo"}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin: 0.75rem 0 0.35rem 0; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.85;">'
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

    # Sidebar Quick Auth Action
    if curr_user:
        if st.button("🚪 " + ("लॉग आउट" if active_lang == "hi" else "Sign Out"), key="sb_logout_btn", use_container_width=True):
            auth.logout()
            st.rerun()
    else:
        if st.button("🔑 " + ("लॉगिन / साइन अप" if active_lang == "hi" else "Sign In / Sign Up"), key="sb_login_btn", use_container_width=True):
            st.session_state["nav"] = "auth"
            st.rerun()

if C.PROJECT_ERROR:
    st.error(t("project_missing"))
    st.code(C.PROJECT_ERROR)

try:
    PAGES[page].render()
except Exception:  # noqa: BLE001 - keep the shell alive; details go to the log
    C.log.exception("Page %s crashed", page)
    st.error("Something went wrong on this page. Details were written to the log.")

st.markdown(f'<div class="footer">{esc(t("disclaimer"))} {esc(t("credits"))}</div>', unsafe_allow_html=True)
