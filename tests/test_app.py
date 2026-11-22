import io
import time

import pytest
from PIL import Image
from streamlit.testing.v1 import AppTest

from krishi import config as C
from krishi.ui.services import get_store
from tests.conftest import APP_DIR

PAGES = ["diagnose", "info", "perf", "history", "insights", "demo", "labs"]


def new_app() -> AppTest:
    return AppTest.from_file(str(APP_DIR / "app.py"), default_timeout=60).run()


def png(colour=(60, 200, 60), size=(200, 200)) -> bytes:
    b = io.BytesIO(); Image.new("RGB", size, colour).save(b, "PNG"); return b.getvalue()


def texts(at) -> str:
    return " ".join([*(m.value for m in at.markdown), *(c.value for c in at.caption), *(s.value for s in at.success),
                     *(w.value for w in at.warning), *(i.value for i in at.info), *(e.value for e in at.error)])


@pytest.mark.parametrize("lang", ["English", "हिन्दी"])
@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_in_both_languages(page, lang):
    at = new_app()
    at.selectbox(key="lang_label").set_value(lang).run()
    at.radio(key="nav").set_value(page).run()
    assert not at.exception, [e.value for e in at.exception]
    assert not at.error, [e.value for e in at.error]
    body = texts(at)
    assert ("प्रयोगशाला" in body or "जाँच" in body or "भाषा" in body or "फोटो" in body or "रोग" in body or "इतिहास" in body or "फसल" in body or "डेमो" in body) if lang != "English" else True


def test_language_switch_translates_navigation():
    at = new_app()
    en = [o for o in at.radio(key="nav").options]
    at.selectbox(key="lang_label").set_value("हिन्दी").run()
    assert at.radio(key="nav").options != en and at.session_state["lang"] == "hi"


def test_full_diagnose_flow_runs_inference_once_and_saves_once(monkeypatch):
    get_store().clear("local")
    import src.predict as sp
    calls = {"n": 0}
    orig = sp.Predictor.predict
    def counting(self, img, with_cam=True):
        calls["n"] += 1; return orig(self, img, with_cam)
    monkeypatch.setattr(sp.Predictor, "predict", counting)

    at = new_app()
    at.file_uploader[0].upload("leaf.png", png(), "image/png").run()
    assert not at.exception and calls["n"] == 0                       # preview only, no inference yet
    assert any("Analyse" in b.label for b in at.button)
    next(b for b in at.button if "Analyse" in b.label).click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert calls["n"] == 1
    body = texts(at)
    assert "Late blight" in body and "Top 3 predictions" in body
    for _ in range(3):                                                  # extra reruns: no new inference or DB rows
        at.run()
    assert calls["n"] == 1
    assert len(get_store().frame("local")) == 1
    assert any(d.label.startswith("⬇️ Download PDF") for d in at.get("download_button"))


def test_invalid_upload_shows_error():
    at = new_app()
    at.file_uploader[0].upload("evil.jpg", b"plain text", "image/jpeg").run()
    assert any("could not be read" in e.value for e in at.error)


def test_history_insights_after_diagnosis_and_demo_filters():
    at = new_app()
    at.radio(key="nav").set_value("history").run()
    assert not at.exception
    at.radio(key="nav").set_value("insights").run()
    assert not at.exception and not at.error
    at.radio(key="nav").set_value("demo").run()
    assert not at.exception and "correct" in texts(at).lower()
    # more samples requested than the 8-image fixture holds -> handled
    ni = [n for n in at.number_input if n.label.startswith("Number of samples")][0]
    ni.set_value(24).run()
    assert not at.exception and "Only 8 samples match" in texts(at)


def test_performance_page_shows_real_values_and_na():
    at = new_app()
    at.radio(key="nav").set_value("perf").run()
    assert not at.exception
    vals = " ".join(m.value for m in at.markdown)
    assert "97.0%" in vals and "50.0%" in vals and "N/A" in vals       # lab acc, field acc, missing metrics -> N/A
