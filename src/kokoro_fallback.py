#!/usr/bin/env python3
"""DarkFactory Kokoro-82M TTS Local Fallback Engine.

Provides zero-cost, local CPU-based neural voice narration with acting-style
mapping from CosyVoice instruct directives to Kokoro voices and pacing factors.
Falls back seamlessly to Edge-TTS ChristopherNeural if Kokoro-ONNX weights are not yet cached.
"""
import argparse
import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("KokoroFallback")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
AUDIO_DIR = DATA_DIR / "audio"
RAW_AUDIO_DIR = AUDIO_DIR / "raw"

# Voice & Pacing Profile Mapping for Documentary Production
# Maps CosyVoice instruct keywords to (Kokoro Voice ID, Speed Rate, Edge-TTS fallback voice)
INSTRUCT_PROFILE_MAP = [
    {
        "keywords": ["urgent", "urgency", "mounting dread", "alarm", "crisis"],
        "voice": "bm_lewis",
        "speed": 1.02,
        "pitch": "-1Hz",
        "edge_fallback": "en-US-ChristopherNeural",
        "style_desc": "High tension, mounting dread, articulate dramatic urgency (Lewis)",
    },
    {
        "keywords": ["grim", "somber", "heavy", "existential", "tragic", "grave"],
        "voice": "bm_george",
        "speed": 0.96,
        "pitch": "-2Hz",
        "edge_fallback": "en-US-EricNeural",
        "style_desc": "Somber, heavy existential baritone, historical gravitas (George)",
    },
    {
        "keywords": ["suspense", "hushed", "mystery", "cliffhanger", "dilemma"],
        "voice": "bm_george",
        "speed": 0.94,
        "pitch": "-1Hz",
        "edge_fallback": "en-US-ChristopherNeural",
        "style_desc": "Intense cinematic suspense, hushed dramatic delivery (George)",
    },
    {
        "keywords": ["documentary", "authoritative", "baritone", "netflix", "bbc", "cadence", "nolan"],
        "voice": "bm_george",
        "speed": 0.98,
        "pitch": "-1Hz",
        "edge_fallback": "en-US-ChristopherNeural",
        "style_desc": "Authoritative historical BBC documentary narrator (George)",
    },
    {
        "keywords": ["american", "commercial", "fast", "modern"],
        "voice": "am_adam",
        "speed": 1.00,
        "pitch": "0Hz",
        "edge_fallback": "en-US-ChristopherNeural",
        "style_desc": "Modern energetic American narrator (Adam)",
    },
]

DEFAULT_VOICE = "bm_george"
DEFAULT_SPEED = 0.98


class KokoroNarrator:
    """Local TTS Narrator with acting direction mapping for Kokoro-82M."""

    def __init__(self, model_path: Optional[Path] = None, voices_path: Optional[Path] = None):
        if model_path is None:
            candidates = [
                PROJECT_ROOT / "data" / "models" / "kokoro" / "kokoro-v0_19.onnx",
                PROJECT_ROOT.parent / "data" / "models" / "kokoro" / "kokoro-v0_19.onnx",
                Path(r"C:\Users\WDAGUtilityAccount\Downloads\Nova pasta\data\models\kokoro\kokoro-v0_19.onnx"),
            ]
            for c in candidates:
                if c.is_file():
                    model_path = c
                    break
        if voices_path is None:
            candidates = [
                PROJECT_ROOT / "data" / "models" / "kokoro" / "voices.bin",
                PROJECT_ROOT.parent / "data" / "models" / "kokoro" / "voices.bin",
                Path(r"C:\Users\WDAGUtilityAccount\Downloads\Nova pasta\data\models\kokoro\voices.bin"),
            ]
            for c in candidates:
                if c.is_file():
                    voices_path = c
                    break

        self.model_path = model_path
        self.voices_path = voices_path
        self.kokoro_instance = None
        self._init_kokoro()

    def _init_kokoro(self) -> None:
        """Attempt to initialize Kokoro-ONNX runtime if available."""
        try:
            from kokoro_onnx import Kokoro  # type: ignore

            if self.model_path and self.model_path.is_file() and self.voices_path and self.voices_path.is_file():
                self.kokoro_instance = Kokoro(str(self.model_path), str(self.voices_path))
                logger.info(f"Kokoro-82M ONNX initialized with model: {self.model_path.name}")
            else:
                logger.debug("Kokoro-82M model files not specified or not found on disk.")
        except ImportError:
            logger.debug("kokoro-onnx package not installed. Edge-TTS local proxy ready.")
        except Exception as e:
            logger.warning(f"Could not load Kokoro-ONNX: {e}")

    @staticmethod
    def map_instruct_to_voice_profile(instruct_text: str) -> Dict[str, Any]:
        """Maps natural language acting instructions to concrete voice parameters."""
        instruct_lower = (instruct_text or "").lower()

        best_match = None
        max_matches = 0

        for profile in INSTRUCT_PROFILE_MAP:
            matched_count = sum(1 for kw in profile["keywords"] if kw in instruct_lower)
            if matched_count > max_matches:
                max_matches = matched_count
                best_match = profile

        if best_match and max_matches > 0:
            return {
                "voice": best_match["voice"],
                "speed": best_match["speed"],
                "pitch": best_match["pitch"],
                "edge_fallback": best_match["edge_fallback"],
                "matched_style": best_match["style_desc"],
            }

        return {
            "voice": DEFAULT_VOICE,
            "speed": DEFAULT_SPEED,
            "pitch": "-1Hz",
            "edge_fallback": "en-US-ChristopherNeural",
            "matched_style": "Default cinematic documentary narrator",
        }

    async def _synthesize_edge_fallback(
        self, text: str, voice_profile: Dict[str, Any], output_path: Path
    ) -> bool:
        """Synthesizes high-fidelity voice using Edge-TTS as reliable local proxy."""
        import edge_tts  # type: ignore

        rate_pct = f"{int((voice_profile['speed'] - 1.0) * 100):+d}%"
        pitch_str = voice_profile.get("pitch", "-1Hz")
        voice_id = voice_profile.get("edge_fallback", "en-US-ChristopherNeural")

        logger.info(f"Synthesizing via Edge-TTS proxy ({voice_id}, rate={rate_pct}, pitch={pitch_str})...")
        comm = edge_tts.Communicate(text, voice_id, rate=rate_pct, pitch=pitch_str)
        audio_buffer = bytearray()

        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        if not audio_buffer:
            logger.error("Empty audio buffer received from TTS generator.")
            return False

        # ADR-02: Write to .tmp and atomically replace
        tmp_target = output_path.with_suffix(f".tmp.{os.getpid()}")
        with open(tmp_target, "wb") as f:
            f.write(audio_buffer)
        tmp_target.replace(output_path)

        logger.info(f"Saved audio ({len(audio_buffer)} bytes) to: {output_path.name}")
        return True

    def synthesize_scene(
        self,
        scene_id: int,
        tts_text: str,
        instruct_text: str = "",
        output_file: Optional[Path] = None,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
    ) -> bool:
        """Generate audio for a single documentary scene."""
        RAW_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        dest_path = output_file or (RAW_AUDIO_DIR / f"scene_{scene_id}.wav")

        profile = self.map_instruct_to_voice_profile(instruct_text)
        chosen_voice = voice or profile["voice"]
        chosen_speed = speed if speed is not None else profile["speed"]

        logger.info(
            f"Scene {scene_id} Direction: '{instruct_text[:60]}...' -> Profile: {profile['matched_style']} "
            f"[Voice: {chosen_voice} | Speed: {chosen_speed}x]"
        )

        # 1. Try native Kokoro-ONNX if instance is active
        if self.kokoro_instance is not None:
            try:
                import soundfile as sf  # type: ignore

                lang = "en-gb" if chosen_voice.startswith("b") else "en-us"
                samples, sample_rate = self.kokoro_instance.create(
                    tts_text, voice=chosen_voice, speed=chosen_speed, lang=lang
                )
                tmp_target = dest_path.with_suffix(f".tmp.{os.getpid()}")
                sf.write(str(tmp_target), samples, sample_rate)
                tmp_target.replace(dest_path)
                logger.info(f"Generated via Kokoro-82M ({chosen_voice}): {dest_path.name}")
                return True
            except Exception as e:
                logger.warning(f"Kokoro synthesis failed, falling back to proxy: {e}")

        # 2. Fallback to Edge-TTS neural proxy
        try:
            # If output is .wav, edge_tts outputs mp3 format by default; we save as .mp3 or let ffmpeg transcode
            if dest_path.suffix.lower() == ".wav":
                temp_mp3 = dest_path.with_suffix(".mp3")
                proxy_profile = dict(profile)
                if speed is not None:
                    proxy_profile["speed"] = chosen_speed
                success = asyncio.run(self._synthesize_edge_fallback(tts_text, proxy_profile, temp_mp3))
                if success:
                    # Convert MP3 to 16-bit 44.1kHz WAV if requested
                    self._transcode_to_wav(temp_mp3, dest_path)
                    if temp_mp3.exists() and temp_mp3 != dest_path:
                        try:
                            temp_mp3.unlink()
                        except OSError:
                            pass
                    return True
            else:
                proxy_profile = dict(profile)
                if speed is not None:
                    proxy_profile["speed"] = chosen_speed
                return asyncio.run(self._synthesize_edge_fallback(tts_text, proxy_profile, dest_path))
        except Exception as e:
            logger.error(f"TTS synthesis failed for scene {scene_id}: {e}")
            return False

        return False

    def _transcode_to_wav(self, input_audio: Path, output_wav: Path) -> None:
        """Converts any audio file to broadcast standard 44.1kHz 16-bit PCM WAV."""
        import subprocess
        import shutil

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            candidates = [
                Path(r"C:\Users\WDAGUtilityAccount\Downloads\Nova pasta\stockcont\venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"),
                Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
            ]
            for c in candidates:
                if c.is_file():
                    ffmpeg_bin = str(c)
                    break

        if ffmpeg_bin:
            cmd = [
                ffmpeg_bin, "-y",
                "-i", str(input_audio),
                "-ar", "44100",
                "-ac", "2",
                "-c:a", "pcm_s16le",
                str(output_wav)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Direct copy if no ffmpeg available
            shutil.copy2(input_audio, output_wav)

    def process_script(
        self, script_path: Path, voice: Optional[str] = None, speed: Optional[float] = None
    ) -> bool:
        """Processes all scenes in a script JSON file and generates raw audio."""
        if not script_path.exists():
            logger.error(f"Script file not found: {script_path}")
            return False

        with open(script_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scenes = data.get("scenes", [])
        logger.info(f"Processing {len(scenes)} scenes from {script_path.name}...")
        all_ok = True

        for s in scenes:
            s_id = s.get("scene_id", 1)
            text = s.get("audio_text", "")
            instruct = s.get("cosyvoice_instruct", "")
            dest = RAW_AUDIO_DIR / f"scene_{s_id}.wav"
            ok = self.synthesize_scene(
                scene_id=s_id,
                tts_text=text,
                instruct_text=instruct,
                output_file=dest,
                voice=voice,
                speed=speed,
            )
            if not ok:
                all_ok = False

        return all_ok


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Kokoro-82M TTS Local Fallback")
    parser.add_argument("--script", type=str, default=None, help="Process entire script JSON")
    parser.add_argument("--scene", type=int, default=1, help="Scene ID")
    parser.add_argument("--text", type=str, default="", help="Narration text")
    parser.add_argument("--instruct", type=str, default="", help="Acting instruction text")
    parser.add_argument("--voice", type=str, default=None, help=f"Kokoro voice ID (default: {DEFAULT_VOICE}, or bm_lewis, am_adam, etc.)")
    parser.add_argument("--speed", type=float, default=None, help=f"Playback speed factor (default: {DEFAULT_SPEED})")
    parser.add_argument("--output", type=str, default=None, help="Output audio path (.wav / .mp3)")
    args = parser.parse_args()

    narrator = KokoroNarrator()

    if args.script:
        script_file = Path(args.script)
        success = narrator.process_script(script_file, voice=args.voice, speed=args.speed)
        if success:
            print("\n🎉 All scenes successfully narrated via local TTS engine!")
            sys.exit(0)
        else:
            print("\n❌ Errors occurred during batch script narration.", file=sys.stderr)
            sys.exit(1)

    if not args.text:
        # Default test phrase
        sample_text = (
            "At 12:15 AM on September 26, 1983, a red siren illuminated a top-secret Soviet bunker outside Moscow. "
            "The radar screens confirmed what every officer dreaded: five American nuclear warheads were already in the air."
        )
        sample_instruct = "Speak with controlled urgency and mounting dread, deep authoritative baritone."
        dest = RAW_AUDIO_DIR / "scene_1.wav"
        print(f"No text supplied. Running verification test on Scene 1 (Voice: {args.voice or DEFAULT_VOICE})...")
        ok = narrator.synthesize_scene(1, sample_text, sample_instruct, dest, voice=args.voice, speed=args.speed)
        if ok:
            print(f"✅ Scene 1 test audio successfully created at: {dest}")
        sys.exit(0 if ok else 1)

    dest_file = Path(args.output) if args.output else None
    ok = narrator.synthesize_scene(
        args.scene, args.text, args.instruct, dest_file, voice=args.voice, speed=args.speed
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
