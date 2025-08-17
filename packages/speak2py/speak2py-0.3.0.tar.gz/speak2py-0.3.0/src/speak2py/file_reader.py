import os
import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    """Detect file extension and load into DataFrame."""
    _, ext = os.path.splitext(path.lower())
    if ext in {'.csv'}:
        return pd.read_csv(path)
    elif ext in {'.xls', '.xlsx'}:
        return pd.read_excel(path)
    elif ext in {'.json'}:
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
