"""Download PlantVillage (HF mohanty/PlantVillage, 'color') and PlantDoc (GitHub zip).
Usage: python -m src.download_data [--pv-limit N] [--from-folder DIR] [--skip-pv] [--skip-plantdoc]"""
import argparse, re, shutil, sys, zipfile
from pathlib import Path
import pandas as pd
import requests
from tqdm import tqdm
from src.utils import *

log = get_logger("download")
PV_REPO = "mohanty/PlantVillage"
PD_ZIP = "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
MANUAL_PV = """
MANUAL FALLBACK (PlantVillage):
  1. git clone --depth 1 https://github.com/spMohanty/PlantVillage-Dataset   (large download)
  2. python -m src.download_data --from-folder <clone>/raw/color --skip-plantdoc
  (this route has no official split; preprocess.py builds a group-aware split itself)
  Or fetch the files from https://huggingface.co/datasets/mohanty/PlantVillage and point --from-folder at the class folders."""
MANUAL_PD = """
MANUAL FALLBACK (PlantDoc): download https://github.com/pratikkayal/PlantDoc-Dataset , then copy its class
folders into data/field_test/plantdoc/<class name>/ and write data/field_test/plantdoc_manifest.csv
with columns path,label (path relative to the project root)."""


def write_manifest(rows, path):
    pd.DataFrame(rows).to_csv(path, index=False)
    log.info("wrote %s (%d rows)", path, len(rows))


def download_plantvillage(limit=None):
    from datasets import load_dataset, Image as HFImage, ClassLabel
    ds = None
    for kw in ({"trust_remote_code": True}, {}):
        try:
            ds = load_dataset(PV_REPO, "color", **kw)
            break
        except Exception as e:  # noqa
            log.warning("load_dataset(%s) failed: %s", kw, str(e)[:200])
    if ds is None:
        raise RuntimeError("Could not load " + PV_REPO)
    rows, out = [], RAW / "plantvillage"
    for split, part in ds.items():
        feats = part.features
        img_col = next((k for k, v in feats.items() if isinstance(v, HFImage)), None)
        lab_col = next((k for k, v in feats.items() if isinstance(v, ClassLabel)), None) or \
            next((k for k in ("class_label", "label", "labels", "class") if k in feats), None)
        if img_col is None or lab_col is None:
            raise RuntimeError(f"Unexpected columns {list(feats)}")
        leaf_col = next((k for k in feats if "leaf" in k.lower() and "group" not in k.lower()), None)
        names = feats[lab_col].names if isinstance(feats[lab_col], ClassLabel) else None
        part = part.cast_column(img_col, HFImage(decode=False))
        if limit:
            part = part.shuffle(seed=0).select(range(min(limit, len(part))))
        sname = "val" if split.startswith("val") else split
        for i, ex in enumerate(tqdm(part, desc=f"saving {split}")):
            label = names[ex[lab_col]] if names else str(ex[lab_col])
            im = ex[img_col]
            data = im.get("bytes") or Path(im["path"]).read_bytes()
            fn = Path(im.get("path") or "").name or "img.jpg"
            dest = out / sname / label / f"{i:06d}_{fn}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            rows.append({"path": dest.relative_to(ROOT).as_posix(), "label": label, "split_official": sname,
                         "leaf_id": str(ex[leaf_col]) if leaf_col else ""})
    write_manifest(rows, RAW / "plantvillage_manifest.csv")


def import_pv_folder(folder):
    rows = []
    for cdir in sorted(p for p in Path(folder).iterdir() if p.is_dir()):
        for f in tqdm(list(cdir.iterdir()), desc=cdir.name):
            if f.suffix.lower() in IMG_EXT:
                dest = RAW / "plantvillage" / "all" / cdir.name / f.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dest)
                rows.append({"path": dest.relative_to(ROOT).as_posix(), "label": cdir.name,
                             "split_official": "", "leaf_id": ""})
    if not rows:
        raise RuntimeError(f"No class folders with images in {folder}")
    write_manifest(rows, RAW / "plantvillage_manifest.csv")


def _download(url, dest):
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); bar.update(len(chunk))


def download_plantdoc():
    """Reads images straight from the zip and saves them with SHORT names (Windows 260-char path limit)."""
    import hashlib
    z = RAW / "plantdoc_master.zip"
    if not z.exists():
        _download(PD_ZIP, z)
    rows = []
    with zipfile.ZipFile(z) as zf:
        for info in tqdm(zf.infolist(), desc="plantdoc"):
            parts = info.filename.split("/")
            # expected layout: PlantDoc-Dataset-master/<train|test>/<class>/<file>
            if info.is_dir() or len(parts) != 4 or parts[1] not in ("train", "test"):
                continue
            _, split, cls, name = parts
            ext = Path(name).suffix.lower()
            if ext not in IMG_EXT:
                continue
            short = hashlib.md5(name.encode("utf-8")).hexdigest()[:12] + ext
            dest = FIELD / "plantdoc" / cls / f"{split}_{short}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out)
            rows.append({"path": dest.relative_to(ROOT).as_posix(), "label": cls, "split_orig": split})
    if not rows:
        raise RuntimeError("No class folders found in the PlantDoc archive")
    write_manifest(rows, FIELD / "plantdoc_manifest.csv")
    print("\nPlantDoc classes (all used ONLY as a field test set):")
    print(pd.DataFrame(rows).groupby("label").size().to_string())

# ---- draft PlantDoc -> PlantVillage class map (token overlap; ALWAYS needs human review) ----
STOP = {"leaf", "leaves", "the", "of", "and", "including", "sour"}
ALIAS = {"soyabean": "soybean", "maize": "corn", "mites": "mite"}


def toks(s):
    return {ALIAS.get(t, t) for t in re.findall(r"[a-z0-9]+", s.lower())} - STOP


def draft_class_map(pd_classes, pv_classes):
    out = {}
    for pdc in pd_classes:
        t, cands = toks(pdc), []
        for pv in pv_classes:
            crop, _, cond = pv.partition("___")
            ct, dt = toks(crop), toks(cond) - toks(crop)
            if not cond or not (ct & t):
                continue
            rest = t - ct
            if "healthy" in dt:
                score = 1.0 if not rest else 0.0
            else:
                score = len(dt & rest) / len(dt | rest) if (dt | rest) else 0.0
            cands.append((pv, round(score, 2)))
        cands.sort(key=lambda c: -c[1])
        best = cands[0] if cands and cands[0][1] >= 0.5 else None
        out[pdc] = {"plantvillage_class": best[0] if best else None,
                    "score": best[1] if best else 0.0, "candidates": cands[:3]}
    return out


def write_class_map():
    pvm, pdm = RAW / "plantvillage_manifest.csv", FIELD / "plantdoc_manifest.csv"
    if not (pvm.exists() and pdm.exists()):
        log.warning("Need both manifests to draft class_map.json; skipping.")
        return
    pv = sorted(pd.read_csv(pvm, keep_default_na=False).label.unique())
    pdc = sorted(pd.read_csv(pdm, keep_default_na=False).label.unique())
    save_json({"reviewed": False,
               "note": "DRAFT. Edit each plantvillage_class (or set null), then set reviewed to true. "
                       "Auto-matching is a token heuristic; check every row.",
               "mapping": draft_class_map(pdc, pv)}, FIELD / "class_map.json")
    print(f"\nDraft written to {FIELD / 'class_map.json'} - please review it.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-pv", action="store_true")
    ap.add_argument("--skip-plantdoc", action="store_true")
    ap.add_argument("--pv-limit", type=int, default=None, help="images per official split (quick tests)")
    ap.add_argument("--from-folder", default=None, help="local PlantVillage raw/color folder (manual route)")
    a = ap.parse_args()
    ensure_dirs()
    ok = True
    if not a.skip_pv:
        try:
            import_pv_folder(a.from_folder) if a.from_folder else download_plantvillage(a.pv_limit)
        except Exception as e:  # noqa
            ok = False; log.error("PlantVillage failed: %s", e); print(MANUAL_PV)
    if not a.skip_plantdoc:
        try:
            download_plantdoc()
        except Exception as e:  # noqa
            ok = False; log.error("PlantDoc failed: %s", e); print(MANUAL_PD)
    write_class_map()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
