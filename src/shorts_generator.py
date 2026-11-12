#!/usr/bin/env python3
"""DarkFactory Vertical Shorts Generator (9:16 High-Retention Mobile Engine).

Transforms 16:9 cinematic master documentary videos into 9:16 vertical Shorts:
1. Extracts high-tension Cold Open (default: 55 seconds, strictly under the 60s Shorts limit).
2. Converts aspect ratio using a dual-layer aesthetic:
   - Blurred cinematic background to fill the 1080x1920 canvas without stretching.
   - Centered foreground maintaining original optical proportions and sharpness.
3. Burns dynamic high-visibility subtitles (yellow/white with bold black outline)
   positioned in the optimal vertical viewing zone (avoiding UI buttons).
4. Preserves 4-Stem master audio mix (Voice + Flow OST + Foley + Sub-Bass).
5. Exports atomically to data/output/shorts/ per ADR-02.
"""
import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# ADR-01: Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ShortsGenerator")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output"
SHORTS_DIR = OUTPUT_DIR / "shorts"
SUBS_DIR = DATA_DIR / "subtitles"


def get_ffmpeg_binary() -> str:
    """Find a valid ffmpeg executable on the system or in the darkfactory venv."""
    path = shutil.which("ffmpeg")
    if path:
        return path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    candidates = [
        PROJECT_ROOT / "venv" / "Lib" / "site-packages" / "imageio_ffmpeg" / "binaries" / "ffmpeg-win-x86_64-v9.0.2.exe",
        Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    raise FileNotFoundError("FFmpeg binary not found on this system.")


def build_shorts_filter_chain(srt_file: Optional[Path] = None) -> str:
    """Builds a high-grade 9:16 FFmpeg filter chain with blurred backdrop and stylized subtitles."""
    # Split input into background (scale & blur) and foreground (sharp center)
    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[combined]"
    )

    if srt_file and srt_file.is_file():
        clean_srt = srt_file.resolve().as_posix().replace(":", "\\:")
        # Styling: Yellow primary (&H0000FFFF), black thick outline (Outline=3), high visibility in mid-lower screen
        subtitle_filter = (
            f"[combined]subtitles='{clean_srt}':"
            "force_style='FontName=Arial,FontSize=22,Bold=1,PrimaryColour=&H0000FFFF,"
            "OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=380'[outv]"
        )
        return f"{filter_complex};{subtitle_filter}"

    return f"{filter_complex};[combined]copy[outv]"


def generate_vertical_short(
    video_input: Path,
    output_short: Path,
    srt_input: Optional[Path] = None,
    start_time: float = 0.0,
    duration_sec: float = 55.0,
    ffmpeg_bin: Optional[str] = None,
) -> bool:
    """Generates an optimized 1080x1920 vertical Short clip under 60 seconds."""
    if not video_input.exists():
        logger.error(f"Input video file not found: {video_input}")
        return False

    output_short.parent.mkdir(parents=True, exist_ok=True)
    bin_path = ffmpeg_bin or get_ffmpeg_binary()

    # Ensure duration is strictly under 60.0s for YouTube Shorts compliance
    duration_sec = min(59.5, max(5.0, duration_sec))

    filter_chain = build_shorts_filter_chain(srt_input)
    temp_output = output_short.with_suffix(f".tmp.{os.getpid()}.mp4")

    cmd = [
        bin_path, "-y",
        "-ss", f"{start_time:.2f}",
        "-t", f"{duration_sec:.2f}",
        "-i", str(video_input),
        "-filter_complex", filter_chain,
        "-map", "[outv]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(temp_output),
    ]

    logger.info(f"Rendering 9:16 Vertical Short ({duration_sec:.1f}s) -> {output_short.name}...")
    res = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if res.returncode != 0:
        logger.error(f"FFmpeg Short generation failed: {res.stderr}")
        if temp_output.exists():
            temp_output.unlink()
        return False

    # Atomic replace (ADR-02)
    temp_output.replace(output_short)
    logger.info(f"✅ Vertical Short successfully generated: {output_short.name}")
    return True


def generate_funnel_shorts_package(
    video_input: Path,
    master_video_id: str = "PENDING_MASTER_UPLOAD",
    srt_input: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    ffmpeg_bin: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Generates the multi-slice Shorts-to-Long-Form funnel package.

    Extracts 3 distinct 50-second micro-mysteries from the master documentary,
    each calibrated with a cliffhanger designed to convert mobile feed viewers into
    long-form watch time via the native YouTube Studio 'Related Video' selector.
    """
    target_dir = output_dir or SHORTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    slices_config = [
        {
            "slice_id": "short_01_hook",
            "title": "The Night Soviet Radar Turned Red",
            "start_time": 0.0,
            "duration": 50.0,
            "narrative_focus": "The Cold Open: Emergency siren blaring in Serpukhov-15 bunker.",
            "cta_hook": "Watch the full classified investigation linked below.",
        },
        {
            "slice_id": "short_02_radar",
            "title": "Why the Computer Swore World War 3 Started",
            "start_time": 35.0,
            "duration": 50.0,
            "narrative_focus": "Tactical telemetry: 5 incoming ballistic missiles confirmed by satellite.",
            "cta_hook": "Tap the linked video on screen to see what happened next.",
        },
        {
            "slice_id": "short_03_dilemma",
            "title": "His Finger Hovered Over the Nuclear Switch",
            "start_time": 70.0,
            "duration": 50.0,
            "narrative_focus": "The 20-minute launch countdown and Petrov's decision to trust gut instinct.",
            "cta_hook": "The full declassified documentary is linked right here.",
        },
    ]

    results = []
    base_stem = video_input.stem
    for cfg in slices_config:
        out_file = target_dir / f"{base_stem}_{cfg['slice_id']}.mp4"
        success = False
        if video_input.exists():
            success = generate_vertical_short(
                video_input=video_input,
                output_short=out_file,
                srt_input=srt_input,
                start_time=cfg["start_time"],
                duration_sec=cfg["duration"],
                ffmpeg_bin=ffmpeg_bin,
            )

        results.append({
            "slice_id": cfg["slice_id"],
            "title": cfg["title"],
            "start_time": cfg["start_time"],
            "duration": cfg["duration"],
            "output_file": str(out_file),
            "generated": success,
            "related_video_binding": {
                "target_master_video_id": master_video_id,
                "studio_selector": "YouTube Studio -> Video Details -> Related Video",
                "purpose": "Directs mobile Shorts viewers directly into the long-form watch time pool.",
            },
            "cta_hook": cfg["cta_hook"],
        })

    logger.info(f"Generated {len(results)} Shorts-to-Long funnel slices in {target_dir.name}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Vertical Shorts Generator")
    parser.add_argument(
        "--input",
        type=str,
        default=str(OUTPUT_DIR / "the_1983_soviet_glitch_final_1080p.mp4"),
        help="Input horizontal master video",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(SHORTS_DIR / "the_1983_soviet_glitch_short_01.mp4"),
        help="Destination 9:16 vertical short video",
    )
    parser.add_argument(
        "--subtitles",
        type=str,
        default=str(SUBS_DIR / "pilot_intro_mastered.srt"),
        help="Subtitles SRT file to burn onto Short",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=55.0,
        help="Duration of the Short in seconds (max 59.5s)",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=0.0,
        help="Start time in seconds",
    )
    args = parser.parse_args()

    in_video = Path(args.input)
    out_video = Path(args.output)
    srt_file = Path(args.subtitles) if args.subtitles else None

    success = generate_vertical_short(
        video_input=in_video,
        output_short=out_video,
        srt_input=srt_file if (srt_file and srt_file.exists()) else None,
        start_time=args.start,
        duration_sec=args.duration,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
