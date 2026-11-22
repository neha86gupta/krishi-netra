"""Builds a throwaway project (fake ``src`` package, KB, reports, images) BEFORE krishi is
imported. The StubPredictor exists only for testing the app plumbing - it is not a model."""
import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image

APP_DIR = Path(__file__).resolve().parents[1]
PROJ = Path(tempfile.mkdtemp(prefix="krishi_test_"))

UTILS = '''
import json
from pathlib import Path
ROOT = Path(r"{root}")
SRC = ROOT / "src"; PROCESSED = ROOT / "data" / "processed"; REPORTS = ROOT / "reports"
def load_json(p):
    with open(p, encoding="utf-8") as f: return json.load(f)
def split_class(c):
    crop, cond = c.split("___"); return crop.replace("_", " "), cond.replace("_", " ")
'''
PREDICT = '''
import numpy as np
from PIL import Image
from src.utils import split_class
CLASSES = ["Tomato___Late_blight", "Tomato___healthy", "Potato___Early_blight"]
class Predictor:
    """TEST STUB: deterministic function of mean brightness. Not a real model."""
    def predict(self, img, with_cam=True):
        m = float(np.asarray(img.convert("L")).mean()) / 255
        conf = round(0.45 + 0.5 * m, 3)
        order = [CLASSES[0], CLASSES[1], CLASSES[2]] if m > 0.3 else [CLASSES[1], CLASSES[0], CLASSES[2]]
        rest = (1 - conf) / 2
        topk = []
        for c, p in zip(order, [conf, rest, rest]):
            crop, cond = split_class(c); topk.append({"class": c, "crop": crop, "condition": cond, "prob": p})
        out = {"topk": topk, "confidence": conf, "status": "unsure" if conf < 0.55 else "ok",
               "reasons": ["stub: low brightness"] if conf < 0.55 else []}
        if with_cam:
            cam = np.linspace(0, 1, 49).reshape(7, 7)
            out["cam"] = cam
            out["cam_overlay"] = img.convert("RGB").copy()
        return out
'''
KB = {"classes": {
    "Tomato___Late_blight": {"causal_agent": "Phytophthora infestans", "cause_group": "oomycete",
                              "symptoms_en": "Dark water-soaked blotches.", "symptoms_hi": "गहरे जलयुक्त धब्बे।",
                              "sources": [{"name": "Example source", "url": "https://example.org/lb"}]},
    "Tomato___healthy": {"cause_group": "none"}},
    "cause_groups": {"oomycete": {"advice_en": "Remove affected leaves.", "advice_hi": "प्रभावित पत्तियाँ हटाएँ।"},
                     "unknown": {"advice_en": "Ask an expert.", "advice_hi": "विशेषज्ञ से पूछें।"}}}


def _img(path: Path, colour, size=(128, 128)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.full((*size, 3), colour, np.uint8)).save(path)


def build() -> None:
    (PROJ / "src").mkdir(parents=True)
    (PROJ / "src" / "__init__.py").write_text("")
    (PROJ / "src" / "utils.py").write_text(UTILS.format(root=str(PROJ)))
    (PROJ / "src" / "predict.py").write_text(PREDICT)
    (PROJ / "src" / "knowledge_base.json").write_text(json.dumps(KB))
    proc, rep = PROJ / "data" / "processed", PROJ / "reports"
    proc.mkdir(parents=True); rep.mkdir(parents=True)
    classes = ["Tomato___Late_blight", "Tomato___healthy", "Potato___Early_blight"]
    (proc / "class_info.json").write_text(json.dumps({"classes": classes}))
    rows = ["path,label"]
    for i in range(8):
        _img(PROJ / "data" / "img" / f"t{i}.png", (40 + 20 * i, 120, 60))
        rows.append(f"data/img/t{i}.png,{classes[i % 3]}")
    (proc / "test.csv").write_text("\n".join(rows))
    frows = ["path,true,pred,confidence,correct,not_sure"]
    for i in range(6):
        ok = i % 2 == 0
        frows.append(f"data/img/t{i}.png,{classes[0]},{classes[0] if ok else classes[1]},{0.9 - 0.1 * i},{ok},False")
    (rep / "field_predictions.csv").write_text("\n".join(frows))
    (rep / "test_metrics.json").write_text(json.dumps({"accuracy": 0.97, "n": 100}))
    (rep / "field_metrics.json").write_text(json.dumps({"field_full_argmax": {"accuracy": 0.5}, "gap_full_argmax": 0.47}))
    (rep / "baseline_metrics.json").write_text(json.dumps({"accuracy": 0.4}))


build()
sys.path.insert(0, str(PROJ))      # fake `src` wins
sys.path.insert(1, str(APP_DIR))   # real `krishi`
os.chdir(PROJ)
