"""Demo & testing centre: real model predictions on held-out data with ground truth."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from krishi import config as C
from krishi.config import ROOT, split_class
from krishi.diagnosis import DiagnosisError, run_diagnosis
from krishi.i18n import t
from krishi.analytics import read_csv
from krishi.knowledge import pretty
from krishi.ui.components import hero, pct
from krishi.ui.services import get_predictor, lang


def _safe(rel: str) -> Path | None:
    """Resolve a CSV path inside the project root only (blocks ../ escapes)."""
    p = (ROOT / str(rel)).resolve()
    return p if p.is_file() and ROOT.resolve() in p.parents else None


@st.cache_data(show_spinner=False, max_entries=512)
def _predict(path: str, _P) -> dict:
    """Cached per image so reruns never repeat inference."""
    d = run_diagnosis(_P, Image.open(path).convert("RGB"), with_cam=False)
    return {"cls": d.cls, "conf": d.confidence, "status": d.status}


@st.cache_data(show_spinner=False, max_entries=64)
def _overlay(path: str, _P):
    return run_diagnosis(_P, Image.open(path).convert("RGB"), with_cam=True).cam_overlay


def _cam_button(P, path: Path, key: str) -> None:
    on = f"cam_{key}"
    if st.button(t("show_cam"), key=f"btn_{key}"):
        st.session_state[on] = True
    if st.session_state.get(on):
        try:
            ov = _overlay(str(path), P)
            st.image(ov, use_container_width=True) if ov is not None else st.caption(t("cam_unavailable"))
        except DiagnosisError:
            st.error(t("analysis_failed"))


def render() -> None:
    hero(t("nav_demo"), t("demo_sub"))
    P, err = get_predictor()
    if P is None:
        st.error(t("model_missing")); st.caption(t("model_missing_help")); st.code(err or "")
        return
    lab, field = st.tabs([t("demo_lab"), t("demo_field")])
    with lab:
        _lab(P)
    with field:
        _field(P)


def _lab(P) -> None:
    st.caption(t("demo_lab_cap"))
    df = read_csv(C.TEST_CSV)
    if df is None or not {"path", "label"} <= set(df.columns):
        st.info(t("missing_file", name="data/processed/test.csv")); return
    c1, c2, c3 = st.columns(3)
    crops = sorted({split_class(str(l))[0] for l in df["label"]})
    crop = c1.selectbox(t("filter_crop"), [None] + crops, format_func=lambda x, _L=lang(): t("all", _L) if x is None else pretty(x), key="lab_crop")
    pool = df if crop is None else df[df["label"].map(lambda l: split_class(str(l))[0] == crop)]
    labels = sorted(pool["label"].unique())
    label = c2.selectbox(t("disease"), [None] + labels, format_func=lambda x, _L=lang(): t("all", _L) if x is None else pretty(split_class(str(x))[1]), key="lab_label")
    if label is not None:
        pool = pool[pool["label"] == label]
    req = int(c3.number_input(t("sample_size"), 1, 24, 6))
    seed = st.session_state.setdefault("seed", 0)
    if st.button(t("redraw")):
        st.session_state.seed += 1; st.rerun()
    if pool.empty:
        st.info(t("no_samples")); return
    n = min(req, len(pool))
    if n < req:
        st.caption(t("fewer_samples", n=n, req=req))
    sample, missing, correct, shown = pool.sample(n, random_state=seed), 0, 0, 0
    cols = st.columns(3)
    for i, r in enumerate(sample.itertuples()):
        path = _safe(r.path)
        if path is None:
            missing += 1; continue
        pred = _predict(str(path), P)
        ok = pred["cls"] == r.label
        correct += ok; shown += 1
        with cols[(shown - 1) % 3]:
            st.image(str(path), use_container_width=True)
            st.markdown(f"**{t('true_label')}:** {pretty(r.label)}  \n**{t('live_pred')}:** {pretty(pred['cls'])} ({pred['conf']:.0%}) {'✅' if ok else '❌'}"
                        + (f"  \n⚠️ {t('not_sure_tag')}" if pred["status"] == "uncertain" else ""))
            _cam_button(P, path, f"lab{i}_{seed}")
    if missing:
        st.warning(t("missing_images", n=missing))
    if shown:
        st.success(t("sample_summary", k=correct, n=shown, acc=pct(correct / shown)))


def _field(P) -> None:
    st.caption(t("demo_field_cap"))
    fp = read_csv(C.FIELD_PREDICTIONS_CSV)
    if fp is None or not {"path", "true", "pred", "confidence", "correct"} <= set(fp.columns):
        st.info(t("missing_file", name="reports/field_predictions.csv") + " `python -m src.evaluate --split field`"); return
    fp = fp.copy()
    fp["ok"] = fp["correct"].astype(str).str.lower().isin({"true", "1", "1.0"})
    fp["crop"] = fp["true"].astype(str).map(lambda c: split_class(c)[0])
    c1, c2, c3 = st.columns(3)
    crop = c1.selectbox(t("filter_crop"), [None] + sorted(fp["crop"].unique()), format_func=lambda x, _L=lang(): t("all", _L) if x is None else pretty(x), key="f_crop")
    res = c2.selectbox(t("result_filter"), ["all", "ok", "bad"], format_func=lambda x, _L=lang(): {"all": t("all", _L), "ok": t("only_correct", _L), "bad": t("only_wrong", _L)}[x])
    req = int(c3.number_input(t("sample_size"), 1, 24, 6, key="f_n"))
    v = fp if crop is None else fp[fp["crop"] == crop]
    if len(v):
        st.success(t("field_summary", n=len(v), k=int(v["ok"].sum()), acc=pct(v["ok"].mean())))
    v = v if res == "all" else v[v["ok"] == (res == "ok")]
    if v.empty:
        st.info(t("no_samples")); return
    n = min(req, len(v))
    if n < req:
        st.caption(t("fewer_samples", n=n, req=req))
    cols, missing = st.columns(3), 0
    for i, r in enumerate(v.head(n).itertuples()):
        path = _safe(r.path)
        if path is None:
            missing += 1; continue
        with cols[i % 3]:
            st.image(str(path), use_container_width=True)
            ns = str(getattr(r, "not_sure", "")).lower() in {"true", "1", "1.0"}
            st.markdown(f"**{t('true_label')}:** {pretty(r.true)}  \n**{t('live_pred')}:** {pretty(r.pred)} ({float(r.confidence):.0%}) {'✅' if r.ok else '❌'}"
                        + (f"  \n⚠️ {t('not_sure_tag')}" if ns else ""))
            _cam_button(P, path, f"fld{i}")
    if missing:
        st.warning(t("missing_images", n=missing))
