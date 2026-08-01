# ADR-0002 — Rolling-Watchlist browser UI: backend, API contract, module layout

- **Status:** PROPOSED (design note — proportionate to a personal side-tool, not ADR-0001 scale).
- **adr_reference id:** `ADR-0002` (cite on the three build tasks below).
- **Author:** Principal Architect. **Date:** 2026-08-01. **Governs:** D-TRADE-023 (equity side-tool → browser UI).
- **Scope:** the equity-side tool `tools/rolling_watchlist.py` ONLY. Does **not** reopen HELM Phase-1's
  no-web-surface framing (`<1.1>`/`<3.5>`) — that stays as-is (D-TRADE-023).
- **UI-mockup gate (protocol 10): SATISFIED** — the Director already commissioned + approved the
  "Rolling Watchlist" dashboard mockup. The Designer's task here is **wiring, not redesign**.

## 1 · Context (grounded in the real source)
`tools/rolling_watchlist.py` (1367 lines, wired to live Massive data) is a library+CLI whose functions
already return clean, JSON-serializable dicts. `main()` (line 1172) is the reference pipeline:
`load_daily → scan_rollover_watchlist → [for each holding-up ticker] lookup_recent_catalyst /
lookup_short_interest / scan_guardrail_criteria / load_intraday / scan_all_patterns / compute_s3_score /
classify_pnd_phase / analyze_intraday_alignment / (opt) simulate_day_trades`.

The **approved mockup** (fetched to
`…/517ca982-…/tool-results/artifact-7601fb84-1785090475-b26e.html`, 193 KB) is **fully self-contained** —
embedded TradeSlab/TradeMono fonts, **inlined D3** (no CDN), vanilla JS. Its render functions
(`renderStats`/`renderTable`/`renderDetail`) consume a single `const DATA = [...]` array of **camelCase
per-candidate objects**; a `hashSeed` generator + synthetic prior-day H/L/C fabricate illustrative values.
**Only that generator is replaced** by a real fetch — every class (`tw-*`), font, and layout stays untouched.

## 2 · Decisions

### 2.1 Backend framework → **Flask** (not FastAPI)
A single-user localhost tool that wraps **synchronous** pandas/Massive calls and returns JSON to one static
page. Flask + Werkzeug is the minimal fit: `flask --app tools/web/app run` is one command; no async,
Pydantic, uvicorn, or OpenAPI machinery is warranted for one user hitting a blocking pipeline. FastAPI's
wins (async I/O, auto-schema, concurrency) don't apply here. **Correctness note:** run with `threaded=True`
so a long scan doesn't block a health poll. Cost: $0 either way (pure-Python pip install, like ruff/mypy);
decided on simplicity + fit. Consistent with `<3.5>` Python core (Node stays dropped — no re-verify needed).

### 2.2 Adapt the approved mockup **in-place** (do NOT rebuild)
Reuse the 193 KB self-contained HTML verbatim; the **only** frontend change is replacing the `const DATA`
literal + the `hashSeed`/synthetic-prior-day block with `const DATA = await fetch('/api/scan',…)`. Justify:
the design is Director-approved, offline-self-contained, and its render layer **already encodes the exact
contract** — a rebuild would discard approved design and re-introduce risk for zero benefit (protocol 19:
approved design isn't rebuilt). The source must be **copied into the repo** at `tools/web/static/index.html`.

### 2.3 Module layout — `tools/web/` (disjoint from the scanner)
```
tools/rolling_watchlist.py   # UNCHANGED — the library/CLI; single source of truth for all logic
tools/web/
  app.py            # Flask: routes only → calls scan_service → serialize → JSON
  scan_service.py   # orchestrates rolling_watchlist.py's functions into per-candidate objects
                    #   (mirrors main()'s loop but RETURNS data instead of printing) — no business
                    #   logic of its own; imports the scanner, never forks it
  serialize.py      # Python dict/DataFrame → the §3 camelCase contract (NaN→null, Timestamp→ISO8601,
                    #   DataFrame→records)
  static/index.html # the adapted approved mockup (fonts/D3 already embedded)
  README.md         # run steps + the server-side Massive key requirement
```
The web layer is a **thin adapter over the scanner** (same principle as HELM's lane cut — no logic in the
serving layer). `tools/rolling_watchlist.py` is imported, never modified.

## 3 · API contract (matches the mockup's existing `DATA` consumer)

- `GET /api/health` → `{ "ok": true, "massiveKeyPresent": <bool> }` — presence only, **never the key value** (leg K).
- `POST /api/scan` — request body:
  ```json
  { "tickers": ["OBAI","GME"], "period":"3mo", "lookbackDays":5, "gainThreshold":20.0,
    "pullbackThreshold":50.0,
    "guardrail": { "minGainPct":10.0, "minRelVolume":2.0, "priceMin":2.0, "priceMax":20.0, "maxFloat":20000000 },
    "intraday": { "period":"5d", "interval":"5m" },
    "simulate": { "enabled":false, "stopLossPct":2.0, "minRiskReward":2.0, "sharesPerTrade":100,
                  "maxLossPerTrade":null, "maxDailyLoss":null, "profitGivebackPct":15.0 } }
  ```
  response:
  ```json
  { "meta": { "ranAt":"<ISO8601>", "tickerCount":2, "params":{…echoed…} },
    "stats": { "candidatesScanned":6, "holdingUp":4, "alignedNow":3, "avgS3Pct":86.4 },
    "candidates": [ Candidate, … ] }
  ```
- **`Candidate`** (camelCase; a non-holding-up name carries `holdingUp:false` and **null** for every
  downstream field — mirrors the real scan, which never computes them, and matches the mockup exactly):
  ```json
  { "ticker":"NVXA", "spikeDate":"2026-07-14", "spikeGainPct":62.4, "holdingUp":true,
    "retracementPct":18.2, "worstRetracementPct":22.0, "lastClose":3.42, "relVol":4.8,
    "todayGainPct":11.2, "hasCatalyst":true, "daysToCover":6.2, "phase":"dip_buying", "aligned":true,
    "guardrail": { "gainOk":true,"relVolOk":true,"priceOk":true,"passesCore":true,"passesAll":true,
                   "shortInterestOk":true,"floatOk":null,"catalystGates":false,"shortInterestGates":true },
    "s3": { "pattern_price":[16.5,20], "risk_reward":[15.5,20], "ease_of_entry":[8.8,10],
            "past_performance":[8.5,10], "scorePct":84.4, "rating":"Good", "isPartial":true },
    "patterns": ["micro_pullback","opening_range_breakout"],
    "intraday": { "bars":[{"t":"<ISO8601>","open":..,"high":..,"low":..,"close":..,"volume":..}, …],
                  "pivots":{"pivot":..,"r1":..,"s1":..,"r2":..,"s2":..},
                  "priorHigh":..,"priorLow":..,"priorClose":..,
                  "latestAligned":true,"firstTriggerTime":"<ISO8601|null>" },
    "simulatedTrades": { "enabled":true,"numTrades":3,"winRatePct":66.7,"finalPnl":142.0,
                         "pnlPerShare":1.42,"pnlCurve":[…],"halted":false,"haltReason":null,
                         "trades":[{"entryTime":"<ISO8601>","exitTime":"<ISO8601>","entryPrice":..,
                                    "exitPrice":..,"pnl":..,"reason":"target"}] } }
  ```
  Field provenance (serializer maps these): `guardrail` ← `scan_guardrail_criteria`; `s3` ← `compute_s3_score`
  (`component_scores`+`component_max` → the `[earned,max]` pairs; `score_pct`/`rating`/`is_partial` top-level);
  `phase` ← `classify_pnd_phase` (latest); `intraday` ← `analyze_intraday_alignment` (`levels`+`annotated`→bars)
  + `load_intraday` + the prior daily bar; `simulatedTrades` ← `simulate_day_trades` (null when `enabled:false`).

**Serialization non-negotiables** (serialize.py): NaN/None → `null`; pandas Timestamp → ISO8601 string;
DataFrame → array of records; return raw floats (the frontend already formats). **Security (leg K/T):** the
Massive key is resolved **server-side only** (`_resolve_massive_api_key()`); `/api/scan` never accepts a key
from the client and no provider call leaves `tools/rolling_watchlist.py`.

## 4 · Ownership (three disjoint build tasks, all `adr_reference: ADR-0002`)
- **AI/ML** — `tools/web/{app.py, scan_service.py, serialize.py}` (backend wiring; separate from its blocked
  HELM Phase-1 work). Owns the §3 contract's server side.
- **Designer** — `tools/web/static/index.html`: copy the approved source in, swap the `DATA` literal for the
  `/api/scan` fetch, add loading/empty/error states; keep the design system 1:1. UI-gate already satisfied.
- **DevOps** — `flask` install (pure-Python, like ruff/mypy), a run entry (`.claude/launch.json` or a
  `scripts/` runner), the server-side Massive-key env wiring, and a boot smoke check.

## 5 · Open points & non-goals
- **OP-A · long scans block the request** (N tickers × Massive latency = seconds→minutes). v1 = synchronous
  with a frontend loading state (one user, acceptable). If annoying, a later job model (`POST`→run_id, `GET`
  poll) — flagged, not built now.
- **OP-B · the intraday chart is the one place the contract meets real bars.** The mockup synthesizes
  prior-day H/L/C + intraday; the real backend supplies them from `load_intraday` + the prior daily bar.
  **Designer + AI/ML confirm the exact bar-array shape against the mockup's D3 code together** before wiring
  the chart (the single cross-seat interface point).
- **Non-goals:** no auth, no multi-user, no remote deploy — localhost personal tool (D-TRADE-023 personal
  framing). No change to `tools/rolling_watchlist.py`'s logic.
- **Complexity tier: STANDARD** — a thin read-only serving layer over an existing library; no schema, no
  money-truth surface, no auth beyond keeping the key server-side (covered by existing legs K/T).
