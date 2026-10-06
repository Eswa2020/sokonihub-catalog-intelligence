"""Encode pass: offline stub by default, live Hugging Face pipeline when LIVE_HF=1.

Writes encode_cache.json recording which mode produced the vectors, so no
report can claim a model that did not run. A failed live call falls back to
the stub and says so.
"""
import json
import os
from pathlib import Path

import yaml

from mismatch import VOCAB

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "encode_cache.json"


def stub_encode(tags: list[str]) -> list[float]:
    """Deterministic tag-presence vector over VOCAB."""
    return [1.0 if t in tags else 0.0 for t in VOCAB]


def live_encode(text: str, cfg: dict):
    from transformers import pipeline

    pipe = pipeline(
        cfg["task"], model=cfg["model"], revision=str(cfg["revision"]), device=cfg["device"]
    )
    return pipe(text)


def main() -> int:
    try:
        rows = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: catalog.json missing")
        return 1

    cfg = yaml.safe_load((ROOT / "hf_pipeline.yaml").read_text(encoding="utf-8"))
    live = os.environ.get("LIVE_HF") == "1"
    mode = "live-transformers" if live else "offline-stub"
    vectors = {}

    if live:
        try:
            first = rows[0]
            vectors[first["sku"]] = live_encode(first.get("title") or "", cfg)
        except Exception as e:  # optional path; fall back honestly
            print("Live encode failed, falling back to stub:", e)
            mode, live, vectors = "offline-stub-after-live-fail", False, {}

    if not live:
        for r in rows:
            vectors[r["sku"]] = stub_encode(r.get("image_tags") or [])

    encoder = f"{cfg['model']}@{cfg['revision']}" if mode == "live-transformers" else "lab-bow-v1"
    OUT.write_text(
        json.dumps({"mode": mode, "encoder": encoder, "vectors": vectors}, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {OUT.name} (mode={mode}, encoder={encoder}, {len(vectors)} listings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())