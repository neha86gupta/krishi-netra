"""Shared paths, constants and helpers."""
import json, logging, random
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
RAW, PROCESSED = ROOT / "data" / "raw", ROOT / "data" / "processed"
FIELD, MODELS, REPORTS, SRC = ROOT / "data" / "field_test", ROOT / "models", ROOT / "reports", ROOT / "src"
IMG_SIZE = 224
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def ensure_dirs():
    for d in (RAW, PROCESSED, FIELD, MODELS, REPORTS):
        d.mkdir(parents=True, exist_ok=True)


def get_logger(name):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    return logging.getLogger(name)


def set_seed(seed=42):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def save_json(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    def _default(o):
        if hasattr(o, "tolist"):      # numpy arrays AND numpy scalars
            return o.tolist()
        return str(o)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=_default)

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def split_class(name):
    """'Tomato___Late_blight' -> ('Tomato', 'Late blight')"""
    crop, _, cond = name.partition("___")
    return crop.replace("_", " ").strip(), cond.replace("_", " ").strip()
