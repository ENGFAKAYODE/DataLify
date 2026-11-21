
import csv
from io import BytesIO
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataset(uploaded_file, sheet_name=None):
    """Load a CSV or Excel upload into a Pandas DataFrame."""
    filename = uploaded_file.name.lower()

    if not any(filename.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
        raise ValueError("Upload a CSV, XLSX, or XLS file.")

    uploaded_file.seek(0)

    if filename.endswith(".csv"):
        raw = uploaded_file.getvalue()
        sniff_text = None
        sniff_encoding = None
        for candidate in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
            try:
                sniff_text = raw[:65536].decode(candidate)
                sniff_encoding = candidate
                break
            except UnicodeDecodeError:
                continue
        if sniff_text is None:
            raise ValueError("Could not decode this CSV with common text encodings.")

        try:
            delimiter = csv.Sniffer().sniff(
                sniff_text, delimiters=",;\t|"
            ).delimiter
        except csv.Error:
            delimiter = ","

        last_error = None
        df = None
        for encoding in (sniff_encoding, "utf-8-sig", "utf-8", "cp1252", "latin1"):
            try:
                df = pd.read_csv(BytesIO(raw), sep=delimiter, encoding=encoding)
                df.attrs["source_encoding"] = encoding
                df.attrs["source_delimiter"] = delimiter
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as error:
                last_error = error
        if df is None:
            raise ValueError(f"Could not parse this CSV: {last_error}")
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(
            BytesIO(uploaded_file.getvalue()),
            sheet_name=sheet_name or 0,
            engine="openpyxl",
        )
    else:
        df = pd.read_excel(
            BytesIO(uploaded_file.getvalue()),
            sheet_name=sheet_name or 0,
        )

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Select one worksheet at a time.")

    return df


def get_dataset_summary(df):
    """Return key dataset metrics calculated directly with Pandas."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())

    completeness = (
        ((total_cells - missing_cells) / total_cells) * 100
        if total_cells else 100.0
    )

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": missing_cells,
        "completeness": round(completeness, 2),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
    }


def get_schema(df):
    """Return column-level metadata for the Schema tab."""
    return pd.DataFrame({
        "column": df.columns.astype(str),
        "data_type": [str(dtype) for dtype in df.dtypes],
        "missing_count": df.isna().sum().to_numpy(),
        "missing_percent": (
            df.isna().mean().mul(100).round(2).to_numpy()
        ),
        "unique_count": df.nunique(dropna=True).to_numpy(),
    })
