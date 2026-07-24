import sqlite3
import uuid
import os
import pandas as pd

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

_registry: dict[str, str] = {}  # session_id -> db path


def create_session(df: pd.DataFrame) -> str:
    session_id = str(uuid.uuid4())
    path = os.path.join(SESSIONS_DIR, f"{session_id}.db")
    conn = sqlite3.connect(path)
    df.to_sql("data", conn, if_exists="replace", index=False)
    conn.close()
    _registry[session_id] = path
    return session_id


def get_db_path(session_id: str) -> str | None:
    return _registry.get(session_id)


def run_sql(session_id: str, sql: str) -> tuple[list[str], list[dict]]:
    """Executes engine-provided SQL against the session's db. Raises KeyError if unknown_session."""
    path = get_db_path(session_id)
    if path is None:
        raise KeyError("unknown_session")
    conn = sqlite3.connect(path)
    try:
        cur = conn.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        return cols, rows
    finally:
        conn.close()

