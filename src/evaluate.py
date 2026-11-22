"""Evaluation. python -m src.evaluate [--split test|field|all] [--ood-dir DIR] [--cam-per-crop 8]
Outputs go to reports/. Nothing is hard-coded; every figure comes from this run."""
import argparse, re
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageOps
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from torch.utils.data import DataLoader
from src import model as M
from src.calibration import collect, ece
from src.dataset import LeafDataset
from src.gradcam import GradCAM, cam_focus, leaf_mask, overlay
from src.predict import Predictor
from src.utils import *

log = get_logger("evaluate")


def outputs(P, df):
    logits, feats, y = collect(P.model, P.arch, DataLoader(LeafDataset(df, P.tf), batch_size=64))
    return logits, feats, y.numpy(), torch.softmax(logits / P.T, 1)


def core_metrics(P, probs, feats, y, labels=None):
    pred, conf = probs.argmax(1).numpy(), probs.max(1).values.numpy()
    p, r, f, _ = precision_recall_fscore_support(y, pred, average="macro", zero_division=0, labels=labels)
    uns = P.unsure_mask(probs, feats).numpy()
    m = {"n": int(len(y)), "accuracy": float((pred == y).mean()), "macro_precision": float(p), "macro_recall": float(r),
         "macro_f1": float(f), "ece_calibrated": ece(probs, torch.tensor(y)), "mean_confidence": float(conf.mean()),
         "not_sure_rate": float(uns.mean()),
         "accuracy_when_answering": float((pred[~uns] == y[~uns]).mean()) if (~uns).any() else None}
    return m, pred, conf, uns


def reliability(probs, y, path, title):
    conf, pred = probs.max(1); acc = (pred == torch.tensor(y)).float(); e = np.linspace(0, 1, 11); xs, ys = [], []
    for lo, hi in zip(e[:-1], e[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            xs.append(conf[m].mean().item()); ys.append(acc[m].mean().item())
    plt.figure(figsize=(4, 4)); plt.plot([0, 1], [0, 1], "--", c="gray"); plt.plot(xs, ys, "o-")
    plt.xlabel("mean confidence"); plt.ylabel("accuracy"); plt.title(title); plt.savefig(path, dpi=100, bbox_inches="tight"); plt.close()


def confusion_outputs(y, pred, classes, prefix, png=True):
    cm = confusion_matrix(y, pred, labels=list(range(len(classes))))
    pd.DataFrame(cm, index=classes, columns=classes).to_csv(REPORTS / f"{prefix}_confusion_matrix.csv")
    if png:
        fig, ax = plt.subplots(figsize=(11, 10)); ax.imshow(cm / np.maximum(cm.sum(1, keepdims=True), 1), cmap="Blues")
        ax.set_xticks(range(len(classes))); ax.set_yticks(range(len(classes)))
        ax.set_xticklabels(classes, rotation=90, fontsize=5); ax.set_yticklabels(classes, fontsize=5)
        ax.set_xlabel("predicted"); ax.set_ylabel("true"); fig.savefig(REPORTS / f"{prefix}_confusion_matrix.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    pairs = sorted([(classes[i], classes[j], int(cm[i, j])) for i in range(len(classes)) for j in range(len(classes))
                    if i != j and cm[i, j] > 0], key=lambda t: -t[2])[:20]
    pd.DataFrame(pairs, columns=["true", "predicted", "count"]).to_csv(REPORTS / f"{prefix}_top_confusions.csv", index=False)


def crop_analysis(classes, info, y, pred, probs):
    """Per-crop results + checks for reliance on crop identity."""
    crop_of = np.array([split_class(c)[0] for c in classes])
    healthy = np.array(["healthy" in split_class(c)[1].lower() for c in classes])
    tc, pr, rows = np.array(info["train_counts"]), probs.numpy(), []
    for crop in sorted(set(crop_of)):
        m = crop_of[y] == crop
        if not m.any():
            continue
        yi, pi = y[m], pred[m]; ids = np.where(crop_of == crop)[0]
        err = yi != pi; cross = err & (crop_of[pi] != crop)
        oracle = ids[pr[m][:, ids].argmax(1)]; maj = ids[tc[ids].argmax()]
        mixed = healthy[ids].any() and (~healthy[ids]).any(); crop_ok = crop_of[pi] == crop
        rows.append({"crop": crop, "n_test": int(m.sum()), "n_classes": len(ids),
                     "kind": "mixed" if mixed else ("healthy_only" if healthy[ids].all() else "disease_only"),
                     "accuracy": float((yi == pi).mean()), "crop_id_accuracy": float(crop_ok.mean()),
                     "share_of_errors_that_are_cross_crop": float(cross.sum() / err.sum()) if err.any() else 0.0,
                     "accuracy_if_true_crop_known": float((oracle == yi).mean()),
                     "always_predict_majority_class_baseline": float((yi == maj).mean()),
                     "healthy_vs_diseased_acc": float((healthy[pi] == healthy[yi])[crop_ok].mean()) if mixed and crop_ok.any() else None})
    return pd.DataFrame(rows)


def patch_shuffle(x, g=4):
    B, C, H, W = x.shape; h, w = H // g, W // g
    p = x.unfold(2, h, h).unfold(3, w, w).reshape(B, C, g * g, h, w)[:, :, torch.randperm(g * g)]
    return p.reshape(B, C, g, g, h, w).permute(0, 1, 2, 4, 3, 5).reshape(B, C, H, W)


def shuffle_probe(P, df, n=1500, seed=0):
    """If crop identity survives patch shuffling but class accuracy collapses, the model reads crop from global
    colour/texture while disease needs spatial symptom patterns. Suggestive, not proof."""
    df = df.sample(min(n, len(df)), random_state=seed); torch.manual_seed(seed)
    crop_of = np.array([split_class(c)[0] for c in P.classes]); out = {"n": len(df)}
    for name, fn in (("original", lambda x: x), ("shuffled", patch_shuffle)):
        ps, ys = [], []
        with torch.no_grad():
            for x, y in DataLoader(LeafDataset(df, P.tf), batch_size=64):
                ps.append(M.classify(P.model, P.arch, M.features(P.model, P.arch, fn(x))).argmax(1)); ys.append(y)
        p, y = torch.cat(ps).numpy(), torch.cat(ys).numpy()
        out[f"accuracy_{name}"] = float((p == y).mean()); out[f"crop_id_accuracy_{name}"] = float((crop_of[p] == crop_of[y]).mean())
    return out


def cam_probe(P, df, per_crop=8, seed=0):
    cam, outdir, rows = GradCAM(P.model, P.arch), REPORTS / "gradcam_samples", []
    outdir.mkdir(exist_ok=True)
    for crop, g in df.groupby("crop"):
        g = g.sample(min(per_crop, len(g)), random_state=seed)
        fig, axs = plt.subplots(2, len(g), figsize=(2.2 * len(g), 5), squeeze=False)
        for k, (_, r) in enumerate(g.iterrows()):
            img = ImageOps.exif_transpose(Image.open(ROOT / r.path)).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
            heat, logits = cam(P.tf(img).unsqueeze(0)); pred = int(logits.argmax(1))
            ins, frac, enr = cam_focus(heat, leaf_mask(img))
            rows.append({"crop": crop, "true": r.label, "pred": P.classes[pred], "correct": pred == r.y,
                         "cam_inside_mask": ins, "mask_fraction": frac, "enrichment": enr})
            axs[0, k].imshow(img); axs[1, k].imshow(overlay(img, heat))
            axs[0, k].set_title(f"T: {split_class(r.label)[1][:14]}", fontsize=6); axs[1, k].set_title(f"P: {split_class(P.classes[pred])[1][:14]}", fontsize=6)
            axs[0, k].axis("off"); axs[1, k].axis("off")
        fig.savefig(outdir / (re.sub(r"[^A-Za-z0-9]+", "_", crop) + ".png"), dpi=90, bbox_inches="tight"); plt.close(fig)
    cam.remove()
    return pd.DataFrame(rows)


def restricted_pred(probs, ov):
    pr = torch.full_like(probs, -1.0); pr[:, ov] = probs[:, ov]
    return pr.argmax(1).numpy()


def evaluate_field(P, test):
    cm = load_json(FIELD / "class_map.json"); chk_path = FIELD / "plantdoc_checked.csv"
    if not chk_path.exists():
        raise SystemExit("Run `python -m src.preprocess` first (it creates plantdoc_checked.csv).")
    mp = {k: v["plantvillage_class"] for k, v in cm["mapping"].items() if v["plantvillage_class"] in P.classes}
    if not cm.get("reviewed"):
        log.warning("class_map.json is NOT marked reviewed - treat field results as provisional.")
    chk = pd.read_csv(chk_path, keep_default_na=False)
    keep = (chk.ok.astype(str) == "True") & (chk.in_pv.astype(str) == "False") & chk.label.isin(mp)
    f = chk[keep].copy()
    sp = FIELD / "field_split.csv"
    if sp.exists():      # evaluate ONLY on the held-out PlantDoc test part
        sd = pd.read_csv(sp, keep_default_na=False)
        f = f[f.path.isin(set(sd[sd.split == "test"].path))].copy()
        log.info("field eval restricted to held-out PlantDoc test part: %d images", len(f))
    f["y"] = f.label.map(lambda l: P.classes.index(mp[l])); ov = sorted(set(f.y))
    logits, feats, y, probs = outputs(P, f)
    m_full, pred, conf, uns = core_metrics(P, probs, feats, y, labels=ov)
    pred_r = restricted_pred(probs, ov); crop_of = np.array([split_class(c)[0] for c in P.classes])
    m_res = {"accuracy": float((pred_r == y).mean())}
    rep = classification_report(y, pred_r, labels=ov, target_names=[P.classes[i] for i in ov], output_dict=True, zero_division=0)
    pd.DataFrame(rep).T.to_csv(REPORTS / "field_per_class_restricted.csv")
    confusion_outputs(y, pred, P.classes, "field", png=False); reliability(probs, y, REPORTS / "field_reliability.png", "Field (PlantDoc)")
    pd.DataFrame({"path": f.path.values, "plantdoc_label": f.label.values, "true": [P.classes[i] for i in y],
                  "pred": [P.classes[i] for i in pred], "pred_restricted": [P.classes[i] for i in pred_r],
                  "confidence": conf, "not_sure": uns, "correct": pred == y}).to_csv(REPORTS / "field_predictions.csv", index=False)
    lab = test[test.y.isin(ov)]; _, _, yl, pl = outputs(P, lab)
    res = {"class_map_reviewed": bool(cm.get("reviewed")), "n_images_used": int(len(f)), "overlapping_classes": [P.classes[i] for i in ov],
           "plantdoc_classes_unmapped": sorted(k for k in cm["mapping"] if k not in mp),
           "excluded_as_duplicates_or_unreadable": int((~keep & chk.label.isin(mp)).sum()),
           "field_full_argmax": m_full, "field_restricted_to_overlap": m_res,
           "field_crop_id_accuracy": float((crop_of[pred] == crop_of[y]).mean()),
           "lab_test_same_classes": {"n": int(len(yl)), "accuracy_full_argmax": float((pl.argmax(1).numpy() == yl).mean()),
                                     "accuracy_restricted": float((restricted_pred(pl, ov) == yl).mean())}}
    res["gap_full_argmax"] = res["lab_test_same_classes"]["accuracy_full_argmax"] - m_full["accuracy"]
    save_json(res, REPORTS / "field_metrics.json"); log.info("field: %s", res)


def ood_check(P, folder, test_not_sure):
    paths = [p for p in Path(folder).rglob("*") if p.suffix.lower() in IMG_EXT]
    if not paths:
        log.warning("no images in %s", folder); return
    df = pd.DataFrame({"path": [str(p) for p in paths], "y": 0})
    _, feats, _, probs = outputs(P, df); uns = P.unsure_mask(probs, feats).numpy()
    save_json({"n": len(df), "rejected_as_not_sure": float(uns.mean()), "in_distribution_test_not_sure_rate": test_not_sure,
               "note": "Share of YOUR non-leaf photos that triggered 'not sure'; 1 - this is the share that slipped through."},
              REPORTS / "ood_check.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="all", choices=["test", "field", "all"])
    ap.add_argument("--ood-dir", default=None); ap.add_argument("--cam-per-crop", type=int, default=8)
    a = ap.parse_args(); ensure_dirs()
    P = Predictor(cam=False); classes = P.classes
    info = load_json(PROCESSED / "class_info.json"); test = pd.read_csv(PROCESSED / "test.csv", keep_default_na=False)
    test_uns = None
    if a.split in ("test", "all"):
        logits, feats, y, probs = outputs(P, test)
        m, pred, conf, uns = core_metrics(P, probs, feats, y); test_uns = m["not_sure_rate"]
        m.update(ece_uncalibrated=ece(torch.softmax(logits, 1), torch.tensor(y)), temperature=P.T, thresholds=P.thresholds())
        rep = classification_report(y, pred, labels=list(range(len(classes))), target_names=classes, output_dict=True, zero_division=0)
        pd.DataFrame(rep).T.to_csv(REPORTS / "per_class_metrics.csv")
        confusion_outputs(y, pred, classes, "test"); reliability(probs, y, REPORTS / "test_reliability.png", "Lab test set")
        crop_df = crop_analysis(classes, info, y, pred, probs); crop_df.to_csv(REPORTS / "per_crop_metrics.csv", index=False)
        cdf = cam_probe(P, test, a.cam_per_crop); cdf.to_csv(REPORTS / "gradcam_focus.csv", index=False)
        m["crop_reliance_probes"] = {"patch_shuffle": shuffle_probe(P, 200),
                                     "gradcam_mean_enrichment": float(cdf.enrichment.mean()),
                                     "gradcam_enrichment_correct": float(cdf[cdf.correct].enrichment.mean()) if cdf.correct.any() else None,
                                     "gradcam_enrichment_wrong": float(cdf[~cdf.correct].enrichment.mean()) if (~cdf.correct).any() else None,
                                     "crops_with_single_kind_only": crop_df[crop_df.kind != "mixed"].crop.tolist()}
        pd.DataFrame({"path": test.path, "true": [classes[i] for i in y], "pred": [classes[i] for i in pred],
                      "confidence": conf, "not_sure": uns}).to_csv(REPORTS / "test_predictions.csv", index=False)
        save_json(m, REPORTS / "test_metrics.json"); log.info("test: %s", {k: m[k] for k in ("accuracy", "macro_f1", "ece_calibrated")})
    if a.split in ("field", "all"):
        evaluate_field(P, test)
    if a.ood_dir:
        ood_check(P, a.ood_dir, test_uns)


if __name__ == "__main__":
    main()
