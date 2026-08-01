"""
Shapes scan_service's raw per-candidate objects (dicts holding DataFrames,
pandas Timestamps, NaN) into the exact camelCase JSON contract in
ADR-0002 SS3. All shaping lives here -- scan_service and app.py never touch
JSON keys or serialization directly (ADR-0002 SS2.3).

Non-negotiables (ADR-0002 SS3): NaN/None -> null, pandas Timestamp -> ISO8601
string, DataFrame -> array of records, raw floats (no client-side formatting).
"""
import math

import numpy as np
import pandas as pd


def _clean(value):
    """None/NaN -> None; pandas/numpy scalars -> native Python; recurses into dicts/lists."""
    if value is None:
        return None
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, (pd.Timestamp,)):
        return _iso(value)
    if isinstance(value, (np.floating, float)):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _iso(ts):
    if ts is None:
        return None
    if isinstance(ts, str):
        return ts
    return pd.Timestamp(ts).isoformat()


def _date_str(d):
    if d is None:
        return None
    if isinstance(d, str):
        return d
    return str(d)


def _s3_component_pairs(s3):
    """component_scores/component_max -> {name: [earned, max]}, keys left snake_case
    (the mockup's D3 code keys on pattern_price/risk_reward/ease_of_entry/past_performance
    verbatim -- ADR-0002 SS3, not camelCased)."""
    scores, maxes = s3["component_scores"], s3["component_max"]
    return {k: [_clean(scores[k]), _clean(maxes.get(k))] for k in scores}


def _serialize_intraday(intraday_df, alignment, prior_high, prior_low, prior_close):
    if alignment is None or intraday_df is None or intraday_df.empty:
        return None
    bars = [
        {
            "t": _iso(ts),
            "open": _clean(row["Open"]), "high": _clean(row["High"]),
            "low": _clean(row["Low"]), "close": _clean(row["Close"]),
            "volume": _clean(row["Volume"]),
        }
        for ts, row in intraday_df.iterrows()
    ]
    return {
        "bars": bars,
        "pivots": _clean(alignment["levels"]),
        "priorHigh": _clean(prior_high), "priorLow": _clean(prior_low), "priorClose": _clean(prior_close),
        "latestAligned": _clean(alignment["latest_aligned"]),
        "firstTriggerTime": _iso(alignment["first_trigger_time"]),
    }


def _serialize_simulated_trades(sim):
    if sim is None:
        return None
    return {
        "enabled": True,
        "numTrades": _clean(sim["num_trades"]),
        "winRatePct": _clean(sim["win_rate_pct"]),
        "finalPnl": _clean(sim["final_pnl"]),
        "pnlPerShare": _clean(sim["pnl_per_share"]),
        "pnlCurve": _clean(sim["pnl_curve"]),
        "halted": _clean(sim["halted"]),
        "haltReason": sim["halt_reason"],
        "trades": [
            {
                "entryTime": _iso(t["entry_time"]), "exitTime": _iso(t["exit_time"]),
                "entryPrice": _clean(t["entry_price"]), "exitPrice": _clean(t["exit_price"]),
                "pnl": _clean(t["pnl"]), "reason": t["reason"],
            }
            for t in sim["trades"]
        ],
    }


def serialize_candidate(raw):
    guardrail = None
    if raw.get("guardrail"):
        gr = raw["guardrail"]
        guardrail = {
            "gainOk": _clean(gr["gain_ok"]), "relVolOk": _clean(gr["relative_volume_ok"]),
            "priceOk": _clean(gr["price_ok"]), "passesCore": _clean(gr["passes_core"]),
            "passesAll": _clean(gr["passes_all"]), "shortInterestOk": _clean(gr["short_interest_ok"]),
            "floatOk": _clean(gr["float_ok"]), "catalystGates": _clean(gr["catalyst_gates"]),
            "shortInterestGates": _clean(gr["short_interest_gates"]),
        }

    s3 = None
    if raw.get("s3"):
        s3_raw = raw["s3"]
        s3 = {
            **_s3_component_pairs(s3_raw),
            "scorePct": _clean(s3_raw["score_pct"]), "rating": s3_raw["rating"],
            "isPartial": _clean(s3_raw["is_partial"]),
        }

    return {
        "ticker": raw["ticker"],
        "spikeDate": _date_str(raw["spike_date"]),
        "spikeGainPct": _clean(raw["spike_gain_pct"]),
        "holdingUp": _clean(raw["holding_up"]),
        "retracementPct": _clean(raw["retracement_pct"]),
        "worstRetracementPct": _clean(raw["worst_retracement_pct"]),
        "lastClose": _clean(raw["last_close"]),
        "relVol": _clean(raw["rel_vol"]),
        "todayGainPct": _clean(raw["today_gain_pct"]),
        "hasCatalyst": _clean(raw["has_catalyst"]),
        "daysToCover": _clean(raw["days_to_cover"]),
        "phase": raw["phase"],
        "aligned": _clean(raw["aligned"]),
        "guardrail": guardrail,
        "s3": s3,
        "patterns": raw.get("patterns_fired") or [],
        "intraday": _serialize_intraday(raw.get("intraday_df"), raw.get("alignment"),
                                         raw.get("prior_high"), raw.get("prior_low"), raw.get("prior_close")),
        "simulatedTrades": _serialize_simulated_trades(raw.get("simulated_trades")),
    }


def build_scan_response(raw_candidates, params):
    candidates = [serialize_candidate(c) for c in raw_candidates]

    holding = [c for c in candidates if c["holdingUp"]]
    aligned_now = [c for c in holding if c["aligned"]]
    s3_pcts = [c["s3"]["scorePct"] for c in holding if c.get("s3")]
    avg_s3_pct = round(sum(s3_pcts) / len(s3_pcts), 1) if s3_pcts else None

    return {
        "meta": {
            "ranAt": pd.Timestamp.now(tz="UTC").isoformat(),
            "tickerCount": len(params.get("tickers", [])),
            "params": params,
        },
        "stats": {
            "candidatesScanned": len(candidates),
            "holdingUp": len(holding),
            "alignedNow": len(aligned_now),
            "avgS3Pct": avg_s3_pct,
        },
        "candidates": candidates,
    }
