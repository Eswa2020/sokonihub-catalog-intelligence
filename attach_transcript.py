"""Attach seller voice-note transcripts to catalog rows by SKU.

Writes catalog_with_audio.json; rows without a voice note get an empty
transcript. Transcripts are seller data and must not be written to logs.
"""
import json
from pathlib import Path

from voice_stub import AUDIO_DIR, transcribe_seller_note

ROOT = Path(__file__).resolve().parent


def attach(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        row = dict(r)
        row["transcript"] = transcribe_seller_note(AUDIO_DIR / f"{r['sku'].lower()}.ogg")
        out.append(row)
    return out


def main() -> int:
    try:
        rows = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json not found")
        return 1
    enriched = attach(rows)
    (ROOT / "catalog_with_audio.json").write_text(
        json.dumps(enriched, indent=2), encoding="utf-8"
    )
    with_audio = sum(1 for r in enriched if r["transcript"])
    print(f"wrote catalog_with_audio.json ({with_audio}/{len(enriched)} with transcripts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())