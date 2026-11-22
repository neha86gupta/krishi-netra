import io

import numpy as np
from PIL import Image
from pypdf import PdfReader

from krishi.diagnosis import run_diagnosis
from krishi.knowledge import DiseaseInfo, get_info
from krishi.report_pdf import build_report
from krishi.severity import estimate
from krishi.ui import components
from src.predict import Predictor
from tests.conftest import KB


def _pdf_text(b: bytes) -> str:
    return " ".join(p.extract_text() for p in PdfReader(io.BytesIO(b)).pages)


def test_pdf_confident_diagnosis_contents():
    img = Image.new("RGB", (200, 150), (60, 200, 60))
    d = run_diagnosis(Predictor(), img)
    info = get_info(KB, d.cls, "en")
    pdf = build_report(d, img, info)
    txt = _pdf_text(pdf)
    assert pdf[:4] == b"%PDF"
    for needle in ("Krishi Netra", "Late blight", "Top 3 predictions", "Educational prototype", "Dark water-soaked blotches",
                   "Phytophthora", "Grad-CAM overlay", "Example source", "Generated:"):
        assert needle in txt, needle
    assert len(PdfReader(io.BytesIO(pdf)).pages) <= 2


def test_pdf_uncertain_hides_disease_advice_and_handles_missing_cam():
    img = Image.new("RGB", (200, 150), (5, 5, 5))
    d = run_diagnosis(Predictor(), img, with_cam=False)
    assert d.is_uncertain
    txt = _pdf_text(build_report(d, img, get_info(KB, d.cls, "en")))
    assert "Not sure" in txt and "Dark water-soaked blotches" not in txt and "Grad-CAM not available" in txt


def test_pdf_unknown_disease_does_not_invent():
    img = Image.new("RGB", (100, 100), (60, 200, 60))
    d = run_diagnosis(Predictor(), img)
    txt = _pdf_text(build_report(d, img, DiseaseInfo(d.cls, d.crop, d.condition, in_kb=False)))
    assert "not in the knowledge base" in txt and "Symptom text not added yet" in txt


def test_knowledge_lookup_languages_and_fallback():
    assert get_info(KB, "Tomato___Late_blight", "hi").symptoms.startswith("गहरे")
    assert get_info(KB, "Tomato___Late_blight", "en").care == "Remove affected leaves."
    missing = get_info(KB, "Potato___Early_blight", "en")
    assert not missing.in_kb and missing.symptoms == "" and missing.sources == [] and missing.care == "Ask an expert."


def test_severity_bands():
    green = np.zeros((200, 200, 3), np.uint8); green[:] = (40, 170, 50)
    assert estimate(Image.fromarray(green)).band == "none"
    sick = green.copy(); sick[50:150, 50:150] = (150, 95, 30)      # brown patch inside the leaf
    r = estimate(Image.fromarray(sick))
    assert r.band in ("some", "lots") and r.overlay is not None and r.ratio and r.ratio > 0.05
    assert estimate(Image.fromarray(np.full((120, 120, 3), 255, np.uint8))).band == "na"   # no leaf found


def test_component_escaping():
    assert "<script>" not in components.badge("x", "<script>alert(1)</script>")
    assert components.pct(None) == "N/A" and components.pct(0.5) == "50.0%" and components.num(None) == "N/A"
