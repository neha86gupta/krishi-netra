"""Inspect -> clean -> group -> split -> leakage check -> class weights,
plus PlantVillage-vs-PlantDoc duplicate check.  python -m src.preprocess [--hash-thresh 6] [--keep-near-dups]"""
import argparse, hashlib, io, os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold
from tqdm import tqdm
from src.utils import *

log = get_logger("preprocess")
_POP = np.array([bin(i).count("1") for i in range(256)], dtype=np.uint8)
_ROTS = [None, Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_180, Image.Transpose.ROTATE_270]


def popcount(a):
    a = np.ascontiguousarray(a, dtype=np.uint64)
    return _POP[a.view(np.uint8).reshape(a.shape + (8,))].sum(-1, dtype=np.int32)


def _dhash(gray):
    g = np.asarray(gray.resize((9, 8), Image.LANCZOS), dtype=np.int16)
    return np.packbits((g[:, 1:] > g[:, :-1]).ravel()).view(np.uint64)[0]


def inspect_image(rel):
    """Fully decode (catches corrupt files); size, md5 of file bytes, dHash under 4 rotations."""
    try:
        data = (ROOT / rel).read_bytes()
        img = Image.open(io.BytesIO(data)); img.load()
        gray = img.convert("L")
        h = [_dhash(gray if r is None else gray.transpose(r)) for r in _ROTS]
        return {"ok": True, "w": img.width, "h": img.height, "md5": hashlib.md5(data).hexdigest(), "hash": h}
    except Exception as e:  # noqa
        return {"ok": False, "err": str(e)[:80]}


def hash_all(paths):
    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as ex:
        return list(tqdm(ex.map(inspect_image, paths), total=len(paths), desc="decode+hash"))


def assign_groups(df, H, thresh):
    """Keep images of the same leaf together: official leaf_id if complete, else near-duplicate components."""
    if (df["leaf_id"].astype(str).str.len() > 0).all():
        return (df["label"] + "::" + df["leaf_id"].astype(str)).values, "official leaf_id"
    parent = list(range(len(df)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    hi = df["hi"].values
    for _, idx in df.groupby("label").indices.items():
        hr = H[hi[idx]]; hb = hr[:, 0]
        for a in range(len(idx) - 1):
            d = popcount(hr[a + 1:] ^ hb[a]).min(1)
            for b in np.nonzero(d <= thresh)[0]:
                ra, rb = find(idx[a]), find(idx[a + 1 + b])
                if ra != rb:
                    parent[ra] = rb
    return np.array([f"g{find(i)}" for i in range(len(df))]), f"near-duplicate components (dHash<={thresh})"


def make_splits(df, seed, val_frac=0.10, test_frac=0.20):
    if df["split_official"].isin(["train", "test"]).all():
        df["split"], mode = df["split_official"], "official train/test"
    else:
        sg = StratifiedGroupKFold(n_splits=round(1 / test_frac), shuffle=True, random_state=seed)
        _, te = next(sg.split(df, df["label"], df["group"]))
        df["split"] = "train"; df.loc[te, "split"] = "test"; mode = "own group-aware split"
    dev = df[df.split == "train"]
    n = max(2, round(len(dev) / (val_frac * len(df))))
    sg = StratifiedGroupKFold(n_splits=n, shuffle=True, random_state=seed)
    _, va = next(sg.split(dev, dev["label"], dev["group"]))
    df.loc[dev.index[va], "split"] = "val"
    return df, mode


def leakage_check(df, H, thresh, drop):
    rep, S = {}, {s: df[df.split == s] for s in ("train", "val", "test")}
    for key in ("group", "md5"):
        rep[f"{key}_overlap"] = {f"{a}-{b}": len(set(S[a][key]) & set(S[b][key]))
                                 for a, b in (("train", "val"), ("train", "test"), ("val", "test"))}
    pairs = []
    for cls, sub in df.groupby("label"):
        tr = sub[sub.split == "train"]
        if tr.empty:
            continue
        Htr = H[tr["hi"].values]
        for s in ("val", "test"):
            q = sub[sub.split == s]
            for ridx, hb in zip(q.index, H[q["hi"].values, 0]):
                d = popcount(Htr ^ hb).min(1); j = int(d.argmin())
                if d[j] <= thresh:
                    pairs.append((ridx, tr.index[j], int(d[j]), s))
    rep["near_duplicate_cross_split_pairs"] = {s: sum(p[3] == s for p in pairs) for s in ("val", "test")}
    if pairs:
        pd.DataFrame([(df.at[a, "path"], df.at[b, "path"], d, s) for a, b, d, s in pairs],
                     columns=["held_out", "train_match", "hamming", "split"]).to_csv(REPORTS / "leakage_pairs.csv", index=False)
    if drop and pairs:
        gone = sorted({p[0] for p in pairs})
        df = df.drop(index=gone).reset_index(drop=True)
        rep["dropped_from_val_test"] = len(gone)
    if rep["group_overlap"]["train-val"] or rep["md5_overlap"]["train-val"]:
        log.warning("train/val overlap found - inspect reports/leakage_report.json")
    return df, rep


def field_overlap(H_ok, md5_ok, paths_ok, thresh):
    mp = FIELD / "plantdoc_manifest.csv"
    if not mp.exists():
        log.warning("No PlantDoc manifest; skipping PlantVillage-vs-PlantDoc check."); return None
    f = pd.read_csv(mp, keep_default_na=False)
    res, md5s, rows = hash_all(f["path"].tolist()), set(md5_ok), []
    for r in res:
        if not r["ok"]:
            rows.append({"ok": False, "exact_dup": False, "min_dist": -1, "pv_match": ""}); continue
        d = popcount(H_ok ^ r["hash"][0]).min(1); j = int(d.argmin())
        rows.append({"ok": True, "exact_dup": r["md5"] in md5s, "min_dist": int(d[j]), "pv_match": paths_ok[j]})
    out = pd.concat([f, pd.DataFrame(rows)], axis=1)
    out["in_pv"] = out["exact_dup"] | ((out["min_dist"] >= 0) & (out["min_dist"] <= thresh))
    out.to_csv(FIELD / "plantdoc_checked.csv", index=False)
    return {"n_plantdoc": len(out), "unreadable": int((~out.ok).sum()), "exact_duplicates_of_pv": int(out.exact_dup.sum()),
            "near_duplicates_of_pv": int(out.in_pv.sum()), "excluded_from_field_eval": int((out.in_pv | ~out.ok).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hash-thresh", type=int, default=6, help="max dHash Hamming distance (of 64) = near-duplicate")
    ap.add_argument("--keep-near-dups", action="store_true", help="do not drop near-duplicate val/test images")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    ensure_dirs()
    man = RAW / "plantvillage_manifest.csv"
    if not man.exists():
        raise SystemExit("Run `python -m src.download_data` first.")
    df = pd.read_csv(man, keep_default_na=False)
    res = hash_all(df["path"].tolist())
    df["ok"] = [r["ok"] for r in res]
    df["w"] = [r.get("w", 0) for r in res]; df["h"] = [r.get("h", 0) for r in res]
    df["md5"] = [r.get("md5", "") for r in res]
    H = np.array([r["hash"] if r["ok"] else [0] * 4 for r in res], dtype=np.uint64)
    df["hi"] = np.arange(len(df))
    S = {"n_manifest": len(df), "n_corrupt": int((~df.ok).sum())}
    ok_all = df[df.ok]
    pv_overlap_inputs = (H[ok_all["hi"].values], ok_all["md5"].tolist(), ok_all["path"].tolist())

    # --- inspection (before cleaning) ---
    S["image_sizes_top5"] = Counter(f"{w}x{h}" for w, h in zip(ok_all.w, ok_all.h)).most_common(5)
    S["n_classes_raw"] = int(ok_all.label.nunique())
    print(f"\nImages: {len(ok_all)} readable / {len(df)}; classes: {S['n_classes_raw']}; sizes: {S['image_sizes_top5']}")
    cnt = ok_all.label.value_counts()
    print(f"Smallest class: {cnt.idxmin()} ({cnt.min()});  largest: {cnt.idxmax()} ({cnt.max()})")

    # --- cleaning: corrupt files, exact duplicates ---
    df = df[df.ok].copy()
    drop, ndup, nconf = [], 0, 0
    for _, g in df[df.duplicated("md5", keep=False)].groupby("md5"):
        if g.label.nunique() > 1:
            drop += list(g.index); nconf += len(g); continue
        keep = g[g.split_official == "train"].index[:1].tolist() or g.index[:1].tolist()
        d = [i for i in g.index if i not in keep]; drop += d; ndup += len(d)
    df = df.drop(index=drop).reset_index(drop=True)
    S.update(exact_duplicates_removed=ndup, label_conflict_images_removed=nconf, n_after_cleaning=len(df))

    # --- groups, splits, leakage ---
    df["group"], S["grouping"] = assign_groups(df, H, a.hash_thresh)
    S["largest_group"] = int(df.group.value_counts().iloc[0])
    df, S["split_mode"] = make_splits(df, a.seed)
    df, leak = leakage_check(df, H, a.hash_thresh, drop=not a.keep_near_dups)
    save_json(leak, REPORTS / "leakage_report.json")
    print("\nLeakage report:", leak)

    # --- classes, crops, weights ---
    classes = sorted(df.label.unique())
    df["y"] = df.label.map({c: i for i, c in enumerate(classes)})
    df["crop"], df["condition"] = zip(*df.label.map(split_class))
    cols = ["path", "label", "y", "crop", "condition", "group", "md5", "split"]
    for s in ("train", "val", "test"):
        df[df.split == s][cols].to_csv(PROCESSED / f"{s}.csv", index=False)
    counts = df.pivot_table(index="label", columns="split", values="path", aggfunc="count", fill_value=0)
    counts.to_csv(REPORTS / "class_counts.csv")
    ntr = counts["train"].reindex(classes).values.astype(float)
    w = ntr.sum() / (len(classes) * np.maximum(ntr, 1)); w = w / w.mean()
    crops = {}
    for c in classes:
        crops.setdefault(split_class(c)[0], []).append(c)
    info_crops = {}
    for k, v in crops.items():
        hh = ["healthy" in split_class(x)[1].lower() for x in v]
        info_crops[k] = {"classes": v, "has_healthy": any(hh), "has_disease": not all(hh),
                         "kind": "mixed" if any(hh) and not all(hh) else ("healthy_only" if all(hh) else "disease_only")}
    save_json({"classes": classes, "train_counts": ntr, "class_weights": w, "crops": info_crops},
              PROCESSED / "class_info.json")
    S["splits"] = df.split.value_counts().to_dict()
    S["crop_kinds"] = {k: v["kind"] for k, v in info_crops.items()}
    print("\nSplit sizes:", S["splits"]); print("Crop kinds:", S["crop_kinds"])

    # --- PlantVillage vs PlantDoc hash check ---
    S["plantvillage_vs_plantdoc"] = field_overlap(*pv_overlap_inputs, a.hash_thresh)
    print("PlantDoc overlap:", S["plantvillage_vs_plantdoc"])
    save_json(S, REPORTS / "data_summary.json")


if __name__ == "__main__":
    main()
