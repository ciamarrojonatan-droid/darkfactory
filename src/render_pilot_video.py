#!/usr/bin/env python3
"""DarkFactory Cinematic Video Renderer & Assembly Engine.

Renders and stitches the complete pilot documentary video:
1. Ingests video clips (scene_1.mp4, scene_2.mp4, scene_3.mp4) from data/broll/.
2. If only images exist (scene_1.jpg/png), generates an Anamorphic Ken-Burns camera move
   (slow cinematic push-in/drift, 35mm grain, color grading).
3. Applies smooth micro-transitions (0.15s dip-to-black cuts between scenes, 0.35s opening fade-in, 0.40s closing fade-out).
4. Employs a Cold War / Kodak 2383 historical documentary 3D LUT for cinematic grade (removes AI glossiness).
5. Adds 2.39:1 anamorphic cinema letterboxing (140px matte top and bottom).
6. Syncs scene visual durations frame-accurately with audio timestamps.
7. Binds mastered audio + procedural sound design mix (with opening sub-bass braam impact).
8. Burns in broadcast-standard documentary subtitles inside the lower letterbox matte.
9. Outputs final master to data/output/the_1983_soviet_glitch_final_1080p.mp4.
"""
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Force UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VideoRenderer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
AUDIO_DIR = DATA_DIR / "audio"
MASTERED_DIR = AUDIO_DIR / "mastered"
BROLL_DIR = DATA_DIR / "broll"
OUTPUT_DIR = DATA_DIR / "output"
SUBS_DIR = DATA_DIR / "subtitles"
LUTS_DIR = DATA_DIR / "luts"


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
    raise FileNotFoundError("FFmpeg binary not found.")


def ensure_cinematic_lut() -> Path:
    """Ensure the historical documentary 3D LUT exists, generating if needed."""
    lut_path = LUTS_DIR / "cold_war_documentary.cube"
    if not lut_path.exists():
        try:
            from generate_cinematic_lut import create_historical_documentary_lut
            create_historical_documentary_lut(lut_path)
            logger.info(f"Generated missing 3D LUT at {lut_path}")
        except Exception as e:
            logger.warning(f"Could not auto-generate 3D LUT: {e}")
    return lut_path


def get_audio_duration(ffmpeg_bin: str, file_path: Path) -> float:
    """Probe audio duration in seconds."""
    cmd = [ffmpeg_bin, "-i", str(file_path), "-f", "null", "-"]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                part = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = part.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
            except Exception:
                break
    return 0.0


def create_procedural_broll_image(
    image_path: Path,
    scene_id: int,
    scene_title: str,
    scene_info: Optional[Dict[str, Any]] = None,
) -> None:
    """Generates an atmospheric dark Cold War documentary plate with tactical grid and telemetry."""
    from PIL import Image, ImageDraw

    width, height = 1920, 1080
    act_num = scene_info.get("act_number", 1) if scene_info else 1
    act_title = scene_info.get("act_title", "DARKFACTORY") if scene_info else "DARKFACTORY"
    style_type = scene_info.get("visual_style_type", "HERO_AI_DUAL_SHOT") if scene_info else "HERO_AI_DUAL_SHOT"
    ts_marker = scene_info.get("timestamp_marker", f"SCENE 0{scene_id}") if scene_info else f"SCENE 0{scene_id}"

    # Palette selection based on act and mood
    if act_num in (1, 3):  # Extreme tension
        bg_color = (12, 16, 24)
        accent_color = (239, 68, 68)  # Crimson
        secondary_color = (56, 189, 248)  # Tactical cyan
    elif act_num == 4:  # Climax zero point
        bg_color = (8, 10, 15)
        accent_color = (245, 158, 11)  # Amber
        secondary_color = (239, 68, 68)
    else:  # Genesis & Aftermath
        bg_color = (11, 15, 20)
        accent_color = (56, 189, 248)  # Cold War Cyan
        secondary_color = (245, 158, 11)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Tactical grid
    for x in range(0, width, 120):
        draw.line([(x, 0), (x, height)], fill=(24, 32, 45), width=1)
    for y in range(0, height, 120):
        draw.line([(0, y), (width, y)], fill=(24, 32, 45), width=1)

    # Outer border & crosshairs
    margin = 80
    draw.rectangle([margin, margin, width - margin, height - margin], outline=(40, 50, 70), width=2)

    # Corner brackets
    for cx, cy in [(margin, margin), (width - margin, margin), (margin, height - margin), (width - margin, height - margin)]:
        draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=accent_color)

    # Headers & Telemetry
    draw.text((margin + 30, margin + 25), f"SOVIET AIR DEFENCE // CLASSIFIED ARCHIVE // {act_title.upper()}", fill=secondary_color)
    draw.text((margin + 30, margin + 60), f"TELEMETRY: {ts_marker.upper()}", fill=(240, 245, 250))
    draw.text((margin + 30, margin + 95), f"VISUAL CLUSTER: {style_type} [35MM ANAMORPHIC]", fill=(140, 160, 180))

    # Center dramatic focal box
    draw.rectangle([width // 2 - 250, height // 2 - 80, width // 2 + 250, height // 2 + 80], outline=accent_color, width=2)
    draw.text((width // 2, height // 2 - 20), f"DARKFACTORY SHOT 0{scene_id}", fill=accent_color, anchor="mm")
    draw.text((width // 2, height // 2 + 25), scene_title.upper()[:45], fill=(220, 230, 240), anchor="mm")

    # Bottom status
    draw.text((margin + 30, height - margin - 45), "STATUS: ARCHIVAL SYNCHRONIZATION // KODAK 2383 BLEACH BYPASS", fill=(100, 120, 140))
    draw.text((width - margin - 350, height - margin - 45), "COORDINATES: 54°54'57\"N 37°24'42\"E", fill=secondary_color)

    img.save(image_path, "JPEG", quality=95)
    logger.info(f"Generated procedural cinematic plate: {image_path.name}")


def render_scene_video(
    ffmpeg_bin: str,
    scene_id: int,
    duration: float,
    output_mp4: Path,
    is_first: bool = False,
    is_last: bool = False,
    transition_sec: float = 0.15,
    scene_info: Optional[Dict[str, Any]] = None,
) -> bool:
    """Renders a scene clip with adaptive speed-matching, overlays, and micro-transitions.

    Supports dual-shot composition for Scene 1 if Beat B video (cena 1b.mp4) is present:
    - Shot 1A (0.0 to 8.44s): Wide bunker siren (cena 1.mp4)
    - Shot 1B (8.44 to 17.89s): Macro radar display (cena 1b.mp4)
    If only one clip exists, dynamically stretches/compresses playback via setpts without ugly loops.
    """
    # Check for dual-shot B-roll composition in Scene 1
    if scene_id == 1:
        shot_1b_candidates = [
            BROLL_DIR / "cena 1b.mp4",
            BROLL_DIR / "cena_1b.mp4",
            BROLL_DIR / "scene_1b.mp4",
            BROLL_DIR / "cena 1b.mov",
            BROLL_DIR / "scene_1b.mov",
        ]
        shot_1b_src = next((c for c in shot_1b_candidates if c.is_file()), None)
        if shot_1b_src:
            t_split = 8.44
            dur_1a = t_split
            dur_1b = max(1.0, duration - t_split)
            logger.info(f"Dual-Shot B-Roll detected for Scene 1! Splitting into Shot 1A ({dur_1a:.2f}s) and Shot 1B ({dur_1b:.2f}s)")
            temp_1a = OUTPUT_DIR / "temp_scene_1a.mp4"
            temp_1b = OUTPUT_DIR / "temp_scene_1b.mp4"

            # Render Shot 1A
            ok_a = render_single_clip(
                ffmpeg_bin=ffmpeg_bin,
                clip_candidates=[BROLL_DIR / "cena 1.mp4", BROLL_DIR / "cena_1.mp4", BROLL_DIR / "scene_1.mp4"],
                fallback_img_candidates=[BROLL_DIR / "scene_1.jpg", BROLL_DIR / "scene_1.png"],
                scene_id=1,
                duration=dur_1a,
                output_mp4=temp_1a,
                is_first=is_first,
                is_last=False,
                transition_sec=transition_sec,
                scene_info=scene_info,
            )
            # Render Shot 1B
            ok_b = render_single_clip(
                ffmpeg_bin=ffmpeg_bin,
                clip_candidates=[shot_1b_src],
                fallback_img_candidates=[BROLL_DIR / "scene_1b.jpg", BROLL_DIR / "scene_1b.png"],
                scene_id=1,
                duration=dur_1b,
                output_mp4=temp_1b,
                is_first=False,
                is_last=is_last,
                transition_sec=transition_sec,
                scene_info=scene_info,
            )
            if ok_a and ok_b:
                concat_txt = OUTPUT_DIR / "scene_1_concat.txt"
                with open(concat_txt, "w", encoding="utf-8") as f:
                    f.write(f"file '{temp_1a.resolve().as_posix()}'\n")
                    f.write(f"file '{temp_1b.resolve().as_posix()}'\n")
                cmd_cat = [ffmpeg_bin, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(output_mp4)]
                res = subprocess.run(cmd_cat, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
                if temp_1a.exists(): temp_1a.unlink()
                if temp_1b.exists(): temp_1b.unlink()
                if concat_txt.exists(): concat_txt.unlink()
                if res.returncode == 0:
                    logger.info("Successfully stitched Scene 1 Dual-Shot (Shot 1A + Shot 1B)!")
                    return True

    # Standard single clip render with speed matching
    video_candidates = [
        BROLL_DIR / f"cena {scene_id}.mp4",
        BROLL_DIR / f"cena_{scene_id}.mp4",
        BROLL_DIR / f"scene_{scene_id}.mp4",
        BROLL_DIR / f"scene {scene_id}.mp4",
        BROLL_DIR / f"cena {scene_id}.mov",
        BROLL_DIR / f"scene_{scene_id}.mov",
    ]

    # Check for tactical vector maps if style is TACTICAL_MAP_MOTION
    if scene_info and scene_info.get("visual_style_type") == "TACTICAL_MAP_MOTION":
        map_cands = [
            DATA_DIR / "final" / "motion_overlays" / "maps" / "map_north_atlantic_north_atlantic_corridor.mp4",
            DATA_DIR / "final" / "motion_overlays" / "maps" / "map_europe_cold_war_europe_theater.mp4",
            DATA_DIR / "final" / "motion_overlays" / "tactical_hud_bunker_diagnostic.mp4",
        ]
        valid_map = next((m for m in map_cands if m.is_file()), None)
        if valid_map:
            video_candidates.insert(0, valid_map)

    img_candidates = [
        BROLL_DIR / f"scene_{scene_id}.jpg",
        BROLL_DIR / f"scene_{scene_id}.png",
        BROLL_DIR / f"cena_{scene_id}.jpg",
        BROLL_DIR / f"cena {scene_id}.jpg",
    ]

    ok = render_single_clip(
        ffmpeg_bin=ffmpeg_bin,
        clip_candidates=video_candidates,
        fallback_img_candidates=img_candidates,
        scene_id=scene_id,
        duration=duration,
        output_mp4=output_mp4,
        is_first=is_first,
        is_last=is_last,
        transition_sec=transition_sec,
        scene_info=scene_info,
    )
    if not ok:
        return False

    # Apply Tactical Overlay (HUD, Lower-Third, or DECLASSIFIED stamp)
    if scene_info and scene_info.get("overlay_recipe"):
        try:
            from src.video.tactical_graphics import TacticalGraphicsEngine, LowerThirdData
            tg = TacticalGraphicsEngine(default_width=1920, default_height=1080)
            overlay_cfg = scene_info["overlay_recipe"]
            template = overlay_cfg.get("template", "tactical_hud")
            temp_overlay = OUTPUT_DIR / f"temp_overlay_{scene_id}.png"

            if template == "tactical_hud":
                tg.create_tactical_hud_overlay(
                    output_png_path=temp_overlay,
                    coordinates=overlay_cfg.get("coordinates", "54°54'57\"N 37°24'42\"E"),
                    target_name=scene_info.get("timestamp_marker", "TARGET: SERPUKHOV-15 BUNKER"),
                    warning_status=overlay_cfg.get("stamp_text", "DEFCON 2 // EARLY WARNING MISSILE RADAR"),
                )
            elif template == "declassified_dossier":
                tg.create_declassified_stamp_overlay(
                    output_png_path=temp_overlay,
                    stamp_text=overlay_cfg.get("stamp_text", "TOP SECRET // DECLASSIFIED"),
                    sub_text=scene_info.get("timestamp_marker", "ARCHIVE ORDER NO. 49-B // EYES ONLY"),
                )
            elif template in ("lower_third", "blueprint_notebook", "anatomy_mechanical"):
                lt_data = overlay_cfg.get("lower_third_data", {})
                tg.create_cinematic_lower_third(
                    output_png_path=temp_overlay,
                    data=LowerThirdData(
                        title=lt_data.get("title", f"SCENE 0{scene_id}"),
                        subtitle=lt_data.get("subtitle", scene_info.get("act_title", "DARKFACTORY")),
                        coordinates=lt_data.get("coordinates", "54.9158° N, 37.4116° E"),
                        date_timestamp=lt_data.get("date_timestamp", scene_info.get("timestamp_marker", "26 SEP 1983")),
                        classification=lt_data.get("classification", "TOP SECRET // LEVEL 1 SPECIAL PROTOCOL"),
                    ),
                )

            if temp_overlay.exists():
                temp_overlaid_mp4 = OUTPUT_DIR / f"temp_ov_{scene_id}.mp4"
                ok_ov = tg.apply_overlay_to_video(
                    input_video_path=output_mp4,
                    overlay_png_path=temp_overlay,
                    output_video_path=temp_overlaid_mp4,
                    start_time_sec=0.2,
                    duration_sec=max(1.0, duration - 0.4),
                    ffmpeg_bin=ffmpeg_bin,
                )
                if ok_ov and temp_overlaid_mp4.exists():
                    shutil.move(str(temp_overlaid_mp4), str(output_mp4))
                if temp_overlay.exists():
                    temp_overlay.unlink()
        except Exception as e:
            logger.warning(f"Could not apply overlay to Scene {scene_id}: {e}")

    return True


def render_single_clip(
    ffmpeg_bin: str,
    clip_candidates: List[Path],
    fallback_img_candidates: List[Path],
    scene_id: int,
    duration: float,
    output_mp4: Path,
    is_first: bool = False,
    is_last: bool = False,
    transition_sec: float = 0.15,
    scene_info: Optional[Dict[str, Any]] = None,
) -> bool:
    """Renders a single video clip or image with adaptive speed-matching and micro-transitions."""
    video_src = next((c for c in clip_candidates if c.is_file()), None)
    actual_img = next((c for c in fallback_img_candidates if c.is_file()), None)

    if not video_src and not actual_img:
        fallback_img = BROLL_DIR / f"scene_{scene_id}.jpg"
        create_procedural_broll_image(fallback_img, scene_id, f"Scene {scene_id}", scene_info=scene_info)
        actual_img = fallback_img

    fps = 30
    total_frames = int(duration * fps)

    fade_in = 0.35 if is_first else transition_sec
    fade_out = 0.40 if is_last else transition_sec
    fade_filter = f"fade=t=in:st=0:d={fade_in:.2f},fade=t=out:st={duration - fade_out:.3f}:d={fade_out:.2f}"

    if video_src:
        # Check source duration for adaptive speed matching
        src_dur = get_audio_duration(ffmpeg_bin, video_src)
        if src_dur > 0.5:
            pts_factor = duration / src_dur
            logger.info(
                f"Adaptive Speed-Matching for Scene {scene_id}: source {src_dur:.2f}s -> target {duration:.2f}s "
                f"(playback speed: {1.0/pts_factor:.2f}x, pts_factor={pts_factor:.4f})"
            )
            speed_filter = f"setpts={pts_factor:.4f}*PTS,"
        else:
            speed_filter = ""

        logger.info(f"Using live b-roll video for Scene {scene_id}: {video_src.name} (dur: {duration:.2f}s)")
        vf_pipeline = (
            f"{speed_filter}"
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"fps={fps},"
            f"{fade_filter},"
            f"format=yuv420p"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(video_src),
            "-t", f"{duration:.3f}",
            "-vf", vf_pipeline,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-an",
            str(output_mp4)
        ]
    else:
        logger.info(f"Applying Anamorphic Ken-Burns zoom on image: {actual_img.name} (dur: {duration:.2f}s)")
        zoom_expr = "min(zoom+0.0004,1.15)"
        vf_pipeline = (
            f"scale=8000:-1,"
            f"zoompan=z='{zoom_expr}':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps},"
            f"{fade_filter},"
            f"format=yuv420p"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-loop", "1",
            "-i", str(actual_img),
            "-t", f"{duration:.3f}",
            "-vf", vf_pipeline,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "18",
            "-r", str(fps),
            "-an",
            str(output_mp4)
        ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        logger.error(f"Scene {scene_id} render failed: {res.stderr}")
        return False
    return True


def assemble_final_video(
    ffmpeg_bin: str,
    scene_videos: List[Path],
    audio_file: Path,
    srt_file: Optional[Path],
    output_video: Path,
    apply_lut: bool = True,
    apply_letterbox: bool = True,
) -> bool:
    """Concatenates scene clips, applies 3D LUT grade & 2.39:1 letterbox, burns subtitles, muxes audio."""
    concat_list = OUTPUT_DIR / "video_concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for v in scene_videos:
            f.write(f"file '{v.resolve().as_posix()}'\n")

    temp_stitched = OUTPUT_DIR / "temp_stitched.mp4"
    cmd_concat = [
        ffmpeg_bin, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(temp_stitched)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.info("Applying Historical Documentary Color Grade, 2.39:1 Cinema Letterbox & Subtitles...")
    vf_filters = []

    # 1. Historical Documentary Color Grade (3D LUT or fallback)
    if apply_lut:
        lut_path = ensure_cinematic_lut()
        if lut_path.is_file():
            lut_clean = lut_path.resolve().as_posix().replace(":", "\\:")
            vf_filters.append(f"lut3d=file='{lut_clean}'")
            logger.info("Using 3D LUT: Kodak 2383 / Cold War Bleach-Bypass profile.")
        else:
            # High-grade fallback filter chain
            fallback_grade = (
                "eq=contrast=1.10:brightness=-0.01:saturation=0.88,"
                "colorbalance=rs=-0.03:gs=0.03:bs=0.01:rh=0.03:gh=0.01:bh=-0.03"
            )
            vf_filters.append(fallback_grade)
            logger.info("Using native FFmpeg Colorbalance / Bleach-Bypass filter.")

    # 2. Cinema Letterbox (2.39:1 Anamorphic Scope = 140px black bars on 1080p canvas)
    if apply_letterbox:
        letterbox_cmd = "drawbox=x=0:y=0:w=iw:h=140:color=black:t=fill,drawbox=x=0:y=ih-140:w=iw:h=140:color=black:t=fill"
        vf_filters.append(letterbox_cmd)
        logger.info("Applied 2.39:1 Anamorphic Cinema Letterbox (140px top/bottom).")

    # 3. Subtitles burned cleanly inside the lower cinema letterbox bar
    if srt_file and srt_file.exists():
        srt_clean_path = srt_file.resolve().as_posix().replace(":", "\\:")
        # MarginV=30 centers text vertically inside the 140px bottom black bar for maximum theatrical readability
        subtitle_filter = (
            f"subtitles='{srt_clean_path}':"
            "force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,BorderStyle=1,Outline=2,"
            "Shadow=1,Alignment=2,MarginV=30'"
        )
        vf_filters.append(subtitle_filter)
        logger.info("Burning subtitles cleanly inside lower cinema letterbox matte.")

    vf_filters.append("format=yuv420p")
    vf_chain = ",".join(vf_filters)

    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", str(temp_stitched),
        "-i", str(audio_file),
        "-vf", vf_chain,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "320k",
        "-movflags", "+faststart",
        "-shortest",
        str(output_video)
    ]

    res = subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        logger.error(f"Final assembly failed: {res.stderr}")
        return False

    if temp_stitched.exists():
        temp_stitched.unlink()

    logger.info(f"✅ Final video master rendered: {output_video.name}")
    return True


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="DarkFactory Cinematic Video Renderer")
    parser.add_argument("--limit-scenes", type=int, default=0, help="Limit number of scenes to render (0 for all)")
    parser.add_argument("--teaser", action="store_true", help="Render only the 3-scene teaser")
    args, _ = parser.parse_known_args()

    BROLL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LUTS_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = get_ffmpeg_binary()
    logger.info(f"Using FFmpeg: {ffmpeg_bin}")

    # Ensure LUT is ready
    ensure_cinematic_lut()

    script_path = SCRIPTS_DIR / "pilot_soviet_glitch.json"
    if not script_path.exists():
        script_path = SCRIPTS_DIR / "nolan_soviet_glitch.json"
    if not script_path.exists():
        candidates = list(SCRIPTS_DIR.glob("*soviet_glitch.json"))
        if candidates:
            script_path = candidates[0]
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    scenes = script_data.get("scenes", [])
    if args.teaser:
        scenes = scenes[:3]
    elif args.limit_scenes > 0:
        scenes = scenes[:args.limit_scenes]

    logger.info(f"Rendering pilot documentary: {script_data.get('title')} ({len(scenes)} scenes)")

    # Discover durations from mastered audio files
    durations = []
    for s in scenes:
        s_id = s["scene_id"]
        mastered_audio = MASTERED_DIR / f"scene_{s_id}_mastered.mp3"
        if not mastered_audio.exists():
            mastered_audio = AUDIO_DIR / f"scene_{s_id}.mp3"

        if mastered_audio.exists():
            d = get_audio_duration(ffmpeg_bin, mastered_audio)
            durations.append(d)
        else:
            durations.append(s.get("estimated_duration_sec", 12.0))

    rendered_scenes = []
    num_scenes = len(scenes)
    for idx, (s, dur) in enumerate(zip(scenes, durations)):
        s_id = s["scene_id"]
        scene_mp4 = OUTPUT_DIR / f"temp_scene_{s_id}.mp4"
        is_first = (idx == 0)
        is_last = (idx == num_scenes - 1)
        logger.info(f"Rendering Scene {s_id} video track ({dur:.2f}s) [first={is_first}, last={is_last}]...")
        success = render_scene_video(
            ffmpeg_bin=ffmpeg_bin,
            scene_id=s_id,
            duration=dur,
            output_mp4=scene_mp4,
            is_first=is_first,
            is_last=is_last,
            transition_sec=0.15,
            scene_info=s,
        )
        if success:
            rendered_scenes.append(scene_mp4)

    # Select final audio mix (with sound design & opening braam)
    final_audio = AUDIO_DIR / "pilot_final_audio_mix.mp3"
    if not final_audio.exists():
        final_audio = MASTERED_DIR / "pilot_intro_full_mastered.mp3"
    if not final_audio.exists():
        final_audio = AUDIO_DIR / "pilot_intro_full.mp3"

    # Select subtitles
    subtitles_file = SUBS_DIR / "pilot_intro_mastered.srt"
    if not subtitles_file.exists():
        subtitles_file = SUBS_DIR / "pilot_intro_full.srt"

    final_output = OUTPUT_DIR / "the_1983_soviet_glitch_final_1080p.mp4"

    logger.info("Assembling final video with LUT, Cinema Letterbox, Audio & Subtitles...")
    success = assemble_final_video(
        ffmpeg_bin=ffmpeg_bin,
        scene_videos=rendered_scenes,
        audio_file=final_audio,
        srt_file=subtitles_file,
        output_video=final_output,
        apply_lut=True,
        apply_letterbox=True
    )

    if success:
        # Clean up temporary scene mp4s and concat list
        for r in rendered_scenes:
            if r.exists():
                r.unlink()
        concat_list = OUTPUT_DIR / "video_concat_list.txt"
        if concat_list.exists():
            concat_list.unlink()

        size_mb = final_output.stat().st_size / (1024 * 1024)
        print(f"\n=======================================================")
        print(f"🎉 PILOT MASTER VIDEO COMPLETE!")
        print(f"   Output File: {final_output}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Resolution: 1920x1080 (2.39:1 Anamorphic Scope Letterbox)")
        print(f"   Color Grade: Cold War Kodak 2383 Bleach-Bypass 3D LUT")
        print(f"   Transitions: Micro Dip-to-Black (0.15s) Between Scenes")
        print(f"   Sound Design: Procedural Sub-Bass Braam Impact + Heartbeat + Sirens")
        print(f"   Subtitles: Matte Burned-in Broadcast Typography")
        print(f"=======================================================\n")


if __name__ == "__main__":
    main()
