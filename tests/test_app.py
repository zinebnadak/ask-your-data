import io
import pandas as pd

from frontend.app import clean_uploaded_file, load_preview


class UploadedFileStub(io.BytesIO):
    def __init__(self, data: bytes, name: str) -> None:
        super().__init__(data)
        self.name = name


def test_load_preview_reads_first_five_rows():
    csv = io.StringIO(
        """name,age
Alice,21
Bob,22
Charlie,23
David,24
Eva,25
Frank,26
"""
    )

    df = load_preview(csv)

    assert len(df) == 5
    assert list(df.columns) == ["name", "age"]
    assert df.iloc[0]["name"] == "Alice"
    assert df.iloc[-1]["name"] == "Eva"


def test_load_preview_resets_file_pointer():
    csv = io.StringIO(
        """name,age
Alice,21
Bob,22
"""
    )

    csv.read()

    df = load_preview(csv)

    assert len(df) == 2


def test_load_preview_returns_dataframe():
    csv = io.StringIO(
        """city
Delhi
Mumbai
"""
    )

    df = load_preview(csv)

    assert isinstance(df, pd.DataFrame)


def test_clean_uploaded_file_returns_cleaned_data():
    uploaded = UploadedFileStub(
        b" First Name , Amount , Empty \nAlice,\"1,200\",\nBob,\"2,500\",\n",
        "sales.csv",
    )

    df, warnings = clean_uploaded_file(uploaded)

    assert list(df.columns) == ["first_name", "amount"]
    assert df["amount"].tolist() == [1200, 2500]
    assert warnings == ["Dropped empty columns: ['empty']"]


def test_clean_uploaded_file_returns_full_cleaned_dataframe():
    uploaded = UploadedFileStub(
        b"name\nAlice\nBob\nCharlie\nDavid\nEva\nFrank\n",
        "people.csv",
    )

    df, warnings = clean_uploaded_file(uploaded)

    assert len(df) == 6
    assert df.iloc[-1]["name"] == "Frank"
    assert warnings == []
