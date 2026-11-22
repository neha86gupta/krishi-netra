"""Classical baseline (context only): HSV colour histogram + logistic regression."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from src.dataset import load_split
from src.utils import *


def feat(rel):
    im = Image.open(ROOT / rel).convert("RGB").resize((64, 64)).convert("HSV")
    h = np.histogramdd(np.asarray(im).reshape(-1, 3), bins=(12, 4, 4), range=((0, 256),) * 3)[0].ravel()
    return h / h.sum()


def feats(df):
    with ThreadPoolExecutor(8) as ex:
        return np.array(list(ex.map(feat, df.path)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--subset", type=int, default=None); a = ap.parse_args()
    tr, te = load_split("train", a.subset), load_split("test")
    clf = LogisticRegression(max_iter=300, class_weight="balanced").fit(feats(tr), tr.y)
    p = clf.predict(feats(te))
    out = {"model": "HSV histogram + logistic regression", "n_train": len(tr), "n_test": len(te),
           "accuracy": accuracy_score(te.y, p), "macro_f1": f1_score(te.y, p, average="macro", zero_division=0)}
    save_json(out, REPORTS / "baseline_metrics.json"); print(out)
