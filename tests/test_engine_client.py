import httpx
import pytest
from frontend import engine_client as ec


def test_mock_engine_returns_contract_shaped_response(monkeypatch):
    monkeypatch.setattr(ec, "MOCK_ENGINE", True)
    result = ec.query_engine("session-1", "top categories?", schema=[])
    assert "sql" in result
    assert "columns" in result
    assert "rows" in result


def test_real_call_success(monkeypatch):
    monkeypatch.setattr(ec, "MOCK_ENGINE", False)

    class FakeResponse:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"sql": "SELECT 1", "columns": ["x"], "rows": [{"x": 1}]}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(ec.httpx, "post", fake_post)
    result = ec.query_engine("session-1", "question", schema=[])
    assert result["sql"] == "SELECT 1"


def test_real_call_422_maps_to_could_not_answer(monkeypatch):
    monkeypatch.setattr(ec, "MOCK_ENGINE", False)

    class FakeResponse:
        status_code = 422
        def json(self): return {"error": "could_not_answer", "last_error": "bad sql"}

    def raise_status(self):
        raise httpx.HTTPStatusError("422", request=None, response=self)
    FakeResponse.raise_for_status = raise_status

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(ec.httpx, "post", fake_post)
    result = ec.query_engine("session-1", "question", schema=[])
    assert result["error"] == "could_not_answer"
    assert result["_status"] == 422


def test_network_error_returns_could_not_answer(monkeypatch):
    monkeypatch.setattr(ec, "MOCK_ENGINE", False)

    def fake_post(*args, **kwargs):
        raise httpx.RequestError("connection failed")

    monkeypatch.setattr(ec.httpx, "post", fake_post)
    result = ec.query_engine("session-1", "question", schema=[])
    assert result["error"] == "could_not_answer"
    assert "unreachable" in result["last_error"]