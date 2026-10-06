"""Validates hf_pipeline.yaml: allowed task, org/name model id, concrete revision."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
ALLOWED_TASKS = {"feature-extraction", "image-classification", "automatic-speech-recognition"}
REQUIRED = ["task", "model", "revision", "device"]
FLOATING_REVS = {"", "main", "master", "latest"}


def main() -> int:
    try:
        cfg = yaml.safe_load((ROOT / "hf_pipeline.yaml").read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("FAIL: hf_pipeline.yaml missing")
        return 1
    except yaml.YAMLError as e:
        print("FAIL: hf_pipeline.yaml is not valid YAML:", e)
        return 1

    if not isinstance(cfg, dict):
        print("FAIL: hf_pipeline.yaml must be a mapping")
        return 1
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        print("FAIL: missing keys", missing)
        return 1
    if cfg["task"] not in ALLOWED_TASKS:
        print(f"FAIL: task '{cfg['task']}' not in {sorted(ALLOWED_TASKS)}")
        return 1
    if "/" not in str(cfg["model"]):
        print("FAIL: model must be an org/name Hub id")
        return 1
    rev = str(cfg["revision"]).strip()
    if rev.lower() in FLOATING_REVS or rev.startswith("PASTE_"):
        print("FAIL: revision must be a concrete commit SHA or tag")
        return 1
    if cfg["device"] not in ("cpu", "cuda"):
        print("FAIL: device must be cpu or cuda")
        return 1

    print(f"pipeline config OK: {cfg['task']} {cfg['model']}@{rev[:8]} on {cfg['device']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())