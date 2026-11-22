"""SQLite history. Every query is scoped to an ``owner`` so one visitor can never
read another's records. The original ``h`` table is left untouched and its rows are
copied once into the new ``diagnoses`` table under the owner ``local``."""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import pandas as pd

from krishi.config import DEDUPE_SECONDS, log
from krishi.diagnosis import Diagnosis

LOCAL_OWNER = "local"
COLS = ["id", "ts", "image_name", "cls", "crop", "condition", "confidence", "status", "top3", "thumb"]


def _csv_safe(v):
    """Neutralise spreadsheet formula injection in exported text."""
    return "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@") else v


class HistoryStore:
    def __init__(self, db_path: Path, thumbs_dir: Path, retention_days: int = 0,
                 keep_thumbs: bool = True, split: Callable[[str], tuple[str, str]] | None = None):
        self.db_path, self.thumbs_dir = Path(db_path), Path(thumbs_dir)
        self.retention_days, self.keep_thumbs = retention_days, keep_thumbs
        self._split = split or (lambda c: (c, c))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()
        self.purge_expired()

    def _con(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def _init(self) -> None:
        with closing(self._con()) as con, con:
            con.execute("""CREATE TABLE IF NOT EXISTS diagnoses(
                id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT NOT NULL, ts TEXT NOT NULL,
                image_name TEXT, image_hash TEXT, cls TEXT, crop TEXT, condition TEXT,
                confidence REAL, status TEXT, top3 TEXT, thumb TEXT)""")
            con.execute("CREATE INDEX IF NOT EXISTS ix_owner_ts ON diagnoses(owner, ts)")
            con.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
            self._migrate_legacy(con)

    def _migrate_legacy(self, con: sqlite3.Connection) -> None:
        done = con.execute("SELECT v FROM meta WHERE k='legacy_migrated'").fetchone()
        has_h = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='h'").fetchone()
        if done or not has_h:
            return
        rows = con.execute("SELECT ts, image, pred, conf, status FROM h").fetchall()
        for r in rows:
            crop, cond = self._split(r["pred"] or "")
            status = "uncertain" if r["status"] == "unsure" else (
                "high" if (r["conf"] or 0) >= 0.85 else "moderate" if (r["conf"] or 0) >= 0.60 else "low")
            con.execute("INSERT INTO diagnoses(owner,ts,image_name,cls,crop,condition,confidence,status,top3)"
                        " VALUES(?,?,?,?,?,?,?,?,?)",
                        (LOCAL_OWNER, r["ts"], r["image"], r["pred"], crop, cond, r["conf"], status, "[]"))
        con.execute("INSERT OR REPLACE INTO meta VALUES('legacy_migrated','1')")
        log.info("Migrated %d legacy history rows", len(rows))

    # ---- writes ---------------------------------------------------------------
    def add(self, owner: str, diag: Diagnosis, image_name: str, image_hash: str,
            thumb_jpeg: bytes | None = None) -> int | None:
        """Insert one record. Returns None if an identical record (same owner, photo
        and prediction) was written within DEDUPE_SECONDS - guards against reruns."""
        now = datetime.now()
        since = (now - timedelta(seconds=DEDUPE_SECONDS)).isoformat(timespec="seconds")
        with closing(self._con()) as con, con:
            dup = con.execute("SELECT id FROM diagnoses WHERE owner=? AND image_hash=? AND cls=? AND ts>=?",
                              (owner, image_hash, diag.cls, since)).fetchone()
            if dup:
                return None
            thumb_name = None
            if self.keep_thumbs and thumb_jpeg:
                self.thumbs_dir.mkdir(parents=True, exist_ok=True)
                thumb_name = f"{uuid.uuid4().hex}.jpg"
                (self.thumbs_dir / thumb_name).write_bytes(thumb_jpeg)
            top3 = [{"label": f"{r['crop']} · {r['condition']}", "prob": round(float(r["prob"]), 4)} for r in diag.topk[:3]]
            cur = con.execute(
                "INSERT INTO diagnoses(owner,ts,image_name,image_hash,cls,crop,condition,confidence,status,top3,thumb)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (owner, now.isoformat(timespec="seconds"), Path(image_name).name, image_hash, diag.cls, diag.crop,
                 diag.condition, diag.confidence, diag.status, json.dumps(top3), thumb_name))
            return cur.lastrowid

    def _delete_thumbs(self, names: list[str | None]) -> None:
        for n in names:
            if n:
                (self.thumbs_dir / Path(n).name).unlink(missing_ok=True)   # Path().name blocks traversal

    def delete(self, owner: str, rec_id: int) -> None:
        with closing(self._con()) as con, con:
            row = con.execute("SELECT thumb FROM diagnoses WHERE owner=? AND id=?", (owner, rec_id)).fetchone()
            con.execute("DELETE FROM diagnoses WHERE owner=? AND id=?", (owner, rec_id))
        if row:
            self._delete_thumbs([row["thumb"]])

    def clear(self, owner: str) -> int:
        with closing(self._con()) as con, con:
            thumbs = [r["thumb"] for r in con.execute("SELECT thumb FROM diagnoses WHERE owner=?", (owner,))]
            n = con.execute("DELETE FROM diagnoses WHERE owner=?", (owner,)).rowcount
        self._delete_thumbs(thumbs)
        return n

    def delete_thumbnails(self, owner: str) -> None:
        with closing(self._con()) as con, con:
            thumbs = [r["thumb"] for r in con.execute("SELECT thumb FROM diagnoses WHERE owner=? AND thumb IS NOT NULL", (owner,))]
            con.execute("UPDATE diagnoses SET thumb=NULL WHERE owner=?", (owner,))
        self._delete_thumbs(thumbs)

    def purge_expired(self) -> int:
        if self.retention_days <= 0:
            return 0
        cutoff = (datetime.now() - timedelta(days=self.retention_days)).isoformat(timespec="seconds")
        with closing(self._con()) as con, con:
            thumbs = [r["thumb"] for r in con.execute("SELECT thumb FROM diagnoses WHERE ts<?", (cutoff,))]
            n = con.execute("DELETE FROM diagnoses WHERE ts<?", (cutoff,)).rowcount
        self._delete_thumbs(thumbs)
        return n

    # ---- reads ----------------------------------------------------------------
    def frame(self, owner: str) -> pd.DataFrame:
        with closing(self._con()) as con:
            df = pd.read_sql("SELECT id,ts,image_name,cls,crop,condition,confidence,status,top3,thumb "
                             "FROM diagnoses WHERE owner=? ORDER BY ts DESC, id DESC", con, params=(owner,))
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        return df

    def thumb_bytes(self, name: str | None) -> bytes | None:
        if not name:
            return None
        p = self.thumbs_dir / Path(name).name
        return p.read_bytes() if p.exists() else None

    def export_csv(self, owner: str) -> bytes:
        df = self.frame(owner).drop(columns=["thumb"])
        df = df.rename(columns={"image_name": "image", "cls": "class"})
        return df.map(_csv_safe).to_csv(index=False).encode("utf-8-sig")
