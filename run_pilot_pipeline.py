#!/usr/bin/env python3
"""DarkFactory Pilot Production Orchestrator.

One-click command center to produce the pilot documentary:
  - Step 0: Pre-Flight Auth & Session Gate (Google Flow & RunningHub session verification)
  - Step 1: Direct (Nolan Dark History Director Screenplay Synthesis)
  - Step 2: Research Engine (Wikipedia Ground-Truth Extraction)
  - Step 3: Google Flow Stealth Bot & Real AI Video Generation (Veo 3.1 & Omni Flash + MiniMax H3 fallback)
  - Step 4: TTS / Audio Ingestion (CosyVoice 3 Instruct 2, Kokoro-82M, or Edge-TTS)
  - Step 5: Broadcast Studio Mastering & SRT Synchronization
  - Step 6: 4-Stem Master Audio Mixer & Dynamic Sidechain Ducking
  - Step 7: Video B-Roll Rendering & Final 1080p Master Assembly
  - Step 8: Shorts Generator (YouTube Shorts 9:16 cuts)
  - Step 9: YouTube Compliance QC
  - Step 10: YouTube Algorithm Booster
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

DRY_RUN_SUPPORTED = {"auth_gate.py", "google_flow_bot.py", "render_pilot_video.py"}


def run_script(script_name: str, dry_run: bool = False, extra_args: list = None) -> bool:
    target = SRC_DIR / script_name
    print(f"\n=======================================================")
    print(f"🎬 EXECUTING: {script_name}")
    print(f"=======================================================")
    cmd = [PYTHON_EXE, str(target)]
    if dry_run and script_name in DRY_RUN_SUPPORTED:
        cmd.append("--dry-run")
    if extra_args:
        cmd.extend(extra_args)
    res = subprocess.run(cmd)
    return res.returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Pilot Production Orchestrator")
    parser.add_argument(
        "--step",
        choices=["auth", "direct", "research", "flow", "tts", "tts-local", "master", "sound", "video", "shorts", "qc", "boost", "publish", "all", "all-local"],
        default=None,
        help="Step to execute"
    )
    parser.add_argument(
        "--phase",
        choices=["auth", "research", "script", "audio", "video", "render", "assembly", "all"],
        default=None,
        help="Cinematic phase to execute (alias mapping to pipeline steps)"
    )
    parser.add_argument(
        "--teaser",
        action="store_true",
        help="Execute teaser slice (Scenes 1 to 3) with Google Flow + Overlays + Master",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode for API / browser services",
    )
    args = parser.parse_args()

    steps = []
    # If phase is specified, map to corresponding steps
    if args.phase:
        if args.phase == "auth":
            steps = ["auth_gate.py"]
        elif args.phase == "research":
            steps = ["auth_gate.py", "research_engine.py"]
        elif args.phase == "script":
            steps = ["nolan_director.py"]
        elif args.phase == "audio":
            steps = ["auth_gate.py", "generate_pilot_audio.py", "cosyvoice_master.py", "audio_mixer_master.py"]
        elif args.phase == "video":
            steps = ["auth_gate.py", "google_flow_bot.py", "render_pilot_video.py"]
        elif args.phase in ("render", "assembly"):
            steps = ["render_pilot_video.py", "shorts_generator.py", "youtube_compliance_qc.py"]
        elif args.phase == "all":
            steps = [
                "auth_gate.py",
                "nolan_director.py",
                "research_engine.py",
                "google_flow_bot.py",
                "generate_pilot_audio.py",
                "cosyvoice_master.py",
                "audio_mixer_master.py",
                "render_pilot_video.py",
                "shorts_generator.py",
                "youtube_compliance_qc.py",
                "youtube_algorithm_booster.py",
            ]
    else:
        # Default step is "all" if neither step nor phase provided
        step_val = args.step or "all"
        if step_val == "auth":
            steps = ["auth_gate.py"]
        elif step_val == "direct":
            steps = ["nolan_director.py"]
        elif step_val == "research":
            steps = ["research_engine.py"]
        elif step_val == "flow":
            steps = ["google_flow_bot.py"]
        elif step_val == "tts":
            steps = ["generate_pilot_audio.py"]
        elif step_val == "tts-local":
            steps = ["kokoro_fallback.py"]
        elif step_val == "master":
            steps = ["cosyvoice_master.py"]
        elif step_val == "sound":
            steps = ["audio_mixer_master.py"]
        elif step_val == "video":
            steps = ["google_flow_bot.py", "render_pilot_video.py"]
        elif step_val == "shorts":
            steps = ["shorts_generator.py"]
        elif step_val == "qc":
            steps = ["youtube_compliance_qc.py"]
        elif step_val == "boost":
            steps = ["youtube_algorithm_booster.py"]
        elif step_val == "publish":
            steps = ["youtube_publisher.py"]
        elif step_val == "all":
            steps = [
                "auth_gate.py",
                "nolan_director.py",
                "research_engine.py",
                "google_flow_bot.py",
                "generate_pilot_audio.py",
                "cosyvoice_master.py",
                "audio_mixer_master.py",
                "render_pilot_video.py",
                "shorts_generator.py",
                "youtube_compliance_qc.py",
                "youtube_algorithm_booster.py",
            ]
        elif step_val == "all-local":
            steps = [
                "auth_gate.py",
                "nolan_director.py",
                "research_engine.py",
                "google_flow_bot.py",
                "kokoro_fallback.py",
                "cosyvoice_master.py",
                "audio_mixer_master.py",
                "render_pilot_video.py",
                "shorts_generator.py",
                "youtube_compliance_qc.py",
                "youtube_algorithm_booster.py",
            ]

    for s in steps:
        extra = []
        if args.teaser:
            if s == "nolan_director.py":
                extra.extend(["--mode", "teaser"])
            elif s in ("google_flow_bot.py", "render_pilot_video.py"):
                extra.append("--teaser")
        success = run_script(s, dry_run=args.dry_run, extra_args=extra)
        if not success:
            print(f"\n❌ Pipeline failed at step: {s}", file=sys.stderr)
            sys.exit(1)

    print(f"\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    print(f"Output video ready at: {PROJECT_ROOT / 'data' / 'output' / 'the_1983_soviet_glitch_final_1080p.mp4'}")


if __name__ == "__main__":
    main()
