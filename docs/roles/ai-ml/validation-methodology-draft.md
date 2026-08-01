# Walk-forward-CV validation engine — methodology draft (AI/ML) — D-TRADE-020 scope

> **Status: DESIGN/PLANNING ONLY. No pipeline code, no data pulled, no numbers computed.**
> Per the Lead's D-TRADE-010 flag (stage-plan.md banner): whether Phase-1 quant-research work falls
> outside D-TRADE-010's no-build ruling is a Lead recommendation, **not yet Director-confirmed**. This
> file is the methodology *contract* — the counterpart AI/ML authors to what AIQ audits against
> (`docs/eval/methodology-draft.md`) — not an implementation. Writing the actual backtest pipeline waits
> for that confirmation (or explicit Lead go-ahead) plus the inputs blocker in §1.

## 0 · Scope (canonical `<1.1>`/`<1.4>`/`<3.4>`, stage-plan P1-2/P1-3, my oracle-boundary row VERIFIER)
Build the walk-forward-CV pipeline testing each **options-screener component** (trend / momentum /
breakout / volume / IV-rank) for whether it predicts the underlying moving far enough in the right
direction within the option's ~25–45 DTE window — **directional correctness only** (`<1.1>`), explicitly
NOT full option P&L (theta/IV-crush/slippage stay out of scope — `<1.4>`, Phase 2). Same discipline as the
4 completed equity studies (LOO-CV + 5-fold/30-seed, pre-registered bar, ships only if it clears).

## 1 · 🔴 BLOCKER — screener + 0DTE backtest engine artifacts not located
Stage-plan's "Inputs to ingest" names two artifacts as "delivered as a ZIP, location TBD": the options
screener and the 0DTE backtest engine. I searched (read-only, this session): all of `Downloads\` including
every `files*.zip`/`files (N).zip` archive by content-listing (none match — contents are unrelated: chart
PNGs/CSVs, an unrelated `stocksim` scaffold, `ibkr_guardrail_scanner.py`/`day_trade_toolkit.py`, a verified
catalyst-CV script), `Desktop\` (empty), `Documents\` (no matches), the legacy `..\Trade\` stub repo (SEC
key holder only, no code), and all 4 completed study directories (equity-only, no options logic). **Not
found anywhere on this host.** This blocks P1-2 (screener ingestion) concretely — I will not reconstruct
the screener's composite-score formula from the canonical doc's prose description; that would be inventing
the artifact I'm supposed to validate, not grounding a fix on a real source (LL-45). Flagged to the Lead
in the same-day report; needs the Director or Data-Eng to locate/deliver the actual files.

**What does NOT block on this:** the methodology below is written at the level of "a component's screener
sub-score, whatever its native form in the source, is one isolated predictor" — it doesn't require the
screener's internals to be specified, only ingested once found.

## 2 · Target / label design (principled, not tuned — LL-45)
Two tiers, so Phase 1 can start on data already confirmed available (underlying OHLCV, used by all 4 prior
studies) without waiting on the options-chain/IV-history discovery item (`<2.1>`, owned by DevOps/Data-Eng,
NOT YET CONFIRMED available):

- **Primary (matches the proven template's mechanics exactly):** continuous forward log-return over each
  DTE-window horizon (e.g., `fwd_25d_ret` / `fwd_35d_ret` / `fwd_45d_ret`, mirroring the 4 studies'
  `fwd_1d/1w/1m_ret` style) — linear regression per (component, horizon), evaluated via LOO-CV + 5-fold CV
  vs. a naive (train-mean) baseline. This is the load-bearing evaluation vehicle; it's the exact mechanic
  already proven 4 times and is what "beats naive OOS" means below.
- **Phase-1-specific pre-registered success criterion — directional correctness, volatility-scaled:** a
  binary label, 1 if `sign(fwd_return) == sign(recommended direction)` AND `|fwd_return|` exceeds a
  threshold `τ = k × trailing realized volatility over the horizon` (own-stock, own-window baseline — same
  principle the short-interest study used when it normalized short interest to the cohort's own 20-day
  volume rather than an external constant, so "far enough" scales to each stock's own noise floor instead
  of an arbitrary flat %). This avoids depending on unconfirmed options-chain/IV data for a first pass.
  **Upgrade path, not a substitute:** once `<2.1>` options-chain/IV history is confirmed, a delta-implied
  OTM-distance threshold (tying "far enough" to the actual 0.40-delta structure) becomes the more faithful
  version of this same label — recorded here as a known Phase-1-to-Phase-1.5 refinement, not invented now
  as if the data already existed.
- `k` (the volatility multiplier) is a calibration value — same HUMAN/Director-ruled category as my
  PROFILE's existing "what the rules *should* believe" line; I propose a starting value with the first CV
  run, not before there's data to justify one.

## 3 · Discipline (directly reused from the proven template, `short-interest-study` + `catalyst-study`)
- **Per-component isolation.** Trend / momentum / breakout / volume / IV-rank tested **separately**, never
  bundled into the composite score for this test — same "don't bundle" instruction the short-interest study
  followed testing `days_to_cover` and `si_over_avg_vol_20d` independently.
- **No lookahead / point-in-time.** Signal computed only from data available strictly before the DTE window
  starts; forward-return window starts strictly after the signal date; point-in-time join (nearest prior
  reading, no revisionary data) — mirrors the short-interest study's `settlement_date <=` sample-date join.
- **Point-in-time universe membership (new relative to the 4 prior studies — flagging, not assuming).** The
  4 equity studies used a static, already-selected observation cohort — no rolling index-membership question.
  Phase 1's universe (`<2.2>`, S&P 500/1500 or Russell 1000-class, multi-year backtest window) is different:
  using **today's** index constituents to backtest **past** dates is survivorship bias (index membership
  changes — delistings, index adds/drops). The universe/backtest join needs point-in-time membership, not a
  current snapshot. This is Data-Eng's `<2.2>` build, but the backtest pipeline's correctness depends on it,
  so recording the requirement here for P1-1 coordination once Data-Eng is live.
- **Pre-registered bar — `<3.4>` addendum, D-TRADE-021 (RATIFIED).** A component is **CLEARED** only if it
  beats naive OOS under **BOTH** LOO-CV **and** 5-fold CV (≥30 seeds), **≥90% of seeds agreeing**; **NOT
  CLEARED** otherwise; **VOID** on any leakage/lookahead/contamination finding regardless. This was AIQ's
  proposal (`docs/eval/methodology-draft.md` §2, citing the catalyst-study addendum's coin-flip near-miss —
  a nominal LOO "win" that was only 68/24/6%-of-seeds, which the short-interest study's looser 50%-bar would
  have falsely cleared); I independently converged on adopting it verbatim rather than proposing a second
  number (the two builder/auditor seats' bars matched before either reached the Lead — protocol 15), and the
  Lead has since ratified it. Binding on every Phase-1 component test now, not a recommendation.
- **Verdict format — matches AIQ's exactly:** each component gets **CLEARED** / **NOT CLEARED** / **VOID**
  (contamination/non-reproducible). No partial credit, same as the 4-study precedent (short-interest kept;
  regime/catalyst/float dropped).

## 4 · Explicitly out of scope for Phase 1 (`<1.4>` — deferred, not dropped)
Theta decay, IV crush, bid-ask slippage, realistic fill/exit modeling, full option P&L. Directional
correctness of the underlying is the entire Phase-1 question. A component clearing this bar is a candidate
for Phase 2's full-P&L simulation (reusing the 0DTE backtest engine's slippage/spread modeling, once
located) — clearing Phase 1 is necessary, not sufficient, for "this makes money as an option trade."

## 5 · Open items / needs
1. **Screener + 0DTE backtest engine location** (§1) — blocks P1-2 concretely. Director or Data-Eng.
2. **Options-chain/IV historical data availability** (`<2.1>`) — not a Phase-1 blocker (§2's primary label
   works on OHLCV alone) but gates the more faithful delta-implied threshold upgrade. DevOps/Data-Eng.
3. **Point-in-time universe membership source** (§3) — needed before P1-1 delivers the final universe list;
   flagging now so Data-Eng scopes it in from the start rather than discovering the gap after the fact.
4. **`k` (volatility-multiplier) starting value** — proposed alongside the first CV run, not before.
