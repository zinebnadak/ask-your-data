from __future__ import annotations

import pandas as pd
import streamlit as st

from Frontend.cleaning import load_csv_bytes


def load_preview(uploaded_file) -> pd.DataFrame:
    uploaded_file.seek(0)
    return pd.read_csv(uploaded_file, nrows=5)


def clean_uploaded_file(uploaded_file) -> tuple[pd.DataFrame, list[str]]:
    uploaded_file.seek(0)
    raw = uploaded_file.read()
    return load_csv_bytes(raw, uploaded_file.name)


def render_app() -> None:
    st.set_page_config(
        page_title="Ask Your Data",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .stApp {
            background: #0b1220;
        }
        section[data-testid="stSidebar"] {
            background: #1f2430;
        }
        .info-card {
            background: rgba(59, 130, 246, 0.18);
            border: 1px solid rgba(96, 165, 250, 0.2);
            border-radius: 16px;
            color: #cfe4ff;
            padding: 1rem 1.1rem;
            line-height: 1.7;
        }
        .preview-note {
            color: #cbd5e1;
            margin-top: 0.5rem;
        }
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #ff5c61, #ff7d6b);
            border: 0;
            border-radius: 14px;
            color: white;
            font-size: 1.05rem;
            font-weight: 700;
            min-height: 3.2rem;
        }
        div[data-testid="stButton"] > button:hover {
            color: white;
            border: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("📊 Ask Your Data")
        st.caption("Query any CSV in plain English.")
        st.divider()
        st.info("No file loaded yet. Upload a CSV to get started.", icon="ℹ️")
        st.divider()
        st.caption("Powered by local LLM + DuckDB")

    st.header("Choose a CSV file")

    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            label_visibility="collapsed",
        )

    with right_col:
        st.markdown(
            """
            <div class="info-card">
                <strong>Supported format:</strong> .csv files only<br>
                <strong>Privacy:</strong> processed locally, never sent to third parties<br>
                <strong>Size:</strong> keep files under a few hundred MB for best performance
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not uploaded:
        st.stop()

    try:
        cleaned_df, cleaning_warnings = clean_uploaded_file(uploaded)
        preview_df = load_preview(uploaded)
    except Exception as exc:
        st.error(f"Could not clean this file: {exc}")
        st.stop()

    st.success("File is cleaned and ready to analyse.")
    for warning in cleaning_warnings:
        st.warning(warning)

    st.subheader("Preview")
    st.dataframe(preview_df, use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="preview-note">Showing first 5 rows from <strong>{uploaded.name}</strong></div>',
        unsafe_allow_html=True,
    )

    st.divider()
    _, button_col, _ = st.columns([2, 3, 2])

    with button_col:
        if st.button("Upload & Analyse ✨", use_container_width=True):
            st.success(f"{uploaded.name} is cleaned and ready to analyse.")


if __name__ == "__main__":
    render_app()
