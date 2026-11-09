
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
        df = pd.read_csv(uploaded_file)
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