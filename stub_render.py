"""Render a labelled placeholder image from the pinned generation prompt.

Writes outputs/<sku>_stub.png plus outputs/<sku>_meta.json. A live DALL-E or
Stable Diffusion call would write the same meta keys with generator set to
'dalle' or 'sd' and a request_id. Outputs never go into images/.
"""
import hashlib
import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
SKU = "KND-01"


def write_stub_png(path: Path) -> None:
    """Write a valid 1x1 PNG using only the standard library."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    header = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    pixels = zlib.compress(b"\x00" + bytes([0, 0, 128]))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) + chunk(b"IEND", b"")
    path.write_bytes(png)


def main() -> int:
    try:
        pin = json.loads((ROOT / "gen_pin.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: gen_pin.json missing; a generator must never invent its own input")
        return 1
    prompt_path = ROOT / pin["prompt_file"]
    if not prompt_path.exists():
        print("FAIL: prompt file missing:", pin["prompt_file"])
        return 1
    actual = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
    if actual != pin["sha256"]:
        print("FAIL: prompt does not match gen_pin.json; refusing to render")
        return 1

    OUT.mkdir(exist_ok=True)
    stem = SKU.lower()
    image = OUT / f"{stem}_stub.png"
    write_stub_png(image)
    meta = {
        "sku": SKU,
        "generator": "stub",
        "format": "png",
        "image_file": image.relative_to(ROOT).as_posix(),
        "prompt_file": pin["prompt_file"],
        "prompt_sha256": pin["sha256"],
        "not_a_photo_of_the_sku": True,
    }
    (OUT / f"{stem}_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"wrote {image.name} and {stem}_meta.json (generator=stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())