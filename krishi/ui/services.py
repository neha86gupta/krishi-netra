"""Cached resources and session helpers shared by pages."""
from __future__ import annotations

import uuid

import streamlit as st

from krishi import config as C
from krishi.config import log
from krishi.history import LOCAL_OWNER, HistoryStore
from krishi.knowledge import load_kb


@st.cache_resource(show_spinner=False)
def get_predictor():
    """Load the existing Predictor exactly once per process. Returns (predictor, error)."""
    try:
        from src.predict import Predictor
        return Predictor(), None
    except Exception as exc:  # noqa: BLE001
        log.exception("Model load failed")
        return None, f"{type(exc).__name__}: {exc}"


@st.cache_resource(show_spinner=False)
def get_store() -> HistoryStore:
    return HistoryStore(C.DB_PATH, C.THUMBS_DIR, C.RETENTION_DAYS, C.KEEP_THUMBNAILS, split=C.split_class)


def _mtime(p) -> float:
    return p.stat().st_mtime if p.exists() else 0.0


@st.cache_data(show_spinner=False)
def _kb_cached(mtime: float) -> dict:
    return load_kb()


def kb() -> dict:
    return _kb_cached(_mtime(C.KB_PATH))


def owner_id() -> str:
    """Single-device mode: shared 'local' owner. Shared deployments: one private id per browser session."""
    if not C.MULTIUSER:
        return LOCAL_OWNER
    return st.session_state.setdefault("owner", uuid.uuid4().hex)


def lang() -> str:
    return st.session_state.get("lang", "en")
