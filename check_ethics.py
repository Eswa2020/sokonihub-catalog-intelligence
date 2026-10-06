"""Gates ethics_note.md: four required sections, each with a real argument."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEADS = ["Who is in the photos", "Whose language", "Generated pixels", "Review path"]
MIN_BODY = 40
BANNED = ["unhackable"]


def sections(text: str) -> dict[str, list[str]]:
    bodies: dict[str, list[str]] = {h: [] for h in HEADS}
    current = None
    for line in text.splitlines():
        raw = line.strip()
        if raw.startswith("#"):
            title = raw.lstrip("#").strip().lower()
            current = next((h for h in HEADS if h.lower() == title), None)
            continue
        if current:
            bodies[current].append(line)
    return bodies


def main() -> int:
    try:
        text = (ROOT / "ethics_note.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        print("FAIL: ethics_note.md missing")
        return 1
    if any(word in text.lower() for word in BANNED):
        print("FAIL: overclaim found")
        return 1
    for h, lines in sections(text).items():
        body = "\n".join(lines).strip()
        if not body:
            print("FAIL: empty section:", h)
            return 1
        if len(body) < MIN_BODY:
            print(f"FAIL: section too thin (< {MIN_BODY} chars): {h}")
            return 1
        if not any(len(s.strip()) >= 20 for s in body.split(".")):
            print("FAIL: no concrete sentence under", h)
            return 1
        print(f"OK   {h} ({len(body)} chars)")
    print("ethics note OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())