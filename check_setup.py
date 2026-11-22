"""Pre-presentation health check.  python check_setup.py [--no-model]
Prints [OK] / [!!] (blocks the demo) / [--] (optional, a page will show N/A). Exit code 1 if anything blocks."""
import importlib, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(errors="replace")   # Windows consoles: never crash on odd characters
except Exception:
    pass

bad = []


def ok(msg): print(f"[OK] {msg}")
def warn(msg): print(f"[--] {msg}")
def fail(msg): print(f"[!!] {msg}"); bad.append(msg)


def check_imports():
    for mod, need, fix in (("streamlit", True, "pip install -r requirements.txt"), ("plotly", True, "pip install plotly"),
                           ("reportlab", True, "pip install reportlab"), ("cv2", True, "pip install opencv-python-headless"),
                           ("torch", True, "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"),
                           ("torchvision", True, "see torch line"), ("PIL", True, "pip install Pillow"),
                           ("pandas", True, "pip install pandas"), ("numpy", True, "pip install numpy")):
        try:
            m = importlib.import_module(mod)
            ok(f"{mod} {getattr(m, '__version__', '')}")
            if mod == "streamlit":
                v = tuple(int(x) for x in m.__version__.split(".")[:2] if x.isdigit())
                if v < (1, 37):
                    fail(f"streamlit {m.__version__} is too old (need >= 1.37): pip install -U streamlit")
        except Exception as e:
            fail(f"{mod} missing ({type(e).__name__}) -> {fix}")


def check_files():
    required = ["models/best.pt", "src/predict.py", "src/utils.py", "src/knowledge_base.json",
                "data/processed/class_info.json", "app.py", "website/index.html"]
    optional = ["models/calibration.json", "models/centroids.pt", "data/processed/test.csv",
                "reports/test_metrics.json", "reports/field_metrics.json", "reports/baseline_metrics.json",
                "reports/field_predictions.csv", "reports/test_predictions.csv", "reports/per_crop_metrics.csv"]
    for r in required:
        (ok if (ROOT / r).exists() else fail)(r if (ROOT / r).exists() else f"{r} MISSING")
    for r in optional:
        (ok if (ROOT / r).exists() else warn)(r if (ROOT / r).exists() else f"{r} not found (related page/tab shows N/A)")


def check_model():
    try:
        from PIL import Image
        from src.predict import Predictor
        t0 = time.time(); P = Predictor(); load = time.time() - t0
        r = P.predict(Image.new("RGB", (256, 256), (60, 140, 60)))
        ok(f"model loads in {load:.1f}s, one prediction in {r['seconds']:.2f}s, {len(P.classes)} classes")
        (ok if "cam" in r else warn)("raw Grad-CAM map exposed" if "cam" in r else
                                      "predict() has no 'cam' key: copy the provided src/predict.py (standalone heatmap hidden otherwise)")
    except Exception as e:
        fail(f"model/Predictor failed: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}  |  project: {ROOT}\n")
    check_imports(); print(); check_files(); print()
    if "--no-model" not in sys.argv and not bad:
        check_model(); print()
    print("READY for the demo." if not bad else f"{len(bad)} blocking problem(s) above.")
    sys.exit(1 if bad else 0)
