"""Diagnose page. One inference per click; results live in session_state so Streamlit
reruns never repeat inference or database writes."""
from __future__ import annotations

from html import escape as esc

import streamlit as st

from krishi import config as C
from krishi.config import log
from krishi.diagnosis import Diagnosis, DiagnosisError, run_diagnosis
from krishi.gradcam import views
from krishi.i18n import t
from krishi.imaging import ImageError, make_thumbnail, sha256, validate_upload, check_quality
from krishi.knowledge import get_info, pretty
from krishi.report_pdf import build_report
from krishi.ui.components import badge, bar, card, disease_details, hero, kvk_block
from krishi.ui.services import get_predictor, get_store, kb, lang, owner_id

STATE = "diag_state"


def render() -> None:
    is_hi = lang() == "hi"
    hero(t("app_name"), t("tagline"))

    # 1. 3-Step Horizontal Workflow Ribbon wrapped in a box matching user design specifications
    workflow_heading = esc(t("guide_workflow"))
    badge_label = "3-Step Diagnosis" if not is_hi else "3-चरणीय जाँच"
    s1_title = esc(t("step_1_title"))
    s1_desc = esc(t("step_1_desc"))
    s2_title = esc(t("step_2_title"))
    s2_desc = esc(t("step_2_desc"))
    s3_title = esc(t("step_3_title"))
    s3_desc = esc(t("step_3_desc"))

    steps_html = (
        '<div class="workflow-box">'
        '<div class="workflow-box-header">'
        f'<span class="workflow-box-title">📋 {workflow_heading}</span>'
        f'<span class="chip" style="background:#dcfce7; color:#15803d; font-size:0.75rem; font-weight:700; margin:0;">{badge_label}</span>'
        '</div>'
        '<div class="workflow-steps-wrap">'
        '<div class="workflow-step-card">'
        '<div class="workflow-step-header">'
        '<span class="workflow-step-num">1</span>'
        '<span class="workflow-step-icon">📷</span>'
        '</div>'
        f'<div class="workflow-step-title">{s1_title}</div>'
        f'<div class="workflow-step-desc">{s1_desc}</div>'
        '</div>'
        '<div class="workflow-step-arrow">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>'
        '</svg>'
        '</div>'
        '<div class="workflow-step-card">'
        '<div class="workflow-step-header">'
        '<span class="workflow-step-num">2</span>'
        '<span class="workflow-step-icon">☁️</span>'
        '</div>'
        f'<div class="workflow-step-title">{s2_title}</div>'
        f'<div class="workflow-step-desc">{s2_desc}</div>'
        '</div>'
        '<div class="workflow-step-arrow">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>'
        '</svg>'
        '</div>'
        '<div class="workflow-step-card">'
        '<div class="workflow-step-header">'
        '<span class="workflow-step-num">3</span>'
        '<span class="workflow-step-icon">✨</span>'
        '</div>'
        f'<div class="workflow-step-title">{s3_title}</div>'
        f'<div class="workflow-step-desc">{s3_desc}</div>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(steps_html, unsafe_allow_html=True)

    predictor, err = get_predictor()
    if predictor is None:
        st.error(t("model_missing"))
        st.caption(t("model_missing_help"))
        st.code(err or "unknown error")
        return

    # Photography Best Practices Guide (Card matching the steps styling)
    tips_title = "📸 फोटो लेने के महत्वपूर्ण सुझाव (Photo Tips for Best Accuracy)" if is_hi else "📸 Photography Best Practices for AI Leaf Diagnosis"
    dos_title = "✅ सही तरीका (Do's)" if is_hi else "✅ Recommended (Do's)"
    donts_title = "❌ इनसे बचें (Don'ts)" if is_hi else "❌ What to Avoid (Don'ts)"
    
    do_1 = "एक ही पत्ती को फ्रेम के केंद्र में रखें (70%+ भरें)" if is_hi else "Frame a single leaf blade filling >70% of view"
    do_2 = "साफ़, प्राकृतिक दिन की रोशनी का प्रयोग करें" if is_hi else "Use even, natural daylight without harsh shadows"
    do_3 = "15–20 सेमी दूरी से स्पष्ट, स्थिर फोकस रखें" if is_hi else "Hold camera steady 15–20 cm away for crisp focus"
    
    dont_1 = "धुंधली, हिलती हुई या कम रोशनी वाली तस्वीरें" if is_hi else "Blurry, shaky, or underexposed photographs"
    dont_2 = "पृष्ठभूमि में मिट्टी, हाथ या कई पत्तियों का बिखराव" if is_hi else "Cluttered soil background, fingers, or overlap"
    dont_3 = "सीधी धूप की तेज चमक (Glare) से बचें" if is_hi else "Avoid harsh midday glare washing out leaf colors"

    photo_guide_html = f"""
    <div class="card photo-tips-card" style="border-left: 5px solid var(--emerald); background: #ffffff; padding: 1rem 1.25rem; margin-bottom: 1.1rem; border-radius: 14px; box-shadow: 0 2px 8px rgba(20,83,45,0.06);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.6rem; flex-wrap:wrap; gap:6px;">
        <span style="font-weight:700; font-size:1.02rem; color:var(--forest);">{tips_title}</span>
        <span class="chip" style="background:#dcfce7; color:#15803d; font-size:0.75rem; font-weight:700;">AI Optimized</span>
      </div>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; font-size: 0.88rem; line-height: 1.5; color: var(--ink);">
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 0.65rem 0.85rem;">
          <b style="color: #15803d;">{dos_title}</b>
          <ul style="margin: 0.35rem 0 0 1.1rem; padding: 0;">
            <li>{do_1}</li>
            <li>{do_2}</li>
            <li>{do_3}</li>
          </ul>
        </div>
        <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 0.65rem 0.85rem;">
          <b style="color: #b91c1c;">{donts_title}</b>
          <ul style="margin: 0.35rem 0 0 1.1rem; padding: 0;">
            <li>{dont_1}</li>
            <li>{dont_2}</li>
            <li>{dont_3}</li>
          </ul>
        </div>
      </div>
    </div>
    """
    st.markdown(photo_guide_html, unsafe_allow_html=True)

    # 2. Consolidated Unified Upload / Camera Box
    st.markdown('<div class="unified-upload-container">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; flex-wrap:wrap; gap:8px;">'
        f'  <span style="font-weight:700; font-size:1.02rem; color:#1B4332;">🌿 {"पत्ती तस्वीर इनपुट (Upload or Camera)" if is_hi else "Leaf Photo Input (Upload or Camera)"}</span>'
        f'  <span style="font-size:0.80rem; color:#5e7862; background:#f0fdf4; padding:3px 8px; border-radius:6px; border:1px solid #bbf7d0;">JPG, PNG (Max {C.MAX_UPLOAD_MB} MB)</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    mode = st.radio(
        "input",
        ["upload", "camera"],
        horizontal=True,
        label_visibility="collapsed",
        key="input_mode",
        format_func=lambda m: t("upload_tab_file") if m == "upload" else t("upload_tab_cam"),
    )
    if mode == "upload":
        f = st.file_uploader(
            t("upload_label", mb=C.MAX_UPLOAD_MB),
            type=list(C.ALLOWED_EXT),
            label_visibility="collapsed",
            key="file_uploader_diag",
        )
    else:
        f = st.camera_input(
            t("camera_label"),
            label_visibility="collapsed",
            key="camera_input_diag",
        )
    st.markdown("</div>", unsafe_allow_html=True)
    if f is None:
        st.session_state.pop(STATE, None)
        return

    data, name = f.getvalue(), getattr(f, "name", "camera.jpg")
    try:
        img = validate_upload(data, name)
    except ImageError as exc:
        st.error(t(exc.key, **(exc.params or {})))
        return
    digest = sha256(data)
    state = st.session_state.get(STATE)
    if state and state["hash"] != digest:  # a different photo was chosen
        state = None

    if state is None:
        q = check_quality(img)
        left, right = st.columns([1, 1.2], gap="large")
        left.image(img, caption=t("preview"), use_container_width=True)

        if q.is_ok:
            quality_html = f"""
            <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:12px 14px; margin-bottom:14px;">
              <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#15803d; font-size:0.92rem;">
                <span>✅ Pre-Scan Quality Check: Passed</span>
              </div>
              <p style="margin:4px 0 0; font-size:0.83rem; color:#166534;">
                Sharp focus (variance {q.blur_score:.0f}), balanced natural lighting, and well-framed leaf tissue ({q.leaf_fill_pct:.1f}% fill).
              </p>
            </div>
            """
        elif q.status == "warn":
            warning_bullets = "".join(f"<li>{esc(w)}</li>" for w in q.warnings)
            quality_html = f"""
            <div style="background:#fffbeb; border:1px solid #fcd34d; border-radius:10px; padding:12px 14px; margin-bottom:14px;">
              <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#b45309; font-size:0.92rem;">
                <span>⚠️ Pre-Scan Quality Advisory</span>
              </div>
              <ul style="margin:6px 0 0; padding-left:18px; font-size:0.83rem; color:#92400e; line-height:1.4;">
                {warning_bullets}
              </ul>
              <p style="margin:6px 0 0; font-size:0.8rem; color:#b45309; font-style:italic;">
                Tip: You may still proceed with analysis, but retaking for optimal sharpness gives highest accuracy.
              </p>
            </div>
            """
        else:
            warning_bullets = "".join(f"<li>{esc(w)}</li>" for w in q.warnings)
            quality_html = f"""
            <div style="background:#fef2f2; border:1px solid #fca5a5; border-radius:10px; padding:12px 14px; margin-bottom:14px;">
              <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:#b91c1c; font-size:0.92rem;">
                <span>⛔ Poor Photo Quality Detected</span>
              </div>
              <ul style="margin:6px 0 0; padding-left:18px; font-size:0.83rem; color:#991b1b; line-height:1.4;">
                {warning_bullets}
              </ul>
              <p style="margin:6px 0 0; font-size:0.8rem; color:#b91c1c; font-weight:600;">
                Retake strongly recommended before analysis to prevent misdiagnosis.
              </p>
            </div>
            """
        right.markdown(quality_html, unsafe_allow_html=True)
        right.markdown(f'<div class="card accent">{esc(t("press_analyse"))}</div>', unsafe_allow_html=True)
        if right.button(t("analyse"), type="primary", key="analyse_btn"):
            with st.spinner(t("analysing")):
                try:
                    diag = run_diagnosis(predictor, img)
                except DiagnosisError:
                    st.error(t("analysis_failed"))
                    return
            st.session_state[STATE] = _store_result(diag, img, name, digest)
            st.rerun()  # redraw with the stored result; no second inference
        return
    _results(state)


def _store_result(diag: Diagnosis, img, name: str, digest: str) -> dict:
    thumb = make_thumbnail(img) if C.KEEP_THUMBNAILS else None
    rec_id = get_store().add(owner_id(), diag, name, digest, thumb)  # None => duplicate suppressed
    pdf = None
    try:
        pdf = build_report(diag, img, get_info(kb(), diag.cls, "en"))
    except Exception:  # noqa: BLE001
        log.exception("PDF build failed")
    return {"hash": digest, "diag": diag, "img": img, "pdf": pdf, "rec_id": rec_id}


def _results(state: dict) -> None:
    diag: Diagnosis = state["diag"]
    img = state["img"]
    left, right = st.columns([1, 1.2], gap="large")
    left.image(img, caption=t("preview"), use_container_width=True)
    with right:
        _result_card(diag)
        if diag.is_uncertain:
            st.warning("⚠️ " + t("low_msg" if diag.status == "low" else "unsure_msg"))
            if diag.reasons:
                st.write(f"{t('why')}: " + "; ".join(diag.reasons))
    tabs = st.tabs([t("tab_info"), t("tab_cam"), t("tab_report")])
    with tabs[0]:
        st.caption(t("ref"))
        if diag.is_uncertain:
            kvk_block()
        else:
            disease_details(get_info(kb(), diag.cls, lang()))
            st.warning(t("consult"))
            kvk_block()
    with tabs[1]:
        _cam_tab(diag, img)
    with tabs[2]:
        st.caption(t("report_help"))
        if state["pdf"]:
            st.download_button(
                t("report_download"),
                state["pdf"],
                file_name="krishi_netra_report.pdf",
                mime="application/pdf",
                key="pdf_dl",
            )
        else:
            st.error(t("report_failed"))


def _result_card(diag: Diagnosis) -> None:
    info = get_info(kb(), diag.cls, lang())
    status_badge = badge(diag.status, t(f"st_{diag.status}"))
    
    # 1. Top-Level Health Verdict Banner
    if diag.is_uncertain:
        v_box = (
            f'<div class="verdict-box uncertain">'
            f'<span class="verdict-icon">❓</span>'
            f'<div>'
            f'<div class="verdict-title uncertain">{esc(t("verdict_unsure_title"))}</div>'
            f'<div class="verdict-desc uncertain">{esc(t("verdict_unsure_desc"))}</div>'
            f'</div></div>'
        )
    elif diag.healthy:
        v_box = (
            f'<div class="verdict-box healthy">'
            f'<span class="verdict-icon">🌿</span>'
            f'<div>'
            f'<div class="verdict-title healthy">{esc(t("verdict_healthy_title"))}</div>'
            f'<div class="verdict-desc healthy">{esc(t("verdict_healthy_desc"))}</div>'
            f'</div></div>'
        )
    else:
        cond_name = pretty(diag.condition)
        crop_name = pretty(diag.crop)
        v_box = (
            f'<div class="verdict-box diseased">'
            f'<span class="verdict-icon">⚠️</span>'
            f'<div>'
            f'<div class="verdict-title diseased">{esc(t("verdict_diseased_title"))}</div>'
            f'<div class="verdict-desc diseased">{esc(t("verdict_diseased_desc", condition=cond_name, crop=crop_name))}</div>'
            f'</div></div>'
        )
    st.markdown(v_box, unsafe_allow_html=True)

    # 2. Plain-Language Layman Explanation
    if diag.healthy:
        meaning_text = (
            "पौधे की पत्ती का रंग और ऊतक पूरी तरह स्वस्थ है। इस पर फफूंद, झुलसा या किसी जीवाणु जनित रोग के कोई लक्षण नहीं हैं।"
            if lang() == "hi"
            else "The leaf exhibits healthy cellular structure and uniform chlorophyll pigmentation with no evidence of fungal blight, viral mottling, or bacterial lesions."
        )
        action_items = [t("safe_action_healthy_1"), t("safe_action_healthy_2"), t("safe_action_healthy_3")]
    elif diag.is_uncertain:
        meaning_text = (
            "AI मॉडल पूरे विश्वास के साथ स्थिति तय नहीं कर सका (संभावित कारण: कम रोशनी, पृष्ठभूमि में हाथ या मिट्टी, या धुंधला फोकस)।"
            if lang() == "hi"
            else "The AI model could not reach a confident diagnosis (possible causes: uneven lighting, cluttered background, or soft camera focus)."
        )
        action_items = [t("safe_action_unsure_1"), t("safe_action_unsure_2"), t("safe_action_unsure_3")]
    else:
        meaning_text = info.description or (
            f"{pretty(diag.crop)} में {pretty(diag.condition)} के लक्षण पाए गए हैं। यह पत्ती के प्रकाश संश्लेषण और फसल के स्वास्थ्य को प्रभावित कर सकता है।"
            if lang() == "hi"
            else f"Identified symptoms of {pretty(diag.condition)} on {pretty(diag.crop)}. This condition can impede photosynthesis and foliage health."
        )
        action_items = [t("safe_action_diseased_1"), t("safe_action_diseased_2"), t("safe_action_diseased_3"), t("safe_action_diseased_4")]

    action_html = "".join(f'<li style="margin-bottom:0.25rem;">{esc(act)}</li>' for act in action_items)
    interp = t("interp_" + {"uncertain": "low"}.get(diag.status, diag.status))
    rows = "".join(
        f'<div class="row"><span>{esc(pretty(r["crop"]))} · {esc(pretty(r["condition"]))}</span><b>{r["prob"]:.0%}</b></div>{bar(r["prob"])}'
        for r in diag.topk[:3]
    )

    val_tag = (
        '<span style="background:#dcfce7; color:#15803d; border:1px solid #86efac; border-radius:12px; padding:2px 8px; font-size:0.75rem; font-weight:700;">'
        '✅ Field-Tested (PlantDoc F1: 90.3%)</span>'
        if info.validation_level == "field_tested"
        else '<span style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; border-radius:12px; padding:2px 8px; font-size:0.75rem; font-weight:700;" title="Evaluated on PlantVillage held-out test set; field validation ongoing.">'
        '🔬 Lab-Validated Only</span>'
    )

    card(
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem; flex-wrap:wrap; gap:6px;">'
        f'  <span style="font-weight:700; color:var(--forest); font-size:1.15rem;">🌱 {esc(pretty(diag.crop))} · {esc(pretty(diag.condition))}</span>'
        f'  <div style="display:flex; gap:6px; align-items:center;">{val_tag} {status_badge}</div>'
        f'</div>'
        f'<div class="row"><b>{esc(t("confidence_level"))}</b><b>{diag.confidence:.0%}</b></div>{bar(diag.confidence)}'
        f'<div class="small" style="margin-bottom:0.75rem;">{esc(interp)}</div>'
        f'<hr style="border:0; border-top:1px solid var(--line); margin:0.75rem 0;" />'
        f'<div style="font-weight:700; color:var(--forest); font-size:0.95rem; margin-bottom:0.3rem;">📖 {esc(t("what_it_means"))}</div>'
        f'<div style="font-size:0.88rem; color:var(--ink); line-height:1.5; margin-bottom:0.75rem;">{esc(meaning_text)}</div>'
        f'<div style="font-weight:700; color:var(--forest); font-size:0.95rem; margin-bottom:0.3rem;">💡 {esc(t("immediate_steps"))}</div>'
        f'<ul style="font-size:0.86rem; color:var(--ink); line-height:1.45; margin:0 0 0.75rem 1.15rem; padding:0;">{action_html}</ul>'
        f'<hr style="border:0; border-top:1px solid var(--line); margin:0.75rem 0;" />'
        f'<div class="small" style="margin-bottom:0.4rem;"><b>{esc(t("top3"))}</b></div>{rows}',
        "accent",
    )


def _cam_tab(diag: Diagnosis, img) -> None:
    items = views(diag, img)
    if len(items) == 1:
        st.info(t("cam_unavailable"))
        return
    cols = st.columns(len(items))
    for col, (key, im) in zip(cols, items):
        col.image(im, caption=t(key), use_container_width=True)
    
    st.markdown(
        f"""
        <div class="card" style="border-left: 5px solid var(--emerald); background: #ffffff; padding: 1.15rem 1.35rem; margin-top: 1rem; border-radius: 14px; box-shadow: 0 2px 8px rgba(20,83,45,0.06);">
          <div style="font-weight: 700; font-size: 1.05rem; color: var(--forest); margin-bottom: 0.45rem;">
            {esc(t("cam_guide_title"))}
          </div>
          <p style="font-size: 0.9rem; line-height: 1.55; color: var(--ink); margin-bottom: 0.75rem;">
            {esc(t("cam_guide_intro"))}
          </p>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0.85rem;">
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 0.75rem 0.9rem;">
              <b style="color: #b91c1c;">{esc(t("cam_red_title"))}</b>
              <p style="margin: 0.3rem 0 0 0; color: #7f1d1d; font-size: 0.85rem;">{esc(t("cam_red_desc"))}</p>
            </div>
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 0.75rem 0.9rem;">
              <b style="color: #15803d;">{esc(t("cam_blue_title"))}</b>
              <p style="margin: 0.3rem 0 0 0; color: #14532d; font-size: 0.85rem;">{esc(t("cam_blue_desc"))}</p>
            </div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem 0.95rem; font-size: 0.88rem; line-height: 1.55;">
            <b style="color: var(--forest);">{esc(t("cam_verify_title"))}</b>
            <ul style="margin: 0.35rem 0 0 1.2rem; padding: 0;">
              <li style="margin-bottom: 0.35rem; color: #166534;">{esc(t("cam_verify_good"))}</li>
              <li style="color: #991b1b;">{esc(t("cam_verify_bad"))}</li>
            </ul>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if len(items) < 3:
        st.caption(t("cam_no_heatmap"))
