#!/usr/bin/env python3
"""DarkFactory Procedural Cinematic Sound Design Generator.

Generates historical Cold War documentary sound design:
- Scene 1: 50Hz sub-electrical drone + muted periodic alarm pulse
- Scene 2: Sub-bass heartbeat thumps (lub-dub) + mechanical clock ticking
- Scene 3: Rising ambient tension drone -> Sudden dead silence -> Heavy switch click
- Blends background sound design with voiceover (-18dB under speech, ducked).
"""
import logging
import math
import os
import struct
import subprocess
import sys
import wave
from pathlib import Path

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SoundDesign")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
AUDIO_DIR = DATA_DIR / "audio"
MASTERED_DIR = AUDIO_DIR / "mastered"


def get_ffmpeg_binary() -> str:
    """Find a valid ffmpeg executable on the system or in the darkfactory venv."""
    import shutil
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
    raise FileNotFoundError("FFmpeg binary not found.")


def generate_procedural_soundscape(output_wav: Path, total_duration: float = 39.65) -> None:
    """Synthesize custom PCM 16-bit 44.1kHz audio sound design layer mathematically."""
    sample_rate = 44100
    total_samples = int(sample_rate * total_duration)
    samples = [0.0] * total_samples

    # Durations of scenes
    t_scene1_end = 16.85
    t_scene2_end = 27.72
    t_silence_start = 35.80  # Sudden drop in room noise before "Petrov decided..."
    t_click = 37.00          # Switch click

    for i in range(total_samples):
        t = i / sample_rate
        val = 0.0

        # === SCENE 1: Bunker Alarm, Electrical Hum & Opening Braam Impact ===
        if t < t_scene1_end:
            # Cinematic Sub-Bass Braam / Low Boom Impact (t = 0.0 to 1.2s)
            braam = 0.0
            if t < 1.2:
                # Frequency sweeps exponentially from 85Hz down to 36Hz
                phase_boom = 2 * math.pi * (36.0 * t + (49.0 / -3.5) * (math.exp(-3.5 * t) - 1.0))
                env_boom = math.exp(-2.2 * t)
                # Fundamental + 2nd harmonic + 3rd harmonic with analog tape saturation (tanh)
                raw_braam = 0.40 * math.sin(phase_boom) + 0.20 * math.sin(2.0 * phase_boom) + 0.08 * math.sin(3.0 * phase_boom)
                braam = env_boom * math.tanh(raw_braam * 1.6)

            # 55Hz industrial bunker electrical hum + 110Hz harmonic
            hum = 0.12 * math.sin(2 * math.pi * 55 * t) + 0.04 * math.sin(2 * math.pi * 110 * t)
            # Muted recurring alarm pulse (sine 750Hz with 1.8s period, soft attack/decay)
            cycle_t = t % 1.8
            alarm_env = math.exp(-6.0 * (cycle_t - 0.2)**2) if cycle_t < 0.8 else 0.0
            alarm = 0.10 * alarm_env * math.sin(2 * math.pi * 780 * t)
            val += hum + alarm + braam

        # === SCENE 2: Petrov's Panic (Heartbeat & Clock Ticking) ===
        elif t < t_scene2_end:
            t_rel = t - t_scene1_end
            # Dark sub-bass rumble (45Hz)
            rumble = 0.14 * math.sin(2 * math.pi * 45 * t)
            # Heartbeat (lub-dub at ~70 BPM = every 0.86s)
            cycle_hb = t_rel % 0.86
            # "Lub" (at 0.05s, 60Hz)
            lub_env = math.exp(-80.0 * (cycle_hb - 0.08)**2) if cycle_hb < 0.2 else 0.0
            lub = 0.25 * lub_env * math.sin(2 * math.pi * 58 * t)
            # "Dub" (at 0.22s, 50Hz)
            dub_env = math.exp(-90.0 * (cycle_hb - 0.24)**2) if cycle_hb < 0.35 else 0.0
            dub = 0.20 * dub_env * math.sin(2 * math.pi * 50 * t)
            # Mechanical clock tick (sharp click at 0.5s of cycle)
            tick_env = math.exp(-400.0 * (cycle_hb - 0.50)**2) if 0.45 < cycle_hb < 0.55 else 0.0
            tick = 0.08 * tick_env * (math.sin(2 * math.pi * 2400 * t) + math.sin(2 * math.pi * 4800 * t))
            val += rumble + lub + dub + tick

        # === SCENE 3: High Tension -> Dead Silence -> Click ===
        else:
            if t < t_silence_start:
                # Rising Shepard-style tension drone (60Hz to 180Hz)
                progress = (t - t_scene2_end) / (t_silence_start - t_scene2_end)
                freq = 55 + progress * 70
                drone = (0.10 + 0.08 * progress) * math.sin(2 * math.pi * freq * t)
                val += drone
            elif t >= t_silence_start and t < t_click:
                # Eerie near-silence (subtle low breath at -36dB)
                val += 0.015 * math.sin(2 * math.pi * 40 * t)
            else:
                # Heavy industrial toggle switch click at t_click
                t_rel_click = t - t_click
                if 0 <= t_rel_click < 0.08:
                    click_env = math.exp(-250.0 * t_rel_click)
                    click = 0.35 * click_env * (math.sin(2 * math.pi * 1200 * t) + math.sin(2 * math.pi * 3200 * t))
                    val += click

        # Clamp between -1.0 and 1.0
        val = max(-1.0, min(1.0, val))
        samples[i] = val

    # Write 16-bit PCM WAV
    with wave.open(str(output_wav), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        raw_bytes = bytearray()
        for s in samples:
            int_val = int(s * 32767.0)
            raw_bytes.extend(struct.pack("<h", int_val))
        wav_file.writeframes(raw_bytes)

    logger.info(f"Synthesized procedural sound design: {output_wav.name} ({total_duration:.2f}s)")


def mix_voice_and_sound_design(ffmpeg_bin: str, voice_file: Path, sound_design_file: Path, output_file: Path) -> bool:
    """Mix voiceover and background sound design with automatic ducking/balance.
    Sound design is blended at -16dB under dialogue for cinema clarity.
    """
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", str(voice_file),
        "-i", str(sound_design_file),
        "-filter_complex",
        "[1:a]volume=0.45[sfx];"
        "[0:a][sfx]amix=inputs=2:duration=first:dropout_transition=2,"
        "loudnorm=I=-14:TP=-1.0:LRA=7[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        "-ar", "44100",
        str(output_file)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        logger.error(f"Mixing failed: {res.stderr}")
        return False
    logger.info(f"Final mixed audio created: {output_file.name}")
    return True


def main() -> None:
    ffmpeg_bin = get_ffmpeg_binary()
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    MASTERED_DIR.mkdir(parents=True, exist_ok=True)

    voice_path = MASTERED_DIR / "pilot_intro_full_mastered.mp3"
    if not voice_path.exists():
        # Fallback to pilot_intro_full.mp3
        voice_path = AUDIO_DIR / "pilot_intro_full.mp3"

    sound_design_wav = AUDIO_DIR / "sound_design_layer.wav"
    final_mix_mp3 = AUDIO_DIR / "pilot_final_audio_mix.mp3"

    logger.info("Generating procedural sound design layer...")
    generate_procedural_soundscape(sound_design_wav, total_duration=39.65)

    logger.info("Mixing voiceover with sound design...")
    success = mix_voice_and_sound_design(ffmpeg_bin, voice_path, sound_design_wav, final_mix_mp3)
    if success:
        print(f"\n✅ Sound Design Generated & Mixed Successfully!")
        print(f"   Sound Design Layer: {sound_design_wav}")
        print(f"   Final Mastered Mix: {final_mix_mp3}")


if __name__ == "__main__":
    main()
