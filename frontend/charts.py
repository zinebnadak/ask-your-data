import pandas as pd
import plotly.express as px


def pick_chart(df: pd.DataFrame):
    """Returns ('bar'|'line'|'table', plotly Figure|None)."""
    if df.empty:
        return "table", None

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()
    # try to catch date-like strings too
    if not datetime_cols:
        for c in df.columns:
            if pd.api.types.is_string_dtype(df[c]):
                parsed = pd.to_datetime(df[c], errors="coerce", format="mixed")
                if parsed.notna().mean() > 0.8:
                    datetime_cols.append(c)

    if datetime_cols and numeric_cols:
        fig = px.line(df, x=datetime_cols[0], y=numeric_cols[0])
        return "line", fig

    non_numeric = [c for c in df.columns if c not in numeric_cols]
    if len(df.columns) == 2 and numeric_cols and non_numeric:
        fig = px.bar(df, x=non_numeric[0], y=numeric_cols[0])
        return "bar", fig

    return "table", None
