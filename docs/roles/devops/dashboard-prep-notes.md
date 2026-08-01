# DevOps prep notes — D-TRADE-023 equity-tool browser dashboard

**Status:** prep only, per the Lead's assignment — waiting on the Architect's design note (framework
choice, API shape, module/entry-point path) before finalizing. Nothing built yet; environment checked so
the moment the contract lands, install + scaffold is a fast, no-surprises step.

**Scope note (D-TRADE-023, verbatim):** this is the equity-side `tools/rolling_watchlist.py` getting a
browser UI — explicitly **not** a HELM Phase-1 reversal (`<1.1>`/`<3.5>` "no web surface" stands for the
options-screener validation work). Separate initiative, does not block or get blocked by the HELM
gate-harness work in `docs/roles/devops/harness-design.md`. No D-TRADE-010-style build freeze applies here
— `tools/rolling_watchlist.py` is a live, already-committed tool (`4252e22`, `5e41dc2`, `ddda930`); this is
additive work on it, team-assigned by the Director.

## 1 · Existing tool (read, not modified)
`tools/rolling_watchlist.py` (66.6 KB) — argparse CLI, already wired to Massive (`MASSIVE_API_KEY` env var
or `massive_api_key.txt`, resolved by `_resolve_massive_api_key()`), matplotlib output. Runs the
rollover-check + intraday pivot/red-to-green pattern detection + a trade simulator. This is the logic the
new browser UI will call into — the CLI presumably keeps working too, the dashboard is a new surface, not
a replacement (to be confirmed by the Architect's note; not assuming).

## 2 · Toolchain check (2026-08-01, this session)
| Package | Status |
|---|---|
| flask, fastapi, uvicorn, starlette, jinja2, gunicorn, waitress, werkzeug, streamlit, dash, plotly, bottle | 🔴 **none installed** — a clean slate, whichever the Architect picks needs a fresh `pip install` |
| Core analysis stack (pandas/numpy/matplotlib) | ✅ already installed (shared with HELM's toolchain check) |
| `webbrowser` (stdlib) | ✅ always available — the "launch and open a tab" mechanic needs zero extra deps regardless of framework choice |

**Cost note (all $0):** Flask and FastAPI are both free, pure-pip installs; no paid tier, no infra floor.
FastAPI additionally needs `uvicorn` (ASGI server) — Flask's built-in dev server needs nothing extra for a
personal single-user tool. Neither choice has a dollar cost; this is a pure engineering tradeoff for the
Architect, not a FinOps item.

## 3 · Ports checked free (2026-08-01)
5000 (Flask default) · 8000 (a common FastAPI/uvicorn default) · 8080 · 8501 (Streamlit default, in case
that's considered) — all FREE. Whichever port the Architect's note specifies, no collision to design
around.

## 4 · Dev-run tooling — recommendation (light, pending Architect confirmation)
For a personal, single-user tool: `python tools/web/app.py` (or whatever entry path the Architect
specifies) that (a) starts the dev server, (b) calls stdlib `webbrowser.open(url)` once the server is up,
so the Director never has to type a URL. No process manager, no reverse proxy, no Docker — matches the
"no need for anything heavier" framing. If FastAPI is chosen, `uvicorn.run(...)` from inside `app.py`
keeps the single-entry-point property (vs. requiring a separate `uvicorn app:app` CLI invocation).

## 5 · Secret hygiene (already correct, verified)
`MASSIVE_API_KEY` / `massive_api_key.txt` are already gitignored and clean in history (`ddda930`,
2026-08-01 — the rotated key was caught in the *template* file, not the real one, before it ever reached
git). The browser UI reuses the same resolution path — no new secret-handling surface, but the leg K
secret-scan (already designed for HELM, `docs/roles/devops/harness-design.md` §C) should extend to cover
this tool's tree too once the dashboard's actual paths are known, since `tools/` is currently outside
HELM's `helm/` package and needs its own coverage check.

## 6 · Holding on (waiting for the Architect's note)
- Framework choice (Flask vs. FastAPI vs. other) — affects the `pip install` list and the entry-point shape.
- API shape — what the browser UI actually calls (REST endpoints? a single results-JSON on load? SSE for
  live updates during a long scan?) — affects whether this needs any dev-run complexity beyond §4.
- Module/entry-point path (`tools/web/app.py` was the Lead's example, not confirmed).

Ready to finalize the instant the Architect's note lands — no design blockers, just waiting on the input
that determines *which* light scaffold to stand up.
