"""Seller voice-note transcription.

Reads a transcript sidecar (<audio>.txt) beside the audio file. A live
speech-to-text model can replace the body of transcribe_seller_note()
without changing any caller. Missing audio returns an empty string.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIO_DIR = ROOT / "audio"


def transcribe_seller_note(audio_path: str | Path) -> str:
    sidecar = Path(str(audio_path) + ".txt")
    if sidecar.exists():
        return sidecar.read_text(encoding="utf-8").strip()
    return ""


if __name__ == "__main__":
    AUDIO_DIR.mkdir(exist_ok=True)
    (AUDIO_DIR / "knd-01.ogg.txt").write_text(
        "Navy sisal kiondo, handmade.", encoding="utf-8"
    )
    print(transcribe_seller_note(AUDIO_DIR / "knd-01.ogg"))