"""Prediction logic: wraps the existing ``src.predict.Predictor`` without altering it.

Interface relied upon (taken from the original app.py):
  Predictor().predict(img, with_cam=True) -> dict with
    topk: list[{class, crop, condition, prob}], confidence: float,
    status: str ('unsure' = model abstains), reasons: list[str],
    cam_overlay: image/array (when with_cam)
  Optional (used if present): cam -> HxW float array in 0..1 (raw Grad-CAM map).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PIL import Image

from krishi import config as C
from krishi.config import log
from krishi.imaging import to_pil


class DiagnosisError(RuntimeError):
    pass


@dataclass
class Diagnosis:
    cls: str
    crop: str
    condition: str
    confidence: float
    status: str                 # high | moderate | low | uncertain
    topk: list[dict]
    reasons: list[str] = field(default_factory=list)
    cam_overlay: Image.Image | None = None
    cam: Any = None             # raw map if the predictor exposes it

    @property
    def healthy(self) -> bool:
        return self.condition.lower().startswith("healthy")

    @property
    def is_uncertain(self) -> bool:
        """True when no specific diagnosis should be presented."""
        return self.status in {"low", "uncertain"}


def confidence_tier(conf: float, raw_status: str | None) -> str:
    """The model's own abstention ('unsure') always wins; otherwise display bands.
    Bands are display conventions, not calibrated probabilities."""
    if raw_status == "unsure":
        return "uncertain"
    if conf >= C.CONF_HIGH:
        return "high"
    if conf >= C.CONF_MODERATE:
        return "moderate"
    return "low"


def from_raw(res: dict) -> Diagnosis:
    try:
        topk = [dict(r) for r in res["topk"]]
        top = topk[0]
        conf = float(res["confidence"])
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise DiagnosisError(f"Unexpected predictor output: {exc}") from exc
    return Diagnosis(
        cls=top["class"], crop=top["crop"], condition=top["condition"], confidence=conf,
        status=confidence_tier(conf, res.get("status")), topk=topk,
        reasons=list(res.get("reasons") or []),
        cam_overlay=to_pil(res.get("cam_overlay")), cam=res.get("cam"),
    )


def run_diagnosis(predictor, img: Image.Image, with_cam: bool = True) -> Diagnosis:
    """One model inference. Callers must not call this on every Streamlit rerun."""
    try:
        raw = predictor.predict(img) if with_cam else predictor.predict(img, with_cam=False)  # same call forms as the original app
    except Exception as exc:  # noqa: BLE001
        log.exception("Inference failed")
        raise DiagnosisError(str(exc)) from exc
    return from_raw(raw)
