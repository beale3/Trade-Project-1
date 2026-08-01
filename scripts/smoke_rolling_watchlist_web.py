"""
Boot smoke check for the rolling-watchlist web UI (D-TRADE-023, ADR-0002 §4 — DevOps deliverable).

Starts `tools/web/app.py` as a subprocess, polls GET /api/health, asserts the server is up and that
the response has the expected shape -- then kills the server. Never prints or logs the Massive key
itself (leg K discipline): only checks that `massiveKeyPresent` is present and boolean.

Usage:
    python scripts/smoke_rolling_watchlist_web.py

Exit code 0 = smoke check passed. Non-zero = failed (see printed reason). Exit code 2 specifically
means `tools/web/app.py` does not exist yet (AI/ML's ADR-0002 deliverable, not yet delivered) -- an
expected, informative SKIP while that work is in flight, not a hard failure of this script.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.join(REPO_ROOT, "tools", "web", "app.py")
HEALTH_URL = "http://127.0.0.1:5000/api/health"
BOOT_TIMEOUT_S = 10
POLL_INTERVAL_S = 0.5


def main() -> int:
    if not os.path.isfile(APP_PATH):
        print(f"SKIP: {APP_PATH} does not exist yet (ADR-0002 section 4 -- AI/ML's deliverable).")
        print("Nothing to smoke-check until it lands. This is expected, not a failure.")
        return 2

    env = dict(os.environ)
    proc = subprocess.Popen(
        ["flask", "--app", "tools/web/app", "run", "--port", "5000"],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.time() + BOOT_TIMEOUT_S
        last_error = None
        while time.time() < deadline:
            if proc.poll() is not None:
                out = proc.stdout.read() if proc.stdout else ""
                print("FAIL: server process exited early.\n--- output ---\n" + out)
                return 1
            try:
                with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                if body.get("ok") is not True:
                    print(f"FAIL: /api/health responded but ok != true: {body}")
                    return 1
                if not isinstance(body.get("massiveKeyPresent"), bool):
                    print(f"FAIL: massiveKeyPresent missing or not boolean: {body}")
                    return 1
                print(f"PASS: /api/health up, ok=true, massiveKeyPresent={body['massiveKeyPresent']}")
                return 0
            except (urllib.error.URLError, ConnectionError) as e:
                last_error = e
                time.sleep(POLL_INTERVAL_S)
        print(f"FAIL: server did not respond within {BOOT_TIMEOUT_S}s. Last error: {last_error}")
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
