"""Title tokens the encoder vocabulary does not cover.

Writes vocab_gaps.json as {sku, token} rows. Gaps are a coverage and bias
input: a dropped token cannot contribute to the score, so listings written
in uncovered languages are scored on less evidence.
"""
import json
from pathlib import Path

from mismatch import VOCAB, tokens

ROOT = Path(__file__).resolve().parent


def gaps(catalog: list[dict]) -> list[dict]:
    known = set(VOCAB)
    return [
        {"sku": r["sku"], "token": t}
        for r in catalog
        for t in tokens(r.get("title") or "")
        if t not in known
    ]


def main() -> int:
    try:
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json missing")
        return 1
    rows = gaps(catalog)
    (ROOT / "vocab_gaps.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    by_sku: dict[str, list[str]] = {}
    for g in rows:
        by_sku.setdefault(g["sku"], []).append(g["token"])
    for sku, toks in by_sku.items():
        print(f"{sku:<8} {', '.join(toks)}")
    print(f"wrote vocab_gaps.json ({len(rows)} uncovered tokens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())