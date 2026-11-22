"""Plotly figure builders (forest/emerald palette)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

FOREST, EMERALD, LEAF, EARTH, SAND, GREY = "#14532d", "#059669", "#84cc16", "#a16207", "#f4f1e6", "#94a3b8"
SCALE = [[0, "#f7f5ee"], [0.5, "#6ee7b7"], [1, FOREST]]


def _base(fig: go.Figure, h: int = 320, title: str | None = None) -> go.Figure:
    fig.update_layout(height=h, margin=dict(l=8, r=8, t=40 if title else 10, b=8), title=dict(text=title or "", font=dict(size=14)),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#1f2a1f"),
                      legend=dict(orientation="h", y=-0.2))
    fig.update_xaxes(gridcolor="#e6e8dc"); fig.update_yaxes(gridcolor="#e6e8dc")
    return fig


def hbar(s: pd.Series, title: str | None = None, xlabel: str = "", color: str = EMERALD) -> go.Figure:
    s = s.sort_values()
    fig = go.Figure(go.Bar(x=s.values, y=[str(i).replace("_", " ") for i in s.index], orientation="h", marker_color=color))
    fig.update_xaxes(title=xlabel)
    return _base(fig, max(240, 28 * len(s) + 70), title)


def histogram(values, title: str | None = None, xlabel: str = "") -> go.Figure:
    fig = go.Figure(go.Histogram(x=values, xbins=dict(start=0, end=1.0001, size=0.1), marker_color=EMERALD))
    fig.update_xaxes(title=xlabel, range=[0, 1])
    return _base(fig, 280, title)


def donut(s: pd.Series, title: str | None = None, names: dict | None = None) -> go.Figure:
    palette = {"healthy": EMERALD, "diseased": EARTH, "uncertain": GREY}
    names = names or {}
    fig = go.Figure(go.Pie(labels=[names.get(i, i) for i in s.index], values=list(s.values), hole=0.55, sort=False,
                           marker=dict(colors=[palette.get(i, LEAF) for i in s.index])))
    return _base(fig, 280, title)


def line(s: pd.Series, title: str | None = None, ylabel: str = "") -> go.Figure:
    fig = go.Figure(go.Scatter(x=list(s.index), y=list(s.values), mode="lines+markers", line=dict(color=EMERALD)))
    fig.update_yaxes(title=ylabel, rangemode="tozero")
    return _base(fig, 280, title)


def reliability(tbl: pd.DataFrame, labels: tuple[str, str, str]) -> go.Figure:
    mean_conf, acc, n = labels
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(dash="dash", color=GREY), name="ideal"))
    fig.add_trace(go.Bar(x=tbl["mean_conf"], y=tbl["accuracy"], width=0.07, marker_color=EMERALD, name=acc,
                         customdata=tbl["n"], hovertemplate=f"{mean_conf}: %{{x:.0%}}<br>{acc}: %{{y:.0%}}<br>%{{customdata}} {n}<extra></extra>"))
    fig.update_xaxes(title=mean_conf, range=[0, 1], tickformat=".0%"); fig.update_yaxes(title=acc, range=[0, 1], tickformat=".0%")
    return _base(fig, 340)


def grouped(categories: list[str], series: dict[str, list]) -> go.Figure:
    colors = [FOREST, LEAF, EARTH]
    fig = go.Figure([go.Bar(name=n, x=categories, y=v, marker_color=colors[i % 3]) for i, (n, v) in enumerate(series.items())])
    fig.update_layout(barmode="group"); fig.update_yaxes(range=[0, 1], tickformat=".0%")
    return _base(fig, 320)


def heatmap(cm: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Heatmap(z=cm.values, x=list(cm.columns), y=list(cm.index), colorscale=SCALE,
                               hovertemplate="true: %{y}<br>predicted: %{x}<br>count: %{z}<extra></extra>"))
    fig.update_yaxes(autorange="reversed"); fig.update_xaxes(tickangle=-60)
    return _base(fig, max(420, 14 * len(cm) + 200))
