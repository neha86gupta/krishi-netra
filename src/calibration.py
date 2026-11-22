"""Temperature scaling, ECE, 'not sure' thresholds, feature-centroid gate."""
import torch
import torch.nn.functional as F
from tqdm import tqdm
from src import model as M


@torch.no_grad()
def collect(model, arch, loader):
    model.eval(); L, Fe, Y = [], [], []
    for x, y in tqdm(loader, leave=False, desc="forward"):
        f = M.features(model, arch, x)
        L.append(M.classify(model, arch, f)); Fe.append(f); Y.append(y)
    return torch.cat(L), torch.cat(Fe), torch.cat(Y)


def fit_temperature(logits, y):
    T = torch.nn.Parameter(torch.ones(1))
    opt = torch.optim.LBFGS([T], lr=0.1, max_iter=100)

    def closure():
        opt.zero_grad(); loss = F.cross_entropy(logits / T.clamp(min=0.05), y); loss.backward(); return loss
    opt.step(closure)
    return float(T.detach().clamp(min=0.05))


def entropy(p):
    return -(p * torch.log(p + 1e-12)).sum(1)


def ece(probs, y, bins=15):
    conf, pred = probs.max(1); acc = (pred == y).float(); edges = torch.linspace(0, 1, bins + 1); e = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            e += m.float().mean().item() * abs(acc[m].mean().item() - conf[m].mean().item())
    return e


def class_centroids(feats, y, k):
    f = F.normalize(feats, dim=1); c = torch.zeros(k, f.shape[1]); c.index_add_(0, y, f)
    return F.normalize(c, dim=1)


def feat_sim(feats, centroids, cls):
    return (F.normalize(feats, dim=1) * centroids[cls]).sum(1)


def choose_thresholds(probs, feats, centroids, y, target_acc=0.98, floor=0.5):
    """Heuristics tuned on VALIDATION (lab-style) data - expect them to be too lenient on field photos."""
    conf, pred = probs.max(1); ok = pred == y
    order = conf.argsort(descending=True)
    cum = ok[order].float().cumsum(0) / torch.arange(1, len(y) + 1)
    good = (cum >= target_acc).nonzero()
    tau = max(float(conf[order][int(good.max())]) if len(good) else 1.0, floor)
    ent_thr = float(torch.quantile(entropy(probs)[ok], 0.99)) if ok.any() else 1e9
    sim_thr = float(torch.quantile(feat_sim(feats, centroids, pred)[ok], 0.02)) if ok.any() else -1.0
    return {"conf_threshold": tau, "entropy_threshold": ent_thr, "sim_threshold": sim_thr}
