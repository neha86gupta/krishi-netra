"""Global CSS Theme: Synchronized with the Krishi Netra Website Design System.
Fonts: Space Grotesk (display), Inter (UI), JetBrains Mono, Noto Sans Devanagari.
Palette: Deep Forest (#09210d, #0f3314, #1b5e20), Emerald (#2e7d32, #43a047), Mint Warm White (#f6faf5).
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

html, body, .stApp, [data-testid="stSidebar"] {
  font-family: 'Inter', 'Noto Sans Devanagari', -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--ink-primary);
  background: var(--surface-page);
}

.stApp {
  background: var(--surface-page);
}

[data-testid="stHeader"] {
  background: transparent;
}

.block-container {
  padding-top: 1.5rem;
  padding-bottom: 3rem;
  max-width: 1220px;
}

h1, h2, h3, h4 {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  color: var(--green-900);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Sidebar styling to match website deep green */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--green-950) 0%, var(--green-900) 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] * {
  color: #e8f5e9 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
  color: #14361a !important;
}

[data-testid="stSidebar"] .stRadio label {
  padding: 0.45rem 0.75rem;
  border-radius: 12px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 2px;
}

[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(255, 255, 255, 0.10);
  transform: translateX(4px);
}

/* Website-matching Brand Header */
.brand {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0.2rem 0 1rem 0;
  color: #ffffff !important;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  letter-spacing: -0.01em;
}
.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, var(--green-500) 0%, var(--green-700) 100%);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(67, 160, 71, 0.35);
}
.brand-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(67, 160, 71, 0.25);
  border: 1px solid rgba(102, 187, 106, 0.4);
  color: #a5d6a7 !important;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

/* Hero Section matching website page-hero */
.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, var(--green-950) 0%, var(--green-800) 100%);
  padding: 1.8rem 2.2rem;
  border-radius: 20px;
  margin-bottom: 1.4rem;
  border: 1px solid rgba(102, 187, 106, 0.2);
  box-shadow: 0 10px 30px rgba(9, 33, 13, 0.18);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='450' height='160' viewBox='0 0 450 160'%3E%3Cg fill='none' stroke='%2366bb6a' stroke-opacity='.18' stroke-width='1.5'%3E%3Cpath d='M20 80 C140 80 220 20 440 26'/%3E%3Cpath d='M80 80 L130 40 M120 78 L170 45 M160 70 L215 48 M110 82 L150 120 M150 76 L200 110 M200 60 L260 84'/%3E%3C/g%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right center;
}
.hero-title {
  font-family: 'Space Grotesk', 'Noto Sans Devanagari', sans-serif;
  font-size: 2.15rem;
  font-weight: 700;
  color: #ffffff !important;
  line-height: 1.2;
  letter-spacing: -0.02em;
}
.hero-sub {
  font-size: 1.05rem;
  color: #d1fae5 !important;
  margin-top: 0.5rem;
  max-width: 52rem;
  line-height: 1.55;
}

/* Cards matching website .card */
.card {
  background: var(--surface-card);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 1.35rem 1.55rem;
  margin-bottom: 1.1rem;
  box-shadow: 0 2px 10px rgba(15, 51, 20, 0.05);
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

/* Badges matching website styling */
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

/* Status verdict boxes */
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

.big {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--green-900);
  margin: 0.4rem 0 0.1rem 0;
  line-height: 1.2;
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

/* Interactive buttons matching website */
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

.stTabs [aria-selected="true"] {
  color: var(--green-800) !important;
  font-weight: 700;
  font-family: 'Space Grotesk', sans-serif;
  border-bottom: 3px solid var(--green-600) !important;
}

.footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  color: var(--ink-muted);
  font-size: 0.85rem;
  line-height: 1.5;
}

@media (max-width: 640px) {
  .hero { padding: 1.3rem 1.2rem; }
  .hero-title { font-size: 1.55rem; }
  .big { font-size: 1.45rem; }
  .block-container { padding-left: 0.9rem; padding-right: 0.9rem; }
}
</style>"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
