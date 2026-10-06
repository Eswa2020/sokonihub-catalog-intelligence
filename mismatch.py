"""Image-vs-title mismatch scoring for marketplace listings.

Each listing's image evidence (image_tags, a stand-in for an image encoder)
and title are mapped onto a shared vocabulary and compared with cosine
similarity. Scores below THRESHOLD are flagged for human review; titles are
never rewritten automatically.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Single source of truth for the token encoder vocabulary.
VOCAB = [
    "kiondo", "bag", "sisal", "navy", "nike", "shoe",
    "white", "leso", "maize", "cloth", "red", "woven",
]
THRESHOLD = 0.25


def tokens(text: str) -> list[str]:
    """Lower-case and split text into word-like tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def bow(toks: list[str]) -> list[float]:
    """Bag-of-words vector over VOCAB. Unknown tokens are dropped."""
    idx = {t: i for i, t in enumerate(VOCAB)}
    v = [0.0] * len(VOCAB)
    for t in toks:
        if t in idx:
            v[idx[t]] += 1.0
    return v


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length vectors; 0.0 if either is all zeros."""
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / ((na * nb) or 1.0)


def score_row(row: dict) -> dict:
    """Score agreement between a listing's image evidence and its title."""
    image_vec = bow(row.get("image_tags") or [])
    title_vec = bow(tokens(row.get("title") or ""))
    s = cosine(image_vec, title_vec)
    return {"sku": row["sku"], "score": round(s, 4), "flag": s < THRESHOLD}


def main() -> int:
    path = ROOT / "catalog.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json not found at", path)
        return 1
    except json.JSONDecodeError as e:
        print("FAIL: catalog.json is not valid JSON:", e)
        return 1

    report = [score_row(r) for r in rows]
    (ROOT / "mismatch_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    for r in report:
        print(f"{r['sku']:<8} score={r['score']:<6} flag={r['flag']}")
    print(f"wrote mismatch_report.json ({len(report)} listings, threshold={THRESHOLD})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())