import io
import json
import pandas as pd
import pandas.testing as pdt
import pytest

from speak2py.session import load_data

def test_load_csv(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    p = tmp_path / "t.csv"
    df.to_csv(p, index=False)
    out = load_data(str(p))
    pdt.assert_frame_equal(out, df)

def test_load_json(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    p = tmp_path / "t.json"
    df.to_json(p, orient="records")
    # read_json with default orient is fine for this case
    out = load_data(str(p))
    # normalize ordering
    out = out.astype(df.dtypes.to_dict())
    pdt.assert_frame_equal(out.reset_index(drop=True), df.reset_index(drop=True))

def test_load_xlsx(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")  # skip if engine not installed
    df = pd.DataFrame({"x": [10, 20], "y": [1.5, 2.5]})
    p = tmp_path / "t.xlsx"
    df.to_excel(p, index=False)
    out = load_data(str(p))
    # Excel loader may upcast ints to floats; align dtypes for comparison
    for c in df.columns:
        if pd.api.types.is_integer_dtype(df[c]):
            out[c] = out[c].astype(int)
    pdt.assert_frame_equal(out, df)

def test_bad_extension_raises(tmp_path):
    p = tmp_path / "t.txt"
    p.write_text("hello")
    with pytest.raises(ValueError):
        load_data(str(p))
