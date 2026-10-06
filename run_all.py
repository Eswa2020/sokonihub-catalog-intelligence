"""Run the full pipeline and every quality gate in order; stop at the first failure.

write_gen_pin.py is intentionally excluded: the prompt pin changes only through
a reviewed pull request, never as a side effect of a pipeline run.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    "mismatch.py", "check_mismatch.py",
    "voice_stub.py", "attach_transcript.py",
    "insights.py", "check_insights.py",
    "check_encoder_pin.py", "check_pipeline_yaml.py", "pipeline_smoke.py",
    "check_gen_pin.py", "stub_render.py", "check_generation_outputs.py",
    "analytics.py", "vocab_gaps.py", "check_analytics.py",
    "privacy_flag.py", "check_ethics.py",
]


def main() -> int:
    for step in STEPS:
        print(f"\n==> {step}")
        result = subprocess.run([sys.executable, str(ROOT / step)], cwd=ROOT)
        if result.returncode != 0:
            print(f"\nFAIL at {step} (exit {result.returncode})")
            return result.returncode
    print(f"\nAll {len(STEPS)} steps passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())