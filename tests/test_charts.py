import pandas as pd
import plotly.graph_objects as go
from frontend.charts import pick_chart


def test_empty_df_returns_table():
    kind, fig = pick_chart(pd.DataFrame())
    assert kind == "table"
    assert fig is None


def test_two_cols_one_numeric_returns_bar():
    df = pd.DataFrame({"category": ["a", "b", "c"], "total": [10, 20, 30]})
    kind, fig = pick_chart(df)
    assert kind == "bar"
    assert isinstance(fig, go.Figure)


def test_date_and_numeric_returns_line():
    df = pd.DataFrame({
        "order_date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "amount": [5, 15, 25],
    })
    kind, fig = pick_chart(df)
    assert kind == "line"
    assert isinstance(fig, go.Figure)


def test_date_like_string_column_detected_as_date():
    df = pd.DataFrame({
        "order_date": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "amount": [5, 15, 25],
    })
    kind, fig = pick_chart(df)
    assert kind == "line"


def test_three_plus_columns_falls_back_to_table():
    df = pd.DataFrame({
        "category": ["a", "b"],
        "subcat": ["x", "y"],
        "total": [1, 2],
    })
    kind, fig = pick_chart(df)
    assert kind == "table"
    assert fig is None


def test_all_text_columns_falls_back_to_table():
    df = pd.DataFrame({"name": ["a", "b"], "city": ["x", "y"]})
    kind, fig = pick_chart(df)
    assert kind == "table"
    assert fig is None