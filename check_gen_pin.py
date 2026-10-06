"""Fails if the generation prompt has drifted from its pinned hash."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    try:
        pin = json.loads((ROOT / "gen_pin.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: gen_pin.json missing. Run write_gen_pin.py.")
        return 1
    path = ROOT / pin["prompt_file"]
    if not path.exists():
        print("FAIL: pinned prompt file missing:", pin["prompt_file"])
        return 1
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != pin["sha256"]:
        print(f"FAIL: prompt drift\n  pinned {pin['sha256']}\n  actual {got}")
        return 1
    print(f"gen pin OK ({pin['prompt_file']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())