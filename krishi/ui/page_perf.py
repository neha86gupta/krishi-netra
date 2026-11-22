"""Model performance dashboard. Everything is read from reports/ or computed from the
prediction tables found there. Missing values are shown as N/A, never estimated."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from krishi import analytics as A
from krishi import charts
from krishi.config import FIELD_PREDICTIONS_CSV, REPORTS, TEST_PREDICTIONS_CSV, split_class
from krishi.i18n import t
from krishi.ui.services import lang
from krishi.ui.components import card, hero, num, pct, tiles

FILES = {"test": "test_metrics.json", "field": "field_metrics.json", "base": "baseline_metrics.json"}


def _sig() -> tuple:
    paths = [REPORTS / n for n in [*FILES.values(), "per_crop_metrics.csv"]] + [FIELD_PREDICTIONS_CSV, TEST_PREDICTIONS_CSV]
    return tuple(p.stat().st_mtime if p.exists() else 0 for p in paths)


@st.cache_data(show_spinner=False)
def _load(sig: tuple) -> dict:
    return {"test": A.read_json(REPORTS / FILES["test"]), "field": A.read_json(REPORTS / FILES["field"]),
            "base": A.read_json(REPORTS / FILES["base"]), "per_crop": A.read_csv(REPORTS / "per_crop_metrics.csv"),
            "test_pred": A.read_csv(TEST_PREDICTIONS_CSV), "field_pred": A.read_csv(FIELD_PREDICTIONS_CSV)}


def _scalar(x):
    return x if isinstance(x, (int, float, str)) and not isinstance(x, bool) else None


def _first(d, keys):
    return _scalar(A.first_key(d, keys))


def render() -> None:
    hero(t("nav_perf"), t("perf_sub"))
    R = _load(_sig())
    if not any(R[k] for k in ("test", "field", "base")) and R["field_pred"] is None:
        st.info(t("no_report", name="reports/*.json"))
        return

    mt = A.metrics_from_predictions(R["test_pred"])
    mf = A.metrics_from_predictions(R["field_pred"])
    lab = {"accuracy": _first(R["test"], ("accuracy",)) if _first(R["test"], ("accuracy",)) is not None else (mt or {}).get("accuracy"),
           "precision": _first(R["test"], ("macro_precision", "precision_macro", "precision")) or (mt or {}).get("precision"),
           "recall": _first(R["test"], ("macro_recall", "recall_macro", "recall")) or (mt or {}).get("recall"),
           "f1": _first(R["test"], ("macro_f1", "f1_macro", "f1", "f1_score", "f1-score")) or (mt or {}).get("f1")}
    f_acc = R["field"].get("field_full_argmax", {}).get("accuracy")
    field = {"accuracy": f_acc if f_acc is not None else (mf or {}).get("accuracy"),
             "precision": (mf or {}).get("precision"), "recall": (mf or {}).get("recall"), "f1": (mf or {}).get("f1")}
    gap = R["field"].get("gap_full_argmax")

    tabs = st.tabs([t("tab_overview"), t("tab_classwise"), t("tab_cropwise"), t("tab_confusion"), t("tab_calibration"), t("tab_raw")])
    with tabs[0]:
        tiles([(t("lab_acc"), pct(lab["accuracy"])), (t("field_acc"), pct(field["accuracy"])),
               (t("gap"), pct(gap)), (t("baseline"), pct(R["base"].get("accuracy")))])
        st.write("")
        names = [("accuracy", t("accuracy")), ("precision", t("precision")), ("recall", t("recall")), ("f1", t("f1"))]
        table = pd.DataFrame({"": [n for _, n in names], t("lab_label"): [pct(lab[k]) for k, _ in names],
                              t("field_label"): [pct(field[k]) for k, _ in names]})
        st.dataframe(table, hide_index=True, use_container_width=True)
        srcs = [t("computed_from", file=n) for n, m in (("test_predictions.csv", mt), ("field_predictions.csv", mf)) if m]
        if srcs:
            st.caption(" · ".join(srcs))
        if any(v is not None for v in lab.values()) or any(v is not None for v in field.values()):
            st.plotly_chart(charts.grouped([n for _, n in names], {"Lab": [lab[k] for k, _ in names], "Field": [field[k] for k, _ in names]}),
                            use_container_width=True)
        card(f"<b>{t('perf_summary')}.</b> " + (t("perf_summary_txt", lab=pct(lab["accuracy"]), field=pct(field["accuracy"]), gap=pct(gap))), "accent")
        card(t("perf_how"))
        meta = []
        for label, rep, fname, pred in ((t("lab_label"), R["test"], FILES["test"], R["test_pred"]),
                                        (t("field_label"), R["field"], FILES["field"], R["field_pred"])):
            n = _first(rep, ("n", "num_samples", "n_samples", "samples", "total", "support"))
            meta.append({t("split"): label, t("n_samples"): num(n if n is not None else (len(pred) if pred is not None else None)),
                         t("eval_date"): _first(rep, ("date", "evaluated_at", "evaluation_date", "timestamp")) or t("na"),
                         t("model_version"): _first(rep, ("model_version", "version", "model_name")) or t("na"),
                         t("file_modified"): A.file_stamp(REPORTS / fname) or t("na")})
        st.dataframe(pd.DataFrame(meta), hide_index=True, use_container_width=True)

    with tabs[1]:
        which = st.radio(t("split"), ["lab", "field"], horizontal=True, format_func=lambda x, _L=lang(): t("lab_label" if x == "lab" else "field_label", _L))
        rep = R["test"] if which == "lab" else R["field"]
        metrics = mt if which == "lab" else mf
        cls_tbl = A.class_report_from_json(rep)
        if cls_tbl is None and metrics:
            cls_tbl = metrics["per_class"]
        if cls_tbl is None:
            st.info(t("na") + " - " + t("no_report", name=f"{'test' if which == 'lab' else 'field'}_predictions.csv"))
        else:
            st.dataframe(cls_tbl.rename(columns={"class": t("class"), "support": t("support")}), hide_index=True, use_container_width=True)
            f1 = pd.to_numeric(cls_tbl.set_index("class")["f1"], errors="coerce").dropna()
            if len(f1):
                st.plotly_chart(charts.hbar(f1, t("f1"), color=charts.EMERALD), use_container_width=True)

    with tabs[2]:
        if R["per_crop"] is not None:
            st.caption(t("crop_note"))
            st.dataframe(R["per_crop"], hide_index=True, use_container_width=True)
            acc_cols = [c for c in R["per_crop"].columns if "acc" in c.lower()]
            name_col = R["per_crop"].columns[0]
            if acc_cols:
                s = pd.to_numeric(R["per_crop"].set_index(name_col)[acc_cols[0]], errors="coerce").dropna()
                st.plotly_chart(charts.hbar(s, acc_cols[0], color=charts.FOREST), use_container_width=True)
        else:
            computed = A.crop_accuracy(R["field_pred"], split_class)
            if computed is None:
                st.info(t("no_report", name="per_crop_metrics.csv"))
            else:
                st.caption(t("computed_from", file="field_predictions.csv") + " · " + t("field_label"))
                st.dataframe(computed, hide_index=True, use_container_width=True)
                st.plotly_chart(charts.hbar(computed.set_index("crop")["accuracy"], color=charts.FOREST), use_container_width=True)

    with tabs[3]:
        shown = False
        for key, pred, label in (("test", R["test_pred"], t("lab_label")), ("field", R["field_pred"], t("field_label"))):
            cm = A.confusion(pred)
            if cm is not None:
                st.markdown(f"**{label}**"); st.plotly_chart(charts.heatmap(cm), use_container_width=True); shown = True
        if not shown:
            png = REPORTS / "test_confusion_matrix.png"
            if png.exists():
                st.image(str(png), caption=t("lab_label")); shown = True
        if not shown:
            st.info(t("no_report", name="test_confusion_matrix.png"))

    with tabs[4]:
        st.caption(t("reliability_help"))
        any_shown = False
        for pred, label, png in ((R["test_pred"], t("lab_label"), "test_reliability.png"), (R["field_pred"], t("field_label"), "field_reliability.png")):
            tbl = A.reliability_table(pred)
            if tbl is not None:
                any_shown = True
                st.markdown(f"**{label}**")
                a, b = st.columns(2)
                a.plotly_chart(charts.histogram(pd.to_numeric(pred["confidence"], errors="coerce").dropna(), t("conf_dist"), t("confidence")), use_container_width=True)
                b.plotly_chart(charts.reliability(tbl, (t("mean_conf"), t("accuracy"), t("n_bins"))), use_container_width=True)
            elif (REPORTS / png).exists():
                any_shown = True
                st.image(str(REPORTS / png), caption=label)
        if not any_shown:
            st.info(t("no_report", name="*_predictions.csv / *_reliability.png"))

    with tabs[5]:
        for key, label in (("test", t("lab_label")), ("field", t("field_label")), ("base", t("baseline"))):
            if R[key]:
                with st.expander(label):
                    st.json(R[key])
            else:
                st.info(t("no_report", name=FILES[key]))
        d = REPORTS / "gradcam_samples"
        if d.exists() and list(d.glob("*.png")):
            pick = st.selectbox(t("gradcam_samples"), sorted(p.name for p in d.glob("*.png")))
            st.image(str(d / pick))
