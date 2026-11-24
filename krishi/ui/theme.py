"""Global CSS Theme: Krishi Netra Design System.
Fonts: Space Grotesk (display), Inter (UI), JetBrains Mono, Noto Sans Devanagari.
Sidebar: Dark forest-green gradient matching the website navigation.
Page Background: Warm mint-white #f6faf5 with subtle agricultural dot pattern.
"""
import streamlit as st

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');

:root {
  --green-950: #09210d;
  --green-900: #0f3314;
  --green-800: #14361a;
  --green-700: #1b5e20;
  --green-600: #2e7d32;
  --green-500: #43a047;
  --green-400: #66bb6a;
  --green-200: #c8e6c9;
  --green-100: #e8f5e9;
  --green-50:  #f4faf3;

  --surface-page: #f6faf5;
  --surface-alt:  #ebf4e9;
  --surface-card: #ffffff;
  --border-light: rgba(27, 94, 32, 0.12);
  --border-med:   rgba(27, 94, 32, 0.24);

  --ink-primary:   #122b16;
  --ink-secondary: #37533b;
  --ink-muted:     #5e7862;

  --forest: #0f3314;
  --emerald: #2e7d32;
  --leaf: #43a047;
  --paper: #f6faf5;
  --sand: #e8f5e9;
  --earth: #b45309;
  --ink: #122b16;
  --muted: #5e7862;
  --line: rgba(27, 94, 32, 0.14);
}

/* ==========================================================================
   APP BACKGROUND — mint-white dot grid matching website
   ========================================================================== */
html, body, .stApp {
  background-color: #f6faf5 !important;
  background-image: radial-gradient(rgba(27, 94, 32, 0.08) 1.2px, transparent 1.2px) !important;
  background-size: 24px 24px !important;
  font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--ink-primary) !important;
}

[data-testid="stHeader"] { display: none !important; }

.block-container {
  padding-top: 1.6rem !important;
  padding-bottom: 3.5rem !important;
  max-width: 1200px !important;
  margin: 0 auto !important;
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  color: var(--green-900);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* ==========================================================================
   SIDEBAR — dark forest-green matching website header
   ========================================================================== */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #09210d 0%, #0f3314 55%, #122b16 100%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
  box-shadow: 4px 0 24px rgba(9, 33, 13, 0.35) !important;
}

/* All text in sidebar defaults to light green-white */
[data-testid="stSidebar"] * {
  color: #e8f5e9 !important;
}

/* Don't override select dropdowns inside sidebar */
[data-testid="stSidebar"] [data-baseweb="select"] * {
  color: #14361a !important;
}

/* Sidebar scrollbar */
[data-testid="stSidebar"]::-webkit-scrollbar { width: 4px; }
[data-testid="stSidebar"]::-webkit-scrollbar-track { background: transparent; }
[data-testid="stSidebar"]::-webkit-scrollbar-thumb { background: rgba(200,230,201,0.25); border-radius: 4px; }

/* ==========================================================================
   LANGUAGE RADIO (.sidebar-lang-box) — 2 horizontal pill tabs
   ========================================================================== */
.sidebar-lang-box div[data-testid="stRadio"] {
  margin: 0 !important;
  padding: 0 !important;
}
.sidebar-lang-box div[role="radiogroup"] {
  display: flex !important;
  flex-direction: row !important;
  gap: 3px !important;
  background: rgba(255, 255, 255, 0.07) !important;
  border: 1px solid rgba(200, 230, 201, 0.16) !important;
  border-radius: 11px !important;
  padding: 3px !important;
  width: 100% !important;
}
.sidebar-lang-box div[role="radiogroup"] label {
  flex: 1 !important;
  justify-content: center !important;
  text-align: center !important;
  padding: 6px 10px !important;
  border-radius: 8px !important;
  margin: 0 !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
}
.sidebar-lang-box div[role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.10) !important;
}
.sidebar-lang-box div[role="radiogroup"] label:has(input:checked) {
  background: rgba(200, 230, 201, 0.24) !important;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15) !important;
}
.sidebar-lang-box div[role="radiogroup"] label p {
  font-family: 'Inter', 'Noto Sans Devanagari', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  text-align: center !important;
  color: rgba(241, 248, 233, 0.85) !important;
  margin: 0 !important;
  white-space: nowrap !important;
}
.sidebar-lang-box div[role="radiogroup"] label:has(input:checked) p {
  color: #ffffff !important;
  font-weight: 700 !important;
}
/* Hide the dot */
.sidebar-lang-box div[role="radiogroup"] label > div:first-child {
  display: none !important;
}
.sidebar-lang-box label[data-testid="stWidgetLabel"] {
  display: none !important;
}

/* ==========================================================================
   NAVIGATION RADIO (.sidebar-nav-box) — Pill-styled nav items
   ========================================================================== */
.sidebar-nav-box div[data-testid="stRadio"] {
  margin: 0 !important;
  padding: 0 !important;
}
.sidebar-nav-box div[role="radiogroup"] {
  display: flex !important;
  flex-direction: column !important;
  gap: 3px !important;
  background: transparent !important;
  border: none !important;
  width: 100% !important;
}
.sidebar-nav-box div[role="radiogroup"] label {
  width: 100% !important;
  padding: 9px 13px !important;
  border-radius: 10px !important;
  transition: all 0.18s ease !important;
  margin: 0 !important;
  cursor: pointer !important;
  background: transparent !important;
  border-left: 3px solid transparent !important;
}
.sidebar-nav-box div[role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.09) !important;
  transform: translateX(3px) !important;
}
/* Active Pill Highlight matching website */
.sidebar-nav-box div[role="radiogroup"] label:has(input:checked) {
  background: rgba(200, 230, 201, 0.22) !important;
  border-left: 3px solid #66bb6a !important;
}
.sidebar-nav-box div[role="radiogroup"] label p {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif !important;
  font-size: 0.90rem !important;
  font-weight: 500 !important;
  color: rgba(241, 248, 233, 0.85) !important;
  margin: 0 !important;
}
.sidebar-nav-box div[role="radiogroup"] label:has(input:checked) p {
  color: #ffffff !important;
  font-weight: 700 !important;
}
/* Hide the dot */
.sidebar-nav-box div[role="radiogroup"] label > div:first-child {
  display: none !important;
}
.sidebar-nav-box label[data-testid="stWidgetLabel"] {
  display: none !important;
}

/* Sidebar action buttons (Sign In / Sign Out / Profile) */
[data-testid="stSidebar"] .stButton > button {
  background: rgba(255, 255, 255, 0.09) !important;
  border: 1px solid rgba(200, 230, 201, 0.26) !important;
  color: #e8f5e9 !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.84rem !important;
  padding: 0.45rem 0.8rem !important;
  box-shadow: none !important;
  transition: all 0.18s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255, 255, 255, 0.18) !important;
  border-color: rgba(200, 230, 201, 0.55) !important;
  color: #ffffff !important;
  transform: none !important;
}

/* ==========================================================================
   WORKFLOW STEPS HORIZONTAL GRID (3 Equal Columns)
   ========================================================================== */
.workflow-steps-wrap {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin-bottom: 1.35rem;
}
.workflow-step-card {
  background: #F8FAF9;
  border: 1px solid #D8E2DC;
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(15, 51, 20, 0.04);
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  min-height: 130px;
}
.workflow-step-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(20, 54, 26, 0.09);
  border-color: #86efac;
  background: #ffffff;
}
.workflow-step-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.55rem;
}
.workflow-step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1B4332;
  color: #ffffff;
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(27, 67, 50, 0.35);
  flex-shrink: 0;
}
.workflow-step-icon {
  font-size: 1.35rem;
  line-height: 1;
}
.workflow-step-title {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  font-size: 1.02rem;
  font-weight: 700;
  color: #1B4332;
  margin-bottom: 0.35rem;
  letter-spacing: -0.015em;
  display: flex;
  align-items: center;
  gap: 6px;
}
.workflow-step-desc {
  font-size: 0.83rem;
  line-height: 1.48;
  color: #496350;
  margin: 0;
}
.workflow-step-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.70;
  padding: 0 2px;
}

@media (max-width: 820px) {
  .workflow-steps-wrap {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .workflow-step-arrow {
    transform: rotate(90deg);
    padding: 4px 0;
  }
}

/* ==========================================================================
   CONSOLIDATED UNIFIED UPLOAD & CAMERA BOX
   ========================================================================== */
.unified-upload-container {
  background: #ffffff;
  border: 1px solid #D8E2DC;
  border-radius: 16px;
  padding: 1.25rem 1.45rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 18px rgba(15, 51, 20, 0.05);
}
.unified-upload-container div[data-testid="stRadio"] {
  margin: 0 0 1rem 0 !important;
  padding: 0 !important;
}
.unified-upload-container div[role="radiogroup"] {
  display: flex !important;
  flex-direction: row !important;
  gap: 6px !important;
  background: #f0f5f1 !important;
  border: 1px solid rgba(27, 94, 32, 0.12) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  width: 100% !important;
}
.unified-upload-container div[role="radiogroup"] label {
  flex: 1 !important;
  justify-content: center !important;
  text-align: center !important;
  padding: 8px 14px !important;
  border-radius: 9px !important;
  margin: 0 !important;
  cursor: pointer !important;
  transition: all 0.2s ease !important;
  background: transparent !important;
  border: none !important;
}
.unified-upload-container div[role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.75) !important;
}
.unified-upload-container div[role="radiogroup"] label:has(input:checked) {
  background: #1B4332 !important;
  box-shadow: 0 2px 8px rgba(27, 67, 50, 0.28) !important;
}
.unified-upload-container div[role="radiogroup"] label p {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif !important;
  font-size: 0.90rem !important;
  font-weight: 600 !important;
  color: #2d4a34 !important;
  margin: 0 !important;
  text-align: center !important;
  white-space: nowrap !important;
}
.unified-upload-container div[role="radiogroup"] label:has(input:checked) p {
  color: #ffffff !important;
  font-weight: 700 !important;
}
.unified-upload-container div[role="radiogroup"] label > div:first-child {
  display: none !important;
}
.unified-upload-container label[data-testid="stWidgetLabel"] {
  display: none !important;
}

/* Dropzone inside unified container */
.unified-upload-container [data-testid="stFileUploaderDropzone"] {
  background: #fbfdfb !important;
  border: 2px dashed rgba(27, 94, 32, 0.32) !important;
  border-radius: 14px !important;
  padding: 1.6rem 1.2rem !important;
  transition: all 0.2s ease !important;
}
.unified-upload-container [data-testid="stFileUploaderDropzone"]:hover {
  border-color: #2e7d32 !important;
  background: #f2faf3 !important;
}

/* ==========================================================================
   CARDS & COMPONENTS (Main Content Area)
   ========================================================================== */
.card {
  background: var(--surface-card);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 1.45rem 1.65rem;
  margin-bottom: 1.15rem;
  box-shadow: 0 4px 18px rgba(15, 51, 20, 0.05);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(20, 54, 26, 0.10);
  border-color: rgba(46, 125, 50, 0.35);
}
.card.accent { border-left: 5px solid var(--green-600); }
.card.warn   { border-left: 5px solid var(--earth); background: #fffdf7; }

/* Hero Section */
.hero {
  position: relative;
  overflow: hidden;
  background: radial-gradient(130% 140% at 85% 15%, rgba(52, 211, 153, 0.26) 0%, rgba(20, 83, 45, 0.94) 45%, #06220c 100%);
  padding: 2.1rem 2.4rem;
  border-radius: 22px;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(134, 239, 172, 0.24);
  box-shadow: 0 14px 38px rgba(6, 34, 12, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.15);
}
.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.20);
  color: #a7f3d0 !important;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
.hero-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #34d399; box-shadow: 0 0 8px #34d399; display: inline-block;
}
.hero-title {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  font-size: 2.25rem; font-weight: 700; color: #ffffff !important;
  line-height: 1.2; letter-spacing: -0.025em; margin: 0;
}
.hero-sub {
  font-size: 1.05rem; color: #d1fae5 !important;
  margin-top: 0.55rem; max-width: 54rem; line-height: 1.55; font-weight: 400;
}

/* Badges */
.badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 0.25rem 0.8rem; border-radius: 999px;
  font-weight: 700; font-size: 0.8rem; letter-spacing: 0.02em;
  transition: transform 0.15s ease;
}
.badge-green  { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.badge-amber  { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-sky    { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.badge-coral  { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-purple { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }

.chip {
  display: inline-block; padding: 0.2rem 0.75rem; border-radius: 999px;
  background: var(--green-50); color: var(--green-800);
  border: 1px solid rgba(46, 125, 50, 0.2);
  font-size: 0.82rem; font-weight: 600;
  margin-right: 0.4rem; margin-bottom: 0.3rem; transition: all 0.18s ease;
}
.chip:hover { background: #dcfce7; color: #15803d; border-color: #86efac; }

/* Buttons (main content area) */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, var(--green-600) 0%, var(--green-700) 100%);
  color: #ffffff !important;
  border: 0; border-radius: 12px; font-weight: 600; font-size: 0.95rem;
  padding: 0.65rem 1.45rem; transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(46, 125, 50, 0.25);
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background: linear-gradient(135deg, var(--green-700) 0%, var(--green-900) 100%);
  color: #ffffff !important; transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(46, 125, 50, 0.35);
}
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(0); }

[data-testid="stFileUploaderDropzone"] {
  background: #ffffff; border: 2px dashed rgba(46, 125, 50, 0.4);
  border-radius: 16px; padding: 1.5rem; transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--green-600); background: var(--green-50);
}

.tile {
  background: #ffffff; border: 1px solid var(--border-light);
  border-radius: 16px; padding: 1.1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(15, 51, 20, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tile:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(20, 54, 26, 0.08); }
.tile .k { font-size: 0.85rem; color: var(--ink-muted); font-weight: 500; }
.tile .v { font-family: 'Space Grotesk', sans-serif; font-size: 1.85rem; font-weight: 700; color: var(--green-900); line-height: 1.2; }

.verdict-box {
  border-radius: 16px; padding: 1.25rem 1.45rem; margin-bottom: 1.1rem;
  box-shadow: 0 4px 16px rgba(20, 83, 45, 0.06);
  display: flex; align-items: flex-start; gap: 1rem;
}
.verdict-box.healthy   { background: #f0fdf4; border: 2px solid #22c55e; }
.verdict-box.diseased  { background: #fef2f2; border: 2px solid #ef4444; }
.verdict-box.uncertain { background: #fffbeb; border: 2px solid #f59e0b; }
.verdict-icon   { font-size: 2.3rem; line-height: 1; flex-shrink: 0; }
.verdict-title  { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; line-height: 1.2; }
.verdict-title.healthy   { color: #15803d; }
.verdict-title.diseased  { color: #b91c1c; }
.verdict-title.uncertain { color: #b45309; }
.verdict-desc { font-size: 0.94rem; line-height: 1.5; margin-top: 0.3rem; }
.verdict-desc.healthy   { color: #166534; }
.verdict-desc.diseased  { color: #991b1b; }
.verdict-desc.uncertain { color: #92400e; }

.footer {
  margin-top: 2.5rem; padding-top: 1.2rem;
  border-top: 1px solid var(--line);
  color: var(--ink-muted); font-size: 0.85rem; line-height: 1.5; text-align: center;
}

@media (max-width: 900px) {
  .hero { padding: 1.4rem 1.2rem; }
  .hero-title { font-size: 1.6rem; }
}
</style>"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
