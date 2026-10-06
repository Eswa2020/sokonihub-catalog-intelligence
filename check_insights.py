"""Quality gate for insights.json.

Fails on missing keys, flagged messages too short to act on, or messages
that overclaim verification (nothing in a review queue is verified yet).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["sku", "score", "flag", "seller_message"]
MIN_FLAGGED_LEN = 20
BANNED = ["verified", "authentic"]


def main() -> int:
    try:
        rows = json.loads((ROOT / "insights.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: insights.json not found. Run insights.py first.")
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: insights.json is not valid JSON:", e)
        return 1

    for r in rows:
        missing = [k for k in REQUIRED if k not in r]
        if missing:
            print(f"FAIL {r.get('sku', '?')}: missing {missing}")
            return 1
        if r["flag"] and len(r["seller_message"]) < MIN_FLAGGED_LEN:
            print(f"FAIL {r['sku']}: flagged message too short")
            return 1
        msg = r["seller_message"].lower()
        if any(word in msg for word in BANNED):
            print(f"FAIL {r['sku']}: message overclaims verification")
            return 1
    print(f"insights OK ({len(rows)} listings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())