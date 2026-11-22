"""Grad-CAM presentation helpers. The heatmap always comes from the model's own
Grad-CAM (``cam_overlay`` / ``cam``). Nothing is synthesised here: if the predictor
does not expose the raw map, the standalone heatmap is simply not shown."""
from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

from krishi.diagnosis import Diagnosis


def _valid_cam(cam) -> np.ndarray | None:
    if cam is None:
        return None
    arr = np.asarray(cam, dtype=np.float32)
    if arr.ndim != 2 or arr.size == 0 or not np.isfinite(arr).all():
        return None
    lo, hi = float(arr.min()), float(arr.max())
    return (arr - lo) / (hi - lo) if hi > lo else None


def heatmap_image(cam, size: tuple[int, int]) -> Image.Image | None:
    """Colourise the raw Grad-CAM map (cv2 JET) at the photo's size."""
    arr = _valid_cam(cam)
    if arr is None:
        return None
    arr = cv2.resize(arr, size, interpolation=cv2.INTER_LINEAR)
    colour = cv2.applyColorMap((arr * 255).astype(np.uint8), cv2.COLORMAP_JET)
    return Image.fromarray(cv2.cvtColor(colour, cv2.COLOR_BGR2RGB))


def views(diag: Diagnosis, original: Image.Image) -> list[tuple[str, Image.Image]]:
    """Ordered (i18n-key, image) pairs available for this diagnosis."""
    out: list[tuple[str, Image.Image]] = [("cam_original", original)]
    heat = heatmap_image(diag.cam, original.size)
    if heat is not None:
        out.append(("cam_heatmap", heat))
    if diag.cam_overlay is not None:
        out.append(("cam_overlay", diag.cam_overlay))
    return out
