# src/speak2py/__init__.py
from .session import speak2py, speak2py_code, _get_session, Session

CLIENT = _get_session()

# Back-compat: expose a module-level _METRICS like the old API
_METRICS = CLIENT.metrics  # dict with llm_calls, llm_errors, exec_errors, llm_latency, exec_latency

__all__ = ["speak2py", "speak2py_code", "CLIENT", "Session", "_METRICS"]
