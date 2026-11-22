"""Central configuration: project paths, thresholds and feature flags.

Paths come from the existing ``src.utils`` module so nothing about the trained
model, dataset or report locations changes. If ``src.utils`` cannot be imported
the app still starts and reports exactly what is missing (see ``PROJECT_ERROR``).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logging.basicConfig(level=os.getenv("KRISHI_LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("krishi")

PROJECT_ERROR: str | None = None
try:
    from src.utils import PROCESSED, REPORTS, ROOT, SRC, load_json, split_class
except Exception as exc:  # noqa: BLE001 - report any import problem to the user
    PROJECT_ERROR = f"{type(exc).__name__}: {exc}"
    log.error("Could not import src.utils (%s). Using fallback paths.", PROJECT_ERROR)
    ROOT = Path(__file__).resolve().parents[1]
    SRC = ROOT / "src"
    PROCESSED = ROOT / "data" / "processed"
    REPORTS = ROOT / "reports"

    def load_json(path: Path) -> Any:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def split_class(name: str) -> tuple[str, str]:
        for sep in ("___", "__"):
            if sep in name:
                crop, cond = name.split(sep, 1)
                return crop.replace("_", " "), cond.replace("_", " ")
        return name, name


def _flag(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {"1", "true", "yes", "on"}


# --- Deployment mode -------------------------------------------------------
# MULTIUSER=1 isolates history per browser session and keeps no thumbnails by default.
MULTIUSER = _flag("KRISHI_MULTIUSER", False)
RETENTION_DAYS = int(os.getenv("KRISHI_RETENTION_DAYS", "90"))   # 0 = keep forever
KEEP_THUMBNAILS = _flag("KRISHI_KEEP_THUMBS", not MULTIUSER)
ENABLE_LABS = _flag("KRISHI_ENABLE_LABS", True)

# --- Files -------------------------------------------------------------------
DB_PATH = ROOT / "data" / "history.db"          # same location as the original app
THUMBS_DIR = ROOT / "data" / "thumbs"
KB_PATH = SRC / "knowledge_base.json"
CLASS_INFO_PATH = PROCESSED / "class_info.json"
TEST_CSV = PROCESSED / "test.csv"
FIELD_PREDICTIONS_CSV = REPORTS / "field_predictions.csv"
TEST_PREDICTIONS_CSV = REPORTS / "test_predictions.csv"   # optional, used if present

# --- Image validation (same limits as the original app) ------------------------
MAX_UPLOAD_MB = 8
ALLOWED_EXT = ("jpg", "jpeg", "png")
ALLOWED_FORMATS = {"JPEG", "PNG"}
MIN_SIDE_PX = 64
MAX_PIXELS = 50_000_000      # guards against decompression bombs
INFER_MAX_SIDE = 2048        # larger photos are downscaled before inference

# --- Confidence bands (display only; the model is NOT calibrated to these) ------
CONF_HIGH = float(os.getenv("KRISHI_CONF_HIGH", "0.85"))
CONF_MODERATE = float(os.getenv("KRISHI_CONF_MODERATE", "0.60"))

KVK_URL = "https://kvk.icar.gov.in/"
DEDUPE_SECONDS = 10
