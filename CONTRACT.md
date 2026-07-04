# CONTRACT.md — Ask Your Data
 
> Any change to this file must be agreed by both of us and go through a PR. Never change it silently.
 
This is the API boundary between the two halves (`app/` = Nitesh, `engine/` = Zineb). Each half is built against a mock of the other, using the exact JSON shapes below.
 
---
 
## POST /query — the engine (Zineb)
 
Takes a session and a plain-English question, returns validated, executed SQL results as raw rows.
 
### Request
 
```json
{
  "session_id": "abc123",
  "question": "Which region had the highest revenue in 2024?"
}
```
 
No constraint on question length in v1 (decided, not forgotten).
 
### Success response — 200
 
`rows` are lists of values; column order is given by `columns`. (Matches sqlite3 cursor output, keeps the payload small, and preserves column order for chart rules.)
 
```json
{
  "sql": "SELECT region, SUM(revenue) AS revenue FROM data WHERE strftime('%Y', order_date) = '2024' GROUP BY region ORDER BY revenue DESC LIMIT 100",
  "columns": ["region", "revenue"],
  "rows": [["EMEA", 4200], ["APAC", 3100]],
  "attempts": 1,
  "duration_ms": 840
}
```
 
### Errors
 
All errors share one envelope: an `"error"` field naming the kind, plus details for that kind.
 
**422 — the retry loop exhausted (max 3 attempts):**
 
```json
{
  "error": "could_not_answer",
  "attempts": 3,
  "last_sql": "SELECT regoin FROM data",
  "last_error": "no such column: regoin"
}
```
 
**400 — the session doesn't exist:**
 
```json
{
  "error": "unknown_session",
  "detail": "No database found for session_id 'abc123'. Re-upload the CSV."
}
```
 
---
 
## POST /upload — the product (Nitesh)
 
> **Nitesh: this is your endpoint — edit freely, then approve this file.**
 
Takes a CSV file, cleans it, creates a session with its own SQLite database, returns the detected schema.
 
### Request
 
Multipart form upload (`file` field, CSV) — not JSON.
 
### Success response — 200
 
```json
{
  "session_id": "abc123",
  "columns": [
    {"name": "region", "dtype": "text"},
    {"name": "revenue", "dtype": "number"},
    {"name": "order_date", "dtype": "date"}
  ],
  "row_count": 200,
  "warnings": ["dropped 3 rows with unparseable dates"]
}
```
 
### Errors
 
**400 — bad file (non-CSV, empty, oversized):**
 
```json
{
  "error": "invalid_file",
  "detail": "File must be a non-empty CSV under 10 MB."
}
```
 
---
 
## Data type rules
 
- Values in `rows` are numbers, strings, or `null` — nothing else.
- Dates are returned as ISO strings, e.g. `"2024-03-01"`.
- An empty result is `"rows": []` — never a missing field.


## Ground rules
 
- The engine returns raw rows only. Answer text and chart selection are product-side.
- The generated SQL is always included in the response (including the 422 (`last_sql`))
- Sessions live in memory for MVP. Server restart = sessions gone.
- This contract changes only by agreement between both of us, via PR :)