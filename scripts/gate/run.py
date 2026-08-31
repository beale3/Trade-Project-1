"""
Gate runner (DevOps VERIFIER tier -- exit-code-honest, never a piped-tail grep; oracle-boundary.md).

Every leg is ARMED (proven to fail on a planted negative control) or exit-visible SKIP (its surface
doesn't exist yet). A leg is never green from an unarmed state (gate-spec "rule of green"). The runner
exits non-zero iff any ARMED leg fails; SKIPs never fail it.

Usage:
    python scripts/gate/run.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import legs.secret_scan as secret_scan  # noqa: E402


# (leg_id, tier, status, description) -- status is "ARMED" or "SKIP (reason)".
# Only secret_scan (leg K) is wired so far -- this task's scope (open-items-ledger item 13). The rest
# are declared here, SKIP-visible, so the runner already knows its own eventual shape (harness-design.md
# §B.3) rather than silently omitting them.
LEG_TABLE = [
    ("K", "SecOps ORACLE / DevOps wires", "ARMED", "no-secret (docs/security/key-denylist.md)"),
    ("T", "SecOps ORACLE / DevOps wires", "SKIP (not yet wired -- next DevOps task)", "provider-taint, static"),
    ("G", "FinOps PARTIAL / DevOps wires", "SKIP (no helm/spend/ yet)", "spend guard block-on-breach"),
    ("lint/type-check", "DevOps/B3", "SKIP (no pyproject.toml / package yet)", "ruff+mypy"),
    ("unit tests", "DevOps/B3", "SKIP (no test suite yet)", "pytest"),
    ("CV reproducibility", "QA VERIFIER", "SKIP (no validation engine yet)", "leg 3"),
    ("C", "Legal HUMAN", "SKIP (unarmed pending Legal <4.3>)", "compliance"),
]


def main():
    print("=" * 78)
    print("GATE RUN -- exit-code-honest, no piped tails")
    print("=" * 78)

    failed = False
    ran_something = False

    for leg_id, tier, status, desc in LEG_TABLE:
        if status.startswith("ARMED"):
            ran_something = True
            if leg_id == "K":
                rc = secret_scan.main_scan()
                result = "PASS" if rc == 0 else "FAIL"
                if rc != 0:
                    failed = True
                print(f"  leg {leg_id:4s} [{tier:28s}] ARMED  -> {result:4s}  ({desc})")
            else:
                raise NotImplementedError(f"leg {leg_id} marked ARMED but has no runner wired")
        else:
            print(f"  leg {leg_id:4s} [{tier:28s}] {status:35s}  ({desc})")

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
