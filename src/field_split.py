"""Split the usable PlantDoc images into train / val / test parts, keeping near-duplicates together.
Run AFTER src.preprocess and after reviewing data/field_test/class_map.json.
    python -m src.field_split [--test-frac 0.35] [--val-frac 0.15]
Writes data/field_test/field_split.csv (path,label,y,group,split)."""
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from src.preprocess import hash_all, assign_groups
from src.utils import *

log = get_logger("field_split")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-frac", type=float, default=0.35)
    ap.add_argument("--val-frac", type=float, default=0.15)
    ap.add_argument("--hash-thresh", type=int, default=6)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args(); ensure_dirs()
    cm = load_json(FIELD / "class_map.json")
    if not cm.get("reviewed"):
        log.warning("class_map.json is NOT marked reviewed - review it, set reviewed=true, then re-run this script.")
    classes = load_json(PROCESSED / "class_info.json")["classes"]
    mp = {k: v["plantvillage_class"] for k, v in cm["mapping"].items() if v["plantvillage_class"] in classes}
    chk = pd.read_csv(FIELD / "plantdoc_checked.csv", keep_default_na=False)
    keep = (chk.ok.astype(str) == "True") & (chk.in_pv.astype(str) == "False") & chk.label.isin(mp)
    df = chk[keep][["path", "label"]].reset_index(drop=True)
    df["y"] = df.label.map(lambda l: classes.index(mp[l]))
    res = hash_all(df.path.tolist())
    H = np.array([r["hash"] if r["ok"] else [0] * 4 for r in res], dtype=np.uint64)
    df["hi"] = np.arange(len(df)); df["leaf_id"] = ""
    df["group"], how = assign_groups(df, H, a.hash_thresh)
    log.info("grouping: %s; %d images, %d groups", how, len(df), df.group.nunique())
    sg = StratifiedGroupKFold(n_splits=round(1 / a.test_frac), shuffle=True, random_state=a.seed)
    rest, te = next(sg.split(df, df.y, df.group))
    df["split"] = "train"; df.loc[te, "split"] = "test"
    dev = df[df.split == "train"]
    sg = StratifiedGroupKFold(n_splits=max(2, round(1 / (a.val_frac / (1 - a.test_frac)))), shuffle=True, random_state=a.seed)
    _, va = next(sg.split(dev, dev.y, dev.group)); df.loc[dev.index[va], "split"] = "val"
    df[["path", "label", "y", "group", "split"]].to_csv(FIELD / "field_split.csv", index=False)
    print("\nPlantDoc parts:", df.split.value_counts().to_dict())
    print("Classes per part:", df.groupby("split").y.nunique().to_dict())
    print("Wrote", FIELD / "field_split.csv")


if __name__ == "__main__":
    main()