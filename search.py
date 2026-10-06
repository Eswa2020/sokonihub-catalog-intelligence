"""Text-to-image search ranked on listing image evidence, not seller titles.

Ranking on titles would let a mislabelled listing rank for the wrong query.
Relevance labels for recall@k are derived from image tags here; production
evaluation would use human-labelled relevance.
"""
import json
import sys
from pathlib import Path

from mismatch import bow, cosine, tokens

ROOT = Path(__file__).resolve().parent


def search(query: str, catalog: list[dict], k: int = 3) -> list[tuple[float, str]]:
    qv = bow(tokens(query))
    scored = [(round(cosine(qv, bow(r.get("image_tags") or [])), 4), r["sku"]) for r in catalog]
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[:k]


def recall_at_k(results: list[tuple[float, str]], relevant: set[str]) -> float:
    if not relevant:
        return 0.0
    return sum(1 for _, sku in results if sku in relevant) / len(relevant)


def main() -> int:
    try:
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json missing")
        return 1
    query = " ".join(sys.argv[1:]) or "kiondo"
    q = set(tokens(query))
    relevant = {r["sku"] for r in catalog if q & set(r.get("image_tags") or [])}
    results = search(query, catalog, k=3)
    print(f"query: {query!r}")
    for rank, (score, sku) in enumerate(results, 1):
        print(f"  {rank}. {sku:<8} score={score}")
    print(f"recall@3 = {recall_at_k(results, relevant):.2f} (relevant: {sorted(relevant)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())