# Ask Your Data
 
> Upload a CSV, ask questions in plain English — an LLM generates the SQL, the system validates and runs it, and answers with text and a chart. Ollama for local privacy, OpenAI for the hosted demo.
 
<!-- Demo GIF goes here once we have one: ![demo](docs/demo.gif) -->
 
## The Problem
 
[2–3 sentences. Who has this problem and what it costs them. Written for a non-technical reader]
 
## What It Does
 
[3–5 sentences. Plain-English walkthrough of the user flow: upload → ask → validated SQL → answer + chart. The generated SQL is always shown to the user.]
 
## Architecture
 
<!-- Diagram linked here -->
 
[1–2 sentences on why the engine and the app are separate services.]
 
## Safety & Guardrails
 

## Evaluation

 
## How to Run 

### Local LLM (Ollama)
 
```
[steps: install Ollama, pull model, install deps, run engine, run app]
```
 
### Hosted mode (OpenAI)
 
```
[steps: .env setup from .env.example]
```
 
## Stack
 
| Layer | Tool | Why |
|---|---|---|

 
*Anything not on this list needs both of us to agree before it enters the project.*
 
## Honest Notes
 
[What broke, what was left incomplete and why, what we would do differently. Written at the end. Keep it honest.]
 
## Built By
 
- [Zineb Nadak](https://github.com/zinebnadak) — engine: schema introspection, SQL generation, validation & guardrails, self-correction loop, evaluation
- [Nitesh Verma](https://github.com/niteshver) — product: Streamlit UI, CSV upload, data cleaning pipeline, sessions, answers & charts


## References

