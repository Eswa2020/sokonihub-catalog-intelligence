"""Hash the generation prompt and write gen_pin.json. Re-run only via a reviewed PR."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "prompts" / "gen" / "kiondo_lifestyle_v1.txt"


def main() -> int:
    if not PROMPT.exists():
        print("FAIL: prompt file missing:", PROMPT)
        return 1
    pin = {
        "prompt_file": PROMPT.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
    }
    (ROOT / "gen_pin.json").write_text(json.dumps(pin, indent=2), encoding="utf-8")
    print(f"wrote gen_pin.json ({pin['prompt_file']} sha256={pin['sha256'][:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())