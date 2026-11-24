"""Krishi Netra - AI crop leaf disease detection.   Run: streamlit run app.py
Sidebar layout with dark forest-green styling matching the website.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Krishi Netra — AI Crop Leaf Disease Detection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

from html import escape as esc  # noqa: E402

from krishi import auth  # noqa: E402
from krishi import config as C  # noqa: E402
from krishi.i18n import t  # noqa: E402
from krishi.ui import (  # noqa: E402
    page_about,
    page_auth,
    page_contact,
    page_diagnose,
    page_history,
    page_how,
    page_info,
    page_labs,
    page_perf,
    theme,
)

# ---------------------------------------------------------------------------
# PAGE MAP
# ---------------------------------------------------------------------------
PAGES = {
    "diagnose": page_diagnose,
    "about":    page_about,
    "how":      page_how,
    "labs":     page_labs,
    "history":  page_history,
    "perf":     page_perf,
    "info":     page_info,
    "contact":  page_contact,
    "auth":     page_auth,
}

NAV_KEYS = ["diagnose", "about", "how", "labs", "history", "perf", "info", "contact"]

NAV_LABELS = {
    "en": {
        "diagnose": "🏠  Home",
        "about":    "📖  About",
        "how":      "⚙️  How It Works",
        "labs":     "✨  Features",
        "history":  "🔬  Technology",
        "perf":     "📊  Performance",
        "info":     "🗄️  Datasets",
        "contact":  "📬  Contact",
        "auth":     "👤  Account",
    },
    "hi": {
        "diagnose": "🏠  गृह (जाँच)",
        "about":    "📖  परिचय",
        "how":      "⚙️  कार्यप्रणाली",
        "labs":     "✨  सुविधाएँ",
        "history":  "🔬  तकनीक",
        "perf":     "📊  प्रदर्शन",
        "info":     "🗄️  डेटासेट",
        "contact":  "📬  संपर्क",
        "auth":     "👤  खाता",
    },
}

# ---------------------------------------------------------------------------
# INJECT CSS
# ---------------------------------------------------------------------------
theme.inject()

# ---------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"
    try:
        q = str(st.query_params.get("lang", "")).lower()
        if q in ("hi", "hindi"):
            st.session_state["lang"] = "hi"
    except Exception:
        pass

if "active_page" not in st.session_state:
    st.session_state["active_page"] = "diagnose"


# ---------------------------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------------------------
def _on_lang_change() -> None:
    choice = st.session_state.get("lang_choice", "🇬🇧 English")
    st.session_state["lang"] = "hi" if "हिन्दी" in choice else "en"


def _on_nav_change() -> None:
    selected = st.session_state.get("sidebar_nav_radio")
    if selected in NAV_KEYS:
        st.session_state["active_page"] = selected


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    # ── Brand block ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            display:flex; align-items:center; gap:11px;
            padding: 0.6rem 0.2rem 0.4rem 0.2rem;
            user-select:none;
        ">
            <div style="
                width:42px; height:42px; border-radius:12px; flex-shrink:0;
                background:linear-gradient(135deg,#2e7d32 0%,#43a047 100%);
                display:flex; align-items:center; justify-content:center;
                box-shadow:0 4px 14px rgba(67,160,71,0.45);
            ">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
                     stroke="#ffffff" stroke-width="2.2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                </svg>
            </div>
            <div>
                <div style="
                    font-family:'Space Grotesk',sans-serif;
                    font-weight:700; font-size:1.15rem; color:#ffffff;
                    letter-spacing:-0.015em; line-height:1.2;
                ">Krishi Netra</div>
                <span style="
                    font-family:'Inter',sans-serif; font-size:0.62rem;
                    font-weight:700; text-transform:uppercase; letter-spacing:0.07em;
                    background:rgba(200,230,201,0.18); color:#c8e6c9;
                    padding:2px 7px; border-radius:5px; display:inline-block;
                ">PROTOTYPE</span>
            </div>
        </div>
        <hr style="border:none; border-top:1px solid rgba(255,255,255,0.10); margin:0.5rem 0 0.8rem 0;">
        """,
        unsafe_allow_html=True,
    )

    # ── Language toggle ──────────────────────────────────────────────────────
    active_lang = st.session_state.get("lang", "en")
    is_hi = active_lang == "hi"

    st.markdown('<div class="sidebar-lang-box">', unsafe_allow_html=True)
    st.radio(
        "Language / भाषा",
        ["🇬🇧 English", "🇮🇳 हिन्दी"],
        index=1 if is_hi else 0,
        horizontal=True,
        key="lang_choice",
        on_change=_on_lang_change,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Re-evaluate active_lang in case of change
    active_lang = st.session_state.get("lang", "en")
    is_hi = active_lang == "hi"

    st.markdown("<div style='margin-bottom:0.6rem'></div>", unsafe_allow_html=True)

    # ── User account card (Option B) ─────────────────────────────────────────
    curr_user = auth.get_current_user()
    if curr_user:
        icon   = curr_user.get("icon", "👤")
        name   = curr_user.get("name", "User")
        role   = curr_user.get("role_badge", curr_user.get("role", "Member"))
        loc    = curr_user.get("location", "")
        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.07);
                border:1px solid rgba(200,230,201,0.22);
                border-radius:12px; padding:0.75rem 0.9rem; margin-bottom:0.5rem;
            ">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg, #2e7d32, #43a047); display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0;">
                        {icon}
                    </div>
                    <div style="min-width:0; flex:1;">
                        <div style="color:#ffffff;font-weight:600;font-size:0.88rem;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{esc(name)}</div>
                        <div style="color:#a7f3d0;font-size:0.72rem;font-weight:600;">{esc(role)}</div>
                        {"<div style='color:rgba(200,230,201,0.60);font-size:0.70rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>📍 "+esc(loc)+"</div>" if loc else ""}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c_act1, c_act2 = st.columns([1, 1], gap="small")
        with c_act1:
            if st.button("👤 " + ("खाता" if is_hi else "Account"), key="sb_account_btn", use_container_width=True):
                st.session_state["active_page"] = "auth"
                st.session_state["sidebar_nav_radio"] = None
                st.rerun()
        with c_act2:
            if st.button("🚪 " + ("लॉगआउट" if is_hi else "Sign Out"), key="sb_signout_btn", use_container_width=True):
                auth.logout()
                st.session_state["active_page"] = "diagnose"
                st.rerun()
    else:
        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.05);
                border:1px solid rgba(200,230,201,0.14);
                border-radius:12px; padding:0.75rem 0.9rem; margin-bottom:0.5rem;
            ">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:34px; height:34px; border-radius:50%; background:rgba(200,230,201,0.12); display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0;">
                        👤
                    </div>
                    <div>
                        <div style="color:#ffffff;font-weight:600;font-size:0.88rem;line-height:1.2;">
                            {"अतिथि मोड" if is_hi else "Guest Access"}
                        </div>
                        <div style="color:rgba(200,230,201,0.60);font-size:0.72rem;">
                            {"1-क्लिक डेमो उपलब्ध" if is_hi else "1-Click Demo Available"}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔑 " + ("लॉगिन / साइन अप" if is_hi else "Sign In / Sign Up"), key="sb_signin_btn", use_container_width=True):
            st.session_state["active_page"] = "auth"
            st.session_state["sidebar_nav_radio"] = None
            st.rerun()

    # ── Section Header ───────────────────────────────────────────────────────
    st.markdown(
        f"<div style='font-size:0.68rem;color:rgba(200,230,201,0.50);text-transform:uppercase;"
        f"letter-spacing:0.08em;padding:0.75rem 0.2rem 0.35rem;font-weight:700;'>"
        f"{'नेविगेशन / मेनू' if is_hi else 'NAVIGATION'}</div>",
        unsafe_allow_html=True,
    )

    # ── Sidebar nav (pill-styled radio) ──────────────────────────────────────
    current_page = st.session_state.get("active_page", "diagnose")
    radio_idx = NAV_KEYS.index(current_page) if current_page in NAV_KEYS else None

    # Sync radio state if needed
    if current_page not in NAV_KEYS:
        st.session_state["sidebar_nav_radio"] = None

    st.markdown('<div class="sidebar-nav-box">', unsafe_allow_html=True)
    st.radio(
        "Navigation",
        options=NAV_KEYS,
        index=radio_idx,
        label_visibility="collapsed",
        format_func=lambda k: NAV_LABELS[active_lang].get(k, k.capitalize()),
        key="sidebar_nav_radio",
        on_change=_on_nav_change,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Sidebar footer ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            margin-top:2.2rem; padding-top:0.8rem;
            border-top:1px solid rgba(255,255,255,0.10);
            color:rgba(200,230,201,0.45); font-size:0.72rem; text-align:center;
            line-height:1.4;
        ">
            🌿 Krishi Netra v2.1<br>
            <span style="color:rgba(200,230,201,0.65);">Reyaansh Gupta</span> · Apeejay School
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------------------------
active_view = st.session_state.get("active_page", "diagnose")

if C.PROJECT_ERROR:
    st.error(t("project_missing"))
    st.code(C.PROJECT_ERROR)

try:
    target = PAGES.get(active_view, page_diagnose)
    target.render()
except Exception:  # noqa: BLE001
    C.log.exception("Page %s crashed", active_view)
    st.error("Something went wrong on this page. Details were written to the log.")

st.markdown(
    f'<div class="footer">{esc(t("disclaimer"))} {esc(t("credits"))}</div>',
    unsafe_allow_html=True,
)
