#!/usr/bin/env python3
"""DarkFactory Pilot Production Orchestrator.

One-click command center to produce the pilot documentary:
  - Step 0: Direct (Nolan Dark History Director Screenplay Synthesis)
  - Step 1: Research Engine (Wikipedia Ground-Truth Extraction)
  - Step 2: TTS / Audio Ingestion (CosyVoice 3 Instruct 2, Kokoro-82M, or Edge-TTS)
  - Step 3: Broadcast Studio Mastering & SRT Synchronization
  - Step 4: 4-Stem Master Audio Mixer & Dynamic Sidechain Ducking (Google Flow + MMAudio)
  - Step 5: Video B-Roll Rendering & Final 1080p Master Assembly
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
        choices=["direct", "research", "flow", "tts", "tts-local", "master", "sound", "video", "shorts", "publish", "all", "all-local"],
        default="all",
        help="Step to execute (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode for API / browser services",
    )
    args = parser.parse_args()

    steps = []
    if args.step == "direct":
        steps = ["nolan_director.py"]
    elif args.step == "research":
        steps = ["research_engine.py"]
    elif args.step == "flow":
        steps = ["google_flow_bot.py"]
    elif args.step == "tts":
        steps = ["generate_pilot_audio.py"]
    elif args.step == "tts-local":
        steps = ["kokoro_fallback.py"]
    elif args.step == "master":
        steps = ["cosyvoice_master.py"]
    elif args.step == "sound":
        steps = ["audio_mixer_master.py"]
    elif args.step == "video":
        steps = ["render_pilot_video.py"]
    elif args.step == "shorts":
        steps = ["shorts_generator.py"]
    elif args.step == "publish":
        steps = ["youtube_publisher.py"]
    elif args.step == "all":
        steps = [
            "nolan_director.py",
            "research_engine.py",
            "generate_pilot_audio.py",
            "cosyvoice_master.py",
            "audio_mixer_master.py",
            "render_pilot_video.py",
            "shorts_generator.py"
        ]
    elif args.step == "all-local":
        steps = [
            "nolan_director.py",
            "research_engine.py",
            "kokoro_fallback.py",
            "cosyvoice_master.py",
            "audio_mixer_master.py",
            "render_pilot_video.py",
            "shorts_generator.py"
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
