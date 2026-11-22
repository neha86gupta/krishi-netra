"""Disease information centre: search, filters, cards. Content comes only from the knowledge base."""
from __future__ import annotations

from html import escape as esc

import streamlit as st

from krishi.config import split_class
from krishi.i18n import t
from krishi.knowledge import get_info, list_classes, pretty
from krishi.ui.components import card, disease_details, hero
from krishi.ui.services import kb, lang

MAX_CARDS = 50


def render() -> None:
    is_hi = lang() == "hi"
    hero(t("nav_info"), t("info_sub"))
    knowledge = kb()
    classes = list_classes(knowledge)
    if not classes:
        st.info(t("run_preprocess"))
        return
    L = lang()

    # Quick interactive summary metrics
    total_classes = len(classes)
    total_crops = len({split_class(c)[0] for c in classes})
    healthy_count = sum(1 for c in classes if "healthy" in split_class(c)[1].lower())
    disease_count = total_classes - healthy_count

    st.markdown(
        f"""
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.2rem;">
            <div class="tile" style="text-align:center; padding: 0.75rem;">
                <div class="k">{"कुल श्रेणियां (Total)" if is_hi else "Total Classes"}</div>
                <div class="v" style="font-size: 1.55rem; color: var(--forest);">{total_classes}</div>
            </div>
            <div class="tile" style="text-align:center; padding: 0.75rem;">
                <div class="k">{"फसलें (Crops)" if is_hi else "Crops Covered"}</div>
                <div class="v" style="font-size: 1.55rem; color: var(--emerald);">{total_crops}</div>
            </div>
            <div class="tile" style="text-align:center; padding: 0.75rem;">
                <div class="k">{"रोग श्रेणियां (Diseases)" if is_hi else "Diseases"}</div>
                <div class="v" style="font-size: 1.55rem; color: var(--earth);">{disease_count}</div>
            </div>
            <div class="tile" style="text-align:center; padding: 0.75rem;">
                <div class="k">{"स्वस्थ संदर्भ (Healthy)" if is_hi else "Healthy Controls"}</div>
                <div class="v" style="font-size: 1.55rem; color: #15803d;">{healthy_count}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    q = c1.text_input(t("search"), placeholder="e.g. blight, alternaria, tomato, fungus").strip().lower()
    crops = sorted({split_class(c)[0] for c in classes})
    crop = c2.selectbox(
        t("filter_crop"),
        [None] + crops,
        format_func=lambda x, _L=lang(): t("all", _L) if x is None else pretty(x),
    )
    cat = c3.selectbox(
        t("filter_category"),
        ["all", "healthy", "diseased"],
        format_func=lambda x, _L=lang(): t("all", _L)
        if x == "all"
        else t("cat_healthy" if x == "healthy" else "cat_diseased", _L),
    )
    groups = sorted(knowledge.get("cause_groups", {}))
    grp = c4.selectbox(
        t("cause_group"),
        [None] + groups,
        format_func=lambda x, _L=lang(): t("all", _L) if x is None else x.replace("_", " "),
    )

    rows = []
    for cls in classes:
        info = get_info(knowledge, cls, L)
        if crop and info.crop != crop:
            continue
        if cat != "all" and info.healthy != (cat == "healthy"):
            continue
        if grp and info.cause_group != grp:
            continue
        searchable_text = f"{cls} {info.crop} {info.condition} {info.symptoms} {info.causal_agent} {info.cause_group} {info.description}".lower()
        if q and q not in searchable_text:
            continue
        rows.append(info)

    st.caption(t("results_count", n=len(rows)) + " · " + t("kb_origin_note"))
    if not rows:
        st.info(t("no_results"))
        return

    cols = st.columns(2, gap="large")
    for i, info in enumerate(rows[:MAX_CARDS]):
        with cols[i % 2]:
            chips = f'<span class="chip">🌱 {esc(pretty(info.crop))}</span>'
            if info.cause_group:
                badge_color = "#15803d" if info.cause_group == "healthy" else "#b45309"
                chips += f'<span class="chip" style="color:{badge_color};">{esc(info.cause_group.replace("_", " "))}</span>'
            if info.causal_agent:
                chips += f'<span class="chip" style="font-style:italic;">{esc(info.causal_agent)}</span>'

            snippet = (info.symptoms[:140] + "…") if len(info.symptoms) > 140 else info.symptoms
            card(
                f'{chips}<div class="big" style="font-size:1.22rem">{esc(pretty(info.condition))}</div>'
                f'<div class="small" style="line-height:1.5;">{esc(snippet or t("no_symptoms"))}</div>'
            )
            with st.expander("📖 " + t("details")):
                disease_details(info)
