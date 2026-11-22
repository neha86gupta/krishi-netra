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
