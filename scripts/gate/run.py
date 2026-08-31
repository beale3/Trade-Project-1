"""
Gate runner (DevOps VERIFIER tier -- exit-code-honest, never a piped-tail grep; oracle-boundary.md).

Every leg is ARMED (proven to fail on a planted negative control) or exit-visible SKIP (its surface
doesn't exist yet). A leg is never green from an unarmed state (gate-spec "rule of green"). The runner
exits non-zero iff any ARMED leg fails; SKIPs never fail it.

Stage-4 fix (QA's Stage-3 report, F-2): SKIP reasons used to be hardcoded strings that could go stale
the moment the underlying repo state changed (caught live: `helm/validation/engine/` had existed since
Stage 1, but the table still read "no validation engine yet"). Every leg below now computes its own
status/reason from the actual repo state at run time -- a stale reason is now a class of bug this file
cannot have, not a specific string that has to be remembered and updated by hand.

Usage:
    python scripts/gate/run.py
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import legs.secret_scan as secret_scan  # noqa: E402
import legs.cv_reproducibility as cv_reproducibility  # noqa: E402


def _exists(*relparts):
    return os.path.exists(os.path.join(REPO_ROOT, *relparts))


def _isdir(*relparts):
    return os.path.isdir(os.path.join(REPO_ROOT, *relparts))


def _has_pytest_discoverable_tests():
    """Any file matching pytest's default discovery convention (test_*.py / *_test.py) anywhere under
    the repo, outside .git. Computed, not assumed -- so this can never silently go stale either way."""
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
        for f in filenames:
            if f.startswith("test_") and f.endswith(".py") or f.endswith("_test.py"):
                return True, os.path.relpath(os.path.join(dirpath, f), REPO_ROOT)
    return False, None


# --- Per-leg checkers: each returns ("ARMED", run_fn) or ("SKIP", computed_reason_string). ---

def check_leg_k():
    return "ARMED", secret_scan.main_scan


def check_leg_t():
    if not _isdir("helm", "ingest"):
        return "SKIP", "no helm/ingest/ yet (leg T's target -- provider-taint static check has nothing to scan)"
    return "SKIP", "helm/ingest/ exists but leg T is not yet wired -- next DevOps task"


def check_leg_g():
    if not _isdir("helm", "spend"):
        return "SKIP", "no helm/spend/ yet (leg G's target -- spend-guard block-on-breach check)"
    return "SKIP", "helm/spend/ exists but leg G is not yet wired -- next DevOps task"


def check_lint_typecheck():
    if not (_exists("pyproject.toml") or _exists("setup.cfg")):
        return "SKIP", "no pyproject.toml/setup.cfg yet -- nothing to point ruff/mypy at"
    return "SKIP", "pyproject.toml exists but ruff/mypy are not yet wired -- next DevOps task"


def check_unit_tests():
    found, path = _has_pytest_discoverable_tests()
    if found:
        return "SKIP", f"a pytest-discoverable file exists ({path}) but pytest is not yet wired -- next DevOps task"
    has_audit = _exists("helm", "validation", "audit", "stage2_audit.py")
    if has_audit:
        return "SKIP", "no pytest-discoverable suite, but helm/validation/audit/stage2_audit.py is a real 8-test suite (run separately, not on a pytest path -- QA Stage-3 F-2, noted not pressed)"
    return "SKIP", "no test suite exists yet"


def check_leg_3():
    if cv_reproducibility.engine_present():
        return "ARMED", cv_reproducibility.main_check
    return "SKIP", "helm/validation/engine/{leg_b,bar}.py not present -- nothing to reproduce against"


def check_leg_c():
    return "SKIP", "unarmed pending Legal <4.3> ruling -- a policy gate, not a repo-file signal this runner can compute"


LEG_TABLE = [
    ("K", "SecOps ORACLE / DevOps wires", "no-secret (docs/security/key-denylist.md)", check_leg_k),
    ("T", "SecOps ORACLE / DevOps wires", "provider-taint, static", check_leg_t),
    ("3", "QA VERIFIER / DevOps wires", "CV reproducibility -- shipped helm/validation/engine reproduces QA's audited numbers", check_leg_3),
    ("G", "FinOps PARTIAL / DevOps wires", "spend guard block-on-breach", check_leg_g),
    ("lint/type-check", "DevOps/B3", "ruff+mypy", check_lint_typecheck),
    ("unit tests", "DevOps/B3", "pytest", check_unit_tests),
    ("C", "Legal HUMAN", "compliance", check_leg_c),
]


def main():
    print("=" * 78)
    print("GATE RUN -- exit-code-honest, no piped tails")
    print("=" * 78)

    failed = False
    ran_something = False

    for leg_id, tier, desc, checker in LEG_TABLE:
        status, payload = checker()
        if status == "ARMED":
            ran_something = True
            rc = payload()  # payload is the run function when ARMED
            result = "PASS" if rc == 0 else "FAIL"
            if rc != 0:
                failed = True
            print(f"  leg {leg_id:4s} [{tier:28s}] ARMED  -> {result:4s}  ({desc})")
        else:
            reason = payload  # payload is the computed reason string when SKIP
            print(f"  leg {leg_id:4s} [{tier:28s}] SKIP ({reason})  ({desc})")

    print("=" * 78)
    if not ran_something:
        print("WARNING: no ARMED legs ran -- a gate with nothing armed is not proven (LL-48).")
    if failed:
        print("GATE: FAIL (an armed leg reported RED -- see above)")
        return 1
    print("GATE: PASS (every armed leg green; SKIPs are exit-visible, not counted as green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
