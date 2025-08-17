import pandas as pd
import os
from speak2py import speak2py
import speak2py.session as sessmod  # to reset singleton for a clean test

def _reset_session():
    # ensure each test starts fresh
    sessmod._SESSION = None

def test_head_and_describe_and_hist(tmp_path):
    _reset_session()
    df = pd.DataFrame({"order_value": [50, 120, 75, 200, 30]})
    p = tmp_path / "orders.csv"
    df.to_csv(p, index=False)

    # head
    out1 = speak2py(f'read "{p}" and head 2')
    assert hasattr(out1, "shape") and out1.shape[0] == 2

    # describe
    out2 = speak2py(f'read "{p}" and describe as stats')
    # returns a DataFrame with summary rows
    assert hasattr(out2, "shape") and "order_value" in out2.columns

    # histogram (returns PNG path)
    out3 = speak2py(f'read "{p}" and plot a histogram of order_value')
    assert isinstance(out3, str) and out3.endswith(".png")
    assert os.path.exists(out3)
