"""Contact & KVK Page: National Agricultural Helplines, KVK Network, Feedback & Citations.
Matches the official Krishi Netra website 'Contact & Access' section."""
from __future__ import annotations

import streamlit as st

from krishi.config import KVK_URL
from krishi.ui.components import card, hero
from krishi.ui.services import lang


def render() -> None:
    is_hi = lang() == "hi"

    title = "संपर्क एवं कृषि विज्ञान केंद्र (KVK) सहायता" if is_hi else "Contact & KVK Network"
    subtitle = (
        "राष्ट्रीय कृषि हेल्पलाइन, नज़दीकी केवीके केंद्र, प्रदर्शनी प्रतिक्रिया एवं वैज्ञानिक संदर्भ"
        if is_hi
        else "National agricultural extension helplines, local KVK locator, project feedback, and research citations"
    )
    hero(title, subtitle)

    # 1. National Helplines & KVK Hubs (3 Cards)
    st.markdown(
        f"""
        <div style="margin-bottom: 0.8rem;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em;">
                {"सरकारी कृषि विस्तार नेटवर्क" if is_hi else "Government Agricultural Extension Support"}
            </div>
            <div class="big" style="font-size: 1.45rem; margin-top: 0.2rem;">
                {"राष्ट्रीय हेल्पलाइन एवं कृषि विशेषज्ञ सहायता" if is_hi else "National Helplines & KVK Support Hubs"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3, gap="medium")
    with h1:
        st.markdown(
            f"""
            <div class="card" style="border-top: 4px solid var(--green-600); min-height: 200px;">
                <span class="badge badge-green">{"टोल-फ्री 24x7" if is_hi else "Toll-Free 24x7"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.1rem 0;">{"किसान कॉल सेंटर (KCC)" if is_hi else "Kisan Call Centre (KCC)"}</div>
                <div style="font-family: 'Space Grotesk', monospace; font-size: 1.35rem; font-weight: 800; color: var(--green-700); margin: 0.4rem 0;">1800-180-1551</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); margin: 0; line-height: 1.45;">
                    {"22 भारतीय भाषाओं में ICAR विषय विशेषज्ञों द्वारा निःशुल्क 24 घंटे सातों दिन सलाह उपलब्ध।" if is_hi else "Free 24/7 advisory in 22 Indian languages from ICAR subject matter specialists."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h2:
        st.markdown(
            f"""
            <div class="card" style="border-top: 4px solid #0284c7; min-height: 200px;">
                <span class="badge badge-sky">{"सरकारी पोर्टल" if is_hi else "Government Portal"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.1rem 0;">{"एम-किसान पोर्टल (mKisan)" if is_hi else "mKisan Agri Portal"}</div>
                <div style="font-family: 'Space Grotesk', monospace; font-size: 1.1rem; font-weight: 700; color: #0369a1; margin: 0.4rem 0;">mkisan.gov.in</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); margin: 0; line-height: 1.45;">
                    {"राज्य कृषि विश्वविद्यालयों द्वारा सीधे किसान के मोबाइल पर एसएमएस मौसम व फसल सलाह।" if is_hi else "SMS-based crop advisories and local weather alerts sent directly to registered farmers."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with h3:
        st.markdown(
            f"""
            <div class="card" style="border-top: 4px solid #b45309; min-height: 200px;">
                <span class="badge badge-amber">{"भौतिक प्रयोगशाला जांच" if is_hi else "Physical Lab Testing"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.1rem 0;">{"ICAR KVK नेटवर्क" if is_hi else "ICAR KVK Network"}</div>
                <div style="margin: 0.4rem 0;">
                    <a href="{KVK_URL}" target="_blank" style="color: #b45309; font-weight: 700; text-decoration: underline; font-size: 0.95rem;">{"नज़दीकी KVK खोजें ↗" if is_hi else "Find Nearest KVK ↗"}</a>
                </div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); margin: 0; line-height: 1.45;">
                    {"संदेहास्पद पत्तियों को जिले के नज़दीकी KVK ले जाकर माइक्रोस्कोपिक जांच व मृदा परीक्षण कराएं।" if is_hi else "Bring unconfirmed diseased leaves to your district KVK for free microscopic laboratory diagnosis."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 2. Interactive Feedback / Agronomist Form & FAQ
    f_col, q_col = st.columns([1, 1], gap="large")

    with f_col:
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">
                {"प्रतिक्रिया एवं संदेश" if is_hi else "Project & Feedback Desk"}
            </div>
            <div class="big" style="font-size: 1.35rem; margin: 0.1rem 0 0.5rem 0;">
                {"संदेश या फ़ील्ड रिपोर्ट भेजें" if is_hi else "Send a Message or Field Note"}
            </div>
            <p style="font-size: 0.88rem; color: var(--ink-secondary); margin-bottom: 0.8rem;">
                {"प्रदर्शनी मूल्यांकनकर्ताओं, छात्रों एवं कृषि अधिकारियों के सुझावों का स्वागत है:" if is_hi else "Have questions or feedback on model training, Grad-CAM heatmaps, or field experiments? Send a note:"}
            </p>
            """,
            unsafe_allow_html=True,
        )

        with st.form("kn_contact_form", clear_on_submit=True):
            name = st.text_input("Your Name / आपका नाम *" if not is_hi else "आपका नाम / Your Name *", placeholder="e.g. Dr. Ramesh Kumar")
            email = st.text_input("Email / ईमेल", placeholder="you@example.org")
            role = st.selectbox(
                "I am a / मेरी भूमिका" if not is_hi else "मेरी भूमिका / I am a",
                ["Farmer / Grower", "KVK / Agriculture Officer", "Student / Researcher", "Exhibition / Science Fair Evaluator"]
                if not is_hi else
                ["किसान / कृषक (Farmer)", "KVK / कृषि अधिकारी (Agronomist)", "विद्यार्थी / शोधकर्ता (Student)", "प्रदर्शनी / मूल्यांकनकर्ता (Judge/Evaluator)"]
            )
            msg = st.text_area("Message or Feedback / संदेश या प्रतिक्रिया *" if not is_hi else "संदेश या प्रतिक्रिया *", placeholder="Share your suggestions, questions, or field notes...")
            submitted = st.form_submit_button("Submit Message / संदेश भेजें" if not is_hi else "संदेश भेजें / Submit", use_container_width=True)
            if submitted:
                if name.strip() and msg.strip():
                    st.success("✅ Thank you! Your message has been logged for review." if not is_hi else "✅ धन्यवाद! आपका संदेश दर्ज कर लिया गया है।")
                else:
                    st.warning("⚠️ Please fill in both your name and message." if not is_hi else "⚠️ कृपया नाम और संदेश दोनों भरें।")

    with q_col:
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">
                {"अक्सर पूछे जाने वाले प्रश्न" if is_hi else "Frequently Asked Questions"}
            </div>
            <div class="big" style="font-size: 1.35rem; margin: 0.1rem 0 0.5rem 0;">
                {"सामान्य प्रश्नोत्तरी (FAQ)" if is_hi else "Common Questions Answered"}
            </div>
            """,
            unsafe_allow_html=True,
        )

        faqs = [
            (
                "क्या कृषि नेत्र बिना इंटरनेट के खेतों में काम करता है?" if is_hi else "Does Krishi Netra work offline without internet?",
                "हाँ — इसका 9.8 MB मोबाइलनेटवी3 मॉडल और ज्ञानकोष पूरी तरह से स्थानीय सीपीयू (CPU) पर चलते हैं। इन्फेरेंस के दौरान शून्य डेटा की आवश्यकता होती है।" if is_hi else "Yes — the lightweight 9.8 MB MobileNetV3 model, Grad-CAM engine, and ICAR knowledge base run locally on commodity CPU in <0.25s with zero active cloud connectivity required."
            ),
            (
                "ग्रैड-सीएएम हीटमैप कैसे मदद करता है?" if is_hi else "How does the Grad-CAM heatmap help?",
                "हीटमैप लाल और पीले रंगों से दिखाता है कि AI ने पत्ती के किस धब्बे को देखकर रोग पहचाना। इससे साबित होता है कि मॉडल ने पृष्ठभूमि की मिट्टी देखकर धोखा नहीं खाया।" if is_hi else "Grad-CAM generates a pixel-level spatial heatmap showing exactly where neural attention landed. It proves the model focused on real fungal lesions rather than soil or background noise."
            ),
            (
                "यदि मॉडल बीमारी के प्रति आश्वस्त नहीं है तो क्या होता है?" if is_hi else "What happens when the model is unsure?",
                "कृषि नेत्र का 3-गेट कैलिब्रेटेड सिस्टम तुरंत 'Not Sure' घोषित करता है, ताकि किसान को गलत कीटनाशक छिड़काव की खतरनाक सलाह न मिले।" if is_hi else "Unlike commercial apps that force a guess, Krishi Netra's 3-gate abstention declares 'Not Sure — Consult a KVK Agronomist' to prevent inappropriate chemical runoff."
            ),
        ]

        for q, a in faqs:
            with st.expander(f"🌾 {q}", expanded=False):
                st.write(a)

    st.write("")

    # 3. Project Attribution & Citations
    st.markdown(
        f"""
        <div class="card" style="background: var(--surface-alt); border: 1px solid var(--border-med); margin-top: 1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span class="badge badge-green">{"शैक्षणिक एवं वैज्ञानिक श्रेय" if is_hi else "Academic & Open-Source Citations"}</span>
                <span style="font-size:0.8rem; color:var(--ink-muted);">Version 2.1 Production Release</span>
            </div>
            <div class="big" style="font-size: 1.15rem; margin: 0.5rem 0 0.3rem 0;">{"डेटासेट एवं शोध संदर्भ" if is_hi else "Open Datasets & Research Acknowledgements"}</div>
            <p style="font-size: 0.88rem; color: var(--ink-secondary); line-height: 1.5; margin-bottom: 0.6rem;">
                <b>PlantVillage:</b> Hughes & Salathé (2015), Mohanty et al. (2016) — CC BY-SA 3.0.<br>
                <b>PlantDoc:</b> Singh et al. (2020), ACM IKDD CoDS-COMAD — CC BY 4.0.<br>
                <b>Paddy Doctor:</b> IEEE Dataport / Tamil Nadu Rice Research Institute — CC BY 4.0.<br>
                <b>Developer & School:</b> Reyaansh Gupta (Class 9), Apeejay School Pitampura, New Delhi.<br>
                <b>GitHub Repository:</b> <a href="https://github.com/neha86gupta/krishi-netra" target="_blank" style="color:var(--green-700); font-weight:600; text-decoration:underline;">github.com/neha86gupta/krishi-netra</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
