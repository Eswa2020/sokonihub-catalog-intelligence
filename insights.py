"""Seller-facing insights from mismatch scores.

Produces insights.json: score, flag, privacy routing, and one actionable
sentence per SKU. Uses catalog_with_audio.json when present so transcripts
travel with the row.
"""
import json
from pathlib import Path

from mismatch import score_row
from privacy_flag import needs_privacy_review

ROOT = Path(__file__).resolve().parent

FLAGGED_MSG = (
    "The listing photo does not appear to match the title. "
    "Please review the photo or update the title before the listing goes live."
)
ALIGNED_MSG = "Photo and title look aligned."


def insight(row: dict, scored: dict) -> dict:
    return {
        "sku": row["sku"],
        "score": scored["score"],
        "flag": scored["flag"],
        "needs_privacy_review": needs_privacy_review(row.get("image_tags")),
        "seller_message": FLAGGED_MSG if scored["flag"] else ALIGNED_MSG,
        "transcript": row.get("transcript") or "",
    }


def main() -> int:
    source = ROOT / "catalog_with_audio.json"
    if not source.exists():
        source = ROOT / "catalog.json"
    try:
        rows = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json missing")
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: catalog JSON error:", e)
        return 1

    pack = [insight(r, score_row(r)) for r in rows]
    (ROOT / "insights.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    flagged = sum(r["flag"] for r in pack)
    privacy = sum(r["needs_privacy_review"] for r in pack)
    print(f"wrote insights.json ({len(pack)} listings, {flagged} flagged, "
          f"{privacy} privacy review, source={source.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())