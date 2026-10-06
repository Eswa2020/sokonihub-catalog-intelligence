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