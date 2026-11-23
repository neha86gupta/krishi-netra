"""About Page: Project Vision, Purpose, Core Pillars & Founder Spotlight.
Matches the official Krishi Netra website 'About' section."""
from __future__ import annotations

import streamlit as st

from krishi.ui.components import card, hero
from krishi.ui.services import lang


def render() -> None:
    is_hi = lang() == "hi"

    title = "परियोजना परिचय एवं उद्देश्य" if is_hi else "About Krishi Netra"
    subtitle = (
        "भारतीय कृषि के लिए उत्तरदायी, पारदर्शी एवं व्याख्यात्मक कृत्रिम बुद्धिमत्ता (Responsible AI for Indian Agriculture)"
        if is_hi
        else "Responsible, transparent, and explainable AI engineered for early crop leaf screening"
    )
    hero(title, subtitle)

    # 1. Agricultural Challenge & Distinct Value
    col1, col2 = st.columns([1.1, 0.9], gap="large")
    with col1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1.2rem;">
                <span class="badge badge-amber">{"कृषि चुनौती" if is_hi else "The Agricultural Challenge"}</span>
                <div class="big" style="font-size: 1.45rem; margin: 0.5rem 0 0.4rem 0;">
                    {"समय पर पहचान और प्रामाणिक अनिश्चितता क्यों आवश्यक है?" if is_hi else "Why Early Recognition & Honest Uncertainty Matter"}
                </div>
                <p style="color: var(--ink-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.8rem;">
                    {"पत्तियों के रोग अक्सर देर से पहचाने जाते हैं, जिससे फसल की पैदावार और गुणवत्ता को भारी नुकसान होता है। कई आधुनिक AI मॉडल केवल एक बंद-डिब्बे (ब्लैक-बॉक्स) का अनुमान दे देते हैं, बिना यह समझाए कि उन्होंने निर्णय कैसे लिया।" if is_hi else "Foliar diseases reduce crop yield and quality when left unnoticed until late stages. Smartphone leaf screening offers rapid detection, yet commercial black-box apps force an overconfident diagnosis without explaining why."}
                </p>
                <p style="color: var(--ink-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.8rem;">
                    {"गलत अनुमान से किसान अनावश्यक रसायन खरीदते हैं। कृषि नेत्र एक हल्के मोबाइलनेटवी3 मॉडल को <b>कैलिब्रेटेड अनिश्चितता ('Not Sure')</b>, <b>ग्रैड-सीएएम हीटमैप</b> और <b>ICAR-KVK वैज्ञानिक सलाह</b> के साथ जोड़ता है।" if is_hi else "In real farm settings, an uncalibrated overconfident misdiagnosis leads to wasted agrochemicals. Krishi Netra addresses this directly with <b>calibrated confidence gates ('Not Sure')</b>, <b>Grad-CAM visual heatmaps</b>, and <b>static ICAR-KVK cultural advisories</b>."}
                </p>
                <p style="color: var(--ink-secondary); font-size: 0.95rem; line-height: 1.6;">
                    {"यह प्रणाली विशेषज्ञों की जगह लेने के बजाय किसानों को उनके नज़दीकी <b>कृषि विज्ञान केंद्र (KVK)</b> से जोड़ती है।" if is_hi else "Rather than replacing agronomists, Krishi Netra serves as an initial safety-first screening companion linking farmers directly to their local <b>Krishi Vigyan Kendra (KVK)</b>."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="card" style="background: var(--surface-alt); border: 1px solid var(--border-med);">
                <span class="badge badge-green">{"प्रमुख सिद्धांत" if is_hi else "Core Principles"}</span>
                <div class="big" style="font-size: 1.25rem; margin: 0.4rem 0 0.6rem 0;">{"कृषि नेत्र को क्या अलग बनाता है?" if is_hi else "What Makes Krishi Netra Distinct"}</div>
                <ul style="margin: 0; padding-left: 1.2rem; display: grid; gap: 0.65rem; color: var(--ink-secondary); font-size: 0.9rem; line-height: 1.5;">
                    <li><b>{"एकल पत्ती स्पष्टता" if is_hi else "Single-Leaf Clarity"}:</b> {"प्राकृतिक daylight में स्पष्ट पत्ती की तस्वीर पर आधारित।" if is_hi else "Built around capturing a single leaf in daylight rather than cluttered wide scenes."}</li>
                    <li><b>{"अस्वीकार करने का अधिकार ('Not Sure')" if is_hi else "Right to Abstain ('Not Sure')"}:</b> {"अस्पष्ट तस्वीर पर गलत अनुमान लगाने से इनकार।" if is_hi else "Three-gate calibrated thresholds prevent forced guesses on ambiguous photos."}</li>
                    <li><b>{"AI और सलाह का अलगाव" if is_hi else "Separation of AI & Care"}:</b> {"पहचान न्यूरल नेटवर्क करता है, पर उपचार केवल ICAR वैज्ञानिक पुस्तकों से आता है।" if is_hi else "Neural classification is strictly separated from static ICAR non-chemical guidance."}</li>
                    <li><b>{"द्वैभाषिक पहुंच" if is_hi else "Bilingual Accessibility"}:</b> {"अंग्रेजी और हिन्दी में पूर्ण समर्थन।" if is_hi else "Complete workflow support in both English and Hindi."}</li>
                    <li><b>{"खेत-सत्यापित बेंचमार्क" if is_hi else "Field-Proven Benchmarks"}:</b> {"95.8% लैब सटीकता और 90.3% वास्तविक खेत F1-स्कोर।" if is_hi else "Reports 95.8% lab accuracy and 90.3% outdoor field F1 openly side by side."}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 2. Four Core Engineering Pillars
    st.markdown(
        f"""
        <div style="margin: 1.2rem 0 0.8rem 0;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em;">
                {"इंजीनियरिंग डिज़ाइन दर्शन" if is_hi else "Engineering Design Philosophy"}
            </div>
            <div class="big" style="font-size: 1.5rem; margin-top: 0.2rem;">
                {"कृषि नेत्र के चार मुख्य स्तंभ" if is_hi else "The Four Core Pillars of Krishi Netra"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    p1, p2 = st.columns(2, gap="medium")
    with p1:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid var(--green-600); min-height: 165px;">
                <span class="badge badge-green">{"स्तंभ 1: स्थानीय स्वायत्तता" if is_hi else "Pillar 1: Edge-First Independence"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"शून्य क्लाउड — ऑफलाइन कार्यक्षम" if is_hi else "Zero Cloud Dependency — Fast Edge CPU"}</div>
                <p style="font-size: 0.88rem; color: var(--ink-secondary); margin: 0; line-height: 1.5;">
                    {"भारतीय खेतों में नेटवर्क अक्सर कमजोर होता है। मोबाइलनेटवी3 का हल्का 9.8MB मॉडल साधारण कंप्यूटर या फोन पर बिना इंटरनेट के 0.25 सेकंड में तुरंत चलता है।" if is_hi else "Indian farm fields frequently suffer poor connectivity. The 9.8 MB MobileNetV3 runs entirely on local CPU hardware in <0.25s without external data transmission."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #0284c7; min-height: 165px;">
                <span class="badge badge-sky">{"स्तंभ 2: दृश्य व्याख्यात्मकता" if is_hi else "Pillar 2: Radical Explainability"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"कोई अंधा ब्लैक-बॉक्स नहीं — ग्रैड-सीएएम" if is_hi else "Auditable Spatial Heatmaps (Grad-CAM)"}</div>
                <p style="font-size: 0.88rem; color: var(--ink-secondary); margin: 0; line-height: 1.5;">
                    {"ग्रैड-सीएएम हीटमैप साबित करता है कि मॉडल ने रोग के धब्बे को देखा या पृष्ठभूमि की मिट्टी को, जिससे किसान और कृषि अधिकारी मॉडल पर भरोसा कर सकें।" if is_hi else "Spatial Grad-CAM overlays verify whether the model is focusing on a pathogenic fungal lesion versus background soil, ensuring visual trust for agronomists."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #b45309; min-height: 165px;">
                <span class="badge badge-amber">{"स्तंभ 3: कैलिब्रेटेड विनम्रता" if is_hi else "Pillar 3: Calibrated Humility"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"सुरक्षित 'Not Sure' गेटिंग" if is_hi else "Honest 'Not Sure' Safety Gate"}</div>
                <p style="font-size: 0.88rem; color: var(--ink-secondary); margin: 0; line-height: 1.5;">
                    {"तापमान स्केलिंग, शैनन एन्ट्रॉपी और सेंट्रोइड दूरी अनिश्चित तस्वीरों पर मॉडल को जबरन अनुमान लगाने से रोकती हैं, जिससे गलत कीटनाशक छिड़काव का जोखिम टलता है।" if is_hi else "Temperature scaling, Shannon entropy (H > 1.70), and centroid similarity force the model to abstain on ambiguous leaves rather than prompting inappropriate chemical application."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #15803d; min-height: 165px;">
                <span class="badge badge-green">{"स्तंभ 4: कृषि विस्तार केंद्र" if is_hi else "Pillar 4: Extension Centricity"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"ICAR-KVK वैज्ञानिक सलाह" if is_hi else "ICAR-KVK Certified Bilingual Guidance"}</div>
                <p style="font-size: 0.88rem; color: var(--ink-secondary); margin: 0; line-height: 1.5;">
                    {"निदान सीधे भारतीय कृषि अनुसंधान परिषद (ICAR) के मानकों के अनुरूप हिंदी और अंग्रेजी सलाह में बदलता है, जिसमें सीधे नजदीकी केवीके का संदर्भ दिया जाता है।" if is_hi else "Predictions map to certified non-commercial cultural management packages from ICAR, with direct geolocation referral to local Krishi Vigyan Kendras."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 3. Founder Spotlight (Reyaansh Gupta)
    st.markdown(
        f"""
        <div class="card" style="border: 1px solid var(--border-med); background: #ffffff; padding: 1.8rem 2rem; box-shadow: 0 8px 24px rgba(20,54,26,0.08);">
            <div style="display: flex; gap: 2rem; align-items: center; flex-wrap: wrap;">
                <div style="text-align: center; min-width: 170px;">
                    <div style="width: 100px; height: 100px; margin: 0 auto 0.7rem auto; border-radius: 50%; background: linear-gradient(135deg, #2e7d32 0%, #0f3314 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(15,51,20,0.25); border: 3px solid #86efac; color: white; font-size: 2.5rem;">
                        👨‍💻
                    </div>
                    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; color: var(--green-950);">Reyaansh Gupta</div>
                    <div style="font-size: 0.82rem; font-weight: 600; color: var(--green-700);">{"कक्षा 9 छात्र अन्वेषक" if is_hi else "Class 9 Student Innovator"}</div>
                    <div style="font-size: 0.78rem; color: var(--ink-muted);">Apeejay School, Pitampura</div>
                    <div style="margin-top: 0.5rem; display: flex; gap: 4px; justify-content: center; flex-wrap: wrap;">
                        <span class="chip" style="font-size: 0.7rem; padding: 2px 7px;">PyTorch</span>
                        <span class="chip" style="font-size: 0.7rem; padding: 2px 7px;">MobileNetV3</span>
                        <span class="chip" style="font-size: 0.7rem; padding: 2px 7px;">Grad-CAM</span>
                    </div>
                </div>
                <div style="flex: 1; min-width: 260px;">
                    <span class="badge badge-sky" style="margin-bottom: 0.4rem;">{"कृषि नेत्र की प्रेरणा एवं विकास यात्रा" if is_hi else "The Story Behind Krishi Netra"}</span>
                    <div class="big" style="font-size: 1.3rem; margin: 0.2rem 0 0.5rem 0;">{"उन्नत AI और भारतीय खेतों के बीच सेतु" if is_hi else "Bridging Advanced AI & Real Indian Smallholder Agriculture"}</div>
                    <p style="color: var(--ink-secondary); font-size: 0.92rem; line-height: 1.6; margin-bottom: 0.6rem;">
                        {"यह देखकर कि पत्तियों के अचानक रोग भारतीय छोटे किसानों को भारी आर्थिक नुकसान पहुंचाते हैं, अपीजे स्कूल पीतमपुरा के 9वीं कक्षा के छात्र <b>रेयांश गुप्ता</b> ने एक ऐसा व्याख्यात्मक और सुरक्षित AI विकसित करने की ठानी जिस पर किसान आंख मूंदकर नहीं, बल्कि समझकर भरोसा कर सकें।" if is_hi else "Seeing how sudden crop diseases cause severe financial hardship for smallholder farmers across India, <b>Reyaansh Gupta</b>, a Class 9 student at <b>Apeejay School Pitampura</b>, set out to build an accessible, explainable AI disease detector that farmers could genuinely trust."}
                    </p>
                    <p style="color: var(--ink-secondary); font-size: 0.92rem; line-height: 1.6; margin: 0;">
                        {"प्रयोगशाला के सीमित परिणामों से आगे बढ़कर, रेयांश ने वास्तविक खेतों की तस्वीरों पर मॉडल को पुनः प्रशिक्षित किया (90.3% फील्ड F1 स्कोर), ग्रैड-सीएएम हीटमैप जोड़े, कंप्यूटर विज़न द्वारा स्वचालित रोग गंभीरता (% Severity Lab, R²=0.81) मापी, और द्विभाषी ICAR केवीके सलाह को जोड़ा।" if is_hi else "Rather than accepting black-box predictions that fail outdoors, Reyaansh retrained a lightweight MobileNetV3 backbone on real field imagery—achieving a <b>90.3% validation F1 score</b>—and integrated <b>Grad-CAM visual attention heatmaps</b> so farmers can see exactly which leaf spots guided the diagnosis. He also engineered automated <b>disease severity estimation (R²=0.81)</b> and bilingual guidance directly linked to ICAR Krishi Vigyan Kendras."}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
