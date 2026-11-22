"""Diagnosis history: search, filter, sort, view, export, delete."""
from __future__ import annotations

import base64
import json
from html import escape as esc

import pandas as pd
import streamlit as st

from krishi import config as C
from krishi.i18n import t
from krishi.knowledge import get_info, pretty
from krishi.ui.components import bar, badge, card, disease_details, hero
from krishi.ui.services import get_store, kb, lang, owner_id

STATUSES = ["high", "moderate", "low", "uncertain"]


def _data_uri(b: bytes | None) -> str | None:
    return f"data:image/jpeg;base64,{base64.b64encode(b).decode()}" if b else None


def _confirm_clear(store, owner: str, n: int) -> None:
    @st.dialog(t("clear_confirm_title"))
    def dlg() -> None:
        st.write(t("clear_confirm_body", n=n))
        a, b = st.columns(2)
        if a.button(t("confirm_delete"), type="primary"):
            store.clear(owner)
            st.rerun()
        if b.button(t("cancel")):
            st.rerun()
    dlg()


def render() -> None:
    hero(t("nav_history"), t("hist_sub"))
    store, owner = get_store(), owner_id()
    store.purge_expired()
    df = store.frame(owner)

    with st.expander("🔒 " + t("privacy")):
        st.write(t("privacy_multi" if C.MULTIUSER else "privacy_local"))
        st.write(t("retention_days", d=C.RETENTION_DAYS) if C.RETENTION_DAYS > 0 else t("retention_off"))
        st.write(t("thumbs_on" if C.KEEP_THUMBNAILS else "thumbs_off"))
        if C.KEEP_THUMBNAILS and st.button(t("delete_thumbs")):
            store.delete_thumbnails(owner)
            st.success(t("deleted"))
            st.rerun()

    if df.empty:
        card(esc(t("hist_empty")), "accent")
        return

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    q = c1.text_input(t("hist_search")).strip().lower()
    crop = c2.selectbox(t("col_crop"), [None] + sorted(df["crop"].replace("", pd.NA).dropna().unique()),
                        format_func=lambda x, _L=lang(): t("all", _L) if x is None else pretty(x))
    status = c3.selectbox(t("hist_status"), [None] + STATUSES, format_func=lambda x, _L=lang(): t("all", _L) if x is None else t(f"st_{x}", _L))
    sort = c4.selectbox(t("sort_by"), ["new", "old", "conf_hi", "conf_lo"], format_func=lambda x, _L=lang(): t(f"sort_{x}", _L))

    v = df
    if q:
        v = v[(v["cls"].str.lower().str.contains(q, regex=False)) | (v["crop"].str.lower().str.contains(q, regex=False))
              | (v["condition"].str.lower().str.contains(q, regex=False))]
    if crop:
        v = v[v["crop"] == crop]
    if status:
        v = v[v["status"] == status]
    v = {"new": v.sort_values("ts", ascending=False), "old": v.sort_values("ts"),
         "conf_hi": v.sort_values("confidence", ascending=False), "conf_lo": v.sort_values("confidence")}[sort]

    show = v.head(200)
    table = pd.DataFrame({
        t("col_time"): show["ts"], t("col_photo"): [_data_uri(store.thumb_bytes(x)) for x in show["thumb"]],
        t("col_crop"): show["crop"].map(pretty), t("col_pred"): show["condition"].map(pretty),
        t("col_conf"): show["confidence"], t("col_status"): show["status"].map(lambda s: t(f"st_{s}") if s in STATUSES else s)})
    st.dataframe(table, hide_index=True, use_container_width=True, column_config={
        t("col_photo"): st.column_config.ImageColumn(),
        t("col_time"): st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm"),
        t("col_conf"): st.column_config.ProgressColumn(format="percent", min_value=0.0, max_value=1.0)})
    st.caption(t("results_count", n=len(v)))

    a, b = st.columns([1, 1])
    a.download_button(t("export_csv"), store.export_csv(owner), file_name="krishi_netra_history.csv", mime="text/csv")
    if b.button("🗑️ " + t("clear_history")):
        _confirm_clear(store, owner, len(df))

    st.divider()
    ids = list(v["id"])
    if not ids:
        return
    labels = {int(r.id): f"{r.ts:%Y-%m-%d %H:%M} · {pretty(r.crop)} · {pretty(r.condition)} ({r.confidence:.0%})" for r in v.itertuples()}
    rid = st.selectbox(t("view_record"), ids, format_func=lambda i: labels[int(i)])
    rec = v[v["id"] == rid].iloc[0]
    left, right = st.columns([1, 2], gap="large")
    img_bytes = store.thumb_bytes(rec["thumb"])
    if img_bytes:
        left.image(img_bytes, use_container_width=True)
    with right:
        try:
            top3 = json.loads(rec["top3"] or "[]")
        except ValueError:
            top3 = []
        rows = "".join(f'<div class="row"><span>{esc(r["label"])}</span><b>{r["prob"]:.0%}</b></div>{bar(r["prob"])}' for r in top3)
        card(f'{badge(rec["status"], t("st_" + rec["status"]) if rec["status"] in STATUSES else rec["status"])}'
             f'<div class="big">{esc(pretty(rec["condition"]))}</div><div class="sub">{esc(pretty(rec["crop"]))} · {rec["ts"]:%Y-%m-%d %H:%M}</div>'
             f'<div class="row"><b>{esc(t("confidence"))}</b><b>{rec["confidence"]:.0%}</b></div>{bar(rec["confidence"])}{rows}', "accent")
        if rec["status"] in ("high", "moderate"):
            with st.expander(t("tab_info")):
                disease_details(get_info(kb(), rec["cls"], lang()))
        if st.button(t("delete_record"), key=f"del_{rid}"):
            store.delete(owner, int(rid))
            st.rerun()
