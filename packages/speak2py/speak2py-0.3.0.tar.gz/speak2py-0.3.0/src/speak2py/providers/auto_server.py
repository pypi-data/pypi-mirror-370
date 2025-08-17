# src/speak2py/providers/auto_server.py
from __future__ import annotations
"""
AutoLlamaServerProvider
-----------------------
Runs a local `llama.cpp` HTTP server (llama-server) and uses it to turn
natural language into Python code. Designed for "AI on by default" with
zero credentials and fully local inference.

Behavior
- Ensures a model (GGUF) and a server binary exist in ~/.cache/speak2py/.
  * If missing and URLs are provided via env, downloads them.
  * Otherwise raises a clear error.
- Starts the server on 127.0.0.1:<port> if not already running.
- Calls modern `/v1/chat/completions`; falls back to `/v1/completions` and
  legacy `/completion` for older servers.
- Strips code fences and returns only code text.

Env knobs
- SPEAK2PY_LLAMA_HOST           (default 127.0.0.1)
- SPEAK2PY_LLAMA_PORT           (default 11435)
- SPEAK2PY_HTTP_TIMEOUT         (default 300 seconds)
- SPEAK2PY_MAX_TOKENS           (default 256)
- SPEAK2PY_CTX                  (default 4096)
- SPEAK2PY_MODEL_PATH           (override model path)
- SPEAK2PY_LLAMA_BIN            (override server binary path)
- SPEAK2PY_MODEL_URL            (download model if missing)
- SPEAK2PY_LLAMA_SERVER_URL     (download server binary if missing)
"""

import os
import re
import json
import time
import stat
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

# -------------------- constants & paths --------------------
DEFAULT_HOST   = os.getenv("SPEAK2PY_LLAMA_HOST", "127.0.0.1")
DEFAULT_PORT   = int(os.getenv("SPEAK2PY_LLAMA_PORT", "11435"))
TIMEOUT        = int(os.getenv("SPEAK2PY_HTTP_TIMEOUT", "300"))
MAX_TOKENS     = int(os.getenv("SPEAK2PY_MAX_TOKENS", "256"))
DEFAULT_CTX    = int(os.getenv("SPEAK2PY_CTX", "4096"))

CACHE_DIR   = Path.home() / ".cache" / "speak2py"
RUNTIME_DIR = Path(os.getenv("SPEAK2PY_RUNTIME_DIR", str(CACHE_DIR / "runtime")))
MODEL_DIR   = Path(os.getenv("SPEAK2PY_MODEL_DIR",   str(CACHE_DIR / "models")))

BIN_PATH   = Path(os.getenv("SPEAK2PY_LLAMA_BIN",   str(RUNTIME_DIR / ("llama-server.exe" if os.name == "nt" else "llama-server"))))
MODEL_PATH = Path(os.getenv("SPEAK2PY_MODEL_PATH",  str(MODEL_DIR / "default.gguf")))

BIN_URL   = os.getenv("SPEAK2PY_LLAMA_SERVER_URL", "")
MODEL_URL = os.getenv("SPEAK2PY_MODEL_URL",        "")


# -------------------- provider --------------------
class AutoLlamaServerProvider:
    """Downloads (if URLs set), starts, and talks to a local llama.cpp server."""

    def __init__(self, ctx: int = DEFAULT_CTX) -> None:
        self.ctx = int(ctx)
        self._proc: Optional[subprocess.Popen] = None
        self._ensure_assets()
        self._ensure_server()
        self._ready = True  # compat

    # Back-compat for callers that probe .available
    @property
    def available(self) -> bool:  # pragma: no cover
        return True

    # --------------- asset management ---------------
    def _download(self, url: str, out: Path, label: str) -> None:
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(url) as r, open(out, "wb") as f:
                # simple streamed copy
                chunk = 1024 * 1024
                while True:
                    buf = r.read(chunk)
                    if not buf:
                        break
                    f.write(buf)
        except Exception as e:  # pragma: no cover - network/env specific
            raise RuntimeError(f"Failed to download {label} from {url}: {e}")

    def _ensure_assets(self) -> None:
        # model
        if not MODEL_PATH.exists():
            if MODEL_URL:
                self._download(MODEL_URL, MODEL_PATH, "GGUF model")
            else:
                raise RuntimeError(
                    f"Model not found at {MODEL_PATH}. Set SPEAK2PY_MODEL_URL or place a GGUF there.")
        # binary
        if not BIN_PATH.exists():
            if BIN_URL:
                self._download(BIN_URL, BIN_PATH, "llama-server binary")
                try:
                    BIN_PATH.chmod(BIN_PATH.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                except Exception:
                    pass
            else:
                raise RuntimeError(
                    f"Server binary not found at {BIN_PATH}. Set SPEAK2PY_LLAMA_SERVER_URL or place it there.")
        else:
            # ensure executable bit on *nix
            try:
                BIN_PATH.chmod(BIN_PATH.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except Exception:
                pass

    # --------------- server lifecycle ---------------
    def _ping(self) -> bool:
        for path in ("/v1/models", "/health"):
            try:
                with urllib.request.urlopen(f"http://{DEFAULT_HOST}:{DEFAULT_PORT}{path}", timeout=1) as r:
                    if r.status == 200:
                        return True
            except Exception:
                continue
        return False

    def _ensure_server(self) -> None:
        if self._ping():
            return
        args = [
            str(BIN_PATH),
            "-m", str(MODEL_PATH),
            "--host", DEFAULT_HOST,
            "--port", str(DEFAULT_PORT),
            "-c", str(self.ctx),
        ]
        # quiet background spawn
        try:
            self._proc = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0),
            )
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to start llama-server: {e}")

        # wait for readiness
        t0 = time.time()
        while time.time() - t0 < 60:
            if self._ping():
                return
            # early exit if crashed
            if self._proc and self._proc.poll() is not None:
                break
            time.sleep(0.5)
        raise RuntimeError("Embedded llama-server failed to start (timeout).")

    def stop(self) -> None:  # pragma: no cover - exercised at process exit usually
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass

    # --------------- HTTP helpers ---------------
    def _post_json(self, path: str, payload: dict, timeout: int = TIMEOUT) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"http://{DEFAULT_HOST}:{DEFAULT_PORT}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    # --------------- main API ---------------
    def to_code(self, prompt: str) -> str:
        system = (
            "Write ONLY Python code. No explanations.\n"
            "Allowed: pandas as pd, matplotlib.pyplot as plt, and load_data(path).\n"
            "Do not import anything. Final line must assign to variable result.\n"
            "If not DataFrame-related, still return valid Python with result.\n"
        )

        # Preferred: OpenAI-style chat
        chat = {
            "model": "embedded",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": MAX_TOKENS,
        }
        try:
            resp = self._post_json("/v1/chat/completions", chat)
            code = resp["choices"][0]["message"]["content"].strip()
        except Exception:
            # Retry ensure + fallbacks for broad server compatibility
            self._ensure_server()
            try:
                resp = self._post_json("/v1/chat/completions", chat)
                code = resp["choices"][0]["message"]["content"].strip()
            except Exception:
                # OpenAI text completions
                comp = {
                    "model": "embedded",
                    "prompt": f"{system}\nUser: {prompt}\n",
                    "temperature": 0.2,
                    "max_tokens": MAX_TOKENS,
                }
                try:
                    resp = self._post_json("/v1/completions", comp)
                    code = resp["choices"][0]["text"].strip()
                except Exception:
                    # Legacy llama.cpp endpoint
                    legacy = {
                        "prompt": f"{system}\nUser: {prompt}\n",
                        "temperature": 0.2,
                        "n_predict": MAX_TOKENS,
                        "stop": ["```", "</s>"],
                    }
                    req = urllib.request.Request(
                        f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/completion",
                        data=json.dumps(legacy).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                        resp = json.loads(r.read().decode("utf-8"))
                    code = resp.get("content", "").strip()

        # Strip code fences if present
        if code.startswith("```"):
            code = re.sub(r"^```[a-zA-Z0-9_-]*\n|```$", "", code, flags=re.S)
        if not code:
            raise RuntimeError("Local model returned empty code.")
        return code
