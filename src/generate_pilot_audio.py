#!/usr/bin/env python3
"""DarkFactory Pilot Audio Engine.

Generates broadcast-mastered neural narration for the pilot documentary using:
1. Kokoro-82M ONNX (Local Zero-Cost Neural Engine) — Default: bm_george (BBC / Nolan style)
2. Dynamic voice selection (--voice bm_george / bm_lewis / am_adam)
3. Broadcast EQ & Compression filter chain (Ableton Live Complex Pro curve, -14 LUFS)
4. Synchronized SRT Subtitles
5. Edge-TTS ChristopherNeural fallback proxy
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Force UTF-8 on Windows stdout/stderr (ADR-01)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "data" / "scripts"
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"
SUBS_DIR = PROJECT_ROOT / "data" / "subtitles"
MODEL_DIR = PROJECT_ROOT / "data" / "models" / "kokoro"

# Fallback path to local models if not inside PROJECT_ROOT/data/models
if not (MODEL_DIR / "kokoro-v0_19.onnx").exists():
    ALT_MODEL_DIR = PROJECT_ROOT.parent / "data" / "models" / "kokoro"
    if (ALT_MODEL_DIR / "kokoro-v0_19.onnx").exists():
        MODEL_DIR = ALT_MODEL_DIR

SCRIPT_FILE = SCRIPTS_DIR / "pilot_soviet_glitch.json"
DEFAULT_VOICE = "bm_george"
DEFAULT_SPEED = 0.98


def get_ffmpeg_bin() -> str:
    """Finds ffmpeg executable."""
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
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
    return ffmpeg_bin or "ffmpeg"


def format_srt_time(seconds: float) -> str:
    """Format seconds into SRT timestamp: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(scenes: List[dict], durations: List[float], output_srt: Path) -> str:
    """Generates broadcast documentary SRT subtitles aligned to scene timings."""
    srt_entries = []
    current_time = 0.0
    counter = 1

    for scene, dur in zip(scenes, durations):
        text = scene["audio_text"]
        clauses = []
        for sentence in text.replace("...", ".").split(". "):
            sentence = sentence.strip()
            if not sentence:
                continue
            if not sentence.endswith("."):
                sentence += "."
            if len(sentence) > 60 and ", " in sentence:
                parts = sentence.split(", ", 1)
                clauses.append(parts[0].strip() + ",")
                clauses.append(parts[1].strip())
            else:
                clauses.append(sentence)

        total_chars = sum(len(c) for c in clauses)
        scene_start = current_time

        for clause in clauses:
            portion = len(clause) / max(total_chars, 1)
            clause_dur = dur * portion
            start_str = format_srt_time(current_time)
            end_str = format_srt_time(current_time + clause_dur - 0.08)

            srt_entries.append(f"{counter}\n{start_str} --> {end_str}\n{clause}\n")
            current_time += clause_dur
            counter += 1

        current_time = scene_start + dur

    full_srt = "\n".join(srt_entries)
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(full_srt)
    return full_srt


def master_audio(input_wav: Path, output_file: Path) -> None:
    """Applies documentary broadcast mastering (Ableton Live Complex Pro curve, -14 LUFS)."""
    filter_chain = (
        "highpass=f=60,"
        "equalizer=f=90:width_type=q:w=1.0:g=2.5,"
        "equalizer=f=350:width_type=q:w=1.5:g=-1.5,"
        "highshelf=f=3500:width_type=q:w=1.0:g=2.0,"
        "acompressor=threshold=-18dB:ratio=3:attack=15:release=120:makeup=2dB,"
        "loudnorm=I=-14:TP=-1.0:LRA=7"
    )

    cmd = [
        get_ffmpeg_bin(),
        "-y",
        "-i", str(input_wav),
        "-af", filter_chain,
    ]
    if output_file.suffix.lower() == ".mp3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", "320k", "-ar", "44100"])
    else:
        cmd.extend(["-c:a", "pcm_s24le", "-ar", "48000"])
    cmd.append(str(output_file))

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg mastering error: {res.stderr}")


async def generate_scene_edge_fallback(text: str, output_mp3: Path, voice: str = "en-US-ChristopherNeural") -> bytes:
    """Fallback to Edge-TTS if Kokoro is unavailable."""
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate="-2%", pitch="-1Hz")
    audio_data = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    with open(output_mp3, "wb") as f:
        f.write(audio_data)
    return bytes(audio_data)


def run_pipeline(voice: str = DEFAULT_VOICE, speed: float = DEFAULT_SPEED) -> dict:
    """Executes full pilot audio synthesis, broadcast mastering, and SRT generation."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SUBS_DIR.mkdir(parents=True, exist_ok=True)

    target_file = SCRIPT_FILE
    if not target_file.exists():
        target_file = SCRIPTS_DIR / "nolan_soviet_glitch.json"
    if not target_file.exists():
        candidates = list(SCRIPTS_DIR.glob("*soviet_glitch.json"))
        if candidates:
            target_file = candidates[0]
    if not target_file.exists():
        print(f"Error: Script file not found: {SCRIPT_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(target_file, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    print(f"Loaded script: {script_data.get('title')} ({len(scenes)} scenes)")
    print(f"Voice: {voice} (Speed: {speed}x) | Target Engine: Kokoro-82M ONNX (Local)")

    # Check Kokoro ONNX model
    onnx_path = MODEL_DIR / "kokoro-v0_19.onnx"
    voices_path = MODEL_DIR / "voices.bin"
    kokoro = None

    if onnx_path.is_file() and voices_path.is_file():
        try:
            from kokoro_onnx import Kokoro
            kokoro = Kokoro(str(onnx_path), str(voices_path))
            print("✅ Initialized Kokoro-82M ONNX local neural runtime.")
        except Exception as e:
            print(f"⚠️ Kokoro ONNX init warning: {e}. Falling back to Edge-TTS proxy.")

    raw_dir = AUDIO_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    full_text_parts = []
    durations = []
    scene_mastered_files = []

    # Synthesize individual scenes
    for scene in scenes:
        s_id = scene["scene_id"]
        text = scene["audio_text"]
        full_text_parts.append(text)

        scene_raw = raw_dir / f"scene_{s_id}_raw.wav"
        scene_mastered = AUDIO_DIR / f"scene_{s_id}.wav"
        scene_mp3 = AUDIO_DIR / f"scene_{s_id}.mp3"

        print(f"  -> Generating Scene {s_id} with voice '{voice}'...")
        if kokoro is not None:
            import soundfile as sf
            lang = "en-gb" if voice.startswith("b") else "en-us"
            samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
            sf.write(str(scene_raw), samples, sr)
            master_audio(scene_raw, scene_mastered)
            master_audio(scene_raw, scene_mp3)
            info = sf.info(str(scene_mastered))
            dur = float(info.duration)
        else:
            asyncio.run(generate_scene_edge_fallback(text, scene_mp3))
            dur = float(scene.get("estimated_duration_sec", 12.0))

        durations.append(dur)
        scene_mastered_files.append(scene_mastered)
        print(f"     [OK] Scene {s_id}: {dur:.2f}s | Saved: {scene_mastered.name}")

    # Synthesize Full Combined Intro
    full_text = " ".join(full_text_parts)
    full_raw = raw_dir / f"pilot_{voice}_full_raw.wav"
    full_wav = AUDIO_DIR / f"pilot_{voice}_mastered.wav"
    full_mp3 = AUDIO_DIR / f"pilot_{voice}_mastered.mp3"
    full_srt = SUBS_DIR / f"pilot_{voice}_full.srt"

    # Also keep standard generic filenames for downstream editors
    generic_wav = AUDIO_DIR / "pilot_intro_mastered.wav"
    generic_mp3 = AUDIO_DIR / "pilot_intro_full.mp3"
    generic_srt = SUBS_DIR / "pilot_intro_full.srt"

    print(f"\n  -> Synthesizing and mastering full documentary intro ({voice})...")
    if kokoro is not None:
        import soundfile as sf
        lang = "en-gb" if voice.startswith("b") else "en-us"
        full_samples, full_sr = kokoro.create(full_text, voice=voice, speed=speed, lang=lang)
        sf.write(str(full_raw), full_samples, full_sr)
        master_audio(full_raw, full_wav)
        master_audio(full_raw, full_mp3)
        shutil.copy2(full_wav, generic_wav)
        shutil.copy2(full_mp3, generic_mp3)
    else:
        asyncio.run(generate_scene_edge_fallback(full_text, full_mp3))
        shutil.copy2(full_mp3, generic_mp3)

    # Subtitles
    srt_content = generate_srt(scenes, durations, full_srt)
    shutil.copy2(full_srt, generic_srt)

    print("\n🎉 Broadcast Narration Pipeline Complete!")
    print(f"   Voice: {voice}")
    print(f"   Master WAV (24-bit 48kHz): {full_wav}")
    print(f"   Master MP3 (320kbps): {full_mp3}")
    print(f"   Subtitles SRT: {full_srt}")
    print(f"   Total Duration: {sum(durations):.2f}s across {len(scenes)} scenes")

    return {
        "voice": voice,
        "wav": str(full_wav),
        "mp3": str(full_mp3),
        "srt": str(full_srt),
        "durations": durations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Pilot Audio Engine")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help=f"Kokoro voice ID (default: {DEFAULT_VOICE}, or bm_lewis, am_adam)")
    parser.add_argument("--speed", type=float, default=DEFAULT_SPEED, help=f"Playback speed (default: {DEFAULT_SPEED})")
    args = parser.parse_args()

    run_pipeline(voice=args.voice, speed=args.speed)


if __name__ == "__main__":
    main()
