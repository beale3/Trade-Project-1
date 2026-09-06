"""
AIQ independent verification of D-TRADE-044 (symmetric class-balance floor),
commit 7635bcc. This is mechanism verification (protocol 14's admission
test: "show me the input this green would reject") against the actual
armed functions -- a different task from a real-data re-derivation (NN-3's
"never import as ground truth for a verdict"), so calling
helm.validation.engine directly here is deliberate, not a lapse: I am
testing whether the CODE correctly implements the ratified rule on
controlled fixtures of my own construction, not trusting the engine's
output as my verdict on real data (that re-derivation is stage3's job and
already done independently, without importing this package).

Fixtures below are my own -- different n/signal values from both AI/ML's
(140/10, 75/75) and the Lead's own check, so this is a genuinely separate
negative control, not a re-run of theirs with different names.

Run: python helm/validation/audit/stage4_d044_verification.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from helm.validation.engine.bar import clearance_verdict, MIN_SUPPORT
from helm.validation.engine import leg_a, leg_b

RNG = np.random.RandomState(20260906)


def make_signal(n, fired_mask, effect=0.06, noise=0.05):
    y = np.where(fired_mask, RNG.normal(effect, noise, n), RNG.normal(0.0, noise, n))
    return y


def test_boundary_exactly_30_30_passes():
    """My own boundary case: exactly 30/30 -- must PASS (>=30, not >30) and actually run CV."""
    n = 60
    fired = np.array([True] * 30 + [False] * 30)
    y = make_signal(n, fired, effect=0.08)
    r = leg_a.evaluate_component(fired, y, "my_boundary_component", "1d")
    assert r["n_support"] == 30 and r["n_not_fired"] == 30
    assert r["verdict"] != "UNMEASURED", f"exactly 30/30 should NOT be UNMEASURED, got {r['verdict']}"
    assert r["loo"] is not None, "CV should have actually run at exactly the boundary"
    return f"PASS: n_fired=30/n_not_fired=30 (exact boundary) runs CV, verdict={r['verdict']}"


def test_boundary_29_fails():
    """One side at 29 (one below the floor) must return UNMEASURED, CV not run."""
    n = 60
    fired = np.array([True] * 29 + [False] * 31)
    y = make_signal(n, fired, effect=0.08)
    r = leg_a.evaluate_component(fired, y, "my_boundary_fail_component", "1d")
    assert r["n_support"] == 29 and r["n_not_fired"] == 31
    assert r["verdict"] == "UNMEASURED", f"29/31 should be UNMEASURED, got {r['verdict']}"
    assert r["loo"] is None, "CV must not run when one side fails the floor"
    return "PASS: n_fired=29 (one below floor) -> UNMEASURED, CV not run"


def test_imbalanced_strong_signal_my_own_numbers():
    """
    My own imbalanced fixture (different from AI/ML's 140/10 and the Lead's
    check): n=220, fired=205/not_fired=15, with a STRONG planted effect that
    would clear under the old one-sided-only floor (n_fired=205 >> 30).
    Must now return UNMEASURED because n_not_fired=15 < 30.
    """
    n = 220
    fired = np.array([True] * 205 + [False] * 15)
    y = make_signal(n, fired, effect=0.15, noise=0.03)  # strong, clean signal
    r = leg_a.evaluate_component(fired, y, "my_imbalanced_component", "1d")
    assert r["n_support"] == 205 and r["n_not_fired"] == 15
    assert r["verdict"] == "UNMEASURED", (
        f"n_fired=205 (>>30) but n_not_fired=15 (<30) with a strong signal that would "
        f"have cleared under the old floor -- should be UNMEASURED, got {r['verdict']}"
    )
    assert r["loo"] is None
    return "PASS: strong signal + n_not_fired=15 (<30) -> correctly UNMEASURED, not a false CLEAR"


def test_balanced_same_signal_clears():
    """The SAME effect size as the imbalanced test above, but balanced (110/110) -- should actually run and clear."""
    n = 220
    fired = np.array([True] * 110 + [False] * 110)
    y = make_signal(n, fired, effect=0.15, noise=0.03)
    r = leg_a.evaluate_component(fired, y, "my_balanced_component", "1d")
    assert r["n_support"] == 110 and r["n_not_fired"] == 110
    assert r["verdict"] == "CLEARED", f"balanced + strong clean signal should CLEAR, got {r['verdict']}"
    return "PASS: same signal strength, balanced 110/110 -> CLEARED (floor is not a blanket suppressor)"


def test_n_comparison_required_not_optional():
    """bar.py's clearance_verdict must reject a call missing n_comparison -- no silent skip."""
    try:
        clearance_verdict({"beats_naive_baseline": True}, {"pct_seeds_beating_naive": 100.0}, 50)
        return "FAIL: call without n_comparison did not raise"
    except TypeError:
        return "PASS: omitting n_comparison raises TypeError, not a silent bypass"


def test_void_overrides_even_when_floor_also_fails():
    """leakage_detected=True must return VOID even when n_comparison also fails the floor."""
    v = clearance_verdict({"beats_naive_baseline": True}, {"pct_seeds_beating_naive": 100.0},
                           n_support=5, n_comparison=5, leakage_detected=True)
    assert v == "VOID", f"expected VOID to override a failing floor, got {v}"
    return "PASS: VOID overrides even when the floor would also fail"


def test_leg_b_paired_floor_my_own_fixture():
    """
    My own Leg-B fixture (not reusing the real 149-trade sample): 28 paired
    trades (below 30) -- both arms equal length by construction. Must be
    UNMEASURED even though the paired difference itself is large.
    """
    n = 28
    t_ret = RNG.normal(5.0, 1.0, n)
    f_ret = RNG.normal(-5.0, 1.0, n)
    r = leg_b.evaluate_exit_config(t_ret, f_ret, "my_test_config", is_primary=True)
    assert r["n_support"] == 28 and r["n_comparison"] == 28
    assert r["verdict"] == "UNMEASURED", f"n=28 (<30) paired sample should be UNMEASURED, got {r['verdict']}"
    return "PASS: Leg B paired n=28 (<30) -> UNMEASURED despite a large paired difference"


def test_leg_b_paired_floor_passes_at_30():
    n = 30
    t_ret = RNG.normal(5.0, 1.0, n)
    f_ret = RNG.normal(-5.0, 1.0, n)
    r = leg_b.evaluate_exit_config(t_ret, f_ret, "my_test_config_30", is_primary=True)
    assert r["n_support"] == 30 and r["n_comparison"] == 30
    assert r["verdict"] != "UNMEASURED", f"exactly n=30 paired should run, got {r['verdict']}"
    return f"PASS: Leg B paired n=30 (exact boundary) runs, verdict={r['verdict']}"


if __name__ == "__main__":
    tests = [
        test_boundary_exactly_30_30_passes, test_boundary_29_fails,
        test_imbalanced_strong_signal_my_own_numbers, test_balanced_same_signal_clears,
        test_n_comparison_required_not_optional, test_void_overrides_even_when_floor_also_fails,
        test_leg_b_paired_floor_my_own_fixture, test_leg_b_paired_floor_passes_at_30,
    ]
    failures = 0
    for t in tests:
        try:
            print(f"[{t.__name__}] {t()}")
        except AssertionError as e:
            failures += 1
            print(f"[{t.__name__}] FAIL: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
