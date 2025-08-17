# speak2py v0.3.0— English → Python (stateful, optional offline AI)

Turn plain English into executable Python. Works out-of-the-box for common data tasks; add a tiny local model (one-time download) to unlock full AI code generation — no keys, no cloud.

pip install speak2py

from speak2py import speak2py

# Zero-setup (no AI needed):

df = speak2py('read "data/iris.csv" and head 5')

# With AI (optional; see “Enable AI” below):

out = speak2py('create a function is_prime(n); return {n:is_prime(n) for n in [2,3,4,17]}')

What you can do

Data basics (no setup): read / head / describe / histogram

Follow-ups that remember state: as orders, then reference orders later

Charts: returns a PNG file path when you ask for plots

Any Python code (with AI on): generate & run small functions/algorithms safely

Install
pip install speak2py

That’s it. You can immediately do:

from speak2py import speak2py
print(speak2py('read "data/iris.csv" and describe'))

Enable AI (optional, no build)

AI lets you ask for “any code” (not just data). To keep setup painless, speak2py looks for two files in your user cache and will also auto-download them if you give it URLs:

A small model (GGUF), e.g. TinyLlama (fast on CPU)

A tiny server binary (llama-server) that runs locally

You do not compile anything.

Option A — One-time auto-download (recommended)

Set these two environment variables to URLs you control (e.g., from your GitHub Release or shared drive) and run any speak2py command once. The library will download the files to your cache and start the local server automatically.

Windows (PowerShell):

$env:SPEAK2PY_MODEL_URL="https://<your-url>/default.gguf"
$env:SPEAK2PY_LLAMA_SERVER_URL="https://<your-url>/llama-server.exe"
python -c "from speak2py import speak2py; print(speak2py('1'))"

macOS/Linux (bash):

export SPEAK2PY_MODEL_URL="https://<your-url>/default.gguf"
export SPEAK2PY_LLAMA_SERVER_URL="https://<your-url>/llama-server"
python -c "from speak2py import speak2py; print(speak2py('1'))"

After this first run, no internet or keys are required. The server starts automatically in the background whenever you call speak2py(...).

Option B — Manual copy (also simple)

If you don’t want auto-download, just place the two files yourself:

Model →
Windows: %USERPROFILE%\.cache\speak2py\models\default.gguf
macOS/Linux: ~/.cache/speak2py/models/default.gguf

Server binary →
Windows: %USERPROFILE%\.cache\speak2py\runtime\llama-server.exe
macOS/Linux: ~/.cache/speak2py/runtime/llama-server (and chmod +x)

Then use speak2py(...) — the AI is on.

Examples
Data (no AI required)
speak2py('read "data/orders.csv" as orders and head 10')
speak2py('filter orders where status == "shipped" and amount > 100 as shipped_big')
speak2py('group shipped_big by region and sum amount as totals')
png = speak2py('plot a bar chart of totals_amount by region from totals')
print(png) # path to saved image

Any Python (with AI enabled)
speak2py('create a function fib(n); return [fib(i) for i in range(8)]')
speak2py('make a function is_palindrome(s); result = [is_palindrome(x) for x in ["aba","abc","abba"]]')

Prefer to see the code without running it?

from speak2py import speak2py_code
code = speak2py_code('write a function fizzbuzz(n) and set result = [fizzbuzz(i) for i in range(1,21)]')
print(code)

How it works (short)

Fast path (no AI): a tiny parser handles read/head/describe/hist and returns DataFrames/plots quickly.

AI path (local): speak2py talks to a local llama.cpp server running the small GGUF model. No network, no keys.

Safe sandbox: the generated code runs with a strict allowlist (no imports/OS/network). Final value must be result.

Tips & knobs (optional)

Slow CPU? Use a smaller model and shorter generations:

# optional

set SPEAK2PY_MAX_TOKENS=200 # Windows (PowerShell: $env:SPEAK2PY_MAX_TOKENS="200")
export SPEAK2PY_MAX_TOKENS=200 # macOS/Linux

If your IT blocks downloads, do Option B (manual copy).

Default server port is 11435. To change:

set SPEAK2PY_LLAMA_PORT=11436 # Windows
export SPEAK2PY_LLAMA_PORT=11436 # macOS/Linux

Troubleshooting (plain English)

“Model not found at …/default.gguf”
You haven’t provided the model yet. Use Option A (auto-download env vars) or Option B (manual copy).

“Server binary not found at …/llama-server(.exe)”
Same as above: either set the download URL env var or copy the file to the runtime path.

It’s slow
Use a smaller GGUF (e.g., TinyLlama “instruct”, Q4) and keep SPEAK2PY_MAX_TOKENS around 200.

“invalid magic … expected GGUF”
Your model file is not a real GGUF (probably an HTML page). Re-download the model and make sure the first 4 bytes spell GGUF.

FAQ

Do I need to build anything?
No. You either let speak2py auto-download a tiny server + model once, or you copy two files into your user cache. That’s it.

Do I need API keys?
No. It runs locally.

Will this hit the internet after first run?
No. After the one-time download (or manual copy), everything is local.

Can I still use speak2py without AI?
Yes. The data basics work immediately after pip install.

Release maintainer notes (not for end users)

Host two files in your GitHub Release (or any static URL):
default.gguf and llama-server(.exe)
Then document those URLs for SPEAK2PY_MODEL_URL and SPEAK2PY_LLAMA_SERVER_URL.

If you prefer to bundle them in the wheel, place them on install and skip URLs entirely (bigger package size).

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## License

MIT © 2025 Speak2Py Contributors
