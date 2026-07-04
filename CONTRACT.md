 CONTRACT.md — Ask Your Data
 
> Any change to this file must be agreed by both of us and go through a PR. Never change it silently.
 
This is the API boundary between the two halves, endpoints and shared rules..:
 
- **`app/` (product half):** Streamlit UI, CSV upload, Pandas cleaning, sessions, answer text, chart selection
- **`engine/` (engine half):** schema introspection, SQL generation, validation, execution, self-correction loop, evaluation
---