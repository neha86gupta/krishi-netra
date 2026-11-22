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
from krishi.imaging import ImageError, make_thumbnail, sha256, validate_upload
from krishi.knowledge import get_info, pretty
from krishi.report_pdf import build_report
from krishi.ui.components import badge, bar, card, disease_details, hero, kvk_block
from krishi.ui.services import get_predictor, get_store, kb, lang, owner_id

STATE = "diag_state"


def render() -> None:
    hero(t("app_name"), t("tagline"))
    st.markdown(
        f'<div class="steps"><div class="step"><b>1</b>{esc(t("s1"))}</div><div class="step"><b>2</b>{esc(t("s2"))}</div>'
        f'<div class="step"><b>3</b>{esc(t("s3"))}</div></div>',
        unsafe_allow_html=True,
    )
    predictor, err = get_predictor()
    if predictor is None:
        st.error(t("model_missing"))
        st.caption(t("model_missing_help"))
        st.code(err or "unknown error")
        return

    # Photography Best Practices Guide (Moved to Diagnose tab)
    is_hi = lang() == "hi"
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

    mode = st.radio(
        "input",
        ["upload", "camera"],
        horizontal=True,
        label_visibility="collapsed",
        key="input_mode",
        format_func=lambda m, _L=lang(): t("mode_upload" if m == "upload" else "mode_camera", _L),
    )
    f = (
        st.file_uploader(t("upload_label", mb=C.MAX_UPLOAD_MB), type=list(C.ALLOWED_EXT))
        if mode == "upload"
        else st.camera_input(t("camera_label"))
    )
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
        left, right = st.columns([1, 1.2], gap="large")
        left.image(img, caption=t("preview"), use_container_width=True)
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
    category = ""
    if not diag.is_uncertain:
        category = badge("healthy", t("healthy")) if diag.healthy else badge("diseased", t("attention"))
    status_badge = badge(diag.status, t(f"st_{diag.status}"))
    if diag.is_uncertain:
        head, sub = (
            esc(t("not_sure_head")),
            f'{esc(t("best_guess"))}: {esc(pretty(diag.crop))} · {esc(pretty(diag.condition))}',
        )
    else:
        head, sub = esc(pretty(diag.condition)), f'🌱 {esc(t("crop"))}: {esc(pretty(diag.crop))}'
    interp = t("interp_" + {"uncertain": "low"}.get(diag.status, diag.status))
    rows = "".join(
        f'<div class="row"><span>{esc(pretty(r["crop"]))} · {esc(pretty(r["condition"]))}</span><b>{r["prob"]:.0%}</b></div>{bar(r["prob"])}'
        for r in diag.topk[:3]
    )
    card(
        f'{category} {status_badge}<div class="big">{head}</div><div class="sub">{sub}</div>'
        f'<div class="row"><b>{esc(t("confidence"))}</b><b>{diag.confidence:.0%}</b></div>{bar(diag.confidence)}'
        f'<div class="small">{esc(interp)}</div><div class="small" style="margin-top:.3rem">{esc(t("interp_note"))}</div>'
        f'<div class="small" style="margin-top:.8rem"><b>{esc(t("top3"))}</b></div>{rows}',
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
    st.caption(t("cam_explain"))
    if len(items) < 3:
        st.caption(t("cam_no_heatmap"))
