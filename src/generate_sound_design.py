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
    try:
        import numpy as np

        total_samples = int(sample_rate * total_duration)
        t = np.linspace(0, total_duration, total_samples, endpoint=False, dtype=np.float32)
        soundscape = np.zeros(total_samples, dtype=np.float32)

        if total_duration <= 45.0:
            t_scene1_end = 16.85
            t_scene2_end = 27.72
            t_silence_start = 35.80
            t_click = 37.00

            # Scene 1: Braam + 55Hz Hum + Alarm
            mask1 = t < t_scene1_end
            t1 = t[mask1]
            braam_mask = t1 < 1.2
            phase_boom = 2 * np.pi * (36.0 * t1[braam_mask] + (49.0 / -3.5) * (np.exp(-3.5 * t1[braam_mask]) - 1.0))
            env_boom = np.exp(-2.2 * t1[braam_mask])
            raw_braam = 0.40 * np.sin(phase_boom) + 0.20 * np.sin(2.0 * phase_boom) + 0.08 * np.sin(3.0 * phase_boom)
            braam_vals = env_boom * np.tanh(raw_braam * 1.6)

            hum = 0.12 * np.sin(2 * np.pi * 55 * t1) + 0.04 * np.sin(2 * np.pi * 110 * t1)
            cycle_t = t1 % 1.8
            alarm_env = np.where(cycle_t < 0.8, np.exp(-6.0 * (cycle_t - 0.2) ** 2), 0.0)
            alarm = 0.10 * alarm_env * np.sin(2 * np.pi * 780 * t1)
            val1 = hum + alarm
            val1[braam_mask] += braam_vals
            soundscape[mask1] = val1

            # Scene 2: Heartbeat + Clock Ticking
            mask2 = (t >= t_scene1_end) & (t < t_scene2_end)
            t2 = t[mask2]
            t_rel2 = t2 - t_scene1_end
            rumble = 0.14 * np.sin(2 * np.pi * 45 * t2)
            cycle_hb = t_rel2 % 0.86
            lub_env = np.where(cycle_hb < 0.2, np.exp(-80.0 * (cycle_hb - 0.08) ** 2), 0.0)
            lub = 0.25 * lub_env * np.sin(2 * np.pi * 58 * t2)
            dub_env = np.where(cycle_hb < 0.35, np.exp(-90.0 * (cycle_hb - 0.24) ** 2), 0.0)
            dub = 0.20 * dub_env * np.sin(2 * np.pi * 50 * t2)
            tick_env = np.where((cycle_hb > 0.45) & (cycle_hb < 0.55), np.exp(-400.0 * (cycle_hb - 0.50) ** 2), 0.0)
            tick = 0.08 * tick_env * (np.sin(2 * np.pi * 2400 * t2) + np.sin(2 * np.pi * 4800 * t2))
            soundscape[mask2] = rumble + lub + dub + tick

            # Scene 3: High Tension -> Silence -> Click
            mask3 = t >= t_scene2_end
            t3 = t[mask3]
            drone_mask = t3 < t_silence_start
            progress = (t3[drone_mask] - t_scene2_end) / max(0.01, (t_silence_start - t_scene2_end))
            freq = 55 + progress * 70
            drone = (0.10 + 0.08 * progress) * np.sin(2 * np.pi * freq * t3[drone_mask])

            silence_mask = (t3 >= t_silence_start) & (t3 < t_click)
            breath = 0.015 * np.sin(2 * np.pi * 40 * t3[silence_mask])

            click_mask = (t3 >= t_click) & (t3 < t_click + 0.08)
            t_rel_click = t3[click_mask] - t_click
            click_env = np.exp(-250.0 * t_rel_click)
            click = 0.35 * click_env * (np.sin(2 * np.pi * 1200 * t3[click_mask]) + np.sin(2 * np.pi * 3200 * t3[click_mask]))

            val3 = np.zeros_like(t3)
            val3[drone_mask] = drone
            val3[silence_mask] = breath
            val3[click_mask] = click
            soundscape[mask3] = val3
        else:
            # Multi-Act Documentary Mode (Continuous Sub-bass + periodic Braams + act pacing)
            # 1. Fundamental sub-electrical hum throughout
            soundscape += 0.08 * np.sin(2 * np.pi * 48.0 * t) + 0.03 * np.sin(2 * np.pi * 96.0 * t)

            # 2. Opening & Act Boundary Braams (every ~20% of duration)
            for act_idx in range(5):
                t_act_start = act_idx * (total_duration / 5.0)
                mask_b = (t >= t_act_start) & (t < t_act_start + 1.5)
                if np.any(mask_b):
                    t_b = t[mask_b] - t_act_start
                    phase_b = 2 * np.pi * (34.0 * t_b + (50.0 / -3.2) * (np.exp(-3.2 * t_b) - 1.0))
                    env_b = np.exp(-2.0 * t_b)
                    soundscape[mask_b] += env_b * np.tanh(0.35 * np.sin(phase_b) + 0.15 * np.sin(2.0 * phase_b))

            # 3. Heartbeat tension buildup during Act III and IV (40% to 80%)
            mask_hb = (t >= 0.40 * total_duration) & (t < 0.80 * total_duration)
            t_hb = t[mask_hb]
            hb_cycle = t_hb % 0.80
            lub_e = np.where(hb_cycle < 0.20, np.exp(-70.0 * (hb_cycle - 0.08) ** 2), 0.0)
            dub_e = np.where(hb_cycle < 0.35, np.exp(-80.0 * (hb_cycle - 0.24) ** 2), 0.0)
            soundscape[mask_hb] += 0.15 * lub_e * np.sin(2 * np.pi * 54 * t_hb) + 0.12 * dub_e * np.sin(2 * np.pi * 46 * t_hb)

            # 4. Act V solemn resolving rumble (80% to 100%)
            mask_v = t >= 0.80 * total_duration
            soundscape[mask_v] += 0.05 * np.sin(2 * np.pi * 36.0 * t[mask_v])

        samples_clipped = np.clip(soundscape, -1.0, 1.0)
        int_samples = (samples_clipped * 32767.0).astype(np.int16)

        output_wav.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = output_wav.with_suffix(f".tmp.{os.getpid()}")
        with wave.open(str(tmp_target), "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(int_samples.tobytes())
        tmp_target.replace(output_wav)
        logger.info(f"Synthesized procedural sound design: {output_wav.name} ({total_duration:.2f}s)")
        return
    except ImportError:
        pass

    total_samples = int(sample_rate * total_duration)
    samples = [0.0] * total_samples

    # Durations of scenes
    t_scene1_end = 16.85
    t_scene2_end = 27.72
    t_silence_start = 35.80
    t_click = 37.00

    for i in range(total_samples):
        t_val = i / sample_rate
        val = 0.0
        if t_val < t_scene1_end:
            braam = 0.0
            if t_val < 1.2:
                phase_boom = 2 * math.pi * (36.0 * t_val + (49.0 / -3.5) * (math.exp(-3.5 * t_val) - 1.0))
                env_boom = math.exp(-2.2 * t_val)
                raw_braam = 0.40 * math.sin(phase_boom) + 0.20 * math.sin(2.0 * phase_boom) + 0.08 * math.sin(3.0 * phase_boom)
                braam = env_boom * math.tanh(raw_braam * 1.6)
            hum = 0.12 * math.sin(2 * math.pi * 55 * t_val) + 0.04 * math.sin(2 * math.pi * 110 * t_val)
            cycle_t = t_val % 1.8
            alarm_env = math.exp(-6.0 * (cycle_t - 0.2)**2) if cycle_t < 0.8 else 0.0
            alarm = 0.10 * alarm_env * math.sin(2 * math.pi * 780 * t_val)
            val += hum + alarm + braam
        elif t_val < t_scene2_end:
            t_rel = t_val - t_scene1_end
            rumble = 0.14 * math.sin(2 * math.pi * 45 * t_val)
            cycle_hb = t_rel % 0.86
            lub_env = math.exp(-80.0 * (cycle_hb - 0.08)**2) if cycle_hb < 0.2 else 0.0
            lub = 0.25 * lub_env * math.sin(2 * math.pi * 58 * t_val)
            dub_env = math.exp(-90.0 * (cycle_hb - 0.24)**2) if cycle_hb < 0.35 else 0.0
            dub = 0.20 * dub_env * math.sin(2 * math.pi * 50 * t_val)
            tick_env = math.exp(-400.0 * (cycle_hb - 0.50)**2) if 0.45 < cycle_hb < 0.55 else 0.0
            tick = 0.08 * tick_env * (math.sin(2 * math.pi * 2400 * t_val) + math.sin(2 * math.pi * 4800 * t_val))
            val += rumble + lub + dub + tick
        else:
            if t_val < t_silence_start:
                progress = (t_val - t_scene2_end) / max(0.01, (t_silence_start - t_scene2_end))
                freq = 55 + progress * 70
                drone = (0.10 + 0.08 * progress) * math.sin(2 * math.pi * freq * t_val)
                val += drone
            elif t_val >= t_silence_start and t_val < t_click:
                val += 0.015 * math.sin(2 * math.pi * 40 * t_val)
            else:
                t_rel_click = t_val - t_click
                if 0 <= t_rel_click < 0.08:
                    click_env = math.exp(-250.0 * t_rel_click)
                    click = 0.35 * click_env * (math.sin(2 * math.pi * 1200 * t_val) + math.sin(2 * math.pi * 3200 * t_val))
                    val += click

        val = max(-1.0, min(1.0, val))
        samples[i] = val

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp_target = output_wav.with_suffix(f".tmp.{os.getpid()}")
    with wave.open(str(tmp_target), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        raw_bytes = bytearray()
        for s in samples:
            int_val = int(s * 32767.0)
            raw_bytes.extend(struct.pack("<h", int_val))
        wav_file.writeframes(raw_bytes)
    tmp_target.replace(output_wav)
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
