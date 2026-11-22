"""Global CSS. Palette: forest #14532d, emerald #059669, leaf #84cc16, off-white #f7f5ee, earth #a16207."""
import streamlit as st

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');
:root{--forest:#14532d;--emerald:#059669;--leaf:#84cc16;--paper:#f7f5ee;--sand:#ecefe3;--earth:#a16207;--ink:#1f2a1f;--muted:#5b6b5d;--line:#d9dfcc;}
html,body,.stApp,[data-testid="stSidebar"]{font-family:'Public Sans','Noto Sans Devanagari',system-ui,sans-serif;color:var(--ink);}
.stApp{background:var(--paper);}
[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:1.4rem;max-width:1200px;}
h1,h2,h3{font-family:'Fraunces','Noto Sans Devanagari',Georgia,serif;color:var(--forest);letter-spacing:-.01em;}
[data-testid="stSidebar"]{background:var(--forest);}
[data-testid="stSidebar"] *{color:#e7f5ea !important;}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#14361a !important;}
[data-testid="stSidebar"] .stRadio label{padding:.4rem .65rem;border-radius:10px;transition:all .18s ease;}
[data-testid="stSidebar"] .stRadio label:hover{background:rgba(255,255,255,.14);transform:translateX(3px);}
.brand{font-family:'Fraunces',Georgia,serif;font-size:1.65rem;font-weight:700;margin:.2rem 0 .8rem 0;color:#fff !important;display:flex;align-items:center;gap:.4rem;}
.hero{position:relative;overflow:hidden;background:var(--forest);padding:1.6rem 1.9rem;border-radius:18px;margin-bottom:1.1rem;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='140' viewBox='0 0 420 140'%3E%3Cg fill='none' stroke='%2334d399' stroke-opacity='.22' stroke-width='1.4'%3E%3Cpath d='M20 70 C120 70 200 20 400 24'/%3E%3Cpath d='M70 70 L120 30 M110 69 L160 36 M150 62 L205 38 M100 71 L140 108 M140 66 L190 100 M190 50 L250 74'/%3E%3C/g%3E%3C/svg%3E");
 background-repeat:no-repeat;background-position:right center;box-shadow:0 4px 20px rgba(20,83,45,.15);}
.hero-title{font-family:'Fraunces','Noto Sans Devanagari',Georgia,serif;font-size:2rem;font-weight:700;color:#fff !important;line-height:1.2;}
.hero-sub{font-size:1.02rem;color:#d1fae5 !important;margin-top:.35rem;max-width:46rem;}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:.9rem;box-shadow:0 2px 6px rgba(20,83,45,.06);transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease;}
.card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(20,83,45,.12);border-color:#86efac;}
.card.accent{border-left:5px solid var(--emerald);}
.card.warn{border-left:5px solid var(--earth);background:#fffaf0;}
.steps{display:flex;gap:.8rem;margin-bottom:1rem;flex-wrap:wrap;}
.step{flex:1;min-width:150px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:.65rem .9rem;font-weight:600;transition:all .2s ease;}
.step:hover{border-color:var(--emerald);transform:translateY(-1px);}
.step b{display:inline-block;width:1.6rem;height:1.6rem;line-height:1.6rem;text-align:center;border-radius:50%;background:var(--emerald);color:#fff;margin-right:.5rem;}
.badge{display:inline-block;padding:.24rem .85rem;border-radius:999px;font-weight:700;font-size:.82rem;color:#fff !important;transition:transform .15s ease;}
.badge:hover{transform:scale(1.05);}
.b-high{background:var(--forest);} .b-moderate{background:var(--emerald);} .b-low{background:var(--earth);} .b-uncertain{background:#64748b;}
.b-healthy{background:var(--emerald);} .b-diseased{background:var(--earth);}
.chip{display:inline-block;padding:.15rem .65rem;border-radius:999px;background:var(--sand);color:var(--forest);font-size:.8rem;font-weight:600;margin-right:.35rem;transition:all .15s ease;}
.chip:hover{background:#dcfce7;color:#15803d;}
.big{font-family:'Fraunces','Noto Sans Devanagari',Georgia,serif;font-size:1.75rem;font-weight:700;color:var(--forest);margin:.45rem 0 .1rem 0;line-height:1.2;}
.sub{color:var(--muted);margin-bottom:.6rem;}
.bar{height:11px;border-radius:8px;background:var(--sand);overflow:hidden;margin:.15rem 0 .55rem 0;}
.bar>div{height:100%;border-radius:8px;background:linear-gradient(90deg,var(--leaf),var(--emerald));transition:width .4s ease;}
.row{display:flex;justify-content:space-between;gap:.6rem;font-size:.95rem;}
.small{font-size:.85rem;color:var(--muted);}
.tile{background:#fff;border:1px solid var(--line);border-radius:14px;padding:.9rem 1.1rem;transition:transform .2s ease,box-shadow .2s ease;}
.tile:hover{transform:translateY(-2px);box-shadow:0 6px 18px rgba(20,83,45,.08);}
.tile .k{font-size:.82rem;color:var(--muted);} .tile .v{font-family:'Fraunces',Georgia,serif;font-size:1.7rem;font-weight:700;color:var(--forest);line-height:1.15;}
.stButton>button,.stDownloadButton>button{background:var(--emerald);color:#fff;border:0;border-radius:10px;font-weight:600;padding:.55rem 1.25rem;transition:all .2s cubic-bezier(.4,0,.2,1);box-shadow:0 2px 6px rgba(5,150,105,.22);}
.stButton>button:hover,.stDownloadButton>button:hover{background:var(--forest);color:#fff;transform:translateY(-2px);box-shadow:0 6px 16px rgba(5,150,105,.35);}
.stButton>button:active,.stDownloadButton>button:active{transform:translateY(0);}
.stButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:3px solid var(--leaf);outline-offset:2px;}
[data-testid="stFileUploaderDropzone"]{background:#fff;border:2px dashed var(--emerald);border-radius:14px;transition:border-color .2s ease,background .2s ease;}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--forest);background:#f0fdf4;}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:.7rem 1rem;}
.stTabs [aria-selected="true"]{color:var(--forest);font-weight:700;border-bottom:3px solid var(--emerald) !important;}
.footer{margin-top:1.6rem;padding-top:.8rem;border-top:1px solid var(--line);color:var(--muted);font-size:.82rem;}
@media (max-width:640px){.hero{padding:1.1rem 1.1rem;}.hero-title{font-size:1.45rem;}.big{font-size:1.4rem;}.block-container{padding-left:.8rem;padding-right:.8rem;}}
@media (prefers-reduced-motion:reduce){*{transition:none !important;animation:none !important;}}
</style>"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
