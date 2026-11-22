import io
import re
import time

import numpy as np
import pandas as pd
import pytest
from PIL import Image

from krishi import analytics as A
from krishi import config as C
from krishi import i18n
from krishi.diagnosis import DiagnosisError, confidence_tier, from_raw, run_diagnosis
from krishi.gradcam import heatmap_image, views
from krishi.history import HistoryStore
from krishi.imaging import ImageError, make_thumbnail, sha256, to_pil, validate_upload
from src.predict import Predictor


def png_bytes(size=(128, 128), colour=(60, 140, 60), fmt="PNG"):
    b = io.BytesIO(); Image.new("RGB", size, colour).save(b, fmt); return b.getvalue()


# ---------------------------------------------------------------- i18n
def test_config_uses_project_utils():
    assert C.PROJECT_ERROR is None


def test_i18n_pairs_and_placeholders():
    for k, (en, hi) in i18n.S.items():
        assert en.strip() and hi.strip(), k
        assert set(re.findall(r"{(\w+)}", en)) == set(re.findall(r"{(\w+)}", hi)), f"placeholder mismatch in {k}"
    assert i18n.t("analyse", "hi") != i18n.t("analyse", "en")
    assert i18n.t("upload_label", "en", mb=8).count("8") == 1
    assert i18n.t("missing_key_x", "hi") == "missing_key_x"


# ---------------------------------------------------------------- imaging
def test_validate_ok_and_rgb():
    assert validate_upload(png_bytes(), "a.png").mode == "RGB"


@pytest.mark.parametrize("name,data,key", [
    ("a.gif", png_bytes(), "err_type"),
    ("a.jpg", b"not an image", "err_unreadable"),
    ("a.jpg", png_bytes((32, 32)), "err_small"),
    ("a.png", b"x" * (C.MAX_UPLOAD_MB * 1024 * 1024 + 1), "err_size"),
])
def test_validate_rejects(name, data, key):
    with pytest.raises(ImageError) as e:
        validate_upload(data, name)
    assert e.value.key == key


def test_validate_rejects_wrong_real_format():
    bmp = io.BytesIO(); Image.new("RGB", (100, 100)).save(bmp, "BMP")
    with pytest.raises(ImageError) as e:
        validate_upload(bmp.getvalue(), "fake.jpg")
    assert e.value.key == "err_format"


def test_decompression_bomb_guard(monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1000)
    with pytest.raises(ImageError) as e:
        validate_upload(png_bytes((100, 100)), "a.png")
    assert e.value.key == "err_huge"


def test_large_image_downscaled_and_exif_rotation():
    big = validate_upload(png_bytes((3000, 2500)), "big.png")
    assert max(big.size) == C.INFER_MAX_SIDE
    im = Image.new("RGB", (200, 100)); ex = Image.Exif(); ex[0x0112] = 6
    b = io.BytesIO(); im.save(b, "JPEG", exif=ex)
    assert validate_upload(b.getvalue(), "r.jpg").size == (100, 200)


def test_helpers():
    assert len(sha256(b"a")) == 64
    assert Image.open(io.BytesIO(make_thumbnail(Image.new("RGB", (500, 300))))).size[0] <= 192
    assert to_pil(np.full((4, 4, 3), 0.5)).getpixel((0, 0))[0] in (127, 128)
    assert to_pil(None) is None


# ---------------------------------------------------------------- diagnosis
def test_confidence_tiers():
    assert confidence_tier(0.99, "unsure") == "uncertain"
    assert confidence_tier(0.90, "ok") == "high"
    assert confidence_tier(0.70, "ok") == "moderate"
    assert confidence_tier(0.30, "ok") == "low"


def test_run_diagnosis_with_and_without_cam():
    img = Image.new("RGB", (128, 128), (60, 200, 60))
    d = run_diagnosis(Predictor(), img)
    assert d.cls == "Tomato___Late_blight" and d.cam_overlay is not None and not d.is_uncertain
    assert run_diagnosis(Predictor(), img, with_cam=False).cam_overlay is None


def test_bad_predictor_output():
    with pytest.raises(DiagnosisError):
        from_raw({"nope": 1})

    class Boom:
        def predict(self, *a, **k): raise RuntimeError("x")
    with pytest.raises(DiagnosisError):
        run_diagnosis(Boom(), Image.new("RGB", (80, 80)))


def test_gradcam_views():
    img = Image.new("RGB", (128, 96), (60, 200, 60))
    d = run_diagnosis(Predictor(), img)
    assert [k for k, _ in views(d, img)] == ["cam_original", "cam_heatmap", "cam_overlay"]
    assert heatmap_image(d.cam, img.size).size == img.size
    d.cam = None
    assert [k for k, _ in views(d, img)] == ["cam_original", "cam_overlay"]
    assert heatmap_image(np.zeros((5, 5)), (10, 10)) is None      # flat map is not fabricated


# ---------------------------------------------------------------- history
@pytest.fixture()
def store(tmp_path):
    return HistoryStore(tmp_path / "h.db", tmp_path / "thumbs", retention_days=30, keep_thumbs=True,
                        split=C.split_class)


def _diag(color=(60, 200, 60)):
    return run_diagnosis(Predictor(), Image.new("RGB", (128, 128), color))


def test_history_add_dedupe_and_isolation(store):
    d = _diag(); th = make_thumbnail(Image.new("RGB", (128, 128)))
    assert store.add("alice", d, "a.jpg", "h1", th) is not None
    assert store.add("alice", d, "a.jpg", "h1", th) is None          # rerun duplicate suppressed
    assert store.add("bob", d, "a.jpg", "h1", th) is not None         # different owner is separate
    assert len(store.frame("alice")) == 1 and len(store.frame("bob")) == 1
    assert store.frame("carol").empty
    rid = int(store.frame("alice").iloc[0]["id"])
    store.delete("bob", rid)                                           # wrong owner cannot delete
    assert len(store.frame("alice")) == 1


def test_history_clear_removes_thumbs_and_traversal_blocked(store, tmp_path):
    d = _diag()
    store.add("a", d, "../../evil.jpg", "h", b"jpegbytes")
    assert store.frame("a").iloc[0]["image_name"] == "evil.jpg"
    assert len(list((tmp_path / "thumbs").glob("*.jpg"))) == 1
    assert store.clear("a") == 1 and not list((tmp_path / "thumbs").glob("*.jpg"))
    assert store.thumb_bytes("../../etc/passwd") is None


def test_no_thumbs_when_disabled(tmp_path):
    s = HistoryStore(tmp_path / "h.db", tmp_path / "t", 0, keep_thumbs=False)
    s.add("a", _diag(), "x.jpg", "h", b"abc")
    assert s.frame("a").iloc[0]["thumb"] is None and not (tmp_path / "t").exists()


def test_retention_purge(store):
    store.add("a", _diag(), "x.jpg", "h", b"abc")
    import sqlite3
    con = sqlite3.connect(store.db_path); con.execute("UPDATE diagnoses SET ts='2000-01-01T00:00:00'"); con.commit(); con.close()
    assert store.purge_expired() == 1 and store.frame("a").empty


def test_csv_injection_and_export(store):
    d = _diag(); d.cls = "=cmd|' /C calc'!A0"
    store.add("a", d, "x.jpg", "h")
    csv = store.export_csv("a").decode("utf-8-sig")
    assert "'=cmd" in csv and "thumb" not in csv.splitlines()[0]


def test_legacy_table_migrated_once(tmp_path):
    import sqlite3
    db = tmp_path / "old.db"; con = sqlite3.connect(db)
    con.execute("CREATE TABLE h(ts TEXT, image TEXT, pred TEXT, conf REAL, status TEXT)")
    con.execute("INSERT INTO h VALUES('2026-01-01T10:00:00','a.jpg','Tomato___Late_blight',0.9,'ok')")
    con.execute("INSERT INTO h VALUES('2026-01-02T10:00:00','b.jpg','Tomato___healthy',0.4,'unsure')"); con.commit(); con.close()
    s = HistoryStore(db, tmp_path / "t", split=C.split_class)
    HistoryStore(db, tmp_path / "t", split=C.split_class)            # second start must not duplicate
    df = s.frame("local")
    assert len(df) == 2 and set(df["status"]) == {"high", "uncertain"} and "Late blight" in set(df["condition"])


# ---------------------------------------------------------------- analytics
def test_metrics_hand_computed():
    df = pd.DataFrame({"true": ["a", "a", "b", "b"], "pred": ["a", "b", "b", "b"]})
    m = A.metrics_from_predictions(df)
    assert m["accuracy"] == 0.75
    assert m["precision"] == pytest.approx((1.0 + 2 / 3) / 2)
    assert m["recall"] == pytest.approx((0.5 + 1.0) / 2)
    assert m["f1"] == pytest.approx((2 / 3 + 0.8) / 2)
    assert A.confusion(df).loc["a", "b"] == 1
    assert A.metrics_from_predictions(None) is None and A.metrics_from_predictions(pd.DataFrame({"x": [1]})) is None


def test_reliability_and_report_json():
    df = pd.DataFrame({"confidence": [0.95, 0.9, 0.55, 0.5], "correct": [True, True, True, False]})
    r = A.reliability_table(df)
    assert r["n"].sum() == 4 and r["accuracy"].max() == 1.0
    assert A.first_key({"x": {"accuracy": 0.9}}, ("accuracy",)) == 0.9 and A.first_key({}, ("a",)) is None
    rep = {"classification_report": {"a": {"precision": 1, "recall": 1, "f1-score": 1, "support": 3}, "macro avg": {}}}
    assert list(A.class_report_from_json(rep)["class"]) == ["a"]


def test_insights():
    s = HistoryStore.__new__(HistoryStore)
    df = pd.DataFrame({"ts": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-02"]), "cls": ["a", "a", "b"],
                       "crop": ["Tomato", "Tomato", "Potato"], "condition": ["Blight", "Blight", "healthy"],
                       "confidence": [0.9, 0.8, 0.3], "status": ["high", "moderate", "uncertain"]})
    I = A.insights(df)
    assert I["total"] == 3 and I["uncertain"] == 1 and I["category"]["diseased"] == 2 and I["n_crops"] == 2
    assert A.insights(df.iloc[0:0]) == {"total": 0}
