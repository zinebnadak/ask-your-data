"""One well-prompted LLM call: (question + result rows) -> 1-2 sentence answer.
No agent framework. Provider switches via .env: LLM_PROVIDER=ollama|openai.
"""
import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

PROMPT = """You answer a user's question about their data using ONLY the rows given.
Be brief (1-2 sentences) and honest: if rows are empty, say no matching data was found.
Never invent numbers not present in the rows.

Question: {question}
Rows (JSON): {rows}

Answer:"""


def generate_answer(question: str, rows: list[dict]) -> str:
    prompt = PROMPT.format(question=question, rows=rows)

    # Langfuse trace (stub - swap in real client: from langfuse import Langfuse)
    trace = _start_trace(name="generate_answer", input={"question": question, "rows": rows})

    if not rows:
        answer = "I didn't find any rows matching that question."
    elif LLM_PROVIDER == "openai":
        answer = _call_openai(prompt)
    else:
        answer = _call_ollama(prompt)

    _end_trace(trace, output=answer)
    return answer


def _call_ollama(prompt: str) -> str:
    import httpx
    r = httpx.post("http://localhost:11434/api/generate", json={
        "model": os.getenv("OLLAMA_MODEL", "llama3.1:latest"),
        "prompt": prompt,
        "stream": False,
    }, timeout=60)
    return r.json()["response"].strip()


def _call_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "example-model"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
    )
    return resp.choices[0].message.content.strip()


def _start_trace(name, input):
    # Replace with: Langfuse().trace(name=name, input=input)
    return {"name": name, "input": input}


def _end_trace(trace, output):
    # Replace with: trace.update(output=output)
    pass
