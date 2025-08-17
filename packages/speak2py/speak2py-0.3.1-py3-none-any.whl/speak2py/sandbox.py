import multiprocessing as mp

SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "len": len, "range": range,
}

def safe_exec(code: str, locals_dict: dict):
    globals_dict = {
        "__builtins__": SAFE_BUILTINS,
        "load_data": __import__("speak2py").file_reader.load_data,
        "pd": __import__("pandas"),
        "plt": __import__("matplotlib").pyplot,
    }
    exec(code, globals_dict, locals_dict)

def _worker(code, queue):
    try:
        loc = {}
        safe_exec(code, loc)
        queue.put(("OK", loc.get("result", None)))
    except Exception as e:
        queue.put(("ERR", str(e)))

def exec_in_sandbox(code: str):
    """
    Run `code` in a separate process, blocking until it finishes.
    Returns the `result` variable or raises on error.
    """
    q = mp.Queue()
    p = mp.Process(target=_worker, args=(code, q), daemon=True)
    p.start()
    p.join()  # <-- no timeout, will wait indefinitely
    status, payload = q.get_nowait()
    if status == "OK":
        return payload
    else:
        raise RuntimeError(f"Sandbox error: {payload}")
