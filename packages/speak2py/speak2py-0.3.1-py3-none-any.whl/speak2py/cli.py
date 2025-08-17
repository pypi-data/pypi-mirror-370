import sys
from .session import speak2py

def main():
    cmd = " ".join(sys.argv[1:]).strip()
    if not cmd:
        print('usage: s2py "read \\"data.csv\\" and describe"'); sys.exit(2)
    out = speak2py(cmd)
    try:
        import pandas as pd
        if isinstance(out, pd.DataFrame):
            print(out.to_string(max_rows=20)); return
    except Exception:
        pass
    print(out)
