"""Crop health intelligence dashboard built from the user's own recorded predictions."""
from __future__ import annotations

import streamlit as st

from krishi import analytics as A
from krishi import charts
from krishi.i18n import t
from krishi.knowledge import pretty
from krishi.ui.components import card, hero, pct, tiles
from krishi.ui.services import get_store, owner_id


def render() -> None:
    hero(t("nav_insights"), t("ins_sub"))
    df = get_store().frame(owner_id())
    I = A.insights(df)
    if not I["total"]:
        card(t("hist_empty"), "accent")
        return
    st.caption(t("ins_note", n=I["total"]))
    tiles([(t("ins_total"), str(I["total"])), (t("ins_uncertain"), str(I["uncertain"])),
           (t("ins_mean_conf"), pct(I["mean_conf"])), (t("ins_crops"), str(I["n_crops"]))])
    st.write("")
    a, b = st.columns(2)
    a.plotly_chart(charts.hbar(I["top_predictions"].rename(lambda c: pretty(c.replace("___", " - "))), t("ins_top_diseases"), t("count")), use_container_width=True)
    b.plotly_chart(charts.hbar(I["by_crop"].rename(pretty), t("ins_crop_dist"), t("count"), charts.FOREST), use_container_width=True)
    c, d = st.columns(2)
    c.plotly_chart(charts.histogram(I["confidence"], t("ins_conf_dist"), t("confidence")), use_container_width=True)
    cat_names = {"healthy": t("cat_healthy"), "diseased": t("cat_diseased"), "uncertain": t("st_uncertain")}
    d.plotly_chart(charts.donut(I["category"], t("ins_category"), cat_names), use_container_width=True)
    st.plotly_chart(charts.line(I["activity"], t("ins_activity"), t("count")), use_container_width=True)
