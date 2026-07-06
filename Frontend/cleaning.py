
import pandas as pd
import re

MAX_MB = 20  # oversized-file guard, used by caller

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [re.sub(r"\s+", "_", c.strip().lower()) for c in df.columns]
    return df

def try_parse_dates(df: pd.DataFrame, warnings: list[str]) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            parsed = pd.to_datetime(df[col], errors="coerce", format="mixed")
            non_null_ratio = parsed.notna().mean()
            if non_null_ratio > 0.8:  # heuristic: mostly parseable -> treat as date
                bad = parsed.isna() & df[col].notna()
                n_bad = int(bad.sum())
                df[col] = parsed
                if n_bad:
                    warnings.append(f"{n_bad} rows had unparseable dates in '{col}'; set to null")
    return df

def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    warnings: list[str] = []
    before_rows = len(df)

    df = normalize_headers(df)

    # drop fully-empty rows/cols
    empty_cols = df.columns[df.isna().all()].tolist()
    if empty_cols:
        df = df.drop(columns=empty_cols)
        warnings.append(f"Dropped empty columns: {empty_cols}")
    df = df.dropna(how="all")
    if len(df) < before_rows:
        warnings.append(f"Dropped {before_rows - len(df)} fully-empty rows")

    # infer numeric columns that pandas left as object (e.g. "1,200")
    for col in df.select_dtypes(include="object").columns:
        cleaned = df[col].astype(str).str.replace(",", "", regex=False)
        numeric = pd.to_numeric(cleaned, errors="coerce")
        if numeric.notna().mean() > 0.9 and df[col].notna().any():
            df[col] = numeric

    df = try_parse_dates(df, warnings)

    return df, warnings


def load_csv_bytes(raw: bytes, filename: str) -> tuple[pd.DataFrame, list[str]]:
    """Handle encoding surprises. Raises ValueError with a user-facing message."""
    if not filename.lower().endswith(".csv"):
        raise ValueError("Only .csv files are supported.")
    if len(raw) == 0:
        raise ValueError("The file is empty.")
    if len(raw) > MAX_MB * 1024 * 1024:
        raise ValueError(f"File too large ({len(raw)/1e6:.1f}MB). Max is {MAX_MB}MB.")

    for enc in ("utf-8", "latin-1"):
        try:
            import io
            df = pd.read_csv(io.BytesIO(raw), encoding=enc)
            if df.empty:
                raise ValueError("The CSV has no rows.")
            return clean_dataframe(df)
        except UnicodeDecodeError:
            continue
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV has no columns/data.")
    raise ValueError("Could not decode file as UTF-8 or Latin-1.")
