"""Inference wrapper + folder-evaluation CLI.
python -m src.predict --folder "C:\\my_photos" [--out reports/folder_eval.csv]
Subfolders named exactly like a PlantVillage class (e.g. Tomato___Late_blight) are scored as labelled."""
import argparse, time
from pathlib import Path
import pandas as pd
import torch
from PIL import Image, ImageOps
from src import model as M
from src.calibration import entropy, feat_sim
from src.dataset import eval_tf
from src.gradcam import GradCAM, overlay
from src.utils import *


class Predictor:
    def __init__(self, ckpt=MODELS / "best.pt", cam=True):
        if not Path(ckpt).exists():
            raise FileNotFoundError(f"{ckpt} not found - run `python -m src.train` first.")
        ck = torch.load(ckpt, map_location="cpu", weights_only=False)
        self.classes, self.arch = ck["classes"], ck["arch"]
        self.model = M.build_model(self.arch, len(self.classes), pretrained=False)
        self.model.load_state_dict(ck["model_state"]); self.model.eval()
        self.tf = eval_tf(ck["img_size"])
        cal = load_json(MODELS / "calibration.json") if (MODELS / "calibration.json").exists() else {}
        self.T = cal.get("temperature", 1.0); self.tau = cal.get("conf_threshold", 0.7)
        self.ent_thr = cal.get("entropy_threshold", 1e9); self.sim_thr = cal.get("sim_threshold", -1.0)
        cp = MODELS / "centroids.pt"
        self.centroids = torch.load(cp) if cp.exists() else None
        self.cam = GradCAM(self.model, self.arch) if cam else None

    def thresholds(self):
        return {"conf": self.tau, "entropy": self.ent_thr, "feature_similarity": self.sim_thr}

    def unsure_mask(self, probs, feats):
        conf, top = probs.max(1)
        m = (conf < self.tau) | (entropy(probs) > self.ent_thr)
        if self.centroids is not None:
            m = m | (feat_sim(feats, self.centroids, top) < self.sim_thr)
        return m

    def predict(self, img, topk=3, with_cam=True):
        t0 = time.time()
        img = ImageOps.exif_transpose(img).convert("RGB"); x = self.tf(img).unsqueeze(0)
        with torch.no_grad():
            f = M.features(self.model, self.arch, x)
            probs = torch.softmax(M.classify(self.model, self.arch, f) / self.T, 1)
        conf, top = probs.max(1); ent = float(entropy(probs))
        sim = float(feat_sim(f, self.centroids, top)) if self.centroids is not None else None
        why = []
        if conf < self.tau:
            why.append(f"low confidence ({float(conf):.0%} < {self.tau:.0%})")
        if ent > self.ent_thr:
            why.append("prediction is spread over many classes")
        if sim is not None and sim < self.sim_thr:
            why.append("image looks unlike the training leaves (non-leaf or unsupported crop?)")
        p, idx = probs[0].topk(min(topk, len(self.classes)))
        res = {"topk": [{"class": self.classes[i], "crop": split_class(self.classes[i])[0],
                         "condition": split_class(self.classes[i])[1], "prob": float(pp)} for pp, i in zip(p, idx)],
               "confidence": float(conf), "entropy": ent, "feat_sim": sim,
               "status": "unsure" if why else "ok", "reasons": why}
        if with_cam and self.cam is not None:
            heat, _ = self.cam(x, int(top)); res["cam_overlay"] = overlay(img, heat); res["cam"] = heat  # raw HxW map in [0,1] for the new UI
        res["seconds"] = time.time() - t0
        return res


def eval_folder(folder, out_csv):
    P, rows = Predictor(cam=False), []
    for f in sorted(Path(folder).rglob("*")):
        if f.suffix.lower() not in IMG_EXT:
            continue
        try:
            r = P.predict(Image.open(f), with_cam=False)
        except Exception as e:  # noqa
            print("skip", f, e); continue
        true = f.parent.name if f.parent.name in P.classes else ""
        rows.append({"file": str(f), "true": true, "pred": r["topk"][0]["class"], "confidence": round(r["confidence"], 3),
                     "status": r["status"], "reasons": "; ".join(r["reasons"])})
    df = pd.DataFrame(rows); df.to_csv(out_csv, index=False)
    print(f"{len(df)} images | 'not sure': {(df.status == 'unsure').mean():.0%}" if len(df) else "no images found")
    lab = df[df.true != ""] if len(df) else df
    if len(lab):
        print(f"labelled: {len(lab)} | accuracy {(lab.true == lab.pred).mean():.1%} | "
              f"accuracy when answering {(lab[lab.status == 'ok'].true == lab[lab.status == 'ok'].pred).mean():.1%}")
    print("saved", out_csv)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--folder", required=True)
    ap.add_argument("--out", default=str(REPORTS / "folder_eval.csv")); a = ap.parse_args()
    eval_folder(a.folder, a.out)
