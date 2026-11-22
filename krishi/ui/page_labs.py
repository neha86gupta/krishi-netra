"""Labs Page: Krishi Netra Future Scope and R&D Roadmap.
Briefly explains next-generation capabilities without running experimental unvalidated demos."""
from __future__ import annotations

import streamlit as st

from krishi.i18n import t
from krishi.ui.components import hero
from krishi.ui.services import lang


def render() -> None:
    is_hi = lang() == "hi"

    title = "प्रयोगशाला एवं आगामी नवाचार" if is_hi else "Krishi Netra Labs & R&D Roadmap"
    subtitle = (
        "भविष्य की उन्नत तकनीकें और आगामी चरण (नवाचार अवलोकन)"
        if is_hi
        else "What we are engineering next to empower smallholder Indian agriculture"
    )
    hero(title, subtitle)

    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid var(--line); border-radius: 16px; padding: 1.3rem 1.5rem; margin-bottom: 1.4rem; box-shadow: 0 2px 10px rgba(20,83,45,0.06);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; flex-wrap:wrap; gap:8px;">
                <span class="chip" style="background: rgba(34,197,94,0.15); color: var(--forest); font-weight:700;">🌱 {"आगामी इंजीनियरिंग चरण" if is_hi else "Active R&D Pipeline"}</span>
                <span style="font-size:0.85rem; color:var(--muted);">{"संस्करण 2.5 और 3.0 योजनाएं" if is_hi else "V2.5 & V3.0 Engineering Scope"}</span>
            </div>
            <p style="margin:0; font-size:0.95rem; line-height:1.6; color:var(--ink);">
                {"कृषि नेत्र संस्करण 2 में फील्ड-ट्रेनिंग, ग्रैड-सीएएम हीटमैप और द्वैभाषिक पहुंच सफलतापूर्वक लागू हो चुकी है। अब हमारी प्रयोगशाला निम्नलिखित 6 प्रमुख क्षेत्रों में मॉडल को खेत-तैयार, स्वचालित और हर किसान के लिए सुलभ बनाने पर काम कर रही है:" if is_hi else "With Version 2 deployed for mobile field inference, explainable Grad-CAM heatmaps, and bilingual accessibility, our lab research is actively advancing these 6 architectural milestones:"}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid var(--emerald); min-height: 185px;">
                <span class="chip" style="background: #dcfce7; color: #15803d; font-weight: 700;">{"चरण 1 · सक्रिय कार्य" if is_hi else "Phase 1 · Active R&D"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">🔬 {"स्वचालित रोग गंभीरता प्रतिशत (Severity % Lab)" if is_hi else "Automated Severity % Estimation"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"कंप्यूटर विज़न कंटूर मास्किंग और HSV कलर सेग्मेंटेशन द्वारा पत्ती के कुल क्षेत्रफल में से संक्रमित भाग का सटीक प्रतिशत निकालना, ताकि दवा का उचित और संतुलित छिड़काव तय हो सके।" if is_hi else "Computer vision contour masking and adaptive color thresholding to quantify exact percentage of diseased leaf surface area, helping optimize targeted pesticide spray volume."}
                </p>
                <div style="font-size: 0.78rem; color: var(--forest); font-weight: 600;">🎯 {"लक्ष्य: रसायनों के अत्यधिक उपयोग को रोकना" if is_hi else "Target: Prevent chemical over-application & runoff"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #0284c7; min-height: 185px;">
                <span class="chip" style="background: #e0f2fe; color: #0369a1; font-weight: 700;">{"चरण 2 · आगामी" if is_hi else "Phase 2 · Planned"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">🌦️ {"सूक्ष्म-मौसम प्रकोप चेतावनी (Weather-Risk Engine)" if is_hi else "Micro-Climate Outbreak Forecasting"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"स्थानीय आईएमडी (IMD) मौसम पूर्वानुमान, तापमान, और सापेक्ष आर्द्रता के आधार पर कवक और जीवाणु संक्रमण के फैलाव की 48 घंटे पूर्व चेतावनी प्रणाली।" if is_hi else "Integrating hyper-local agro-meteorological telemetry (temperature, relative humidity, and rainfall duration) to compute early fungal spore germination risk indices."}
                </p>
                <div style="font-size: 0.78rem; color: #0284c7; font-weight: 600;">🎯 {"लक्ष्य: संक्रमण फैलने से पहले चेतावनी" if is_hi else "Target: 48-hour preventative alert before spore spread"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #8b5cf6; min-height: 185px;">
                <span class="chip" style="background: #ede9fe; color: #6d28d9; font-weight: 700;">{"चरण 2 · आगामी" if is_hi else "Phase 2 · Planned"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">📦 {"मल्टी-लीफ बैच स्कैनर (Batch Scanner)" if is_hi else "Multi-Leaf Batch Scanning"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"एक साथ 5–10 पत्तियों की तस्वीरें अपलोड करके पूरे खेत का औसत स्वास्थ्य स्कोर और प्रभावित पौधों का अनुपात निकालना।" if is_hi else "Batch ingestion pipeline supporting 5–10 leaf photographs simultaneously to compute a farm-wide crop health index and pathogen strain distribution."}
                </p>
                <div style="font-size: 0.78rem; color: #8b5cf6; font-weight: 600;">🎯 {"लक्ष्य: खेत स्तर पर व्यापक निगरानी" if is_hi else "Target: Representative field-scale surveillance"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #ea580c; min-height: 185px;">
                <span class="chip" style="background: #ffedd5; color: #c2410c; font-weight: 700;">{"चरण 1 · सक्रिय कार्य" if is_hi else "Phase 1 · Active R&D"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">📱 {"ऑफलाइन एज-एआई मोबाइल इंजन (Offline Edge AI)" if is_hi else "On-Device Offline Edge TFLite"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"बिना इंटरनेट वाले दूरदराज के गांवों के लिए मोबाइलनेटवी3 को TFLite INT8 में बदलना ताकि बिना नेटवर्क के 0.2 सेकंड में फोन पर ही त्वरित परिणाम मिले।" if is_hi else "INT8 quantization of MobileNetV3 into a lightweight (<15MB) TFLite runtime for low-cost Android smartphones with zero internet connectivity."}
                </p>
                <div style="font-size: 0.78rem; color: #ea580c; font-weight: 600;">🎯 {"लक्ष्य: इंटरनेट के बिना शून्य-डेटा निदान" if is_hi else "Target: Zero-data offline inference in remote villages"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #059669; min-height: 185px;">
                <span class="chip" style="background: #d1fae5; color: #047857; font-weight: 700;">{"चरण 3 · शोध" if is_hi else "Phase 3 · Research"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">🚁 {"ड्रोन एरियल कैनोपी सर्विलांस (Drone Surveillance)" if is_hi else "Drone Aerial Canopy Mapping"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"बड़े बागानों और खेतों में कम ऊंचाई वाले ड्रोन कैमरों से ली गई हवाई तस्वीरों से प्रभावित क्षेत्रों का जीपीएस आधारित हीटमैप तैयार करना।" if is_hi else "Automated low-altitude RGB and multispectral drone footage processing to generate georeferenced disease hotspot maps across commercial plantations."}
                </p>
                <div style="font-size: 0.78rem; color: #059669; font-weight: 600;">🎯 {"लक्ष्य: बड़े बागानों की स्वचालित मैपिंग" if is_hi else "Target: GPS-tagged canopy lesion hotspot maps"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #d97706; min-height: 185px;">
                <span class="chip" style="background: #fef3c7; color: #b45309; font-weight: 700;">{"चरण 2 · आगामी" if is_hi else "Phase 2 · Planned"}</span>
                <div class="big" style="font-size: 1.2rem; margin: 0.4rem 0 0.2rem 0;">🗣️ {"क्षेत्रीय भाषा वॉयस असिस्टेंट (Voice Advisory)" if is_hi else "Multilingual Voice Advisory"}</div>
                <p style="font-size: 0.88rem; color: var(--muted); margin-bottom: 0.6rem; line-height: 1.5;">
                    {"पंजाबी, मराठी, तेलुगु, तमिल और बंगाली में ध्वनि संदेश और बोलकर सवाल पूछने की सुविधा, ताकि किसान बिना टाइप किए ऑडियो मार्गदर्शन पा सकें।" if is_hi else "Speech-to-text input and spoken audio guidance in Punjabi, Marathi, Telugu, Tamil, and Bengali to empower non-literate and regional-language farmers."}
                </p>
                <div style="font-size: 0.78rem; color: #d97706; font-weight: 600;">🎯 {"लक्ष्य: साक्षरता की बाधा को दूर करना" if is_hi else "Target: Screenless, voice-first accessibility"}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "💡 "
        + (
            "ये शोध मॉड्यूल खेत स्तर पर वैज्ञानिक रूप से सत्यापित होने के बाद ही मुख्य निदान प्रणाली में शामिल किए जाएंगे। वर्तमान में मुख्य मॉडल 38 पादप रोगों पर 90.3% फील्ड सटीकता प्रदान करता है।"
            if is_hi
            else "These R&D capabilities will be integrated into the primary inference engine upon rigorous agricultural validation. The current production engine supports 38 crop disease classes with 90.3% field validation accuracy."
        )
    )
