from frontend import answer as ans


def test_empty_rows_returns_fixed_message_no_llm_call(monkeypatch):
    called = {"ollama": False, "openai": False}
    monkeypatch.setattr(ans, "_call_ollama", lambda p: called.update(ollama=True) or "x")
    monkeypatch.setattr(ans, "_call_openai", lambda p: called.update(openai=True) or "x")

    result = ans.generate_answer("any question", [])
    assert "didn't find any rows" in result
    assert called["ollama"] is False
    assert called["openai"] is False


def test_non_empty_rows_calls_ollama_by_default(monkeypatch):
    monkeypatch.setattr(ans, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(ans, "_call_ollama", lambda p: "ollama answer")
    result = ans.generate_answer("q", [{"category": "a", "total": 10}])
    assert result == "ollama answer"


def test_non_empty_rows_calls_openai_when_configured(monkeypatch):
    monkeypatch.setattr(ans, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(ans, "_call_openai", lambda p: "openai answer")
    result = ans.generate_answer("q", [{"category": "a", "total": 10}])
    assert result == "openai answer"


def test_prompt_includes_question_and_rows(monkeypatch):
    captured = {}
    def fake_ollama(prompt):
        captured["prompt"] = prompt
        return "ok"
    monkeypatch.setattr(ans, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(ans, "_call_ollama", fake_ollama)

    ans.generate_answer("what is the top category?", [{"category": "a", "total": 10}])
    assert "what is the top category?" in captured["prompt"]
    assert "'category': 'a'" in captured["prompt"]