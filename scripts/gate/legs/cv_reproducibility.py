"""
Gate leg 3 -- CV reproducibility (QA VERIFIER tier; DevOps wires per Stage-4, F-1).

QA's Stage-3 report (docs/roles/qa/stage3-reproducibility-report.md S3) proved that no armed check in
this repo actually imports and exercises the shipped `helm/validation/engine/` code: AIQ's Stage-2
audit deliberately never imports it (NN-3, builder != judge -- correct for AIQ). QA showed this
concretely by reverting AI/ML's Finding-1 fix in `leg_b.py`, working tree only, and re-running the
audit -- it still reported 8/8 PASS, exit 0. The fixes are real and correct in the shipped code (QA
independently confirmed that too, S4); the gap is coverage, not correctness.

This leg closes that gap. It is the one place in the chain allowed to import the real engine: DevOps
is neither the builder (AI/ML) nor the judge (AIQ) of the engine's correctness, so importing it here
does not violate NN-3 -- this leg is a mechanical regression trip-wire, not a second independent audit.
The fixture values below are QA's OWN already-independently-reproduced numbers (S4), not re-derived
here; re-deriving them would just be a second audit, which is AIQ's job and already done twice
(AIQ's original + QA's reproduction).

Usage:
    python scripts/gate/legs/cv_reproducibility.py            # exit 0 (PASS) / 1 (FAIL) / 2 (SKIP, engine absent)
    python scripts/gate/legs/cv_reproducibility.py --selftest  # negative control: reproduces exactly what
                                                                 # QA did by hand (S3) -- temporarily reintroduce
                                                                 # the pre-fix Finding-1 bug in leg_b.py (working
                                                                 # tree only, via `git checkout --` to revert),
                                                                 # prove this leg goes RED, then prove GREEN again.
"""
import importlib
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ENGINE_DIR = os.path.join(REPO_ROOT, "helm", "validation", "engine")
LEG_B_RELPATH = "helm/validation/engine/leg_b.py"

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def engine_present():
    """True iff the shipped validation-engine files this leg depends on actually exist."""
    return (
        os.path.isdir(ENGINE_DIR)
        and os.path.isfile(os.path.join(ENGINE_DIR, "leg_b.py"))
        and os.path.isfile(os.path.join(ENGINE_DIR, "bar.py"))
    )


def _import_fresh(module_name):
    """Import, or reload if already imported this process (needed for --selftest, which edits leg_b.py
    on disk mid-process and must re-read it, not serve a stale cached module)."""
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)
    return sys.modules[module_name]


def run_checks():
    """Import the real shipped engine and re-run QA's own reproduced fixtures against it.
    Returns (ok: bool, lines: list[str]). Never raises -- every check is caught and reported."""
    import numpy as np

    leg_b = _import_fresh("helm.validation.engine.leg_b")
    bar_mod = _import_fresh("helm.validation.engine.bar")

    lines = []
    ok = True

    # QA S4 fixture 1: 35 trades, one dominant outlier -- must NOT clear (post Finding-1 fix).
    n = 35
    y_t = np.full(n, 0.0)
    y_f = np.full(n, 0.001)
    y_t[-1] = 0.10
    y_f[-1] = 0.0
    r1 = leg_b._loo_paired(y_t, y_f)
    exp1 = {"full_sample_diff": 0.001886, "pct_loo_estimates_agreeing": 97.1, "beats_naive_baseline": False}
    if (
        abs(r1["full_sample_diff"] - exp1["full_sample_diff"]) < 1e-6
        and abs(r1["pct_loo_estimates_agreeing"] - exp1["pct_loo_estimates_agreeing"]) < 0.05
        and r1["beats_naive_baseline"] == exp1["beats_naive_baseline"]
    ):
        lines.append(f"PASS: outlier fixture reproduces QA's numbers ({r1})")
    else:
        ok = False
        lines.append(f"FAIL: outlier fixture MISMATCH -- expected {exp1}, shipped engine returned {r1}")

    # QA S4 fixture 2: 40 trades, uniform outlier-free advantage -- must still clear (fix doesn't overcorrect).
    rng = np.random.RandomState(999)
    y_f2 = rng.normal(0.0, 0.01, 40)
    y_t2 = y_f2 + 0.005
    r2 = leg_b._loo_paired(y_t2, y_f2)
    if (
        abs(r2["full_sample_diff"] - 0.005) < 1e-3
        and r2["pct_loo_estimates_agreeing"] == 100.0
        and r2["beats_naive_baseline"] is True
    ):
        lines.append(f"PASS: no-outlier fixture still clears ({r2})")
    else:
        ok = False
        lines.append(f"FAIL: no-outlier fixture MISMATCH -- expected clear (100.0%, True), shipped engine returned {r2}")

    # bar.clearance_verdict's ratified 4-state enum shape (QA S4).
    cases = [
        (bar_mod.clearance_verdict({"beats_naive_baseline": True}, {"pct_seeds_beating_naive": 100.0}, n_support=5), "UNMEASURED"),
        (bar_mod.clearance_verdict({"beats_naive_baseline": False}, {"pct_seeds_beating_naive": 50.0}, n_support=40), "DROPPED"),
        (bar_mod.clearance_verdict({"beats_naive_baseline": True}, {"pct_seeds_beating_naive": 80.0}, n_support=40), "DROPPED"),
        (bar_mod.clearance_verdict({"beats_naive_baseline": True}, {"pct_seeds_beating_naive": 95.0}, n_support=40), "CLEARED"),
    ]
    for actual, expected in cases:
        if actual == expected:
            lines.append(f"PASS: clearance_verdict -> {expected}")
        else:
            ok = False
            lines.append(f"FAIL: clearance_verdict expected {expected}, got {actual}")

    return ok, lines


def main_check():
    if not engine_present():
        print("leg 3 (CV reproducibility): SKIP -- helm/validation/engine/ not present.")
        return 2
    ok, lines = run_checks()
    for line in lines:
        print(f"  {line}")
    if ok:
        print("leg 3 (CV reproducibility): GREEN -- shipped engine reproduces QA's independently-verified numbers.")
        return 0
    print("leg 3 (CV reproducibility): RED -- shipped engine output diverges from QA's reproduced numbers.")
    return 1


# ---------------------------------------------------------------------------
# Self-test / negative control: reproduce QA's own manual finding (S3) --
# reintroduce the pre-Finding-1-fix bug in leg_b.py (working tree only),
# prove this leg goes RED, `git checkout --` to revert, prove GREEN again.
# Never stages, never commits (LL-48 done-bar, same discipline as leg K).
# ---------------------------------------------------------------------------

_BUGGY_LOO_PAIRED = '''def _loo_paired(y_treatment, y_baseline):
    """SELFTEST-INJECTED pre-fix version (mean-of-diffs, not unanimous agreement) -- Finding-1's bug."""
    n = len(y_treatment)
    full_sample_diff = float(y_treatment.mean() - y_baseline.mean())
    diffs = np.empty(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        diffs[i] = y_treatment[mask].mean() - y_baseline[mask].mean()
    return {
        "n": n,
        "full_sample_diff": round(full_sample_diff, 6),
        "pct_loo_estimates_agreeing": round(float(np.mean(diffs > 0)) * 100 if full_sample_diff > 0 else float(np.mean(diffs < 0)) * 100, 1),
        "beats_naive_baseline": bool(full_sample_diff > 0),
    }
'''


def run_selftest():
    leg_b_path = os.path.join(REPO_ROOT, LEG_B_RELPATH)

    print("leg 3 self-test: confirming clean tree before planting anything...")
    status = subprocess.run(["git", "status", "--porcelain", LEG_B_RELPATH], cwd=REPO_ROOT, capture_output=True, text=True).stdout
    if status.strip():
        print(f"  ABORT: {LEG_B_RELPATH} is not clean before self-test -- refusing to overwrite uncommitted work:\n{status}")
        return 1

    print("leg 3 self-test: confirming GREEN on the real shipped engine first...")
    ok_before = main_check() == 0
    if not ok_before:
        print("  ABORT: leg 3 is not GREEN on the unmodified tree -- can't prove a negative control from a red baseline.")
        return 1

    print(f"leg 3 self-test: reintroducing the pre-Finding-1-fix bug into {LEG_B_RELPATH} (working tree only)...")
    with open(leg_b_path, "r", encoding="utf-8") as f:
        original = f.read()
    import re
    pattern = re.compile(r"def _loo_paired\(y_treatment, y_baseline\):.*?\n\n\n", re.DOTALL)
    patched, n_subs = pattern.subn(_BUGGY_LOO_PAIRED + "\n\n", original, count=1)
    if n_subs != 1:
        print("  ABORT: could not locate _loo_paired to patch -- leg_b.py's shape may have changed; aborting without writing anything.")
        return 1
    with open(leg_b_path, "w", encoding="utf-8") as f:
        f.write(patched)

    try:
        print("leg 3 self-test: re-running against the planted regression, expecting RED...")
        rc = main_check()
        ok = rc == 1
        if ok:
            print("  [PASS] leg 3 correctly went RED on the reintroduced Finding-1 bug (reproduces QA's S3 finding).")
        else:
            print(f"  [FAIL] leg 3 did NOT go RED on the reintroduced bug (exit {rc}) -- the leg is not armed.")
    finally:
        print(f"leg 3 self-test: reverting {LEG_B_RELPATH} via `git checkout --` (never staged, never committed)...")
        subprocess.run(["git", "checkout", "--", LEG_B_RELPATH], cwd=REPO_ROOT, check=True)
        status_after = subprocess.run(["git", "status", "--porcelain", LEG_B_RELPATH], cwd=REPO_ROOT, capture_output=True, text=True).stdout
        if status_after.strip():
            print(f"  WARNING: {LEG_B_RELPATH} not clean after revert:\n{status_after}")
            ok = False

    print("leg 3 self-test: confirming GREEN again after revert...")
    ok_after = main_check() == 0
    if not ok_after:
        print("  [FAIL] leg 3 is not GREEN after reverting the planted bug -- revert or engine state is broken.")
        ok = False

    if ok and ok_after:
        print("\nSELF-TEST PASSED: leg 3 catches the exact regression QA found by hand, and reverts cleanly.")
        return 0
    print("\nSELF-TEST FAILED: see above.")
    return 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(run_selftest())
    sys.exit(main_check())
