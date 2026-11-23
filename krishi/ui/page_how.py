"""How It Works Page: Operational Pipeline, Quality Gating, Grad-CAM & Design Contrast.
Matches the official Krishi Netra website 'How It Works' section."""
from __future__ import annotations

import streamlit as st

from krishi.ui.components import card, hero
from krishi.ui.services import lang


def render() -> None:
    is_hi = lang() == "hi"

    title = "कृषि नेत्र की कार्यप्रणाली" if is_hi else "How Krishi Netra Works"
    subtitle = (
        "तस्वीर खींचने से लेकर ग्रैड-सीएएम हीटमैप और ICAR सलाह तक: 4-चरणीय पारदर्शी निदान पाइपलाइन"
        if is_hi
        else "From capture to OpenCV quality gating, calibrated safety abstention, Grad-CAM visual heatmaps, and ICAR advisory"
    )
    hero(title, subtitle)

    # 1. 4-Stage Pipeline Cards
    st.markdown(
        f"""
        <div style="margin-bottom: 0.8rem;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em;">
                {"चरणबद्ध प्रक्रिया" if is_hi else "Operational Architecture"}
            </div>
            <div class="big" style="font-size: 1.45rem; margin-top: 0.2rem;">
                {"4-चरणीय पारदर्शी निदान पाइपलाइन" if is_hi else "The 4-Stage Transparent Diagnosis Pipeline"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        st.markdown(
            f"""
            <div class="card" style="min-height: 240px; border-top: 4px solid var(--green-600);">
                <span class="badge badge-green">{"चरण 1 · इनपुट" if is_hi else "Stage 1 · Capture"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"पत्ती की तस्वीर" if is_hi else "Photograph Leaf"}</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); line-height: 1.5; margin: 0;">
                    {"प्राकृतिक धूप में एक पत्ती की साफ़ तस्वीर लें। फ्रेम का 70% भाग पत्ती से ढका होना चाहिए ताकि लक्षण स्पष्ट दिखें।" if is_hi else "Capture a single leaf in natural diffuse daylight. Fill ~70% of frame for clearest visual symptom resolution."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="card" style="min-height: 240px; border-top: 4px solid #0284c7;">
                <span class="badge badge-sky">{"चरण 2 · गुणवत्ता जांच" if is_hi else "Stage 2 · OpenCV Quality"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"प्री-चेक सुरक्षा" if is_hi else "Pre-Inference Gating"}</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); line-height: 1.5; margin: 0;">
                    {"मॉडल चलाने से पहले लाप्लासियन ब्लर, सूर्य की तेज़ चमक (ग्लैयर) और पत्ती की स्थिति जांची जाती है। धुंधली फोटो पर तुरंत पुनः फोटो लेने का सुझाव मिलता है।" if is_hi else "Lightweight OpenCV filters verify optical blur (Laplacian), specular sunlight glare, and framing before invoking the neural network."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="card" style="min-height: 240px; border-top: 4px solid #b45309;">
                <span class="badge badge-amber">{"चरण 3 · 3-गेट जांच" if is_hi else "Stage 3 · 3-Gate Safety"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"कैलिब्रेटेड निर्णय" if is_hi else "Calibrated Abstention"}</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); line-height: 1.5; margin: 0;">
                    {"तापमान स्केलिंग (T=1.47), शैनन एन्ट्रॉपी (H) और 576-d क्लास सेंट्रोइड दूरी अनिश्चित पत्तियों पर 'Not Sure' घोषित करती हैं।" if is_hi else "Temperature scaling (T=1.47), Shannon entropy, and 576-d centroid cosine similarity intercept ambiguous leaves safely."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="card" style="min-height: 240px; border-top: 4px solid #15803d;">
                <span class="badge badge-green">{"चरण 4 · आउटपुट" if is_hi else "Stage 4 · Verification"}</span>
                <div class="big" style="font-size: 1.15rem; margin: 0.4rem 0 0.2rem 0;">{"हीटमैप व सलाह" if is_hi else "Grad-CAM & ICAR"}</div>
                <p style="font-size: 0.86rem; color: var(--ink-secondary); line-height: 1.5; margin: 0;">
                    {"ग्रैड-सीएएम हीटमैप दिखाता है कि AI ने कहाँ देखा, रोग गंभीरता (% Severity) मापी जाती है, और ICAR-KVK वैज्ञानिक प्रबंधन सलाह मिलती है।" if is_hi else "Pixel-level Grad-CAM heatmap overlays prove attention focus, severity % is quantified, and ICAR-KVK guidance is provided."}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 2. Farmer Field Photography Guide (Do's and Don'ts)
    st.markdown(
        f"""
        <div style="margin: 1.2rem 0 0.8rem 0;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em;">
                {"किसानों के लिए व्यावहारिक सुझाव" if is_hi else "Practical Field Guide for Farmers"}
            </div>
            <div class="big" style="font-size: 1.45rem; margin-top: 0.2rem;">
                {"सर्वोत्तम परिणाम के लिए पत्ती की फोटो कैसे खींचें" if is_hi else "How to Photograph a Leaf for Best Results"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    g1, g2 = st.columns(2, gap="medium")
    with g1:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #22c55e; background: #ffffff;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 700; color: #15803d; margin-bottom: 0.6rem;">
                    ✅ {"क्या करें (सुझाए गए तरीके)" if is_hi else "Do's (Recommended Practice)"}
                </div>
                <ul style="margin: 0; padding-left: 1.2rem; display: grid; gap: 0.55rem; color: var(--ink-secondary); font-size: 0.89rem; line-height: 1.5;">
                    <li><b>{"सुबह या शाम की धूप" if is_hi else "Diffuse Natural Daylight"}:</b> {"तेज़ दोपहर की चमक के बिना सुबह या शाम का प्रकाश पत्ती के रोगों को सबसे साफ़ दिखाता है।" if is_hi else "Early morning or late afternoon natural light prevents harsh glare on leaf surfaces."}</li>
                    <li><b>{"एकल पत्ती पर ध्यान" if is_hi else "Single Leaf Focus"}:</b> {"फ्रेम के 70% भाग में केवल एक पत्ती रखें जिसमें रोग के लक्षण साफ़ दिख रहे हों।" if is_hi else "Fill ~70% of the frame with one diseased leaf showing visible lesions clearly."}</li>
                    <li><b>{"स्थिर दूरी (15–20 सेमी)" if is_hi else "Steady Distance (15–20 cm)"}:</b> {"फोन को 15-20 सेमी दूर स्थिर रखें और स्क्रीन पर टैप करके फोकस लॉक करें।" if is_hi else "Hold phone 15–20 cm away and tap screen to lock focus directly on the lesion."}</li>
                    <li><b>{"समतल कोण" if is_hi else "Flat Surface Angle"}:</b> {"कैमरा पत्ती की सतह के समानांतर रखें ताकि कवक के छल्ले साफ़ दिखें।" if is_hi else "Keep camera parallel to the leaf surface to reveal concentric fungal rings cleanly."}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with g2:
        st.markdown(
            f"""
            <div class="card" style="border-left: 5px solid #ef4444; background: #ffffff;">
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 700; color: #b91c1c; margin-bottom: 0.6rem;">
                    ❌ {"क्या न करें (इनसे बचें)" if is_hi else "Don'ts (Avoid These)"}
                </div>
                <ul style="margin: 0; padding-left: 1.2rem; display: grid; gap: 0.55rem; color: var(--ink-secondary); font-size: 0.89rem; line-height: 1.5;">
                    <li><b>{"रात में कैमरा फ्लैश" if is_hi else "Direct Flash Photography"}:</b> {"एलईडी फ्लैश से पत्ती पर चमकदार सफेद धब्बे बनते हैं जो बीमारी के धब्बों को छुपा देते हैं।" if is_hi else "LED flash causes specular reflections that wash out subtle fungal lesions."}</li>
                    <li><b>{"पत्तियों का गुच्छा या पूरा पौधा" if is_hi else "Cluttered Plant Clusters"}:</b> {"पूरे पौधे या कई पत्तियों को एक साथ न खींचें; केवल एक पत्ती चुनें।" if is_hi else "Avoid photographing tangled multi-leaf bushes or whole crop canopies."}</li>
                    <li><b>{"हवा में हिलती पत्ती" if is_hi else "Wind Motion Blur"}:</b> {"तेज हवा में हिलती पत्ती की फोटो न लें; हवा थमने का इंतज़ार करें।" if is_hi else "Do not shoot swaying leaves; motion blur destroys high-frequency lesion textures."}</li>
                    <li><b>{"हाथ या मिट्टी से ढकना" if is_hi else "Finger or Mud Obstruction"}:</b> {"उंगलियों या मिट्टी से बीमारी वाले भाग को न ढकें।" if is_hi else "Avoid covering the diseased leaf area with fingers, shadows, or fresh mud."}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # 3. Design Contrast: Krishi Netra vs Black-Box Apps
    st.markdown(
        f"""
        <div style="margin: 1.2rem 0 0.8rem 0;">
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--green-700); text-transform: uppercase; letter-spacing: 0.05em;">
                {"डिज़ाइन तुलना" if is_hi else "Design Contrast"}
            </div>
            <div class="big" style="font-size: 1.45rem; margin-top: 0.2rem;">
                {"कृषि नेत्र और साधारण ब्लैक-बॉक्स ऐप्स में अंतर" if is_hi else "How Krishi Netra Differs from Typical Black-Box Demos"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    contrast_data = [
        (
            "अस्पष्ट / धुंधली तस्वीरें" if is_hi else "Ambiguous / Blurry Photos",
            "कम निश्चितता पर भी किसी एक बीमारी का जबरन नाम देना" if is_hi else "Forces a top-1 disease guess even at low certainty",
            "कैलिब्रेटेड 3-गेट सुरक्षा तुरंत 'Not Sure' घोषित करती है" if is_hi else "3-Gate calibrated abstention returns an honest 'Not Sure' prompt",
        ),
        (
            "दृश्य सत्यापन (Explainability)" if is_hi else "Visual Verification",
            "बिना किसी कारण के केवल नाम की पर्ची थमा देना" if is_hi else "Opaque class label with zero spatial reasoning",
            "ग्रैड-सीएएम हीटमैप दिखाता है कि AI ने पत्ती को देखा या मिट्टी को" if is_hi else "Grad-CAM heatmap exposes whether leaf lesion or soil drove the score",
        ),
        (
            "फसल उपचार सलाह" if is_hi else "Care Recommendations",
            "व्यावसायिक कीटनाशक कंपनियों के उत्पाद बेचने का दबाव" if is_hi else "Directs diagnoses to agrochemical marketplace product sales",
            "ICAR-KVK वैज्ञानिक प्रमाणित गैर-व्यावसायिक सांस्कृतिक मार्गदर्शन" if is_hi else "Unbiased, static ICAR-KVK cultural guidance with zero sales incentive",
        ),
        (
            "सटीकता रिपोर्टिंग" if is_hi else "Performance Reporting",
            "केवल प्रयोगशाला के 95%+ आंकड़ों का दावा करना" if is_hi else "Reports only 95%+ lab validation numbers",
            "95.8% लैब सटीकता और 90.3% वास्तविक खेत F1-स्कोर दोनों पारदर्शी रूप से प्रस्तुत" if is_hi else "Reports 95.8% lab precision and 90.3% outdoor field F1 side by side",
        ),
        (
            "रोग गंभीरता मापन" if is_hi else "Severity Quantification",
            "कोई माप नहीं या अप्रमाणित अनुमान" if is_hi else "Unmeasured or arbitrary severity labels",
            "कॉर्नेल लीफ डॉक्टर प्रोटोकॉल से सत्यापित CV HSV (% Severity, R²=0.81)" if is_hi else "Validated CV HSV segmentation against Cornell Leaf Doctor (R²=0.81, MAE=5.8%)",
        ),
    ]

    contrast_rows = "".join(
        f"""<tr>
            <td style="padding: 10px 14px; font-weight: 600; border-bottom: 1px solid var(--border-light);">{c[0]}</td>
            <td style="padding: 10px 14px; color: #b91c1c; border-bottom: 1px solid var(--border-light); background: #fef2f2;">{c[1]}</td>
            <td style="padding: 10px 14px; color: #15803d; font-weight: 600; border-bottom: 1px solid var(--border-light); background: #f0fdf4;">{c[2]}</td>
        </tr>"""
        for c in contrast_data
    )

    st.markdown(
        f"""
        <div class="card" style="padding: 0; overflow: hidden; border: 1px solid var(--border-med);">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                <thead>
                    <tr style="background: var(--surface-alt); text-align: left;">
                        <th style="padding: 12px 14px; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; color: var(--green-950);">{"क्षमता / आयाम" if is_hi else "Capability / Dimension"}</th>
                        <th style="padding: 12px 14px; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; color: #b91c1c;">{"साधारण ब्लैक-बॉक्स ऐप्स" if is_hi else "Typical Black-Box Leaf Classifier"}</th>
                        <th style="padding: 12px 14px; font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; color: #15803d;">{"कृषि नेत्र का पारदर्शी दृष्टिकोण" if is_hi else "Krishi Netra Safety-First Approach"}</th>
                    </tr>
                </thead>
                <tbody>
                    {contrast_rows}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
