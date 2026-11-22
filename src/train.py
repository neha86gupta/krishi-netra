"""Two-stage transfer learning (CPU). python -m src.train --help"""
import argparse, time
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader
from tqdm import tqdm
from src import model as M
from src.calibration import *
from src.dataset import LeafDataset, eval_tf, load_split, make_loaders
from src.utils import *

log = get_logger("train")


def run_epoch(model, loader, crit, opt=None):
    train = opt is not None
    if train:
        model.train(); M.set_bn_eval(model)
    else:
        model.eval()
    tot, n, P, Y = 0.0, 0, [], []
    with torch.set_grad_enabled(train):
        for x, y in tqdm(loader, leave=False, desc="train" if train else "val"):
            out = model(x); loss = crit(out, y)
            if train:
                opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
            tot += loss.item() * len(y); n += len(y); P.append(out.argmax(1)); Y.append(y)
    P, Y = torch.cat(P).numpy(), torch.cat(Y).numpy()
    return {"loss": tot / n, "acc": float((P == Y).mean()), "f1": float(f1_score(Y, P, average="macro", zero_division=0))}


def fit_stage(name, model, args, loaders, crit, epochs, lr, classes, best, rows):
    params = [p for p in model.parameters() if p.requires_grad]
    log.info("stage %s: %d trainable params", name, sum(p.numel() for p in params))
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1))
    bad = 0
    for ep in range(1, epochs + 1):
        t0 = time.time()
        tr = run_epoch(model, loaders["train"], crit, opt); va = run_epoch(model, loaders["val"], crit)
        lr_now = opt.param_groups[0]["lr"]; sched.step()
        rows.append({"stage": name, "epoch": ep, "lr": lr_now, **{f"train_{k}": v for k, v in tr.items()},
                     **{f"val_{k}": v for k, v in va.items()}, "seconds": time.time() - t0})
        log.info("%s ep%d  train acc %.3f | val acc %.3f macroF1 %.3f | %.0fs", name, ep, tr["acc"], va["acc"], va["f1"], time.time() - t0)
        if va["f1"] > best["f1"]:
            best.update(f1=va["f1"], stage=name, epoch=ep); bad = 0
            torch.save({"model_state": model.state_dict(), "arch": args.arch, "classes": classes, "img_size": IMG_SIZE,
                        "mean": MEAN, "std": STD, "preprocessing": "Resize((224,224)) -> ToTensor -> Normalize(ImageNet)",
                        "stage": name, "epoch": ep, "val": va, "args": vars(args)}, MODELS / args.out)
        else:
            bad += 1
            if bad >= args.patience:
                log.info("early stopping"); break


def calibrate(model, args, classes):
    ck = torch.load(MODELS / args.out, weights_only=False)
    model.load_state_dict(ck["model_state"]); model.eval()
    mk = lambda d: DataLoader(LeafDataset(d, eval_tf()), batch_size=64)
    L, Fv, Y = collect(model, args.arch, mk(load_split("val", args.subset, use_field=args.use_field)))
    _, Ft, Yt = collect(model, args.arch, mk(load_split("train", min(args.subset or 100, 100))))
    cen = class_centroids(Ft, Yt, len(classes))
    T = fit_temperature(L, Y); P = torch.softmax(L / T, 1)
    th = choose_thresholds(P, Fv, cen, Y, args.target_acc)
    ok = P.argmax(1) == Y
    unsure = (P.max(1).values < th["conf_threshold"]) | (entropy(P) > th["entropy_threshold"]) | \
             (feat_sim(Fv, cen, P.argmax(1)) < th["sim_threshold"])
    cal = {"temperature": T, **th, "target_acc": args.target_acc, "fit_on": "validation split (lab-style images)",
           "val_acc": float(ok.float().mean()), "val_ece_uncalibrated": ece(torch.softmax(L, 1), Y), "val_ece_calibrated": ece(P, Y),
           "val_coverage": float(1 - unsure.float().mean()),
           "val_accuracy_when_answering": float(ok[~unsure].float().mean()) if (~unsure).any() else None}
    save_json(cal, MODELS / "calibration.json"); torch.save(cen, MODELS / "centroids.pt")
    log.info("calibration: %s", cal)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="mobilenet_v3_large", choices=M.ARCHS)
    ap.add_argument("--epochs", type=int, default=3, help="stage 1 (frozen backbone)")
    ap.add_argument("--ft-epochs", type=int, default=0, help="stage 2 (fine-tune last blocks); 0 = skip")
    ap.add_argument("--ft-blocks", type=int, default=2)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--ft-lr", type=float, default=None, help="default: lr/10")
    ap.add_argument("--subset", type=int, default=None, help="max train images per class (val gets subset//4)")
    ap.add_argument("--patience", type=int, default=3)
    ap.add_argument("--balanced-sampler", action="store_true", help="instead of class-weighted loss")
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--target-acc", type=float, default=0.98)
    ap.add_argument("--no-pretrained", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="best.pt")
    ap.add_argument("--use-field", action="store_true", help="also train/validate on the PlantDoc train/val parts (run src.field_split first)")
    ap.add_argument("--field-repeat", type=int, default=3, help="repeat each PlantDoc train image this many times per epoch")
    ap.add_argument("--bg-p", type=float, default=0.6, help="probability of random-background augmentation on lab photos")
    args = ap.parse_args()
    if args.threads:
        torch.set_num_threads(args.threads)
    set_seed(args.seed); ensure_dirs()
    loaders, info, w = make_loaders(args.batch_size, args.subset, args.num_workers, args.balanced_sampler,args.use_field, args.field_repeat, args.bg_p)
    classes = info["classes"]
    model = M.build_model(args.arch, len(classes), pretrained=not args.no_pretrained)
    crit = nn.CrossEntropyLoss(weight=None if args.balanced_sampler else torch.tensor(w, dtype=torch.float32), label_smoothing=0.05)
    rows, best = [], {"f1": -1.0}
    M.freeze_backbone(model, args.arch)
    fit_stage("head", model, args, loaders, crit, args.epochs, args.lr, classes, best, rows)
    if args.ft_epochs > 0:
        model.load_state_dict(torch.load(MODELS / args.out, weights_only=False)["model_state"])
        M.unfreeze_last(model, args.arch, args.ft_blocks)
        fit_stage("finetune", model, args, loaders, crit, args.ft_epochs, args.ft_lr or args.lr / 10, classes, best, rows)
    pd.DataFrame(rows).to_csv(REPORTS / "train_log.csv", index=False)
    save_json({"best": best, "args": vars(args)}, REPORTS / "train_summary.json")
    calibrate(model, args, classes)
    log.info("done. best val macro-F1 %.4f (%s epoch %s)", best["f1"], best["stage"], best["epoch"])


if __name__ == "__main__":
    main()
