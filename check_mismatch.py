"""Regression gate for mismatch scoring.

Exits 0 only when every reference listing receives its expected flag.
Run after mismatch.py: python check_mismatch.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "mismatch_report.json"

# Reference listings with known-correct outcomes.
EXPECTED_FLAGS = {
    "KND-01": False,  # photo and title agree
    "NK-99": True,    # sneaker title on a woven-bag photo
    "LSO-02": False,  # textile listing, confirms vocab is not two-row specific
}


def main() -> int:
    try:
        rows = json.loads(REPORT.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: mismatch_report.json not found. Run mismatch.py first.")
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: mismatch_report.json is not valid JSON:", e)
        return 1

    by_sku = {r["sku"]: r for r in rows}
    failures = 0
    for sku, expected in EXPECTED_FLAGS.items():
        row = by_sku.get(sku)
        if row is None:
            print(f"FAIL {sku}: missing from report")
            failures += 1
            continue
        ok = row["flag"] == expected
        failures += 0 if ok else 1
        status = "OK  " if ok else "FAIL"
        print(f"{status} {sku}: score={row['score']} flag={row['flag']} expected={expected}")

    if failures:
        print(f"FAIL: {failures} reference listing(s) did not match")
        return 1
    print(f"Reference set OK ({len(EXPECTED_FLAGS)} listings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())