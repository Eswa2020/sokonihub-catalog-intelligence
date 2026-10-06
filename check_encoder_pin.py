"""Validates encoder_pin.json: the pin must name what actually produced the scores."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLOATING_REVS = {"", "main", "master", "latest"}


def main() -> int:
    try:
        pin = json.loads((ROOT / "encoder_pin.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: encoder_pin.json missing")
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: encoder_pin.json is not valid JSON:", e)
        return 1

    eid = str(pin.get("encoder_id") or "").strip()
    rev = str(pin.get("revision") or "").strip()
    source = str(pin.get("source") or "").strip().lower()
    notes = str(pin.get("notes") or "").strip()
    honesty = str(pin.get("honesty") or "").strip()

    if eid in ("", "REPLACE_ME"):
        print("FAIL: encoder_id is empty or a placeholder")
        return 1
    if rev.lower() in FLOATING_REVS:
        print("FAIL: revision must be a concrete pin, not main/master/latest")
        return 1
    if source == "huggingface":
        if "/" not in eid:
            print("FAIL: Hugging Face ids must be org/name")
            return 1
        if not notes:
            print("FAIL: Hugging Face pins need notes describing the actual run")
            return 1
    elif source in ("lab", "local") or eid.startswith("lab-"):
        if not honesty and not notes:
            print("FAIL: local encoder pins must declare honesty or notes")
            return 1

    print(f"encoder pin OK: {eid}@{rev} (source={source})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())