# SokoniHub Catalog Intelligence

![checks](https://github.com/Eswa2020/sokonihub-catalog-intelligence/actions/workflows/checks.yml/badge.svg)

Cross-modal integrity checks for a Kenyan marketplace catalog. Each listing's photo evidence is
scored against its title; disagreements go to a human review queue with a seller-facing message.
Seller voice notes attach to the same listing as transcripts, campaign images are generated only
from a pinned prompt with provenance, and flag rates are reported per category with sample size.
Titles are never rewritten automatically.

## Quick start

```bash
python -m venv venv
source venv/Scripts/activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python run_all.py                   # full pipeline + every quality gate
pytest -q                           # unit tests
```

## Encoder honesty

- **What produced the scores:** `lab-bow-v1`, a bag-of-words encoder over image tags (`encoder_pin.json`).
- **Did Hugging Face transformers run?** No. `hf_pipeline.yaml` declares the intended live encoder
  (`openai/clip-vit-base-patch32` at a pinned commit, CPU). `pipeline_smoke.py` records
  `mode: offline-stub` in `encode_cache.json`; `LIVE_HF=1` attempts a live call and falls back honestly.

## Catalog join

`mismatch.py` scores image evidence against title tokens with cosine similarity (late fusion) and
flags scores below 0.25, writing `mismatch_report.json`. `check_mismatch.py` gates the reference set:

| SKU | Score | Flag | Expected |
|-----|-------|------|----------|
| KND-01 (kiondo, kiondo title) | 1.0 | clear | clear |
| NK-99 (woven bag, sneaker title) | 0.0 | flagged | flagged |
| LSO-02 (leso, leso title) | 0.8165 | clear | clear |

## Seller insights

`insights.json` holds, per SKU: `score`, `flag`, `needs_privacy_review`, `seller_message`, and
`transcript`. Flagged listings get an actionable message; no code path writes to a listing title.
Voice notes are read from `audio/<sku>.ogg.txt` transcript sidecars and joined by SKU.

## Models and generation

| Artifact | Purpose |
|----------|---------|
| `hf_pipeline.yaml` | Task, model, pinned revision, device for the intended live encoder |
| `gen_twin.json` | DALL-E (managed) and Stable Diffusion (open source) as interchangeable generators |
| `prompts/gen/*.txt` + `gen_pin.json` | Generation prompt as hashed, reviewed config |
| `outputs/*_meta.json` | Provenance: generator, prompt hash, `not_a_photo_of_the_sku: true` |

Generator used: **stub** (`stub_render.py` writes a valid placeholder PNG with the same metadata a
DALL-E or Stable Diffusion call would). Generated images live only in `outputs/`, never in `images/`
or the reference set. Renders are cached by prompt hash rather than regenerated per page view.

## Analytics

Five-listing fixture (`rates.json`):

| Category | n | Flagged | Flag rate |
|----------|---|---------|-----------|
| bags | 3 | 1 | 0.33 |
| shoes | 1 | 1 | 1.0 |
| textiles | 1 | 0 | 0.0 |
| **overall** | **5** | **2** | **0.4** |

One of the two flags (MKB-03) is a false positive: a correctly photographed bag with a Kiswahili
title the English-only vocabulary cannot read. `vocab_gaps.json` lists all 13 uncovered title tokens.
`search.py` ranks listings on image evidence rather than titles; for "kiondo", KND-01 ranks first
with recall@3 = 1.0 (relevance labels derived from tags, a proxy for human labels).

## Responsible deployment

See [`ethics_note.md`](ethics_note.md): who is in the photos, whose language, generated pixels,
review path, manager summary, and transfer. In one sentence: **a flag is a recommendation that a
seller or moderator resolves; the system never rewrites titles or takes listings down on this score.**

## Fallbacks declared

- [x] No GPU / no transformers: scores from `lab-bow-v1`; `hf_pipeline.yaml` documents the live path
- [x] No image-generation API key: `stub_render.py` with full provenance metadata
- [x] No speech-to-text model: transcript sidecars in `audio/`
- [x] Sample size is a five-listing fixture, not marketplace data
- [x] No real people photos or marketplace crawls; person/face/child tags route to privacy review

## Engineering practices applied

- **Embedding comparison:** CLIP-style shared-space scoring, implemented as a swappable encoder.
- **Cost control:** batch rescoring and prompt-hash caching instead of per-view vision calls.
- **Version pinning:** encoder, pipeline revision, and generation prompt pinned and checked in CI.
- **Data protection:** no secrets in git, transcripts kept out of logs, privacy review for photos of
  people under the Kenya Data Protection Act.

## Quality checklist

- [x] NK-99 flagged, KND-01 clear (`check_mismatch.py`, `pytest`)
- [x] Generated outputs separate from reference images (`check_generation_outputs.py`)
- [x] Ethics note has a concrete argument under every heading (`check_ethics.py`)
- [x] No absolute security or fairness claims

## Limitations

The bag-of-words vocabulary is small and English-only; out-of-vocabulary words, including Kiswahili
and Sheng terms, are dropped silently, which understates agreement for those listings. Five
listings demonstrate the controls; they do not measure accuracy or fairness at scale.