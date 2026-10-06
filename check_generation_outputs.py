"""Every generated image must carry provenance; none may sit in images/."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["sku", "generator", "image_file", "prompt_file", "prompt_sha256"]


def main() -> int:
    metas = sorted((ROOT / "outputs").glob("*_meta.json"))
    if not metas:
        print("FAIL: no outputs/*_meta.json found. Run stub_render.py.")
        return 1
    for m in metas:
        meta = json.loads(m.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED if k not in meta]
        if missing:
            print(f"FAIL {m.name}: missing {missing}")
            return 1
        if meta.get("not_a_photo_of_the_sku") is not True:
            print(f"FAIL {m.name}: not_a_photo_of_the_sku must be true")
            return 1
        if not (ROOT / meta["image_file"]).exists():
            print(f"FAIL {m.name}: image file missing")
            return 1
        if meta["image_file"].startswith("images/"):
            print(f"FAIL {m.name}: generated image placed in reference images/")
            return 1
    print(f"generation outputs OK ({len(metas)} labelled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())