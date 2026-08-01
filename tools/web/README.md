# Rolling Watchlist — browser UI

A thin Flask read-only serving layer over `tools/rolling_watchlist.py` (unchanged; imported, never
forked). Personal, single-user, localhost-only — no auth, no remote deploy (ADR-0002 non-goals).

## Run it

```bash
pip install -r tools/requirements.txt   # once
flask --app tools/web/app run --port 5000
```

Then open `http://127.0.0.1:5000` in a browser. Or use the Claude Code preview: the repo's
`.claude/launch.json` has a `rolling-watchlist-web-ui` entry pre-wired to the command above.

Flask's built-in dev server is sufficient here (ADR-0002 §2.1) — a long scan runs synchronously
(`threaded=True` on the app so a health poll isn't blocked by an in-flight scan), acceptable for one
user hitting a blocking pandas/Massive pipeline. No production WSGI server, no process manager, no
Docker.

## The Massive API key requirement

The web UI resolves the key **exactly the same way the CLI does** — `_resolve_massive_api_key()` in
`tools/rolling_watchlist.py`, checked server-side only:

1. the `MASSIVE_API_KEY` environment variable, or
2. a `massive_api_key.txt` file next to the script (`tools/massive_api_key.txt`) or one directory up
   (the repo root) — **gitignored**, never committed. See `massive_api_key.txt.template` at the repo
   root for the exact placement instructions (read it before pasting a key anywhere).

**The key never leaves the server.** `GET /api/health` reports only `massiveKeyPresent: true|false` —
never the value. `POST /api/scan` does not accept a key from the client; every Massive call happens
inside `tools/rolling_watchlist.py`, which is only ever imported by `tools/web/scan_service.py`, never
duplicated or re-implemented in the web layer (ADR-0002 §2.3/§3, "Security (leg K/T)").

If `massiveKeyPresent` is `false` on `/api/health`, follow the template's instructions above before
scanning — the endpoints will otherwise fail exactly as the CLI does today when the key is missing.

## Boot smoke check

`python scripts/smoke_rolling_watchlist_web.py` — starts the server, polls `/api/health`, asserts it
comes up and the response shape is correct, then stops it. Exit 0 = pass. Exit 2 = `tools/web/app.py`
doesn't exist yet (nothing to check yet, not a failure). See the script's docstring.
