"""Authentication Page: Sign In, Create Account (Sign Up), and 1-Click Judge Demo Access.
"""
from __future__ import annotations

import streamlit as st

from krishi import auth
from krishi.ui.components import card, hero
from krishi.ui.services import lang


def render() -> None:
    is_hi = lang() == "hi"
    user = auth.get_current_user()

    title = "उपयोगकर्ता खाता एवं प्रमाणीकरण" if is_hi else "Account & Authentication"
    subtitle = (
        "सुरक्षित किसान एवं वैज्ञानिक लॉगिन, व्यक्तिगत स्कैन इतिहास और त्वरित मूल्यांकनकर्ता एक्सेस"
        if is_hi
        else "Secure sign-in for farmers, KVK agronomists, and judges with saved scan history and 1-click evaluation access"
    )
    hero(title, subtitle, tag="Krishi Netra Portal · Access Gateway")

    # If already logged in, show User Profile Card
    if user:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid var(--green-600); background: #ffffff; padding: 1.8rem 2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:1rem;">
                        <div style="width:65px; height:65px; border-radius:50%; background:linear-gradient(135deg, var(--green-500) 0%, var(--green-700) 100%); display:flex; align-items:center; justify-content:center; font-size:2rem; box-shadow:0 4px 12px rgba(46,125,50,0.25);">
                            {user.get('icon', '👤')}
                        </div>
                        <div>
                            <div class="big" style="font-size:1.35rem; margin:0 0 2px 0;">{user['name']}</div>
                            <div style="font-size:0.88rem; color:var(--ink-secondary);">{user['email']} · 📍 {user.get('location', 'India')}</div>
                        </div>
                    </div>
                    <div>
                        <span class="badge badge-green" style="font-size:0.85rem; padding:4px 12px;">{user.get('role_badge', user.get('role'))}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        col_act1, col_act2 = st.columns([1, 1], gap="medium")
        with col_act1:
            st.info(
                ("🌾 Your diagnoses are linked to this profile. You can view your past leaf assessments anytime in the **Scan History** tab."
                 if not is_hi else
                 "🌾 आपके सभी निदान इस खाते से सुरक्षित जुड़े हुए हैं। आप कभी भी **इतिहास** टैब में अपने पिछले स्कैन देख सकते हैं।")
            )
        with col_act2:
            if st.button("Sign Out / लॉग आउट" if is_hi else "Sign Out / Logout", use_container_width=True):
                auth.logout()
                st.rerun()
        return

    # Tabs for Sign In vs Sign Up
    tabs = st.tabs([
        "🔑 " + ("Sign In" if not is_hi else "प्रवेश करें (लॉगिन)"),
        "📝 " + ("Create Account (Sign Up)" if not is_hi else "नया खाता बनाएं (साइन अप)"),
    ])

    with tabs[0]:
        st.write("")
        c_form, c_quick = st.columns([1.1, 0.9], gap="large")

        with c_form:
            st.markdown(
                f"""
                <div style="margin-bottom: 0.6rem;">
                    <div class="big" style="font-size: 1.25rem;">{"खाते में प्रवेश करें" if is_hi else "Sign In to Krishi Netra"}</div>
                    <p style="font-size: 0.88rem; color: var(--ink-secondary);">
                        {"अपने ईमेल और पासवर्ड से लॉगिन करें:" if is_hi else "Enter your registered email and password:"}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("kn_login_form"):
                email = st.text_input("Email / ईमेल *", placeholder="e.g. judge@krishinetra.ai")
                password = st.text_input("Password / पासवर्ड *", type="password", placeholder="••••••••")
                btn_login = st.form_submit_button("Sign In / प्रवेश करें" if not is_hi else "लॉगिन करें", use_container_width=True)

                if btn_login:
                    if not email or not password:
                        st.warning("Please enter both email and password." if not is_hi else "कृपया ईमेल और पासवर्ड दोनों दर्ज करें।")
                    else:
                        ok, msg, u = auth.login(email, password)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with c_quick:
            st.markdown(
                f"""
                <div class="card" style="border: 1px solid var(--border-med); background: var(--surface-alt); padding: 1.25rem 1.4rem;">
                    <span class="badge badge-amber" style="margin-bottom: 0.5rem;">{"⚡ त्वरित मूल्यांकन एक्सेस" if is_hi else "⚡ 1-Click Quick Demo Access"}</span>
                    <div class="big" style="font-size: 1.15rem; margin: 0.2rem 0 0.4rem 0;">
                        {"बिना पासवर्ड के तुरंत आजमाएं" if is_hi else "Evaluate Instantly (No Typing)"}
                    </div>
                    <p style="font-size: 0.85rem; color: var(--ink-secondary); line-height: 1.45; margin-bottom: 0.9rem;">
                        {"प्रदर्शनी जजों और नए उपयोगकर्ताओं के लिए 1-क्लिक एक्सेस:" if is_hi else "Designed specifically for science fair judges and evaluators to test features immediately:"}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("👨‍⚖️ 1-Click Judge / Evaluator Access", use_container_width=True, key="demo_judge_btn"):
                ok, msg, _ = auth.quick_login("judge")
                st.success(msg)
                st.rerun()

            if st.button("🌾 1-Click Progressive Farmer Access", use_container_width=True, key="demo_farmer_btn"):
                ok, msg, _ = auth.quick_login("farmer")
                st.success(msg)
                st.rerun()

            if st.button("🔬 1-Click KVK Agronomist Access", use_container_width=True, key="demo_kvk_btn"):
                ok, msg, _ = auth.quick_login("kvk")
                st.success(msg)
                st.rerun()

    with tabs[1]:
        st.write("")
        st.markdown(
            f"""
            <div style="max-width: 600px; margin-bottom: 0.8rem;">
                <div class="big" style="font-size: 1.25rem;">{"नया कृषक / वैज्ञानिक खाता बनाएं" if is_hi else "Create a Free Krishi Netra Account"}</div>
                <p style="font-size: 0.88rem; color: var(--ink-secondary);">
                    {"अपने व्यक्तिगत खेत या संस्थान के लिए नि:शुल्क खाता पंजीकृत करें:" if is_hi else "Register your profile to maintain saved diagnoses and personalized KVK guidance:"}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("kn_signup_form"):
            s_name = st.text_input("Full Name / पूरा नाम *", placeholder="e.g. Ramesh Patel")
            s_email = st.text_input("Email / ईमेल *", placeholder="e.g. ramesh@farm.org")
            s_role = st.selectbox(
                "Role / भूमिका",
                ["Farmer / Progressive Grower", "KVK Agronomist / Extension Officer", "Student / Researcher", "Science Fair Evaluator / Judge"]
                if not is_hi else
                ["किसान / कृषक (Farmer)", "KVK कृषि अधिकारी (Agronomist)", "विद्यार्थी / शोधकर्ता (Student)", "मूल्यांकनकर्ता / जज (Judge)"]
            )
            s_loc = st.text_input("State / District (राज्य / जिला)", placeholder="e.g. Karnal, Haryana")
            s_pw = st.text_input("Choose Password / पासवर्ड बनाएं *", type="password", placeholder="At least 4 characters")
            s_btn = st.form_submit_button("Create Account & Sign In / खाता बनाएं" if not is_hi else "खाता बनाएं एवं लॉगिन करें", use_container_width=True)

            if s_btn:
                ok, msg, u = auth.signup(s_name, s_email, s_pw, s_role, s_loc)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
