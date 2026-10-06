# SokoniHub Catalog Intelligence

Multimodal integrity checks for a marketplace catalog. Each listing's photo
evidence is scored against its title; disagreements are routed to a human
review queue with a seller-facing message. Titles are never rewritten
automatically.

## Pipeline

| Step | Script | Output |
|------|--------|--------|
| Score photo vs title | `mismatch.py` | `mismatch_report.json` |
| Reference-set gate | `check_mismatch.py` | exit 0/1, `mismatch_notes.txt` |
| Attach seller voice notes | `attach_transcript.py` | `catalog_with_audio.json` |
| Seller insights | `insights.py` | `insights.json` |
| Insights quality gate | `check_insights.py` | exit 0/1 |

```bash
python -m venv venv && source venv/Scripts/activate
pip install -r requirements.txt
python mismatch.py && python check_mismatch.py
python voice_stub.py && python attach_transcript.py
python insights.py && python check_insights.py
```

## Design decisions

- **Flag, don't rewrite.** A low score sends the listing to review; the seller or a moderator edits the title.
- **Late fusion.** Image evidence and title are scored separately and compared with cosine similarity, so each listing can be tested in isolation.
- **Swappable encoder.** `image_tags` stand in for an image encoder. A pinned CLIP model can replace them without changing the scoring contract.
- **Honest pinning.** `encoder_pin.json` names what actually produced the scores (`lab-bow-v1`), not a model that was never loaded.
- **Audio as a field.** Seller voice notes attach as a `transcript` on the same SKU. Transcripts stay out of logs.

## Limitations

The bag-of-words vocabulary is small; out-of-vocabulary words (including Sheng and Kiswahili terms) are dropped silently, which can understate agreement.

## Model and generation provenance

| Artifact | Purpose | Check |
|----------|---------|-------|
| `encoder_pin.json` | Names the encoder that actually produced the scores (`lab-bow-v1`) | `check_encoder_pin.py` |
| `hf_pipeline.yaml` | Intended live encoder: CLIP at a pinned Hub commit, CPU | `check_pipeline_yaml.py` |
| `pipeline_smoke.py` | Encode pass; offline stub by default, `LIVE_HF=1` for a live call | writes `encode_cache.json` with `mode` |
| `gen_twin.json` | DALL-E (managed) and Stable Diffusion (OSS) as interchangeable generators | — |
| `prompts/gen/*.txt` + `gen_pin.json` | Generation prompt as hashed config | `check_gen_pin.py` |
| `stub_render.py` | Labelled placeholder render with provenance meta | `check_generation_outputs.py` |

**Declared fallback:** no live Hugging Face encode or paid image API was run. Scores come from
`lab-bow-v1`; `encode_cache.json` records `mode: offline-stub`; generated images are
`generator: stub` placeholders. Swapping in a live model changes the pin, not the scoring contract.

**Retrieve vs generate:** mismatch scoring only uses seller evidence. Generated images live in
`outputs/` with `not_a_photo_of_the_sku: true` and never enter `images/` or the reference set.
Renders are cached by prompt hash rather than regenerated per page view. Model cards are reviewed
for licence and commercial-use terms before any checkpoint is pinned for marketplace ads.

```bash
python check_encoder_pin.py && python check_pipeline_yaml.py && python pipeline_smoke.py
python write_gen_pin.py && python check_gen_pin.py
python stub_render.py && python check_generation_outputs.py
```