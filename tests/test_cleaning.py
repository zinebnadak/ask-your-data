import pandas as pd
import pytest

from frontend.cleaning import clean_dataframe, load_csv_bytes, normalize_headers


def test_normalize_headers():
    df = pd.DataFrame(columns=[" First Name ", "AGE", "Order Date"])

    df = normalize_headers(df)

    assert list(df.columns) == ["first_name", "age", "order_date"]


def test_remove_empty_rows_and_columns():
    df = pd.DataFrame({
        "Name": ["Alice", None],
        "Age": [22, None],
        "Empty": [None, None],
    })

    cleaned, _ = clean_dataframe(df)

    assert "empty" not in cleaned.columns
    assert len(cleaned) == 1


def test_convert_numeric_column():
    df = pd.DataFrame({
        "Price": ["100", "200", "300"]
    })

    cleaned, _ = clean_dataframe(df)

    assert cleaned["price"].tolist() == [100, 200, 300]


def test_parse_dates():
    df = pd.DataFrame({
        "Date": [
            "2024-01-01",
            "2024-02-01",
            "2024-03-01",
            "2024-04-01",
            "2024-05-01",
        ]
    })

    cleaned, _ = clean_dataframe(df)

    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])


def test_load_csv_bytes():
    raw = b"name,age\nAlice,21\nBob,22"

    df, _ = load_csv_bytes(raw, "people.csv")

    assert len(df) == 2
    assert list(df.columns) == ["name", "age"]


def test_invalid_file_type():
    with pytest.raises(ValueError):
        load_csv_bytes(b"hello", "people.txt")
