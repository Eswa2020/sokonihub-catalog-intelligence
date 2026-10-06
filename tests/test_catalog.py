"""Unit tests for scoring, insights, privacy routing, and search."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from insights import insight  # noqa: E402
from mismatch import cosine, score_row  # noqa: E402
from privacy_flag import needs_privacy_review  # noqa: E402
from search import search  # noqa: E402

CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
BY_SKU = {r["sku"]: r for r in CATALOG}


def test_cosine_bounds():
    assert cosine([1, 0], [1, 0]) == 1.0
    assert cosine([1, 0], [0, 1]) == 0.0
    assert cosine([0, 0], [1, 0]) == 0.0


def test_reference_pair():
    assert score_row(BY_SKU["KND-01"])["flag"] is False
    assert score_row(BY_SKU["NK-99"])["flag"] is True


def test_known_language_gap_flags_kiswahili_title():
    # Documented limitation: an English-only vocabulary flags a correct Kiswahili listing.
    # Improving language coverage should change this test deliberately.
    assert score_row(BY_SKU["MKB-03"])["flag"] is True


def test_insights_never_carry_or_change_titles():
    row = BY_SKU["NK-99"]
    original = row["title"]
    out = insight(row, score_row(row))
    assert "title" not in out
    assert row["title"] == original
    assert len(out["seller_message"]) >= 20


def test_privacy_routing():
    assert needs_privacy_review(BY_SKU["LSO-02"]["image_tags"]) is True
    assert needs_privacy_review(BY_SKU["KND-01"]["image_tags"]) is False


def test_search_ranks_on_image_evidence():
    ranking = [sku for _, sku in search("kiondo", CATALOG, k=len(CATALOG))]
    assert ranking[0] == "KND-01"
    assert ranking.index("KND-01") < ranking.index("NK-99")