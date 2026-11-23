"""Reusable HTML components. Every dynamic value is escaped."""
from __future__ import annotations

from html import escape as esc

import streamlit as st

from krishi.i18n import t


def hero(title: str, sub: str = "", tag: str = "Krishi Netra · AI Crop Diagnostics") -> None:
    sub_html = f'<div class="hero-sub">{esc(sub)}</div>' if sub else ""
    st.markdown(
        f'<div class="hero">'
        f'<div class="hero-eyebrow"><span class="hero-dot"></span> {esc(tag)}</div>'
        f'<div class="hero-title">{esc(title)}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def card(html: str, kind: str = "") -> None:
    st.markdown(f'<div class="card {kind}">{html}</div>', unsafe_allow_html=True)


def bar(frac: float) -> str:
    return f'<div class="bar"><div style="width:{max(0.0, min(1.0, frac)) * 100:.0f}%"></div></div>'


def badge(kind: str, text: str) -> str:
    return f'<span class="badge b-{esc(kind)}">{esc(text)}</span>'


def tile(label: str, value: str) -> str:
    return f'<div class="tile"><div class="k">{esc(label)}</div><div class="v">{esc(value)}</div></div>'


def tiles(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (k, v) in zip(cols, items):
        col.markdown(tile(k, v), unsafe_allow_html=True)


def pct(x) -> str:
    return f"{x:.1%}" if isinstance(x, (int, float)) and x == x else t("na")


def num(x) -> str:
    return f"{int(x):,}" if isinstance(x, (int, float)) and x == x else t("na")


def kvk_block() -> None:
    from krishi.config import KVK_URL
    st.info(t("kvk"))
    st.markdown(f"[{t('kvk_link')}]({KVK_URL})")


def disease_details(info) -> None:
    """Knowledge-base details for one condition. Shows only what the KB contains."""
    st.caption("📖 " + t("from_kb"))
    if not info.in_kb:
        st.info(t("not_in_kb"))
    if info.description:
        st.markdown(f"**{t('description')}**  \n{info.description}")
    st.markdown(f"**{t('symptoms')}**  \n{info.symptoms}" if info.symptoms else f"_{t('no_symptoms')}_")
    if info.causal_agent or info.cause_group:
        chip = f' <span class="chip">{esc(t("cause_group"))}: {esc(info.cause_group.replace("_", " "))}</span>' if info.cause_group else ""
        st.markdown(f"**{t('causes')}**  \n{esc(info.causal_agent)}{chip}", unsafe_allow_html=True)
    if info.environment:
        st.markdown(f"**{t('env_factors')}**  \n{info.environment}")
    if info.prevention:
        st.markdown(f"**{t('prevention')}**  \n{info.prevention}")
    if info.care:
        st.markdown(f"**{t('care')}**  \n{info.care}")
    for s in info.sources:
        url = s.get("url", "")
        if url.startswith(("http://", "https://")):
            st.markdown(f"- {t('sources')}: [{s.get('name', url)}]({url})")
    if not info.sources:
        st.caption(t("no_source"))
    st.caption(t("no_pesticide"))
