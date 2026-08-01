"""
Flask backend for the Rolling Watchlist browser dashboard (D-TRADE-023,
adr_reference: ADR-0002). Routes only -- all orchestration lives in
scan_service.py, all JSON shaping in serialize.py (ADR-0002 SS2.3).

Run: python tools/web/app.py   (opens a browser tab once the server is up)
 or: flask --app tools/web/app run
"""
import sys
import threading
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from flask import Flask, jsonify, request, send_from_directory

from tools.rolling_watchlist import _resolve_massive_api_key
from tools.web import scan_service, serialize

app = Flask(__name__, static_folder="static", static_url_path="")

DEFAULT_PORT = 5000


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    # Presence only -- the key value itself never leaves the server (leg K/T,
    # ADR-0002 SS3 "Security" note).
    return jsonify({"ok": True, "massiveKeyPresent": _resolve_massive_api_key() is not None})


@app.post("/api/scan")
def scan():
    body = request.get_json(force=True, silent=True) or {}
    tickers = [t.strip() for t in body.get("tickers", []) if isinstance(t, str) and t.strip()]
    if not tickers:
        return jsonify({"error": "tickers is required and must be a non-empty array of strings"}), 400

    params = {
        "tickers": tickers,
        "period": body.get("period", "3mo"),
        "lookbackDays": body.get("lookbackDays", 5),
        "gainThreshold": body.get("gainThreshold", 20.0),
        "pullbackThreshold": body.get("pullbackThreshold", 50.0),
        "guardrail": body.get("guardrail", {}),
        "intraday": body.get("intraday", {}),
        "simulate": body.get("simulate", {}),
    }

    raw_candidates = scan_service.run_scan(
        tickers=params["tickers"], period=params["period"],
        lookback_days=params["lookbackDays"], gain_threshold=params["gainThreshold"],
        pullback_threshold=params["pullbackThreshold"], guardrail=params["guardrail"],
        intraday=params["intraday"], simulate=params["simulate"],
    )

    return jsonify(serialize.build_scan_response(raw_candidates, params))


def _open_browser(port):
    webbrowser.open(f"http://127.0.0.1:{port}")


if __name__ == "__main__":
    threading.Timer(1.0, _open_browser, args=(DEFAULT_PORT,)).start()
    # threaded=True so a long scan doesn't block a concurrent /api/health poll (ADR-0002 SS2.1).
    app.run(host="127.0.0.1", port=DEFAULT_PORT, threaded=True)
