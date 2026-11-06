#!/usr/bin/env python3
"""DarkFactory Pilot Audio Engine.

Generates high-definition neural narration for the pilot documentary using
Microsoft Edge TTS (Christopher Neural - authoritative documentary voice),
along with exact-timed SRT subtitles.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Force UTF-8 on Windows stdout/stderr (ADR-01)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import edge_tts

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "data" / "scripts"
AUDIO_DIR = PROJECT_ROOT / "data" / "audio"
SUBS_DIR = PROJECT_ROOT / "data" / "subtitles"

SCRIPT_FILE = SCRIPTS_DIR / "pilot_soviet_glitch.json"
VOICE = "en-US-ChristopherNeural"


async def generate_scene_audio(text: str, output_mp3: Path) -> bytes:
    """Generate audio bytes and save to MP3."""
    comm = edge_tts.Communicate(text, VOICE, rate="-3%", pitch="-1Hz")
    audio_data = bytearray()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
    with open(output_mp3, "wb") as f:
        f.write(audio_data)
    return bytes(audio_data)


async def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SUBS_DIR.mkdir(parents=True, exist_ok=True)

    if not SCRIPT_FILE.exists():
        print(f"Error: Script file not found: {SCRIPT_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    print(f"Loaded script: {script_data.get('title')} ({len(scenes)} scenes)")

    full_text_parts = []
    # Generate each scene audio individually
    for scene in scenes:
        s_id = scene["scene_id"]
        text = scene["audio_text"]
        full_text_parts.append(text)
        scene_mp3 = AUDIO_DIR / f"scene_{s_id}.mp3"
        print(f"  -> Generating Scene {s_id} audio...")
        data = await generate_scene_audio(text, scene_mp3)
        print(f"     Saved: {scene_mp3.name} ({len(data)} bytes)")

    # Now generate the combined intro with subtitle alignment
    full_text = " ".join(full_text_parts)
    full_mp3 = AUDIO_DIR / "pilot_intro_full.mp3"
    full_srt = SUBS_DIR / "pilot_intro_full.srt"

    print(f"  -> Generating combined pilot intro audio and subtitles...")
    comm = edge_tts.Communicate(full_text, VOICE, rate="-3%", pitch="-1Hz")
    submaker = edge_tts.SubMaker()
    full_audio = bytearray()

    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            full_audio.extend(chunk["data"])
        elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
            submaker.feed(chunk)

    with open(full_mp3, "wb") as f:
        f.write(full_audio)

    srt_content = submaker.get_srt()
    with open(full_srt, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"✅ Success!")
    print(f"   Audio MP3: {full_mp3} ({len(full_audio)} bytes)")
    print(f"   Subtitles: {full_srt} ({len(srt_content)} chars)")
    print("\n--- Generated Subtitles Preview ---")
    print(srt_content.strip())


if __name__ == "__main__":
    asyncio.run(main())
