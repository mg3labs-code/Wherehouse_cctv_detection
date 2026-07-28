"""SQLite event store for GLS safety analytics."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..config import Config


_LOCK = threading.Lock()
_DB_PATH = os.path.join(Config.OUTPUT_DIR, "gls_safety.db")


def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def _db():
    with _LOCK:
        conn = _connect()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def init_db() -> None:
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                source TEXT,
                profile TEXT,
                event_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                payload TEXT,
                worksite TEXT DEFAULT 'Chirala Godown'
            );
            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                source TEXT,
                profile TEXT,
                frames INTEGER DEFAULT 0,
                violations INTEGER DEFAULT 0
            );
            """
        )


def add_event(
    event_type: str,
    *,
    source: str = "",
    profile: str = "warehouse_aisle",
    severity: str = "medium",
    payload: Optional[Dict[str, Any]] = None,
    worksite: str = "Chirala Godown",
) -> int:
    ts = datetime.now().isoformat()
    with _db() as conn:
        cur = conn.execute(
            """
            INSERT INTO events (ts, source, profile, event_type, severity, payload, worksite)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ts,
                source,
                profile,
                event_type,
                severity,
                json.dumps(payload or {}),
                worksite,
            ),
        )
        return int(cur.lastrowid)


def list_events(
    *,
    limit: int = 100,
    worksite: Optional[str] = None,
    event_type: Optional[str] = None,
    since_hours: Optional[int] = None,
) -> List[Dict[str, Any]]:
    clauses = ["COALESCE(source, '') != 'demo'"]
    args: List[Any] = []
    if worksite and worksite != "all":
        clauses.append("worksite = ?")
        args.append(worksite)
    if event_type and event_type != "all":
        clauses.append("event_type = ?")
        args.append(event_type)
    if since_hours:
        since = (datetime.now() - timedelta(hours=since_hours)).isoformat()
        clauses.append("ts >= ?")
        args.append(since)
    where = " WHERE " + " AND ".join(clauses)
    args.append(limit)
    with _db() as conn:
        rows = conn.execute(
            f"SELECT * FROM events{where} ORDER BY id DESC LIMIT ?",
            args,
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        try:
            item["payload"] = json.loads(item.get("payload") or "{}")
        except json.JSONDecodeError:
            item["payload"] = {}
        out.append(item)
    return out


def _count_video_assets() -> int:
    """Real camera/video sources on disk (not a demo constant)."""
    import glob

    video_dir = os.path.join(Config.DATA_DIR, "videos")
    if not os.path.isdir(video_dir):
        return 0
    files = []
    for ext in ("*.mp4", "*.MP4", "*.avi", "*.mkv", "*.mov"):
        files.extend(glob.glob(os.path.join(video_dir, ext)))
    return len(set(files))


def _session_asset_hours() -> float:
    """Monitored hours from real live sessions only."""
    with _db() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(
                (julianday(COALESCE(ended_at, CURRENT_TIMESTAMP)) - julianday(started_at)) * 24.0
            ), 0) AS hours
            FROM sessions
            """
        ).fetchone()
    return round(float(row["hours"] or 0), 1)


def _operators_seen(events: List[Dict[str, Any]]) -> int:
    """Distinct worker counts observed in live event payloads (0 if none)."""
    best = 0
    for e in events:
        payload = e.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        for key in ("workers", "operators", "persons", "people"):
            val = payload.get(key)
            if isinstance(val, (int, float)) and val > best:
                best = int(val)
    return best


# Map UI filter scope → SQL constraints
_PPE_TYPES = ("NO_HELMET", "NO_VEST", "NO_SAFETY_HARNESS")
_FORKLIFT_TYPES = ("FORKLIFT_OVERSPEED",)


def _apply_analytics_filters(
    clauses: List[str],
    args: List[Any],
    *,
    worksite: Optional[str] = None,
    day: Optional[str] = None,
    category: Optional[str] = None,
    scope: Optional[str] = None,
) -> None:
    if worksite and worksite not in ("all", "--All Worksites--"):
        clauses.append("worksite = ?")
        args.append(worksite)
    if day:
        clauses.append("substr(ts, 1, 10) = ?")
        args.append(day)

    cat = (category or "all").lower()
    sc = (scope or "all").lower()

    if cat == "assets":
        if sc == "forklift":
            placeholders = ",".join("?" for _ in _FORKLIFT_TYPES)
            clauses.append(f"(event_type IN ({placeholders}) OR event_type LIKE 'FORKLIFT%')")
            args.extend(_FORKLIFT_TYPES)
        # cameras / all → no event-type filter (all monitored assets)
    elif cat == "operators":
        if sc in ("all", "ppe"):
            placeholders = ",".join("?" for _ in _PPE_TYPES)
            clauses.append(f"event_type IN ({placeholders})")
            args.extend(_PPE_TYPES)
        elif sc == "helmet":
            clauses.append("event_type = ?")
            args.append("NO_HELMET")
        elif sc == "vest":
            clauses.append("event_type = ?")
            args.append("NO_VEST")
    elif cat == "alerts":
        if sc == "high":
            clauses.append("severity = ?")
            args.append("high")
        elif sc == "medium":
            clauses.append("severity = ?")
            args.append("medium")
        elif sc not in ("all", "", None):
            clauses.append("event_type = ?")
            args.append(sc)


def summary_kpis(
    worksite: Optional[str] = None,
    *,
    day: Optional[str] = None,
    category: Optional[str] = None,
    scope: Optional[str] = None,
) -> Dict[str, Any]:
    clauses = ["COALESCE(source, '') != 'demo'"]
    args: List[Any] = []
    _apply_analytics_filters(
        clauses, args, worksite=worksite, day=day, category=category, scope=scope
    )
    where = " WHERE " + " AND ".join(clauses)

    with _db() as conn:
        total = int(conn.execute(f"SELECT COUNT(*) AS c FROM events{where}", args).fetchone()["c"])
        danger = int(
            conn.execute(
                f"SELECT COUNT(*) AS c FROM events{where} AND severity = 'high'",
                args,
            ).fetchone()["c"]
        )
        warn = int(
            conn.execute(
                f"SELECT COUNT(*) AS c FROM events{where} AND severity = 'medium'",
                args,
            ).fetchone()["c"]
        )
        type_rows = conn.execute(
            f"SELECT event_type, COUNT(*) AS c FROM events{where} GROUP BY event_type",
            args,
        ).fetchall()
        worker_rows = conn.execute(
            f"SELECT payload FROM events{where} ORDER BY id DESC LIMIT 200",
            args,
        ).fetchall()

    by_type: Dict[str, int] = {
        (r["event_type"] or "UNKNOWN"): int(r["c"]) for r in type_rows
    }

    recent: List[Dict[str, Any]] = []
    for r in worker_rows:
        try:
            recent.append({"payload": json.loads(r["payload"] or "{}")})
        except json.JSONDecodeError:
            recent.append({"payload": {}})

    if total == 0:
        score = 100
        label = "No data yet"
    else:
        high_ratio = danger / max(total, 1)
        score = max(0, min(100, int(100 - high_ratio * 40 - (warn / max(total, 1)) * 15)))
        label = (
            "Safety Expert" if score >= 85
            else ("Compliant" if score >= 70 else "Needs Attention")
        )

    return {
        "safety_score": score,
        "safety_label": label,
        "incidents_prevented": total,
        "total_alerts": total,
        "asset_hours": _session_asset_hours(),
        "assets": _count_video_assets(),
        "operators": _operators_seen(recent),
        "high_severity": danger,
        "medium_severity": warn,
        "by_type": by_type,
        "online": True,
        "data_source": "live",
        "filter_day": day,
        "filter_category": category or "all",
        "filter_scope": scope or "all",
    }


def _event_matches_filters(
    e: Dict[str, Any],
    *,
    category: Optional[str] = None,
    scope: Optional[str] = None,
) -> bool:
    cat = (category or "all").lower()
    sc = (scope or "all").lower()
    et = str(e.get("event_type") or "")
    sev = str(e.get("severity") or "").lower()

    if cat == "assets":
        if sc == "forklift":
            return et.startswith("FORKLIFT") or et in _FORKLIFT_TYPES
        return True
    if cat == "operators":
        if sc == "helmet":
            return et == "NO_HELMET"
        if sc == "vest":
            return et == "NO_VEST"
        return et in _PPE_TYPES
    if cat == "alerts":
        if sc == "high":
            return sev == "high"
        if sc == "medium":
            return sev == "medium"
        if sc in ("all", ""):
            return True
        want = sc.upper()
        return et == want or et == sc
    return True


def timeseries(
    days: int = 14,
    worksite: Optional[str] = None,
    *,
    category: Optional[str] = None,
    scope: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Daily buckets for charts from real logged live-monitor events only."""
    events = list_events(limit=10000, worksite=worksite, since_hours=days * 24)
    events = [
        e
        for e in events
        if (e.get("source") or "") != "demo"
        and _event_matches_filters(e, category=category, scope=scope)
    ]
    buckets: Dict[str, Dict[str, int]] = {}
    today = datetime.now().date()
    for i in range(days):
        d = (today - timedelta(days=days - 1 - i)).isoformat()
        buckets[d] = {"alerts": 0, "medium": 0, "high": 0}

    for e in events:
        try:
            day = e["ts"][:10]
        except Exception:
            continue
        if day not in buckets:
            continue
        sev = (e.get("severity") or "").lower()
        buckets[day]["alerts"] += 1
        if sev == "medium":
            buckets[day]["medium"] += 1
        if sev == "high":
            buckets[day]["high"] += 1

    return [{"date": d, **buckets[d]} for d in sorted(buckets.keys())]


def worksites() -> List[str]:
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT worksite FROM events
            WHERE COALESCE(source, '') != 'demo'
            ORDER BY worksite
            """
        ).fetchall()
    return [r["worksite"] for r in rows if r["worksite"]]


def start_session(*, source: str = "", profile: str = "") -> int:
    """Record a real live-monitor session start."""
    with _db() as conn:
        cur = conn.execute(
            """
            INSERT INTO sessions (started_at, source, profile, frames, violations)
            VALUES (?, ?, ?, 0, 0)
            """,
            (datetime.now().isoformat(), source, profile),
        )
        return int(cur.lastrowid)


def end_session(session_id: Optional[int], *, frames: int = 0, violations: int = 0) -> None:
    if not session_id:
        return
    with _db() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET ended_at = ?, frames = ?, violations = ?
            WHERE id = ?
            """,
            (datetime.now().isoformat(), frames, violations, session_id),
        )


def purge_demo_events() -> int:
    """Remove previously seeded demo rows so KPIs stay real-time only."""
    with _db() as conn:
        cur = conn.execute("DELETE FROM events WHERE source = 'demo'")
        return int(cur.rowcount or 0)


def consolidate_burst_duplicates() -> int:
    """Keep one row per alert type per second — drop per-frame YOLO spam."""
    with _db() as conn:
        cur = conn.execute(
            """
            DELETE FROM events
            WHERE id NOT IN (
                SELECT MIN(id) FROM events
                GROUP BY event_type, substr(ts, 1, 19), COALESCE(worksite, '')
            )
            """
        )
        return int(cur.rowcount or 0)
