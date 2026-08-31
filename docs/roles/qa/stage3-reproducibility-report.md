# Stage 3 — independent reproducibility re-run (QA, 2026-08-31)

**Verified commit: `7d0919cda72f85c47c62dfa605f6f14d0c6c68b2`** (LL-41 — every claim below was produced
against exactly this hash, in the QA clone, on exit codes).
Environment: `Trade - QA` clone, Python 3.12.10, own filesystem, own git checkout.

Stage 3 of the Director's 2026-08-30 build-chain dispatch (AI/ML → AIQ → **QA** → DevOps). Mandate:
VERIFIER tier — re-run every armed leg on exit codes in my own clone; reproduce the negative controls
myself; never trust "it passed." **I fixed nothing** — findings route to the owning seat (protocol 11).

**Scope, stated up front (LL-35):** Stage 1 delivered validation LOGIC, not a real-data run. No
`helm/ingest/` exists and no historical OHLCV has been pulled, so there is **no real CLEARED/DROPPED
verdict to reproduce** in the full NN-9 sense. Everything below verifies MECHANISM and DETERMINISM on
synthetic fixtures. NN-9 proper stays OPEN — see §Not covered.

---

## §1 · What I ran, and what it returned (exit codes, not tails)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `python scripts/gate/run.py` | **0** | GATE: PASS — 1 armed leg (K) green, 6 exit-visible SKIPs |
| 2 | `python scripts/gate/legs/secret_scan.py --selftest` | **0** | 10/10 positive controls RED · 4/4 placeholders GREEN · self-reference + K0a checks pass |
| 3 | **My own end-to-end plant** (see §2) | **1** | leg K RED, GATE: FAIL — the real scan path genuinely fails closed |
| 4 | `python scripts/gate/run.py` (after revert) | **0** | green restored, tree clean, HEAD unchanged |
| 5 | `python helm/validation/audit/stage2_audit.py` | **0** | 8/8 passed |
| 6 | Same, ×3 consecutive | **0** | outputs **byte-identical** (`diff` clean) |
| 7 | Same, `PYTHONHASHSEED ∈ {0,1,42,12345}` | **0** | all four **byte-identical** to baseline |
| 8 | QA probe against the **shipped** engine (§4) | **0** | shipped `leg_b`/`bar` reproduce AIQ's numbers exactly |
| 9 | NN-3 mechanical independence check (§5) | — | audit loads **zero** `helm.*` modules |

**AIQ's documented numbers, reproduced exactly on my machine:** ratchet exit `101.2` · init floor
`100.0 → 97.0` (pnl `-3.0`) · harness signal/noise separation `100.0%` / `0.0%` · Finding-1 fixture
`full_sample_diff=0.001886`, `pct_agreeing=97.1%`, `beats_naive_baseline=False` · no-outlier fixture
`0.005000`, `100.0%`, `True`. No discrepancy against `docs/eval/stage2-audit-findings.md`.

## §2 · Negative control I produced myself (LL-10 / LL-48)

DevOps's `--selftest` calls `_scan_text()` directly on synthetic strings. It proves the **patterns**
bite; it does **not** exercise the real `run_scan()` → `git ls-files` → exit-code path. So the self-test
alone does not answer "show me the input this green would reject" for the gate as actually invoked.

I closed that myself: planted a synthetic, base64-stored `SEC_API_KEY=`-shaped value (never a real
credential) into **tracked** `README.md`, **working tree only** — never staged, never committed. Result:
`run.py` → **exit 1**, leg K RED, both `K6a` and `K0b` fired, value redacted in output. Reverted with
`git checkout --`; tree clean, `git log -1` still `7d0919c`, `git diff --cached` empty.

**Leg K is genuinely armed on the real path, not just in its own harness.** Reproduced independently —
this is not a re-reading of DevOps's report.

## §3 · 🟠 F-1 (proposed SEV2) — the Stage-2 audit green cannot fail on an engine regression

**Owner: DevOps (Stage 4) · not a defect in AIQ's work.**

I reverted AI/ML's Finding-1 fix in `helm/validation/engine/leg_b.py:123` (working tree only), restoring
the exact pre-fix statistic (`mean(diffs) > 0` instead of unanimous sign agreement), and re-ran the
audit:

```
8/8 passed
=== EXIT CODE WITH DEFECT PLANTED: 0 ===
```

**The defect that Stage 2 exists to certify as fixed was reintroduced, and every check stayed green.**

**Cause — and it is not AIQ's fault.** `helm/validation/audit/stage2_audit.py` never imports the engine;
line 275 states it plainly: *"built from reading the diff, not by importing leg_b.py."* That is **required**
by NN-3 (builder ≠ judge, ADR-0001 §4) and AIQ is correct to honor it — I verified mechanically that it
does (§5). But the consequence is structural: **no runnable, armed check in this repo binds the shipped
`helm/validation/engine/` code.** Stage 2's "all 4 findings CONFIRMED FIXED", and the Lead's confirming
re-run of the same script, are both invariant to what the engine actually contains. That green would have
appeared identically with the fix absent — which is exactly LL-48's vacuous green.

**To be precise about what is and isn't wrong:** the fixes ARE present and correct in the shipped code —
I confirmed that separately by direct probe (§4). AI/ML's work is sound and AIQ's verdict is right. **The
gap is coverage, not correctness.** Nothing would catch a future regression, and Stage 3 is where that
has to be said.

This is the leg already declared in `scripts/gate/run.py` `LEG_TABLE` as
`("CV reproducibility", "QA VERIFIER", ...)` — currently SKIP. Arming it against the real engine is
DevOps's Stage-4 task. Per my oracle-boundary row, *"is coverage sufficient for the risk"* is HUMAN and
escalates: **final severity is GA's/the Director's call, not mine** — I propose SEV2 and route via the Lead.

## §4 · The check nobody had run — does the *shipped* engine reproduce?

Because §3 means nothing binds the engine, I imported the real `helm.validation.engine.leg_b` / `bar`
myself (which AIQ may not do) and re-derived AIQ's documented fixtures against it. All checks PASS:

- Finding-1 outlier fixture → `{'n': 35, 'full_sample_diff': 0.001886, 'pct_loo_estimates_agreeing': 97.1, 'beats_naive_baseline': False}` ✔
- No-outlier fixture → `{'n': 40, 'full_sample_diff': 0.005, 'pct_loo_estimates_agreeing': 100.0, 'beats_naive_baseline': True}` ✔ (fix does not overcorrect)
- `_multiseed_kfold_paired` identical across 10 consecutive calls ✔ (NN-9 determinism, shipped code)
- `bar.clearance_verdict` 4-state enum: thin support → `UNMEASURED`, fails LOO → `DROPPED`, fails k-fold
  → `DROPPED`, passes both → `CLEARED` ✔ — matches the ratified D-TRADE-030 / ADR-0001 §6.1 schema, and
  confirms Findings 3 and 4 are genuinely fixed in the shipped artifact, not just in a reimplementation.

**Conclusion: AI/ML's Stage-1 fixes are real and present at `7d0919c`.** Stage 2's verdict is correct on
the merits; only its mechanical backing is thin.

## §5 · NN-3 independence — verified mechanically, not by reading

Ran AIQ's audit under `runpy` and diffed `sys.modules` before/after:

- `helm.*` modules loaded by the audit: **NONE**
- banned (`helm.validation.engine` / `helm.screener`) imports: **NONE**
- `tools.rolling_watchlist` loaded: **True** (expected — the raw primitive)

**NN-3 HONORED.** AIQ's independence claim is true as a fact about the running process, not just its prose.

## §6 · 🟡 F-2 (SEV3) — the gate prints a false SKIP reason for the QA leg

**Owner: DevOps.** `scripts/gate/run.py:29` hardcodes:

```
("CV reproducibility", "QA VERIFIER", "SKIP (no validation engine yet)", "leg 3"),
```

The validation engine **has existed since Stage 1** (`006db52`/`f8f685e`) —
`helm/validation/engine/{bar,harness,leg_a,leg_b}.py` are all present at this commit. The reason string
is now factually false, and because `LEG_TABLE`'s reasons are **hardcoded strings rather than computed
conditions**, it can never self-correct: the gate will keep telling every reader the engine doesn't exist.
An exit-visible SKIP is the right design; a **stale** SKIP reason is how a skip quietly outlives its
justification. Boundary-honesty defect, not a correctness one.

Same shape, softer (noted, not pressed): line 28's `"SKIP (no test suite yet)"` while
`helm/validation/audit/stage2_audit.py` is a runnable 8-test suite with honest exit codes — defensible,
since it is not `pytest` and not on a discoverable test path.

## §7 · Blocker I hit and resolved (protocol 11 — reported, not sat on)

**The `Trade - QA` clone did not exist.** The directory was present but completely empty — no `.git`, no
files — while all nine other seat directories had populated clones. Stage 3 could not begin: a VERIFIER
with no clone cannot verify anything in its own clone. I bootstrapped it myself
(`git clone https://github.com/beale3/Trade-Project-1 "Trade - QA"`, landed on `main` @ `7d0919c`) rather
than borrow another seat's working tree, which would have destroyed the independence the whole seat exists
to provide. Flagging it because the board's `🔴 NOT SPAWNED` row understated it: the seat wasn't merely
unspawned, its workspace was never created.

## §Not covered (LL-35 — a findings-only report hides its own gaps)

1. **NN-9 proper — the real-data reproducibility mandate — remains OPEN.** No `helm/ingest/` exists, no
   historical OHLCV pulled, therefore no real CV run and no real verdict record to re-derive. Everything
   in this report is mechanism + determinism on synthetic fixtures. **Not mine to fix** — blocked on
   SDE1's `helm/ingest` lane being dispatched (open-items-ledger item 17). Stage 3 cannot close NN-9; it
   can only certify what exists today, which is what this report does.
2. **`helm/screener/adapter.py`, `helm/validation/engine/harness.py`, `leg_a.py` were not run end-to-end** —
   there is no data to run them against. `leg_a` was exercised only indirectly (schema/enum via `bar.py`).
3. **Legs T, G, lint/type-check, unit tests, C are SKIP.** I confirmed each is exit-visible and does not
   count as green. I did **not** verify any of them would be correct once armed — there is nothing to
   verify yet. Their SKIP status is honest; only the QA leg's *reason* is stale (F-2).
4. **The trailing-stop rule was never tested against real market data** — only AIQ's synthetic fixtures
   and my reproduction of them. Correct formula ≠ correct on real bars (LL-40: consistent ≠ correct).
5. **No `pyproject.toml` / `__init__.py`:** importing `helm.*` requires manually setting `PYTHONPATH` to
   the repo root. Noted as reproducibility friction, not raised as a finding — it is consistent with the
   already-declared lint/type-check SKIP and will resolve when DevOps packages the project.
6. **I did not re-audit AI/ML's or AIQ's judgment** on Leg B's methodology adaptation. That was Stage 2's
   call, AIQ made it, and re-litigating it is not Stage 3's mandate.

## §Verdict

**Stage 3 PASSES on everything reproducible at `7d0919c`.** Every armed leg re-run on exit codes in my own
clone; leg K's negative control reproduced end-to-end by my own plant; AIQ's 8/8 audit reproduced exactly
and shown deterministic under repetition and hash-seed variation; NN-3 independence confirmed
mechanically; and the shipped engine independently confirmed to carry all four Stage-2 fixes.

**Two findings route out (F-1 SEV2-proposed, F-2 SEV3) — both to DevOps's Stage-4 lane, neither fixed by
me.** **NN-9's real-data mandate stays open** and no green in this report should be read as closing it.
