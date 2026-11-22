"""Grad-CAM plus a rough leaf-mask helper to check whether the CAM sits on the leaf or the background."""
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from src import model as M


class GradCAM:
    def __init__(self, model, arch):
        self.model, self.acts, self.grads = model.eval(), None, None
        self._h = M.target_layer(model, arch).register_forward_hook(self._fwd)

    def _fwd(self, _m, _i, out):
        self.acts = out.detach()
        if out.requires_grad:
            out.register_hook(lambda g: setattr(self, "grads", g.detach()))

    def remove(self):
        self._h.remove()

    def __call__(self, x, cls=None):
        """x: (1,3,H,W) normalised tensor. Returns (cam in [0,1] as HxW array, logits)."""
        with torch.enable_grad():
            x = x.clone().requires_grad_(True)
            self.model.zero_grad(set_to_none=True)
            logits = self.model(x)
            cls = int(logits.argmax(1)) if cls is None else cls
            logits[0, cls].backward()
            w = self.grads.mean((2, 3), keepdim=True)
            cam = F.relu((w * self.acts).sum(1, keepdim=True))
            cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)[0, 0]
            cam = cam - cam.min(); cam = cam / (cam.max() + 1e-8)
        return cam.detach().numpy(), logits.detach()


def overlay(pil, cam, alpha=0.45):
    import matplotlib
    img = np.asarray(pil.convert("RGB").resize(cam.shape[::-1]), dtype=float) / 255
    heat = matplotlib.colormaps["jet"](cam)[..., :3]
    return Image.fromarray((((1 - alpha) * img + alpha * heat) * 255).astype(np.uint8))


def _otsu(v):
    h, e = np.histogram(v.ravel(), bins=256); p = h / h.sum(); c = (e[:-1] + e[1:]) / 2
    w0 = np.cumsum(p); m = np.cumsum(p * c)
    return c[np.argmax((m[-1] * w0 - m) ** 2 / (w0 * (1 - w0) + 1e-12))]


def leaf_mask(pil, size=224):
    """Foreground = pixels far (RGB) from the median border colour. Only meaningful for plain-background
    lab images such as PlantVillage; unreliable on field photos."""
    a = np.asarray(pil.convert("RGB").resize((size, size)), dtype=np.float32)
    border = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    d = np.linalg.norm(a - np.median(border, 0), axis=2)
    return d > _otsu(d)


def cam_focus(cam, mask):
    """(CAM mass inside mask, mask area fraction, enrichment = ratio; 1.0 means no preference for the leaf)."""
    inside = float(cam[mask].sum() / (cam.sum() + 1e-8)); frac = float(mask.mean())
    return inside, frac, inside / max(frac, 1e-6)
