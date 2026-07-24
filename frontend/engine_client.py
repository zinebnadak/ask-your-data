import os
import httpx

ENGINE_URL = os.getenv("ENGINE_URL", "http://localhost:8000/query")
MOCK_ENGINE = os.getenv("MOCK_ENGINE", "1") == "1"


def query_engine(session_id: str, question: str, schema: list[dict]) -> dict:
    if MOCK_ENGINE:
        return _mock_response(question)
    try:
        r = httpx.post(ENGINE_URL, json={
            "session_id": session_id, "question": question, "schema": schema
        }, timeout=30)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        return e.response.json() | {"_status": e.response.status_code}
    except httpx.RequestError:
        return {"error": "could_not_answer", "last_error": "engine unreachable"}


def _mock_response(question: str) -> dict:
    # Contract-shaped fake data so the frontend can be built in full before the
    # real engine exists.
    return {
        "sql": "SELECT category, SUM(amount) as total FROM data GROUP BY category LIMIT 5;",
        "columns": ["category", "total"],
        "rows": [
            {"category": "A", "total": 120.5},
            {"category": "B", "total": 89.0},
        ],
    }
