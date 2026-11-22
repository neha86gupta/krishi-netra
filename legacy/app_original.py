"""Krishi Netra - Streamlit app.  Run: streamlit run app.py"""
import io, sqlite3
from html import escape as esc
from datetime import datetime
import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError
from src.utils import *

st.set_page_config(page_title="Krishi Netra", page_icon="🌿", layout="wide")
MAX_MB, OK_EXT, KVK, DB = 8, {"jpg", "jpeg", "png"}, "https://kvk.icar.gov.in/", ROOT / "data" / "history.db"
TXT = {
    "en": {"unsure": "Not sure - retake the photo or consult an expert",
           "ref": "Reference advice - static knowledge base, NOT ML",
           "kvk": "Consult your nearest Krishi Vigyan Kendra (KVK) or agriculture officer before treating any crop.",
           "disc": "Educational prototype. Predictions can be wrong; this is not professional agricultural advice.",
           "tagline": "Snap a leaf. Spot the problem early.",
           "tip": "Tip: one leaf, in focus, filling most of the frame, in good daylight.",
           "healthy": "Looks healthy", "attention": "Possible disease", "notsure": "Not sure",
           "confidence": "Confidence", "photo": "Your photo", "heat": "Where the model looked", "care": "Care advice",
           "s1": "Take a clear photo", "s2": "Upload or use camera", "s3": "Read the result"},
    "hi": {"unsure": "निश्चित नहीं - कृपया फोटो दोबारा लें या विशेषज्ञ से सलाह लें",
           "ref": "संदर्भ सलाह - स्थिर ज्ञान-आधार, ML नहीं",
           "kvk": "किसी भी उपचार से पहले अपने नज़दीकी कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से संपर्क करें।",
           "disc": "यह एक शैक्षिक प्रोटोटाइप है। भविष्यवाणी गलत हो सकती है; यह पेशेवर कृषि सलाह नहीं है।",
           "tagline": "पत्ती की फोटो लें, बीमारी जल्दी पहचानें।",
           "tip": "सुझाव: एक पत्ती, साफ़ फोकस में, फ्रेम में बड़ी, अच्छी धूप में।",
           "healthy": "स्वस्थ दिखती है", "attention": "संभावित बीमारी", "notsure": "निश्चित नहीं",
           "confidence": "भरोसा", "photo": "आपकी फोटो", "heat": "मॉडल ने कहाँ देखा", "care": "देखभाल सलाह",
           "s1": "साफ़ फोटो लें", "s2": "अपलोड करें या कैमरा चलाएँ", "s3": "नतीजा पढ़ें"}}

CSS = """<style>
.stApp{background:linear-gradient(160deg,#f1f8e9 0%,#e8f5e9 40%,#dcedc8 100%);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#c8e6c9 0%,#a5d6a7 55%,#81c784 100%);}
[data-testid="stSidebar"] *{color:#14361a;}
.brand{font-size:1.6rem;font-weight:800;color:#1b5e20;margin:.2rem 0 .6rem 0;}
.hero{background:linear-gradient(120deg,#1b5e20 0%,#2e7d32 45%,#7cb342 100%);padding:1.5rem 1.8rem;border-radius:20px;margin-bottom:1.1rem;box-shadow:0 8px 24px rgba(27,94,32,.25);}
.hero-title{font-size:2.1rem;font-weight:800;color:#fff !important;line-height:1.2;}
.hero-sub{font-size:1.05rem;color:#f1f8e9 !important;margin-top:.3rem;}
.card{background:rgba(255,255,255,.9);border-radius:16px;padding:1rem 1.2rem;box-shadow:0 2px 12px rgba(46,125,50,.14);border-left:6px solid #7cb342;margin-bottom:.8rem;color:#1b3a1e;}
.steps{display:flex;gap:.8rem;margin-bottom:1rem;flex-wrap:wrap;}
.step{flex:1;min-width:160px;background:rgba(255,255,255,.85);border-radius:14px;padding:.7rem 1rem;box-shadow:0 2px 10px rgba(46,125,50,.12);color:#1b3a1e;font-weight:600;}
.step b{display:inline-block;width:1.7rem;height:1.7rem;line-height:1.7rem;text-align:center;border-radius:50%;background:linear-gradient(135deg,#2e7d32,#7cb342);color:#fff;margin-right:.5rem;}
.badge{display:inline-block;padding:.25rem .9rem;border-radius:999px;font-weight:700;font-size:.85rem;color:#fff !important;}
.b-ok{background:linear-gradient(90deg,#2e7d32,#66bb6a);}
.b-warn{background:linear-gradient(90deg,#ef6c00,#ffb300);}
.b-unsure{background:linear-gradient(90deg,#607d8b,#90a4ae);}
.big{font-size:1.7rem;font-weight:800;color:#1b5e20;margin:.5rem 0 .1rem 0;line-height:1.2;}
.crop{font-size:1rem;color:#4a6b4d;margin-bottom:.6rem;}
.bar{height:12px;border-radius:8px;background:#dcedc8;overflow:hidden;margin:.15rem 0 .55rem 0;}
.bar>div{height:100%;border-radius:8px;background:linear-gradient(90deg,#aed581,#2e7d32);}
.row{display:flex;justify-content:space-between;font-size:.95rem;color:#1b3a1e;}
.small{font-size:.85rem;color:#4a6b4d;}
.stButton>button{background:linear-gradient(90deg,#2e7d32,#66bb6a);color:#fff;border:0;border-radius:12px;font-weight:700;}
.stButton>button:hover{filter:brightness(1.08);color:#fff;}
[data-testid="stFileUploaderDropzone"]{background:rgba(255,255,255,.75);border:2px dashed #81c784;border-radius:16px;}
[data-testid="stMetric"]{background:rgba(255,255,255,.9);border-radius:14px;padding:.7rem 1rem;box-shadow:0 2px 10px rgba(46,125,50,.12);border-left:6px solid #7cb342;}
.stTabs [aria-selected="true"]{color:#1b5e20;font-weight:700;}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)


def T(k):
    return TXT[st.session_state.get("lang", "en")][k]


def hero(title, sub=""):
    st.markdown(f'<div class="hero"><div class="hero-title">🌿 {esc(title)}</div><div class="hero-sub">{esc(sub)}</div></div>',
                unsafe_allow_html=True)


def card(html):
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)


def bar(frac):
    return f'<div class="bar"><div style="width:{max(0.0, min(1.0, frac)) * 100:.0f}%"></div></div>'


@st.cache_resource(show_spinner="Loading model...")
def predictor():
    from src.predict import Predictor
    try:
        return Predictor()
    except Exception as e:  # noqa
        st.error(f"Model not available: {e}"); return None


def kb():
    p = SRC / "knowledge_base.json"
    return load_json(p) if p.exists() else {"classes": {}, "cause_groups": {}}


def validate(f):
    ext = getattr(f, "name", "camera.jpg").rsplit(".", 1)[-1].lower()
    if ext not in OK_EXT:
        return None, f"Unsupported file type .{ext}. Use JPG or PNG."
    if f.size > MAX_MB * 1024 * 1024:
        return None, f"File is larger than {MAX_MB} MB."
    try:
        img = Image.open(io.BytesIO(f.getvalue())); img.load()
    except (UnidentifiedImageError, OSError):
        return None, "This file could not be read as an image."
    if min(img.size) < 64:
        return None, "Image is too small (minimum 64 px)."
    return img.convert("RGB"), None


def db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS h(ts TEXT, image TEXT, pred TEXT, conf REAL, status TEXT)")
    return con


def advice(cls):
    k, lang = kb(), st.session_state.get("lang", "en")
    e = k["classes"].get(cls); groups = k.get("cause_groups", {})
    g = groups.get(e["cause_group"] if e else "unknown", groups.get("unknown", {}))
    if e and e.get("causal_agent"):
        st.write(f"**Cause (from the dataset paper):** {e['causal_agent']}")
    sym = e and (e.get(f"symptoms_{lang}") or e.get("symptoms_en"))
    st.write(f"**Symptoms:** {sym}" if sym else "_Symptom text not added yet (verification pending)._")
    if g:
        st.write("**General care (by cause group, not disease-specific):**"); st.write(g.get(f"advice_{lang}") or g.get("advice_en", ""))
    for s in (e or {}).get("sources", []):
        st.markdown(f"- Source: [{s.get('name', s['url'])}]({s['url']})")
    if not e or not e.get("sources"):
        st.caption("No verified per-disease source stored yet.")
    st.info(T("kvk")); st.markdown(f"[Find your nearest KVK]({KVK})")


def result_card(res, unsure):
    top = res["topk"][0]
    healthy = top["condition"].lower().startswith("healthy")
    if unsure:
        badge = f'<span class="badge b-unsure">❔ {esc(T("notsure"))}</span>'
    elif healthy:
        badge = f'<span class="badge b-ok">✅ {esc(T("healthy"))}</span>'
    else:
        badge = f'<span class="badge b-warn">⚠️ {esc(T("attention"))}</span>'
    head = esc(top["condition"]) if not unsure else esc(T("notsure"))
    sub = f'🌱 {esc(top["crop"])}' if not unsure else f'Best guess: {esc(top["crop"])} · {esc(top["condition"])}'
    conf = res["confidence"]
    rows = "".join(f'<div class="row"><span>{esc(r["crop"])} · {esc(r["condition"])}</span><span>{r["prob"]:.0%}</span></div>{bar(r["prob"])}'
                   for r in res["topk"])
    card(f'{badge}<div class="big">{head}</div><div class="crop">{sub}</div>'
         f'<div class="row"><b>{esc(T("confidence"))}</b><b>{conf:.0%}</b></div>{bar(conf)}'
         f'<div class="small">Top guesses</div>{rows}')


def page_diagnose():
    hero("Krishi Netra", T("tagline"))
    st.markdown(f'<div class="steps"><div class="step"><b>1</b>{esc(T("s1"))}</div><div class="step"><b>2</b>{esc(T("s2"))}</div>'
                f'<div class="step"><b>3</b>{esc(T("s3"))}</div></div>', unsafe_allow_html=True)
    P = predictor()
    if P is None:
        return
    mode = st.radio("Input", ["📁 Upload a photo", "📷 Use camera"], horizontal=True, label_visibility="collapsed")
    up = "Upload" in mode
    f = st.file_uploader("Leaf photo (JPG/PNG, max 8 MB)", type=list(OK_EXT)) if up else st.camera_input("Photograph one leaf")
    if not f:
        card(T("tip")); return
    img, err = validate(f)
    if err:
        st.error(err); return
    with st.spinner("Analysing..."):
        res = P.predict(img)
    with db() as con:
        con.execute("INSERT INTO h VALUES (?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), getattr(f, "name", "camera"),
                                                          res["topk"][0]["class"], res["confidence"], res["status"]))
    unsure = res["status"] == "unsure"
    a, b = st.columns([1, 1.2], gap="large")
    with a:
        st.image(img, caption=T("photo"), width=360)
    with b:
        result_card(res, unsure)
        if unsure:
            st.warning("⚠️ " + T("unsure")); st.write("Why: " + "; ".join(res["reasons"]))
    t1, t2 = st.tabs([f"🌾 {T('care')}", f"🔥 {T('heat')}"])
    with t1:
        st.caption(T("ref"))
        if unsure:
            st.info(T("kvk")); st.markdown(f"[Find your nearest KVK]({KVK})")
        else:
            advice(res["topk"][0]["class"])
    with t2:
        st.image(res["cam_overlay"], width=360, caption="Warm colours = regions that pushed the model toward its top guess")
        st.caption("Shows where the model looked, not whether it is right. If it highlights background, distrust the result.")


def page_info():
    hero("Disease information", T("ref"))
    classes = load_json(PROCESSED / "class_info.json")["classes"] if (PROCESSED / "class_info.json").exists() else list(kb()["classes"])
    if not classes:
        st.info("Run preprocessing first."); return
    c1, c2 = st.columns(2)
    crop = c1.selectbox("Crop", sorted({split_class(c)[0] for c in classes}))
    cls = c2.selectbox("Condition", [c for c in classes if split_class(c)[0] == crop], format_func=lambda c: split_class(c)[1])
    advice(cls)


def jget(name):
    p = REPORTS / name
    return load_json(p) if p.exists() else {}


def pct(x):
    return f"{x:.1%}" if isinstance(x, (int, float)) else "-"


def page_perf():
    hero("Model performance", "Loaded from reports/, never hard-coded")
    t, f, b = jget("test_metrics.json"), jget("field_metrics.json"), jget("baseline_metrics.json")
    c = st.columns(4)
    c[0].metric("Lab accuracy", pct(t.get("accuracy")), help="PlantVillage held-out test set (plain backgrounds)")
    c[1].metric("Field accuracy", pct(f.get("field_full_argmax", {}).get("accuracy")), help="Real PlantDoc photos, overlapping classes")
    c[2].metric("Lab vs field gap", pct(f.get("gap_full_argmax")), help="How much accuracy drops on real-world photos")
    c[3].metric("Simple baseline", pct(b.get("accuracy")), help="Colour histogram + logistic regression, for context")
    card("<b>How to read this:</b> lab photos have plain backgrounds, field photos do not. A big gap means the model "
         "is better at lab-style images than real farm photos. Both numbers are shown on purpose.")

    def show_json(name, title):
        p = REPORTS / name
        if p.exists():
            with st.expander(title):
                st.json(load_json(p))
        else:
            st.info(f"{name} not found - run the matching command from the README.")
    show_json("test_metrics.json", "Details: lab test set (PlantVillage held-out split)")
    show_json("field_metrics.json", "Details: field photos (PlantDoc) and lab-vs-field gap")
    show_json("baseline_metrics.json", "Details: classical baseline")
    if (REPORTS / "per_crop_metrics.csv").exists():
        st.markdown("**Per-crop results.** Crops marked `healthy_only`/`disease_only` have no healthy-vs-diseased contrast, so their accuracy only shows crop recognition.")
        st.dataframe(pd.read_csv(REPORTS / "per_crop_metrics.csv"), use_container_width=True)
    imgs = [(i, cap) for i, cap in (("test_confusion_matrix.png", "Confusion matrix (test)"), ("test_reliability.png", "Confidence calibration (test)"),
                                    ("field_reliability.png", "Confidence calibration (field)")) if (REPORTS / i).exists()]
    if imgs:
        cols = st.columns(len(imgs))
        for col, (i, cap) in zip(cols, imgs):
            col.image(str(REPORTS / i), caption=cap)
    d = REPORTS / "gradcam_samples"
    if d.exists() and list(d.glob("*.png")):
        pick = st.selectbox("Grad-CAM samples by crop (top: photo, bottom: heatmap)", sorted(p.name for p in d.glob("*.png")))
        st.image(str(d / pick))


def page_history():
    hero("History", "Your earlier diagnoses on this device")
    with db() as con:
        df = pd.read_sql("SELECT * FROM h ORDER BY ts DESC", con)
    if df.empty:
        st.info("No diagnoses yet."); return
    df["ts"] = pd.to_datetime(df["ts"])
    st.dataframe(df.rename(columns={"ts": "time", "image": "image name", "pred": "top prediction", "conf": "confidence"}), use_container_width=True)
    c1, c2 = st.columns(2)
    c1.caption("Most common top predictions (including 'not sure' cases)")
    c1.bar_chart(df.groupby("pred").size().sort_values(ascending=False).head(10), color="#43a047")
    c2.caption("Confidence over time"); c2.line_chart(df.set_index("ts")["conf"], color="#2e7d32")
    if st.checkbox("I want to clear the history") and st.button("Clear"):
        with db() as con:
            con.execute("DELETE FROM h")
        st.rerun()


def page_demo():
    hero("Demo mode", "See live predictions on photos the model never trained on")
    P = predictor()
    if P is None:
        return
    t1, t2 = st.tabs(["🧪 Held-out test samples", "🌾 Field photos (PlantDoc)"])
    with t1:
        st.caption("TEST SAMPLES: lab-style PlantVillage images never used for training. True label vs LIVE prediction.")
        seed = st.session_state.setdefault("seed", 0)
        if st.button("🔄 Draw new samples"):
            st.session_state.seed += 1; st.rerun()
        df = pd.read_csv(PROCESSED / "test.csv", keep_default_na=False).sample(6, random_state=seed)
        cols = st.columns(3)
        for i, (_, r) in enumerate(df.iterrows()):
            img = Image.open(ROOT / r.path).convert("RGB"); res = P.predict(img, with_cam=False); top = res["topk"][0]
            with cols[i % 3]:
                st.image(img, width=220)
                st.markdown(f"**True:** {r.label}  \n**Live:** {top['class']} ({res['confidence']:.0%}) {'✅' if top['class'] == r.label else '❌'}"
                            + ("  \n⚠️ not sure" if res["status"] == "unsure" else ""))
    with t2:
        p = REPORTS / "field_predictions.csv"
        if not p.exists():
            st.info("Run `python -m src.evaluate --split field` first."); return
        st.caption("REAL FIELD PHOTOS from PlantDoc (held-out test part). Mapped classes only.")
        fp = pd.read_csv(p); c1, c2 = st.columns(2)
        for col, ok, title in ((c1, True, "✅ Successes"), (c2, False, "❌ Failures")):
            col.markdown(f"**{title}**")
            for _, r in fp[fp.correct == ok].head(6).iterrows():
                col.image(str(ROOT / r.path), width=200, caption=f"true: {r.true} | pred: {r.pred} ({r.confidence:.0%})" + (" | not sure" if r.not_sure else ""))


st.sidebar.markdown('<div class="brand">🌿 Krishi Netra</div>', unsafe_allow_html=True)
st.session_state["lang"] = {"English": "en", "हिन्दी": "hi"}[st.sidebar.selectbox("Language / भाषा", ["English", "हिन्दी"])]
PAGES = {"🔍 Diagnose": page_diagnose, "📚 Disease information": page_info, "📊 Model performance": page_perf,
         "🕘 History": page_history, "🎯 Demo mode": page_demo}
page = st.sidebar.radio("Page", list(PAGES), label_visibility="collapsed")
st.sidebar.markdown('<div class="card small">📸 <b>Photo tips</b><br>One leaf · in focus · good daylight · fill the frame</div>', unsafe_allow_html=True)
PAGES[page]()
st.divider()
st.caption(T("disc") + " Data: PlantVillage (CC BY-SA 3.0), PlantDoc (CC BY 4.0).")