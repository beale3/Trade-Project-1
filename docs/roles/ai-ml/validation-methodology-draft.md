# Walk-forward-CV validation engine — methodology draft (AI/ML)

> **RE-AUTHORED 2026-08-04 (D-TRADE-028), not patched (LL-19/protocol 19).** The prior version of this
> file designed a directional-correctness label over an *option's* DTE window (calls/puts, 0.40 delta,
> 25–45 DTE, an OTM-distance threshold). **That entire framing is deleted, not parked** — canonical
> `<1.1>`/`<3.6>` (2026-08-04): no options in scope, plain stock buy signals exited via a trailing-stop
> rule. If options ever re-enter scope, that's a new elicitation, not a resurrection of the deleted text.
>
> **Status: DESIGN/PLANNING ONLY. No pipeline code, no data pulled, no numbers computed.** P-1
> (D-TRADE-010 no-build) is **unchanged by this pivot** — still Director-pending, still bars production
> code. **P-2 (locate the screener) is MOOT, not resolved-by-search** — it was never actually missing;
> `tools/rolling_watchlist.py` (already deeply read for D-TRADE-023) is the scanner, already in-repo,
> already Massive-wired.
>
> **Holding on the label/component-list/horizon redesign per the Lead's explicit instruction** — canonical
> `<3.6>` dispatches that to the Architect (an ADR-0001 revision), specifically so AI/ML and the Architect
> converge once rather than drafting two independent guesses (the pattern that worked well the first time
> — protocol 15). This file states what survives unchanged, what's deleted, and the grounding I can offer
> the Architect — not a redesign of my own.

## 0 · What survives unchanged (canonical `<3.6>` says so explicitly — not reopened by this pivot)
- **The CLEARANCE BAR (D-TRADE-021).** A component is **CLEARED** only if it beats naive OOS under
  **BOTH** LOO-CV **and** 5-fold CV (≥30 seeds), **≥90% of seeds agreeing**; **NOT CLEARED** otherwise;
  **VOID** on any leakage/contamination finding regardless. A validation-discipline rule, not an
  options-specific one.
- **The no-lookahead invariant (NN-1, ADR-0001 §8).** Every feature/label at `t` uses only data `≤ t`,
  point-in-time joined exactly as the short-interest study did. Still the single most safety-critical
  non-negotiable.
- **Per-component isolation.** Test each scanner component **separately**, never bundled into the
  composite score — the "don't bundle" discipline the short-interest study followed testing
  `days_to_cover`/`si_over_avg_vol_20d` independently. Applies to whatever the new component list turns
  out to be (`<3.6>`, dispatched).
- **Verdict format.** **CLEARED** / **NOT CLEARED** / **VOID**, no partial credit — the existing 4-study
  precedent (short-interest kept; regime/catalyst/float dropped).

## 1 · What's deleted (D-TRADE-028, LL-19 — not resurrected here even as reference)
The DTE-window directional-correctness label, the volatility-scaled-vs-delta-implied threshold design,
the 25/35/45-DTE horizons, and the IV-rank component — all designed around an option's payoff structure
that no longer exists in scope (`<1.1>`). The "P1-2 screener-location blocker" this file previously led
with is also gone — resolved as moot, not by search (see status banner).

## 2 · Grounding for the Architect's `<3.6>` redesign (facts, not a competing design)
Not proposing a label or component list — holding for the ADR revision. But I already have direct,
load-bearing grounding from building `tools/web/scan_service.py` (D-TRADE-023) worth handing over before
the Architect starts, the same "ground before designing" move that worked well for ADR-0002:

- **`simulate_day_trades()` (`tools/rolling_watchlist.py:723-817`) has a FIXED stop/target today, not a
  trailing stop.** On entry: `stop = entry * (1 - stop_loss_pct/100)` and
  `target = entry + (entry - stop) * min_risk_reward` — both computed once at entry and never adjusted as
  price moves favorably. A trailing-stop rule (canonical `<1.1>`/`<1.4>`) is new logic, not a parameter
  tweak on the existing function — it needs the stop to ratchet up (long) as the highest price-since-entry
  rises, which the current bar-by-bar loop structure can accommodate (it already tracks position state
  across bars) but doesn't implement.
- **The existing halt conditions** (`max_loss_per_trade_dollars`, `max_daily_loss_dollars`,
  `profit_giveback_pct` — a *daily* peak-giveback halt, not a *per-trade* trailing exit) stay orthogonal to
  a trailing-stop redesign; they're circuit breakers on the trading session, not the per-trade exit rule
  itself. Worth the Architect not conflating the two when scoping `<3.6>`.
- **Candidate components already confirmed real and independently computable** (from serializing all of
  them for D-TRADE-023): guardrail (`scan_guardrail_criteria`), S3 (`compute_s3_score`), P&D phase
  (`classify_pnd_phase`), the 8 pattern detectors (`scan_all_patterns` — bull-flag/flat-top/ABCD/
  micro-pullback/round-number/opening-range/premarket-pivot/premarket-high), and the pivot/red-to-green
  alignment trigger (`analyze_intraday_alignment`) — canonical `<1.1>` names the pattern detectors +
  alignment trigger as the ones "not yet validated by the 4 completed studies." All are already
  cleanly separable per-component (no bundling needed) since D-TRADE-023 already wired each independently.
- **Universe (`<2.2>`, also dispatched to Architect/Data-Eng):** flagging conditionally, not asserting —
  my prior point-in-time-universe-membership/survivorship-bias concern was scoped to a rolling S&P/Russell-
  class index backtest, which `<2.2>` now says may not be needed at all (reverting to user-supplied
  tickers, like the 4 prior studies and `tools/rolling_watchlist.py --tickers` already do). If the universe
  question resolves to "user-supplied, no rolling index," this concern doesn't apply and I'm not carrying
  it forward as a requirement.

## 3 · Open items
1. **Architect's `<3.6>` ADR revision** — holding, not drafting a parallel version (Lead's explicit
   instruction). Will engage the moment it's dispatched to me.
2. **P-1 (D-TRADE-010)** — still Director-pending, unchanged by this pivot. No production code regardless
   of how `<3.6>` resolves.
3. **`<2.2>` universe question** — noted above; not mine to resolve, flagged for awareness only.
