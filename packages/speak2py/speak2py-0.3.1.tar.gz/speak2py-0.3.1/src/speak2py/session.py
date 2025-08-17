"""
Stateful Session for speak2py (MVP, AI-on by default via embedded local server).

User UX:
    pip install speak2py
    from speak2py import speak2py
    df = speak2py('read "data/orders.xlsx" and head 5')

Notes
- Works offline with fast rule-based intents (read/head/describe/hist + basic ops).
- AI is enabled by default using an embedded llama.cpp HTTP server provider
  that auto-downloads a small GGUF model + prebuilt binary on first use.
- Sandbox executes generated code with safe builtins (no imports/IO/OS calls).
- Also supports “any code” generation via speak2py(..., return_code=True) or speak2py_code().
"""
from __future__ import annotations

import ast
import logging
import pathlib
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd

# Use a non-interactive backend for plotting
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Embedded local LLM provider (auto-downloads model + server once)
from .providers.auto_server import AutoLlamaServerProvider


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------
_log = logging.getLogger("speak2py.session")
if not _log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    _log.addHandler(_h)
_log.setLevel(logging.INFO)


# ---------------------------------------------------------------------
# Data loader (single source of truth)
# ---------------------------------------------------------------------
def load_data(path: str, **opts: Any) -> pd.DataFrame:
    p = pathlib.Path(path)
    ext = p.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(p, **opts)
    if ext in {".json"}:
        return pd.read_json(p, **opts)
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(p, **opts)
    if ext in {".parquet", ".pq"}:
        try:
            return pd.read_parquet(p, **opts)
        except Exception as e:
            raise RuntimeError("Reading Parquet requires pyarrow or fastparquet.") from e
    raise ValueError(f"Unsupported file type: {ext}")


# ---------------------------------------------------------------------
# Rule-based parser (MVP intents)
# ---------------------------------------------------------------------
@dataclass
class Plan:
    op: str
    args: Dict[str, Any]
    alias: Optional[str] = None  # e.g., ... as orders


# Load + basic summaries/plots
_PAT_LOAD = re.compile(
    r'^(?:read|load)\s+(?:data\s+from\s+)?(?:file\s+)?["\'](?P<path>[^"\']+)["\']',
    re.I,
)
_PAT_HEAD = re.compile(r"\bhead\s+(?P<n>\d+)\b", re.I)
_PAT_DESC = re.compile(r"\bdescribe\b", re.I)
_PAT_HIST = re.compile(r"\bplot\s+(?:a\s+)?hist(?:ogram)?\s+of\s+(?P<col>[\w\.]+)", re.I)
_PAT_ALIAS = re.compile(r"\bas\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b")

# Extra offline ops (filter/select/sort/group/line/bar)
_PAT_FILTER = re.compile(
    r'^filter(?:\s+(?P<src>[A-Za-z_]\w*))?\s+where\s+(?P<cond>.+?)(?:\s+as\s+(?P<alias>[A-Za-z_]\w*))?$',
    re.I,
)
_PAT_SELECT = re.compile(
    r'^select\s+(?P<cols>[A-Za-z0-9_,\s]+)(?:\s+from\s+(?P<src>[A-Za-z_]\w*))?(?:\s+as\s+(?P<alias>[A-Za-z_]\w*))?$',
    re.I,
)
_PAT_SORT = re.compile(
    r'^sort(?:\s+(?P<src>[A-Za-z_]\w*))?\s+by\s+(?P<cols>[A-Za-z0-9_,\s]+)(?:\s+(?P<order>asc|desc))?(?:\s+as\s+(?P<alias>[A-Za-z_]\w*))?$',
    re.I,
)
_PAT_GROUP = re.compile(
    r'^group(?:\s+(?P<src>[A-Za-z_]\w*))?\s+by\s+(?P<keys>[A-Za-z0-9_,\s]+)\s+and\s+(?P<agg>sum|mean|count|min|max)\s+(?P<val>[A-Za-z_]\w*)(?:\s+as\s+(?P<alias>[A-Za-z_]\w*))?$',
    re.I,
)
_PAT_LINE = re.compile(
    r'^plot\s+(?:a\s+)?line\s+(?:chart|plot)\s+of\s+(?P<y>[A-Za-z_]\w*)\s+by\s+(?P<x>[A-Za-z_]\w*)(?:\s+from\s+(?P<src>[A-Za-z_]\w*))?$',
    re.I,
)
_PAT_BAR = re.compile(
    r'^plot\s+(?:a\s+)?bar\s+(?:chart|plot)\s+of\s+(?P<y>[A-Za-z_]\w*)\s+by\s+(?P<x>[A-Za-z_]\w*)(?:\s+from\s+(?P<src>[A-Za-z_]\w*))?$',
    re.I,
)


def parse_basic(command: str) -> Optional[Plan]:
    m = _PAT_LOAD.search(command)
    if not m:
        return None
    plan = Plan(op="load", args={"path": m.group("path")})
    if _PAT_HEAD.search(command):
        n = int(_PAT_HEAD.search(command).group("n"))
        plan.op = "load_head"
        plan.args["n"] = n
    if _PAT_DESC.search(command):
        plan.op = "load_describe"
    ph = _PAT_HIST.search(command)
    if ph:
        plan.op = "load_plot_hist"
        plan.args["col"] = ph.group("col")
    ma = _PAT_ALIAS.search(command)
    if ma:
        plan.alias = ma.group("name")
    return plan


def _coerce(v: str):
    v = v.strip()
    if (len(v) >= 2) and ((v[0] == v[-1]) and v[0] in {"'", '"'}):
        return v[1:-1]
    try:
        if "." in v:
            return float(v)
        return int(v)
    except Exception:
        return v


def _apply_condition(df: pd.DataFrame, cond: str) -> pd.DataFrame:
    parts = re.split(r"\s+and\s+", cond, flags=re.I)
    mask = pd.Series(True, index=df.index)
    for part in parts:
        m = re.match(r"\s*(?P<col>[A-Za-z_]\w*)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<val>.+)\s$", part)
        if not m:
            m = re.match(r"\s*(?P<col>[A-Za-z_]\w*)\s*(?P<op>==|!=|>=|<=|>|<)\s*(?P<val>.+)\s*$", part)
            if not m:
                raise ValueError(f"Could not parse condition: {part!r}")
        col, op, val = m.group("col"), m.group("op"), _coerce(m.group("val"))
        if col not in df.columns:
            raise ValueError(f"Unknown column: {col}")
        lhs = df[col]
        if op == "==":
            cur = lhs == val
        elif op == "!=":
            cur = lhs != val
        elif op == ">=":
            cur = lhs >= val
        elif op == "<=":
            cur = lhs <= val
        elif op == ">":
            cur = lhs > val
        elif op == "<":
            cur = lhs < val
        else:
            raise ValueError(f"Operator not supported: {op}")
        mask &= cur
    return df[mask]


def parse_ops(command: str) -> Optional[Plan]:
    m = _PAT_FILTER.match(command)
    if m:
        return Plan("filter", {"src": m.group("src") or "df", "cond": m.group("cond")}, alias=m.group("alias"))
    m = _PAT_SELECT.match(command)
    if m:
        cols = [c.strip() for c in m.group("cols").split(",") if c.strip()]
        return Plan("select", {"src": m.group("src") or "df", "cols": cols}, alias=m.group("alias"))
    m = _PAT_SORT.match(command)
    if m:
        cols = [c.strip() for c in m.group("cols").split(",") if c.strip()]
        order = (m.group("order") or "asc").lower()
        return Plan("sort", {"src": m.group("src") or "df", "cols": cols, "ascending": order == "asc"}, alias=m.group("alias"))
    m = _PAT_GROUP.match(command)
    if m:
        keys = [k.strip() for k in m.group("keys").split(",") if k.strip()]
        return Plan("group_agg", {"src": m.group("src") or "df", "keys": keys, "agg": m.group("agg"), "val": m.group("val")}, alias=m.group("alias"))
    m = _PAT_LINE.match(command)
    if m:
        return Plan("plot_line", {"src": m.group("src") or "df", "x": m.group("x"), "y": m.group("y")})
    m = _PAT_BAR.match(command)
    if m:
        return Plan("plot_bar", {"src": m.group("src") or "df", "x": m.group("x"), "y": m.group("y")})
    return None


# ---------------------------------------------------------------------
# Safe execution sandbox
# ---------------------------------------------------------------------
_FORBID_NODES = (ast.Import, ast.ImportFrom)
_FORBID_NAMES = {"__import__", "eval", "exec", "open", "compile", "input", "globals", "locals"}
_FORBID_ATTRS = {"system", "popen", "fork", "remove", "rmtree", "unlink"}

# Allow a curated set of safe builtins so “any code” (e.g., primes) can run.
_SAFE_BUILTINS: Dict[str, Any] = {
    # core types / constructors
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,

    # iter/tools
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "sorted": sorted,
    "map": map,
    "filter": filter,

    # math-ish
    "min": min,
    "max": max,
    "sum": sum,
}


def _assert_safe(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, _FORBID_NODES):
            raise RuntimeError("Imports are not allowed in speak2py execution.")
        if isinstance(node, ast.Name) and node.id in _FORBID_NAMES:
            raise RuntimeError(f"Use of {node.id} is not allowed.")
        if isinstance(node, ast.Attribute) and node.attr in _FORBID_ATTRS:
            raise RuntimeError(f"Attribute {node.attr} is not allowed.")


def safe_exec(code: str, scope: Dict[str, Any]) -> Dict[str, Any]:
    tree = ast.parse(code, mode="exec")
    _assert_safe(tree)
    compiled = compile(tree, "<speak2py>", "exec")
    safe_globals: Dict[str, Any] = {"__builtins__": _SAFE_BUILTINS, "pd": pd, "plt": plt, **scope}
    local: Dict[str, Any] = {}
    exec(compiled, safe_globals, local)
    return local


# ---------------------------------------------------------------------
# Session (stateful) + public API
# ---------------------------------------------------------------------
class Session:
    def __init__(self) -> None:
        self.vars: Dict[str, Any] = {}        # named objects (e.g., DataFrames or anything else)
        self.last: Any = None                 # last result
        self.history: list[str] = []          # command history
        self.metrics: Dict[str, Any] = {
            "llm_calls": 0,
            "llm_errors": 0,
            "exec_errors": 0,
            "llm_latency": [],
            "exec_latency": [],
        }
        # AI-first; auto-downloads model + server on first use
        self.llm = AutoLlamaServerProvider()  # default

    def run(self, command: str, *, mode: str = "auto", return_code: bool = False) -> Any:
        """
        mode: "auto" | "data" | "code"
          - auto: try rule-based; else LLM → execute if sandbox-safe; if blocked, return code
          - data: force execution path (only if safe)
          - code: return code only, do not execute
        """
        self.history.append(command)
        alias: Optional[str] = None

        # 1) Fast rule-based plan (load/head/describe/hist)
        plan = parse_basic(command)
        if plan:
            alias = plan.alias
            res = self._execute_plan(plan)
            return self._finalize(res, alias)

        # 1b) Offline ops
        plan2 = parse_ops(command)
        if plan2:
            alias = plan2.alias
            res = self._execute_plan(plan2)
            return self._finalize(res, alias)

        # 2) LLM path (AI is on by default)
        if mode == "code" or return_code:
            return self._to_code(command)

        code = self._to_code(command)
        try:
            res = self._execute_code(code)
            # allow alias like “… as name” even in LLM path
            m = _PAT_ALIAS.search(command)
            if m:
                alias = m.group("name")
            return self._finalize(res, alias)
        except Exception as e:
            _log.warning("Execution blocked or failed; returning code. Error: %s", e)
            return code

    # ---- helpers ----
    def _execute_plan(self, plan: Plan) -> Any:
        if plan.op == "load":
            return load_data(plan.args["path"])
        if plan.op == "load_head":
            df = load_data(plan.args["path"])
            return df.head(plan.args["n"])
        if plan.op == "load_describe":
            df = load_data(plan.args["path"])
            return df.describe()
        if plan.op == "load_plot_hist":
            df = load_data(plan.args["path"])
            ax = df[plan.args["col"]].plot(kind="hist")
            return self._save_plot(ax)

        # Ops require an existing source in state (alias or df)
        if plan.op in {"filter", "select", "sort", "group_agg", "plot_line", "plot_bar"}:
            src = plan.args["src"]
            if src not in self.vars:
                if src != "df" or "df" not in self.vars:
                    raise ValueError(f"Unknown source '{src}'. Load data first or use 'as name'.")
            df = self.vars.get(src, self.vars.get("df"))

            if plan.op == "filter":
                return _apply_condition(df, plan.args["cond"])

            if plan.op == "select":
                cols = plan.args["cols"]
                for c in cols:
                    if c not in df.columns:
                        raise ValueError(f"Unknown column: {c}")
                return df[cols]

            if plan.op == "sort":
                return df.sort_values(plan.args["cols"], ascending=plan.args["ascending"])

            if plan.op == "group_agg":
                keys, agg, val = plan.args["keys"], plan.args["agg"], plan.args["val"]
                if val not in df.columns:
                    raise ValueError(f"Unknown column: {val}")
                g = df.groupby(keys)[val]
                fn = {"sum": "sum", "mean": "mean", "count": "count", "min": "min", "max": "max"}[agg]
                res = getattr(g, fn)().reset_index().rename(columns={val: f"{val}_{fn}"})
                return res

            if plan.op in {"plot_line", "plot_bar"}:
                x, y = plan.args["x"], plan.args["y"]
                if x not in df.columns or y not in df.columns:
                    raise ValueError(f"Unknown column(s): {x}, {y}")
                ax = df.plot(x=x, y=y, kind="line" if plan.op == "plot_line" else "bar")
                return ax

        raise ValueError(f"Unknown plan: {plan.op}")

    def _to_code(self, command: str) -> str:
        t0 = time.time()
        try:
            code = self.llm.to_code(command)   # direct call; provider handles server/downloads
        except Exception:
            self.metrics["llm_errors"] += 1
            raise
        finally:
            self.metrics["llm_calls"] += 1
            self.metrics["llm_latency"].append(time.time() - t0)
        return code

    def _execute_code(self, code: str) -> Any:
        t0 = time.time()
        try:
            # Provide previously named DataFrames in scope for convenience
            df_scope = {k: v for k, v in self.vars.items() if isinstance(v, pd.DataFrame)}
            local = safe_exec(code, {"load_data": load_data, **df_scope})
            if "result" not in local:
                raise RuntimeError("Generated code did not set `result`.")
            return local["result"]
        except Exception:
            self.metrics["exec_errors"] += 1
            raise
        finally:
            self.metrics["exec_latency"].append(time.time() - t0)

    def _finalize(self, res: Any, alias: Optional[str]) -> Any:
        # Promote plots to PNG file path
        if hasattr(res, "savefig"):
            res = self._save_figure(res)
        if isinstance(res, plt.Axes):
            res = self._save_plot(res)

        # Save DataFrame to the canonical "df" for easy follow-ups
        if isinstance(res, pd.DataFrame):
            self.vars["df"] = res
        # Save alias (for any object)
        if alias:
            self.vars[alias] = res

        self.last = res
        return res

    def _save_plot(self, ax: plt.Axes) -> str:
        out = pathlib.Path.home() / ".cache" / "speak2py" / "plots" / f"{uuid.uuid4().hex}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig = ax.get_figure()
        fig.savefig(out)
        plt.close(fig)
        return str(out)

    def _save_figure(self, fig: plt.Figure) -> str:
        out = pathlib.Path.home() / ".cache" / "speak2py" / "plots" / f"{uuid.uuid4().hex}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out)
        plt.close(fig)
        return str(out)


# Singleton
_SESSION: Optional[Session] = None

def _get_session() -> Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = Session()
    return _SESSION


# Public API
def speak2py(command: str, *, mode: str = "auto", return_code: bool = False) -> Any:
    """Primary user entry point (stateful)."""
    return _get_session().run(command, mode=mode, return_code=return_code)

def speak2py_code(command: str) -> str:
    """Return code only (never execute)."""
    return _get_session().run(command, mode="code", return_code=True)
