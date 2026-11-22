"""Transforms, datasets, loaders. Reads data/processed; PlantDoc only via field_split.csv train/val parts (never the test part)."""
import random
import numpy as np
import pandas as pd
import torch
from PIL import Image, ImageFilter, ImageOps
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from torchvision import transforms as T
from src.utils import *


def _otsu(v):
    h, e = np.histogram(v.ravel(), bins=256); p = h / h.sum(); c = (e[:-1] + e[1:]) / 2
    w0 = np.cumsum(p); m = np.cumsum(p * c)
    return c[np.argmax((m[-1] * w0 - m) ** 2 / (w0 * (1 - w0) + 1e-12))]


_NATURAL = [(60, 90, 40), (90, 70, 50), (120, 120, 100), (30, 50, 30), (160, 150, 120), (110, 140, 80), (70, 60, 45)]


class RandomBackground:
    """Breaks the 'plain lab background' shortcut: on PlantVillage-style photos (uniform border) the leaf is cut out
    and pasted on a random natural-looking background. Photos whose border is NOT uniform (field photos) are left alone."""
    def __init__(self, p=0.6, size=IMG_SIZE):
        self.p, self.size = p, size

    def _background(self):
        s, kind = self.size, random.random()
        jit = lambda c: tuple(int(np.clip(v + random.randint(-25, 25), 0, 255)) for v in c)
        if kind < 0.25:                                   # solid colour
            return Image.new("RGB", (s, s), jit(random.choice(_NATURAL)))
        if kind < 0.5:                                    # gradient
            a, b = np.array(jit(random.choice(_NATURAL)), float), np.array(jit(random.choice(_NATURAL)), float)
            t = np.linspace(0, 1, s)[:, None, None]; g = a * (1 - t) + b * t
            arr = np.repeat(g, s, axis=1)
            return Image.fromarray(arr.astype(np.uint8)).rotate(random.choice([0, 90, 180, 270]))
        k = random.choice([4, 6, 10])                     # blotchy "soil / grass / other leaves" texture
        arr = np.array([[jit(random.choice(_NATURAL)) for _ in range(k)] for _ in range(k)], dtype=np.uint8)
        im = Image.fromarray(arr).resize((s, s), Image.BICUBIC)
        return im.filter(ImageFilter.GaussianBlur(random.uniform(1, 4)))

    def __call__(self, img):
        if random.random() > self.p:
            return img
        img = img.convert("RGB").resize((self.size, self.size))
        a = np.asarray(img, dtype=np.float32)
        border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
        if border.std(0).max() > 30:                      # busy border -> real-world photo, do not touch
            return img
        d = np.linalg.norm(a - np.median(border, 0), axis=2)
        m = d > _otsu(d)
        if not 0.15 < m.mean() < 0.95:                    # mask looks wrong -> skip
            return img
        mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))
        return Image.composite(img, self._background(), mask)


def train_tf(size=IMG_SIZE, bg_p=0.6):
    return T.Compose([
        RandomBackground(bg_p, size),
        T.RandomResizedCrop(size, scale=(0.4, 1.0), ratio=(0.8, 1.25)),
        T.RandomHorizontalFlip(), T.RandomVerticalFlip(), T.RandomRotation(30),
        T.ColorJitter(0.3, 0.3, 0.3, 0.05),
        T.RandomApply([T.GaussianBlur(5, (0.1, 2.0))], p=0.3),
        T.ToTensor(), T.Normalize(MEAN, STD),
        T.RandomErasing(p=0.3, scale=(0.02, 0.2))])


def eval_tf(size=IMG_SIZE):
    return T.Compose([T.Resize((size, size)), T.ToTensor(), T.Normalize(MEAN, STD)])


class LeafDataset(Dataset):
    """df needs columns: path (relative to project root, or absolute), y."""
    def __init__(self, df, tf):
        self.paths, self.y, self.tf = df["path"].tolist(), df["y"].astype(int).tolist(), tf

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        try:
            img = ImageOps.exif_transpose(Image.open(ROOT / self.paths[i])).convert("RGB")
        except Exception as e:  # noqa
            raise RuntimeError(f"Cannot read {self.paths[i]}: {e}") from e
        return self.tf(img), self.y[i]


def field_rows(part):
    """PlantDoc rows (train/val/test parts made by `python -m src.field_split`) as path,y."""
    p = FIELD / "field_split.csv"
    if not p.exists():
        raise SystemExit("Run `python -m src.field_split` first.")
    d = pd.read_csv(p, keep_default_na=False)
    return d[d.split == part][["path", "y"]]


def load_split(name, subset=None, seed=0, use_field=False, field_repeat=1):
    df = pd.read_csv(PROCESSED / f"{name}.csv", keep_default_na=False)
    if subset:
        n = subset if name == "train" else max(4, subset // 4)
        df = df.sample(frac=1, random_state=seed).groupby("y").head(n).reset_index(drop=True)
    if use_field and name in ("train", "val"):           # PlantDoc test part is NEVER added here
        fr = pd.concat([field_rows(name)] * (field_repeat if name == "train" else 1), ignore_index=True)
        df = pd.concat([df[["path", "y"]], fr], ignore_index=True)
    return df


def make_loaders(batch_size, subset=None, workers=0, balanced=False, use_field=False, field_repeat=3, bg_p=0.6):
    info = load_json(PROCESSED / "class_info.json")
    k = len(info["classes"])
    dfs = {s: load_split(s, subset, use_field=use_field, field_repeat=field_repeat) for s in ("train", "val")}
    cnt = np.bincount(dfs["train"]["y"], minlength=k).astype(float)
    w = cnt.sum() / (k * np.maximum(cnt, 1)); w = w / w.mean()
    sampler = None
    if balanced:
        sw = (1.0 / np.maximum(cnt, 1))[dfs["train"]["y"].values]
        sampler = WeightedRandomSampler(torch.tensor(sw, dtype=torch.double), len(sw), replacement=True)
    kw = dict(num_workers=workers, persistent_workers=workers > 0)
    loaders = {
        "train": DataLoader(LeafDataset(dfs["train"], train_tf(bg_p=bg_p)), batch_size, shuffle=sampler is None, sampler=sampler, **kw),
        "val": DataLoader(LeafDataset(dfs["val"], eval_tf()), batch_size, shuffle=False, **kw)}
    return loaders, info, w