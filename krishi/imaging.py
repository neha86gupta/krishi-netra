"""Safe image handling: validation, normalisation, thumbnails, hashing."""
from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from krishi import config as C

Image.MAX_IMAGE_PIXELS = C.MAX_PIXELS


@dataclass
class ImageError(Exception):
    """Validation failure. ``key``/``params`` map to an i18n string."""
    key: str
    params: dict | None = None


def validate_upload(data: bytes, name: str = "camera.jpg") -> Image.Image:
    """Return an RGB PIL image or raise ImageError. Checks extension, size, real
    file format (not just the extension), pixel count and minimum size."""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else "jpg"
    if ext not in C.ALLOWED_EXT:
        raise ImageError("err_type", {"ext": ext})
    if len(data) > C.MAX_UPLOAD_MB * 1024 * 1024:
        raise ImageError("err_size", {"mb": C.MAX_UPLOAD_MB})
    try:
        img = Image.open(io.BytesIO(data))
        fmt = img.format
        if fmt not in C.ALLOWED_FORMATS:
            raise ImageError("err_format")
        img.load()
    except ImageError:
        raise
    except Image.DecompressionBombError as exc:
        raise ImageError("err_huge") from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageError("err_unreadable") from exc
    img = ImageOps.exif_transpose(img)   # phone photos store rotation in EXIF
    if min(img.size) < C.MIN_SIDE_PX:
        raise ImageError("err_small", {"px": C.MIN_SIDE_PX})
    img = img.convert("RGB")
    if max(img.size) > C.INFER_MAX_SIDE:
        img.thumbnail((C.INFER_MAX_SIDE, C.INFER_MAX_SIDE), Image.LANCZOS)
    return img


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_thumbnail(img: Image.Image, side: int = 192) -> bytes:
    thumb = img.copy()
    thumb.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    thumb.convert("RGB").save(buf, "JPEG", quality=80)
    return buf.getvalue()


def to_pil(obj) -> Image.Image | None:
    """Accept a PIL image or an HxW(x3) array (uint8 or float in 0..1)."""
    if obj is None:
        return None
    if isinstance(obj, Image.Image):
        return obj.convert("RGB")
    arr = np.asarray(obj)
    if arr.ndim not in (2, 3):
        return None
    if arr.dtype != np.uint8:
        arr = (np.clip(arr, 0, 1) * 255).astype(np.uint8) if arr.max() <= 1.0 else arr.clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr).convert("RGB")


def to_jpeg_bytes(img: Image.Image, quality: int = 88) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=quality)
    return buf.getvalue()


@dataclass
class QualityReport:
    """Pre-inference diagnostic report evaluating photo clarity, lighting, and framing."""
    is_ok: bool
    blur_score: float         # Laplacian variance (higher is sharper; < 70 indicates blur)
    is_blurry: bool
    glare_pct: float          # Percentage of clipped bright highlights (RGB all >= 245)
    has_glare: bool
    leaf_fill_pct: float      # Estimated percentage of frame occupied by plant tissue
    is_poor_framing: bool
    warnings: list[str]       # Human-readable advisory messages
    status: str               # "pass" | "warn" | "fail"


def check_quality(img: Image.Image) -> QualityReport:
    """Pre-inference input verification. Checks blur, specular glare, and leaf fill
    before running the neural network to avoid wasting scans on uninterpretable images."""
    import cv2
    rgb = np.asarray(img.convert("RGB"))
    
    # 1. Blur detection via Laplacian variance on grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = blur_score < 70.0
    
    # 2. Specular glare detection via clipped overexposed pixels
    clipped = (rgb[:, :, 0] >= 245) & (rgb[:, :, 1] >= 245) & (rgb[:, :, 2] >= 245)
    glare_pct = float(clipped.sum() / clipped.size * 100.0)
    has_glare = glare_pct > 7.5
    
    # 3. Leaf framing & fill check via vegetation HSV segmentation
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    green = (hsv[:, :, 0] >= 32) & (hsv[:, :, 0] <= 88) & (hsv[:, :, 1] >= 40) & (hsv[:, :, 2] >= 35)
    k = np.ones((5, 5), np.uint8)
    green = cv2.morphologyEx(green.astype(np.uint8), cv2.MORPH_OPEN, k).astype(bool)
    lesion = ((hsv[:, :, 0] >= 8) & (hsv[:, :, 0] < 32) & (hsv[:, :, 1] > 45) & (hsv[:, :, 2] > 40))
    near_leaf = cv2.dilate(green.astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    plant_tissue = green | (lesion & near_leaf)
    leaf_fill_pct = float(plant_tissue.sum() / plant_tissue.size * 100.0)
    is_poor_framing = leaf_fill_pct < 12.0
    
    warnings = []
    if is_blurry:
        warnings.append(f"Image appears blurry (sharpness score {blur_score:.0f} < 70). Hold your camera steady in bright daylight.")
    if has_glare:
        warnings.append(f"Direct sunlight glare detected ({glare_pct:.1f}% clipped highlights). Shade the leaf with your hand or hat.")
    if is_poor_framing:
        warnings.append(f"Leaf occupies only {leaf_fill_pct:.1f}% of the frame. Get closer so a single leaf fills most of the camera view.")
    
    status = "fail" if (is_blurry and (has_glare or is_poor_framing)) else ("warn" if warnings else "pass")
    is_ok = len(warnings) == 0
    
    return QualityReport(
        is_ok=is_ok,
        blur_score=blur_score,
        is_blurry=is_blurry,
        glare_pct=glare_pct,
        has_glare=has_glare,
        leaf_fill_pct=leaf_fill_pct,
        is_poor_framing=is_poor_framing,
        warnings=warnings,
        status=status,
    )

