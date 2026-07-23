import os
import pytest
import pandas as pd
from frontend import session_store as ss


@pytest.fixture(autouse=True)
def use_tmp_sessions_dir(tmp_path, monkeypatch):
    """Redirect SESSIONS_DIR to a tmp folder and reset the in-memory registry
    so tests never touch real session files or leak state between tests."""
    monkeypatch.setattr(ss, "SESSIONS_DIR", str(tmp_path))
    monkeypatch.setattr(ss, "_registry", {})
    yield


def sample_df():
    return pd.DataFrame({"category": ["a", "b"], "total": [10, 20]})


def test_create_session_returns_id_and_writes_file():
    session_id = ss.create_session(sample_df())
    assert session_id in ss._registry
    path = ss.get_db_path(session_id)
    assert os.path.exists(path)


def test_run_sql_returns_correct_cols_and_rows():
    session_id = ss.create_session(sample_df())
    cols, rows = ss.run_sql(session_id, "SELECT * FROM data ORDER BY total")
    assert cols == ["category", "total"]
    assert rows == [
        {"category": "a", "total": 10},
        {"category": "b", "total": 20},
    ]


def test_run_sql_unknown_session_raises_keyerror():
    with pytest.raises(KeyError):
        ss.run_sql("does-not-exist", "SELECT * FROM data")


def test_get_db_path_unknown_returns_none():
    assert ss.get_db_path("does-not-exist") is None


def test_two_sessions_are_isolated():
    id1 = ss.create_session(pd.DataFrame({"x": [1]}))
    id2 = ss.create_session(pd.DataFrame({"y": [2]}))
    cols1, _ = ss.run_sql(id1, "SELECT * FROM data")
    cols2, _ = ss.run_sql(id2, "SELECT * FROM data")
    assert cols1 == ["x"]
    assert cols2 == ["y"]