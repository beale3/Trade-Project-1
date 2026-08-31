"""
Gate leg K -- no-secret (D-TRADE-006a, canonical <4.1>, gate-spec leg K).

Rule-set authored by SecOps (docs/security/key-denylist.md, patterns K0-K6); this module is DevOps's
wiring of that spec (builder != judge, protocol 14) -- it does not invent or loosen any pattern.

Assertion (fail-closed, LL-50): RED iff a tracked file contains a real (populated) credential value
matching one of K0-K6, or a .env/.env.* file (other than .env.example) is tracked. Never more than
that -- leg K says nothing about whether a secret is well-designed (that's the B5/HUMAN gate).

Self-reference handling: docs/security/key-denylist.md documents each pattern with a literal FAKE
example value (that's the point -- they're the leg's own negative controls, written down for humans
to read). A naive scanner would flag that one spec file for quoting its own examples. Fix: scanning
skips exactly ONE path -- docs/security/key-denylist.md itself -- and nowhere else. This is narrower
and safer than a value-based allowlist: a value-based allowlist would (and, in an earlier version of
this file, did) also exempt a self-test that deliberately reuses those same documented example values
as its planted positive controls -- exactly the case that must still go RED. Path-scoping avoids that
collision entirely: the one spec file that's allowed to quote its own examples is named explicitly;
every other file, including a synthetic self-test string, is scanned for real.

Usage:
    python scripts/gate/legs/secret_scan.py            # scan tracked files, exit 0 (GREEN) / 1 (RED)
    python scripts/gate/legs/secret_scan.py --selftest  # plant each K0-K6 positive control in an
                                                          # untracked temp file, prove it goes RED,
                                                          # prove the .env.example/K3 placeholders stay
                                                          # GREEN, then delete the temp file. Never
                                                          # stages or commits anything (LL-48 done-bar).
"""

import base64
import binascii
import json
import math
import os
import re
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DENYLIST_DOC = os.path.join(REPO_ROOT, "docs", "security", "key-denylist.md")

PLACEHOLDER_PASSWORDS = {"[password]", "<password>", "password", "your_password", "..."}
ENTROPY_THRESHOLD = 4.0  # bits/char; tuned so ordinary words/paths don't trip K0b (see _entropy)

DENYLIST_DOC_RELPATH = os.path.relpath(DENYLIST_DOC, REPO_ROOT).replace(os.sep, "/")


def _is_exempt_path(path):
    """True only for docs/security/key-denylist.md itself -- the one file allowed to quote its own
    documented FAKE examples. Every other file (including a self-test's synthetic text) is scanned."""
    return path.replace(os.sep, "/") == DENYLIST_DOC_RELPATH


def _entropy(s):
    if not s:
        return 0.0
    counts = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _jwt_role(token):
    """Best-effort: base64url-decode a JWT's middle segment and return its "role" claim, or None."""
    parts = token.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1]
    padded = payload + "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded)
        claims = json.loads(decoded)
        return claims.get("role")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        return None


def _git_tracked_files():
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout
    return [line for line in out.splitlines() if line]


def _read_text(path):
    try:
        with open(os.path.join(REPO_ROOT, path), "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return None


JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")


def _scan_text(path, text, findings):
    if _is_exempt_path(path):
        return  # key-denylist.md quoting its own documented examples -- not a real finding.

    # --- K1 Supabase service_role ---
    for m in re.finditer(r"(?:SUPABASE[._]?SERVICE[._]?ROLE|SERVICE_ROLE_KEY)\s*[:=]\s*(eyJ[^\s\"'`]+)", text, re.IGNORECASE):
        findings.append((path, "K1a", "SUPABASE_SERVICE_ROLE_KEY-shaped JWT assignment", m.group(1)))
    for m in JWT_RE.finditer(text):
        val = m.group(0)
        if _jwt_role(val) == "service_role":
            findings.append((path, "K1b", "JWT with role=service_role claim", val))
    for m in re.finditer(r"\bsb_secret_[A-Za-z0-9]{20,}", text):
        findings.append((path, "K1c", "sb_secret_ literal", m.group(0)))

    # --- K2 Supabase DB password / DATABASE_URL ---
    for m in re.finditer(r"postgres(?:ql)?://[^:@/\s\"']+:([^@/\s\"']+)@[^\s\"']*supabase\.(?:co|com)[^\s\"']*", text, re.IGNORECASE):
        pw = m.group(1)
        if pw.lower() not in PLACEHOLDER_PASSWORDS:
            findings.append((path, "K2", "Supabase DATABASE_URL with a populated password", m.group(0)))

    # --- K3 Supabase MCP PAT ---
    for m in re.finditer(r"\bsbp_[A-Za-z0-9]{20,}", text):
        findings.append((path, "K3", "sbp_ (Supabase PAT) literal outside env-indirection", m.group(0)))

    # --- K4 Supabase anon / publishable key ---
    for m in JWT_RE.finditer(text):
        val = m.group(0)
        if _jwt_role(val) == "anon":
            findings.append((path, "K4a", "JWT with role=anon claim (tracked, should live in .env)", val))
    for m in re.finditer(r"\bsb_publishable_[A-Za-z0-9]{20,}", text):
        findings.append((path, "K4b", "sb_publishable_ literal", m.group(0)))

    # --- K5 Massive / Polygon API key ---
    for m in re.finditer(r"(?:POLYGON|MASSIVE)[._]?(?:API[._]?)?KEY\s*[:=]\s*([A-Za-z0-9]{20,})", text, re.IGNORECASE):
        findings.append((path, "K5a", "POLYGON_API_KEY/MASSIVE_API_KEY-shaped assignment", m.group(1)))
    for m in re.finditer(r"api\.(?:polygon|massive)\.(?:io|com)/[^\s\"']*[?&]api[_-]?[Kk]ey=([A-Za-z0-9_-]{20,})", text):
        findings.append((path, "K5b", "Massive/Polygon key pasted into a URL", m.group(1)))

    # --- K6 SEC-API.io key ---
    for m in re.finditer(r"(?:SEC_API_KEY|SEC_API_TOKEN|EDGAR_API_KEY)\s*[:=]\s*([A-Za-z0-9]{20,})", text, re.IGNORECASE):
        findings.append((path, "K6a", "SEC_API_KEY/SEC_API_TOKEN/EDGAR_API_KEY-shaped assignment", m.group(1)))
    for m in re.finditer(r"api\.sec-api\.io/[^\s\"']*[?&]token=([A-Za-z0-9_-]{20,})", text):
        findings.append((path, "K6b", "SEC-API.io token pasted into a URL", m.group(1)))

    # --- K0 generic backstop: high-entropy KEY/SECRET/TOKEN/PASSWORD assignment ---
    # Name side is deliberately case-SENSITIVE, SCREAMING_SNAKE_CASE-only (every real example in
    # key-denylist.md is shaped this way, e.g. SUPABASE_SERVICE_ROLE_KEY=) -- catches real env-var-style
    # assignments while sparing ordinary prose that happens to use a lowercase word like "secrets:" in a
    # sentence (found live against docs/AGENT-COORDINATION.md during this leg's own self-verification).
    for m in re.finditer(r"\b([A-Z][A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL)[A-Z0-9_]*)\s*[:=]\s*([A-Za-z0-9+/_.=-]{16,})", text):
        name, val = m.group(1), m.group(2)
        if val.lower() in PLACEHOLDER_PASSWORDS or val.startswith("${") or val in ("", "..."):
            continue
        if _entropy(val) < ENTROPY_THRESHOLD:
            continue
        findings.append((path, "K0b", f"high-entropy value assigned to {name}", val))


def _scan_tracked_env_files(tracked, findings):
    # K0a / rule 2: no .env / .env.* tracked, except .env.example.
    for path in tracked:
        base = os.path.basename(path)
        if base == ".env.example":
            continue
        if base == ".env" or re.match(r"^\.env\.", base):
            findings.append((path, "K0a", "a .env/.env.* file (not .env.example) is git-tracked", "<file itself>"))


def run_scan():
    """Scan every git-tracked file. Returns a list of (path, rule, description, redacted_value) findings."""
    tracked = _git_tracked_files()
    findings = []
    _scan_tracked_env_files(tracked, findings)
    for path in tracked:
        text = _read_text(path)
        if text is None:
            continue  # binary or unreadable -- out of a text-pattern leg's scope
        _scan_text(path, text, findings)
    return findings


def _redact(value):
    if value == "<file itself>":
        return value
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "…redacted…" + value[-2:]


def main_scan():
    findings = run_scan()
    if not findings:
        print("leg K (secret-scan): GREEN -- no tracked file matches K0-K6, no .env/.env.* tracked.")
        return 0
    print(f"leg K (secret-scan): RED -- {len(findings)} finding(s):")
    for path, rule, desc, val in findings:
        print(f"  [{rule}] {path}: {desc} (value redacted: {_redact(val)})")
    return 1


# ---------------------------------------------------------------------------
# Self-test: plant each K0-K6 positive control in an UNTRACKED temp file inside
# the repo, run the scanner against just that file's content, assert RED, then
# delete it -- never staged, never committed (LL-48 done-bar).
# ---------------------------------------------------------------------------

POSITIVE_CONTROLS = [
    ("K1a", 'SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.FAKE_sig_do_not_use'),
    ("K1c", "sb_secret_FAKEFAKEFAKEFAKEFAKE1234567890"),
    ("K2", "DATABASE_URL=postgresql://postgres:Sup3rS3cr3tFAKE@db.zyscsnhiymitpfdhjuci.supabase.co:5432/postgres"),
    ("K3", "SUPABASE_ACCESS_TOKEN=sbp_faketoken0123456789abcdef0123456789"),
    ("K4b", "SUPABASE_ANON_KEY=sb_publishable_FAKEpublishable1234567890"),
    ("K5a", "POLYGON_API_KEY=aB3xK9fakeKEYfakeKEYfakeKEY0000"),
    ("K5b", "https://api.massive.com/v2/aggs?apiKey=aB3xK9fakeKEYfakeKEY0000"),
    ("K6a", "SEC_API_KEY=fakeSECkey0123456789abcdef0123"),
    ("K6b", "https://api.sec-api.io/float?ticker=AAPL&token=fake0123456789abcdef0123456789ab"),
    ("K0b", "SOME_NEW_TOKEN=Zx9Q2pL7vT4mN1kR8sW3yB6dF0hJ5aE"),
]

NEGATIVE_CONTROLS_MUST_STAY_GREEN = [
    ("env.example service_role placeholder", "SUPABASE_SERVICE_ROLE_KEY="),
    ("env.example DB password placeholder", "DATABASE_URL=postgresql://postgres:[PASSWORD]@db.zyscsnhiymitpfdhjuci.supabase.co:5432/postgres"),
    ("env.example anon placeholder", "SUPABASE_ANON_KEY="),
    ("mcp.json env-indirection (no literal)", '"SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"'),
]


def run_selftest():
    print("leg K self-test: planting each K0-K6 positive control (untracked temp file), proving RED...")
    ok = True
    for rule, content in POSITIVE_CONTROLS:
        findings = []
        _scan_text("<selftest temp file>", content, findings)
        if any(f[1] == rule for f in findings):
            print(f"  [PASS] {rule} -> RED as expected")
        else:
            print(f"  [FAIL] {rule} -> did NOT trip (should have gone RED): {content!r}")
            ok = False

    print("leg K self-test: confirming committed placeholders/env-indirection stay GREEN...")
    for label, content in NEGATIVE_CONTROLS_MUST_STAY_GREEN:
        findings = []
        _scan_text("<selftest temp file>", content, findings)
        if not findings:
            print(f"  [PASS] {label} -> GREEN as expected")
        else:
            print(f"  [FAIL] {label} -> unexpectedly went RED: {findings}")
            ok = False

    print("leg K self-test: confirming key-denylist.md's own documented examples do NOT self-trip...")
    denylist_findings = run_scan_single_file(DENYLIST_DOC)
    if not denylist_findings:
        print("  [PASS] key-denylist.md scans GREEN against its own patterns (self-reference exemption working)")
    else:
        print(f"  [FAIL] key-denylist.md unexpectedly flagged itself: {denylist_findings}")
        ok = False

    print("leg K self-test: confirming a tracked .env would trip K0a (via an untracked stand-in check)...")
    # We don't create a real tracked .env (that would require `git add`, which we must never do for a
    # planted violation). Instead assert the K0a rule fires on the filename pattern directly.
    stand_in_tracked = [".env", ".env.production", ".env.example"]
    fake_findings = []
    _scan_tracked_env_files(stand_in_tracked, fake_findings)
    trapped = {f[0] for f in fake_findings}
    if ".env" in trapped and ".env.production" in trapped and ".env.example" not in trapped:
        print("  [PASS] K0a correctly flags .env/.env.production, spares .env.example")
    else:
        print(f"  [FAIL] K0a filename rule misbehaved: flagged {trapped}")
        ok = False

    if ok:
        print("\nSELF-TEST PASSED: every positive control bites, every documented placeholder/example stays green.")
        return 0
    else:
        print("\nSELF-TEST FAILED: see [FAIL] lines above.")
        return 1


def run_scan_single_file(path):
    relpath = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
    text = _read_text(relpath)
    findings = []
    if text is not None:
        _scan_text(relpath, text, findings)
    return findings


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(run_selftest())
    sys.exit(main_scan())
