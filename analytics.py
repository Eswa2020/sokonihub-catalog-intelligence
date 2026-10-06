"""Mismatch flag rates by category.

Joins catalog.json categories to mismatch_report.json flags and writes
rates.json. Every rate carries its sample size; small n describes this
fixture, not the marketplace.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def rates(catalog: list[dict], report: list[dict]) -> dict:
    flags = {r["sku"]: r["flag"] for r in report}
    buckets: dict[str, dict] = {}
    for row in catalog:
        b = buckets.setdefault(row.get("category") or "unknown", {"n": 0, "n_flagged": 0})
        b["n"] += 1
        if flags.get(row["sku"]):
            b["n_flagged"] += 1

    out = {}
    tot_n = tot_f = 0
    for cat in sorted(buckets):
        b = buckets[cat]
        out[cat] = {
            "n": b["n"],
            "n_flagged": b["n_flagged"],
            "flag_rate": round(b["n_flagged"] / b["n"], 4) if b["n"] else 0.0,
        }
        tot_n += b["n"]
        tot_f += b["n_flagged"]
    out["overall"] = {
        "n": tot_n,
        "n_flagged": tot_f,
        "flag_rate": round(tot_f / tot_n, 4) if tot_n else 0.0,
    }
    return out


def main() -> int:
    try:
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
        report = json.loads((ROOT / "mismatch_report.json").read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        print("FAIL: missing input:", e.filename)
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: bad JSON:", e)
        return 1

    out = rates(catalog, report)
    (ROOT / "rates.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    for cat, r in out.items():
        print(f"{cat:<9} n={r['n']:<3} flagged={r['n_flagged']:<3} flag_rate={r['flag_rate']}")
    print("wrote rates.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())