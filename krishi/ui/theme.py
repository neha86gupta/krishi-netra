"""Global CSS Theme: Replicating the Krishi Netra Website Design System.
Fonts: Space Grotesk (display), Inter (UI), JetBrains Mono, Noto Sans Devanagari.
Top Navbar: Exact dark forest sticky navbar matching user's image with squircle leaf icon and pill tabs.
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

/* Hide Streamlit default sidebar and collapse controls per user request */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
  display: none !important;
}

/* Page Background matching website: soft mint-white with subtle dot grid */
html, body, .stApp {
  background-color: #f6faf5 !important;
  background-image: radial-gradient(rgba(27, 94, 32, 0.08) 1.2px, transparent 1.2px) !important;
  background-size: 24px 24px !important;
  font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--ink-primary) !important;
}

[data-testid="stHeader"] {
  display: none !important;
}

.block-container {
  padding-top: 0 !important;
  padding-bottom: 3.5rem !important;
  max-width: 1260px !important;
  margin: 0 auto !important;
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  color: var(--green-900);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* ==========================================================================
   TOP STICKY NAVBAR - EXACT REPLICATION OF USER IMAGE
   ========================================================================== */
.site-top-bar {
  position: sticky;
  top: 0;
  z-index: 9999;
  background: rgba(12, 41, 17, 0.98);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(200, 230, 201, 0.18);
  padding: 0.65rem 1.4rem;
  margin: 0 -1.5rem 1.5rem -1.5rem;
  box-shadow: 0 4px 22px rgba(9, 33, 13, 0.24);
}

.site-brand-wrap {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  user-select: none;
}
.site-brand-icon {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(67, 160, 71, 0.35);
}
.site-brand-name {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.28rem;
  color: #ffffff;
  letter-spacing: -0.015em;
}
.site-brand-tag {
  font-family: 'Inter', sans-serif;
  font-size: 0.66rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(200, 230, 201, 0.16);
  color: #c8e6c9;
  padding: 2px 7px;
  border-radius: 6px;
}

/* Horizontal Radio Nav styling matching user's image */
.top-nav-radio-wrap div[data-testid="stRadio"] {
  margin: 0 !important;
  padding: 0 !important;
}
.top-nav-radio-wrap div[role="radiogroup"] {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 3px !important;
  flex-wrap: wrap !important;
  background: transparent !important;
  border: none !important;
}
.top-nav-radio-wrap div[role="radiogroup"] label {
  background: transparent !important;
  border: none !important;
  margin: 0 !important;
  padding: 8px 13px !important;
  border-radius: 9px !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
}
.top-nav-radio-wrap div[role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.12) !important;
}
.top-nav-radio-wrap div[role="radiogroup"] label > div:first-child {
  display: none !important;
}
.top-nav-radio-wrap div[role="radiogroup"] label p {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif !important;
  font-size: 0.90rem !important;
  font-weight: 500 !important;
  color: rgba(241, 248, 233, 0.86) !important;
  margin: 0 !important;
  white-space: nowrap !important;
}
/* Active Pill Highlight matching image */
.top-nav-radio-wrap div[role="radiogroup"] label:has(input:checked),
.top-nav-radio-wrap div[role="radiogroup"] label[data-checked="true"] {
  background: rgba(200, 230, 201, 0.22) !important;
}
.top-nav-radio-wrap div[role="radiogroup"] label:has(input:checked) p,
.top-nav-radio-wrap div[role="radiogroup"] label[data-checked="true"] p {
  color: #ffffff !important;
  font-weight: 600 !important;
}

/* Utility buttons in top navbar */
.top-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(200, 230, 201, 0.25);
  border-radius: 9px;
  color: #ffffff;
  padding: 6px 12px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}
.top-action-btn:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: #ffffff;
}

/* ==========================================================================
   CARDS & COMPONENTS
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
.card.accent {
  border-left: 5px solid var(--green-600);
}
.card.warn {
  border-left: 5px solid var(--earth);
  background: #fffdf7;
}

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
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
  display: inline-block;
}
.hero-title {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  font-size: 2.25rem;
  font-weight: 700;
  color: #ffffff !important;
  line-height: 1.2;
  letter-spacing: -0.025em;
  margin: 0;
}
.hero-sub {
  font-size: 1.05rem;
  color: #d1fae5 !important;
  margin-top: 0.55rem;
  max-width: 54rem;
  line-height: 1.55;
  font-weight: 400;
}

/* Badges */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.02em;
  transition: transform 0.15s ease;
}
.badge-green { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.badge-amber { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-sky   { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.badge-coral { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
.badge-purple{ background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }

.chip {
  display: inline-block;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  background: var(--green-50);
  color: var(--green-800);
  border: 1px solid rgba(46, 125, 50, 0.2);
  font-size: 0.82rem;
  font-weight: 600;
  margin-right: 0.4rem;
  margin-bottom: 0.3rem;
  transition: all 0.18s ease;
}
.chip:hover {
  background: #dcfce7;
  color: #15803d;
  border-color: #86efac;
}

/* Buttons */
.stButton>button, .stDownloadButton>button {
  background: linear-gradient(135deg, var(--green-600) 0%, var(--green-700) 100%);
  color: #ffffff !important;
  border: 0;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.65rem 1.45rem;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(46, 125, 50, 0.25);
}
.stButton>button:hover, .stDownloadButton>button:hover {
  background: linear-gradient(135deg, var(--green-700) 0%, var(--green-900) 100%);
  color: #ffffff !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(46, 125, 50, 0.35);
}
.stButton>button:active, .stDownloadButton>button:active {
  transform: translateY(0);
}

[data-testid="stFileUploaderDropzone"] {
  background: #ffffff;
  border: 2px dashed rgba(46, 125, 50, 0.4);
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--green-600);
  background: var(--green-50);
}

.tile {
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 1.1rem 1.25rem;
  box-shadow: 0 2px 8px rgba(15, 51, 20, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tile:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(20, 54, 26, 0.08);
}
.tile .k { font-size: 0.85rem; color: var(--ink-muted); font-weight: 500; }
.tile .v { font-family: 'Space Grotesk', sans-serif; font-size: 1.85rem; font-weight: 700; color: var(--green-900); line-height: 1.2; }

.verdict-box {
  border-radius: 16px;
  padding: 1.25rem 1.45rem;
  margin-bottom: 1.1rem;
  box-shadow: 0 4px 16px rgba(20, 83, 45, 0.06);
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}
.verdict-box.healthy { background: #f0fdf4; border: 2px solid #22c55e; }
.verdict-box.diseased { background: #fef2f2; border: 2px solid #ef4444; }
.verdict-box.uncertain { background: #fffbeb; border: 2px solid #f59e0b; }
.verdict-icon { font-size: 2.3rem; line-height: 1; flex-shrink: 0; }
.verdict-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; line-height: 1.2; }
.verdict-title.healthy { color: #15803d; }
.verdict-title.diseased { color: #b91c1c; }
.verdict-title.uncertain { color: #b45309; }
.verdict-desc { font-size: 0.94rem; line-height: 1.5; margin-top: 0.3rem; }
.verdict-desc.healthy { color: #166534; }
.verdict-desc.diseased { color: #991b1b; }
.verdict-desc.uncertain { color: #92400e; }

.footer {
  margin-top: 2.5rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--line);
  color: var(--ink-muted);
  font-size: 0.85rem;
  line-height: 1.5;
  text-align: center;
}

@media (max-width: 900px) {
  .site-top-bar { padding: 0.5rem 0.8rem; }
  .site-brand-name { font-size: 1.1rem; }
  .hero { padding: 1.4rem 1.2rem; }
  .hero-title { font-size: 1.6rem; }
}
</style>"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
