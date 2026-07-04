"""
Streamlit frontend for Ask Your Data.

Install dependencies:
    uv sync

Launch the frontend:
    uv run streamlit run app.py

If you also have the backend files locally, start that first:
    uv run uvicorn backend_app:app --port 8001
"""

from __future__ import annotations

import streamlit as st
import httpx
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Ask Your Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── optional backend modules ──────────────────────────────────────────────────
try:
    from engine_client import query_engine
    from session_store import run_sql
    from charts import pick_chart, PLOTLY_AVAILABLE
    from answer import generate_answer
    _MODULES_OK = True
except ImportError as e:
    _MODULES_OK = False
    _MISSING = str(e)

BACKEND_URL = "http://localhost:8001/upload"

# ── session defaults ──────────────────────────────────────────────────────────
st.session_state.setdefault("session", None)
st.session_state.setdefault("history", [])
st.session_state.setdefault("prefill", "")

# ════════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📊 Ask Your Data")
    st.caption("Query any CSV in plain English.")
    st.divider()

    if st.session_state.session:
        sess = st.session_state.session
        st.success("✅ File loaded")
        st.metric("Rows", f"{sess['row_count']:,}")
        st.metric("Columns", len(sess["schema"]))
        st.divider()
        if st.button("🗑️ Clear session", use_container_width=True):
            st.session_state.session = None
            st.session_state.history = []
            st.session_state.prefill = ""
            st.rerun()
    else:
        st.info("No file loaded yet. Upload a CSV to get started.", icon="ℹ️")

    if st.session_state.history:
        st.divider()
        st.subheader("🕘 History")
        for item in reversed(st.session_state.history[-8:]):
            st.caption(f"**{item['ts']}** — {item['question']}")
        st.divider()
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.divider()
    st.caption("Powered by local LLM + DuckDB")

# ════════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════════

if not _MODULES_OK:
    st.warning(
        f"Backend modules could not be imported: `{_MISSING}`  \n"
        "Ensure `engine_client`, `session_store`, `charts`, and `answer` "
        "are in the same folder and your virtualenv is active.",
        icon="⚠️",
    )

# ── UPLOAD ────────────────────────────────────────────────────────────────────
if not st.session_state.session:
    st.header("Step 1 — Upload your CSV")

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Your file is processed in-memory and never stored permanently.",
        )

    with col_right:
        st.info(
            "**Supported format:** `.csv` files only  \n"
            "**Privacy:** processed locally, never sent to third parties  \n"
            "**Size:** keep files under a few hundred MB for best performance",
            icon="ℹ️",
        )

    if uploaded:
        st.subheader("Preview")
        try:
            preview_df = pd.read_csv(uploaded, nrows=5)
            uploaded.seek(0)
            st.dataframe(preview_df, use_container_width=True)
            st.caption(f"Showing first 5 rows of **{uploaded.name}**")
        except Exception:
            uploaded.seek(0)
            st.warning("Could not preview this file, but upload may still work.", icon="⚠️")

        st.divider()
        _, btn_col, _ = st.columns([2, 2, 2])
        with btn_col:
            upload_clicked = st.button(
                "Upload & Analyse ✨",
                type="primary",
                use_container_width=True,
            )

        if upload_clicked:
            with st.spinner("Uploading and analysing your data…"):
                files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
                try:
                    resp = httpx.post(BACKEND_URL, files=files, timeout=30)
                except httpx.RequestError:
                    st.error(
                        "Could not reach the upload service.  \n"
                        "Start it with: `uvicorn backend_app:app --port 8001`",
                        icon="🔌",
                    )
                    st.stop()

                if resp.status_code != 200:
                    st.error(
                        resp.json().get("detail", "Upload failed — try a different file."),
                        icon="❌",
                    )
                else:
                    st.session_state.session = resp.json()
                    st.rerun()

    st.stop()


# ── SCHEMA ────────────────────────────────────────────────────────────────────
sess = st.session_state.session

for warning in sess.get("warnings", []):
    st.warning(warning, icon="⚠️")

st.header("Step 2 — Review your schema")

col_schema, col_gap = st.columns([3, 1], gap="large")
with col_schema:
    with st.expander("🗂️ Detected columns & types", expanded=True):
        st.dataframe(
            pd.DataFrame(sess["schema"]),
            use_container_width=True,
            hide_index=True,
        )

st.divider()

# ── ASK ───────────────────────────────────────────────────────────────────────
st.header("Step 3 — Ask a question")

with st.expander("💡 Example questions", expanded=False):
    examples = [
        "What is the average value per category?",
        "Show me the top 10 rows by amount.",
        "How many unique values are in each column?",
        "What is the total grouped by month?",
    ]
    c1, c2 = st.columns(2)
    for i, ex in enumerate(examples):
        col = c1 if i % 2 == 0 else c2
        if col.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state.prefill = ex
            st.rerun()

question = st.text_input(
    "Your question",
    value=st.session_state.prefill,
    placeholder="e.g. What is the total revenue by region?",
    help="Ask anything about your data in plain English.",
)

ask_col, clear_col = st.columns([5, 1])
with ask_col:
    ask = st.button(
        "Ask ✨",
        type="primary",
        use_container_width=True,
        disabled=not question.strip(),
    )
with clear_col:
    if st.button("Clear", use_container_width=True):
        st.session_state.prefill = ""
        st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if ask and question.strip():
    if not _MODULES_OK:
        st.error("Backend modules unavailable — see warning above.", icon="❌")
        st.stop()

    st.session_state.prefill = question
    st.divider()

    with st.spinner("Generating SQL and running query…"):
        result = query_engine(sess["session_id"], question, sess["schema"])

    if result.get("error") == "unknown_session":
        st.warning("Your session expired — please re-upload your file.", icon="⏳")
        st.session_state.session = None
        st.rerun()

    if result.get("error") == "could_not_answer":
        st.warning("I couldn't answer that — try rephrasing your question.", icon="🤔")
        with st.expander("Technical details"):
            st.code(result.get("last_error", "no details"), language="text")
        st.stop()

    # generated SQL
    with st.expander("🔍 Generated SQL", expanded=False):
        st.code(result["sql"], language="sql")

    # run query
    try:
        cols, rows = run_sql(sess["session_id"], result["sql"])
    except KeyError:
        st.warning("Your session expired — please re-upload your file.", icon="⏳")
        st.session_state.session = None
        st.rerun()
    except Exception:
        st.warning("Something went wrong running that query. Try rephrasing.", icon="⚠️")
        st.stop()

    df = pd.DataFrame(rows, columns=cols)
    answer_text = generate_answer(question, rows)

    # answer
    st.subheader("💬 Answer")
    st.success(answer_text, icon="✅")

    # chart / table tabs
    tab_chart, tab_table = st.tabs(["📈 Chart", "📋 Table"])

    with tab_chart:
        try:
            chart_type, fig = pick_chart(df)
        except Exception:
            chart_type, fig = None, None

        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        elif not PLOTLY_AVAILABLE:
            st.info("Plotly is not installed — see the Table tab.", icon="📦")
        else:
            st.info("No suitable chart for this result — see the Table tab.", icon="📋")

    with tab_table:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            label="⬇️ Download as CSV",
            data=df.to_csv(index=False).encode(),
            file_name="result.csv",
            mime="text/csv",
        )

    # save to history
    st.session_state.history.append({
        "question": question,
        "answer":   answer_text,
        "sql":      result["sql"],
        "ts":       datetime.now().strftime("%H:%M"),
    })

# ── PREVIOUS ANSWERS ──────────────────────────────────────────────────────────
past = st.session_state.history[:-1] if st.session_state.history else []
if past:
    st.divider()
    st.subheader("🕘 Earlier answers this session")
    for item in reversed(past):
        with st.expander(f"[{item['ts']}]  {item['question']}", expanded=False):
            st.success(item["answer"], icon="✅")
            st.code(item["sql"], language="sql")
