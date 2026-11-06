#!/usr/bin/env python3
"""DarkFactory Pilot Production Orchestrator.

One-click command center to produce the pilot documentary:
  - Step 1: TTS / Audio Ingestion (CosyVoice 3 Instruct 2 or Fallback)
  - Step 2: Broadcast Studio Mastering & SRT Synchronization
  - Step 3: Procedural Historical Sound Design Synthesis
  - Step 4: Video B-Roll Rendering & Final 1080p Master Assembly
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
PYTHON_EXE = sys.executable


def run_script(script_name: str) -> bool:
    target = SRC_DIR / script_name
    print(f"\n=======================================================")
    print(f"🎬 EXECUTING: {script_name}")
    print(f"=======================================================")
    res = subprocess.run([PYTHON_EXE, str(target)])
    return res.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Pilot Production Orchestrator")
    parser.add_argument(
        "--step",
        choices=["tts", "master", "sound", "video", "all"],
        default="all",
        help="Step to execute: tts, master, sound, video, or all (default: all)"
    )
    args = parser.parse_args()

    steps = []
    if args.step == "tts":
        steps = ["generate_pilot_audio.py"]
    elif args.step == "master":
        steps = ["cosyvoice_master.py"]
    elif args.step == "sound":
        steps = ["generate_sound_design.py"]
    elif args.step == "video":
        steps = ["render_pilot_video.py"]
    elif args.step == "all":
        steps = [
            "generate_pilot_audio.py",
            "cosyvoice_master.py",
            "generate_sound_design.py",
            "render_pilot_video.py"
        ]

    for s in steps:
        success = run_script(s)
        if not success:
            print(f"\n❌ Pipeline failed at step: {s}", file=sys.stderr)
            sys.exit(1)

    print(f"\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    print(f"Output video ready at: {PROJECT_ROOT / 'data' / 'output' / 'the_1983_soviet_glitch_final_1080p.mp4'}")


if __name__ == "__main__":
    main()
