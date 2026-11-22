"""Pure-pandas analytics: crop-health insights from history and performance metrics
from evaluation reports. Nothing is estimated: missing inputs return None (-> N/A)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from krishi.config import load_json, log


# ---------------------------------------------------------------------------
# Crop-health insights (from the user's own history)
# ---------------------------------------------------------------------------
def categorize(row) -> str:
    if row["status"] in ("uncertain", "low"):
        return "uncertain"
    return "healthy" if str(row["condition"]).lower().startswith("healthy") else "diseased"


def insights(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"total": 0}
    d = df.copy()
    d["category"] = d.apply(categorize, axis=1)
    return {
        "total": len(d),
        "uncertain": int((d["category"] == "uncertain").sum()),
        "mean_conf": float(d["confidence"].mean()),
        "n_crops": int(d["crop"].replace("", np.nan).nunique()),
        "top_predictions": d.groupby("cls").size().sort_values(ascending=False).head(10),
        "by_crop": d.groupby("crop").size().sort_values(ascending=False),
        "category": d["category"].value_counts(),
        "activity": d.dropna(subset=["ts"]).groupby(d["ts"].dt.date).size(),
        "confidence": d["confidence"],
    }


# ---------------------------------------------------------------------------
# Evaluation reports
# ---------------------------------------------------------------------------
def first_key(d: dict | None, keys: tuple[str, ...]):
    """First value found under any of ``keys`` (searches one nested level)."""
    if not isinstance(d, dict):
        return None
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    for v in d.values():
        if isinstance(v, dict):
            for k in keys:
                if k in v and v[k] is not None:
                    return v[k]
    return None


def read_json(path: Path) -> dict:
    try:
        return load_json(path) if path.exists() else {}
    except Exception as exc:  # noqa: BLE001
        log.error("Cannot read %s: %s", path, exc)
        return {}


def read_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, keep_default_na=False) if path.exists() else None
    except Exception as exc:  # noqa: BLE001
        log.error("Cannot read %s: %s", path, exc)
        return None


def file_stamp(path: Path) -> str | None:
    return pd.Timestamp(path.stat().st_mtime, unit="s").strftime("%Y-%m-%d") if path.exists() else None


def metrics_from_predictions(df: pd.DataFrame | None, true_col="true", pred_col="pred") -> dict | None:
    """Accuracy and macro precision/recall/F1 computed from a predictions table."""
    if df is None or df.empty or true_col not in df or pred_col not in df:
        return None
    y, p = df[true_col].astype(str), df[pred_col].astype(str)
    rows = []
    for c in sorted(set(y) | set(p)):
        tp = int(((y == c) & (p == c)).sum()); fp = int(((y != c) & (p == c)).sum()); fn = int(((y == c) & (p != c)).sum())
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        rows.append({"class": c, "precision": pr, "recall": rc,
                     "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0, "support": int((y == c).sum())})
    per = pd.DataFrame(rows)
    seen = per[per["support"] > 0]            # macro over classes that actually occur in the ground truth
    return {"n": len(df), "accuracy": float((y == p).mean()),
            "precision": float(seen["precision"].mean()), "recall": float(seen["recall"].mean()),
            "f1": float(seen["f1"].mean()), "per_class": per}


def confusion(df: pd.DataFrame | None, true_col="true", pred_col="pred") -> pd.DataFrame | None:
    if df is None or df.empty or true_col not in df or pred_col not in df:
        return None
    labels = sorted(set(df[true_col].astype(str)) | set(df[pred_col].astype(str)))
    return pd.crosstab(df[true_col].astype(str), df[pred_col].astype(str)).reindex(index=labels, columns=labels, fill_value=0)


def reliability_table(df: pd.DataFrame | None, conf_col="confidence", correct_col="correct", bins=10) -> pd.DataFrame | None:
    if df is not None and correct_col not in df and {"true", "pred"} <= set(df.columns):
        df = df.assign(**{correct_col: df["true"].astype(str) == df["pred"].astype(str)})   # src.evaluate writes no 'correct' column for the lab test set
    if df is None or df.empty or conf_col not in df or correct_col not in df:
        return None
    c = pd.to_numeric(df[conf_col], errors="coerce")
    ok = df[correct_col].astype(str).str.lower().isin({"true", "1", "1.0"})
    b = pd.cut(c, np.linspace(0, 1, bins + 1), include_lowest=True)
    t = pd.DataFrame({"bin": b, "conf": c, "ok": ok}).dropna(subset=["bin"])
    g = t.groupby("bin", observed=True).agg(mean_conf=("conf", "mean"), accuracy=("ok", "mean"), n=("ok", "size")).reset_index()
    g["label"] = g["bin"].astype(str)
    return g


def class_report_from_json(d: dict) -> pd.DataFrame | None:
    """Per-class table if the metrics JSON already holds a classification report."""
    rep = first_key(d, ("classification_report", "per_class", "report"))
    if not isinstance(rep, dict):
        return None
    rows = []
    for name, m in rep.items():
        if isinstance(m, dict) and name not in ("accuracy", "macro avg", "weighted avg", "micro avg"):
            rows.append({"class": name, "precision": m.get("precision"), "recall": m.get("recall"),
                         "f1": m.get("f1-score", m.get("f1")), "support": m.get("support")})
    return pd.DataFrame(rows) if rows else None


def crop_accuracy(df: pd.DataFrame | None, split) -> pd.DataFrame | None:
    if df is None or df.empty or "true" not in df or "pred" not in df:
        return None
    d = df.copy()
    d["crop"] = d["true"].astype(str).map(lambda c: split(c)[0])
    d["ok"] = d["true"].astype(str) == d["pred"].astype(str)
    return d.groupby("crop").agg(accuracy=("ok", "mean"), samples=("ok", "size")).reset_index()
