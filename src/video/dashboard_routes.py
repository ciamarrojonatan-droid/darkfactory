"""DarkFactory Studio Video, Audio & Narrative Dashboard Routes."""

import asyncio
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.dashboard import readers, runner

logger = logging.getLogger("darkfactory.video.dashboard_routes")

router = APIRouter()

# ── Extracted DarkFactory Schemas ──

# ── Audio & Narration Models ─────────────────────────

class NarrationRequest(BaseModel):
    script: str
    emotion: Optional[str] = "Speak with controlled urgency and rising dread, deep baritone documentary tone, sharp articulation."
    speed: Optional[float] = 1.0
    account: Optional[Any] = 4
    engine: Optional[str] = "auto"  # "auto", "deepgram", "cosyvoice", or "kokoro"
    voice: Optional[str] = "aura-helios-en"


class NarrationResponse(BaseModel):
    success: bool
    message: str
    audio_file: Optional[str] = None
    audio_url: Optional[str] = None
    duration_sec: Optional[float] = None
    size_bytes: Optional[int] = None
    provider: Optional[str] = None
    cost_usd: Optional[float] = None



class NarrationItem(BaseModel):
    filename: str
    path: str
    size_bytes: int
    created_at: str
    audio_url: str


# ── Music & Soundtrack Models ───────────────────────

class MusicRequest(BaseModel):
    preset: Optional[str] = "hans_zimmer_tension"
    style: Optional[str] = None
    structure: Optional[str] = None
    duration_sec: Optional[float] = 180.0
    use_runninghub: Optional[bool] = True


class MusicResponse(BaseModel):
    success: bool
    message: str
    audio_file: Optional[str] = None
    audio_url: Optional[str] = None
    duration_sec: Optional[float] = None
    style_used: Optional[str] = None
    engine: Optional[str] = None
    size_bytes: Optional[int] = None



# ── 3-Stem Multitrack Audio Mix Models ──────────────

class AudioMixRequest(BaseModel):
    voice_file: str
    soundtrack_file: Optional[str] = None
    foley_file: Optional[str] = None
    output_filename: Optional[str] = None
    music_volume: Optional[float] = 0.15
    foley_volume: Optional[float] = 0.35
    ducking: Optional[bool] = True


class AudioMixResponse(BaseModel):
    success: bool
    message: str
    mix_file: Optional[str] = None
    mix_url: Optional[str] = None
    size_bytes: Optional[int] = None


# ── MiniMax H3 Cinematic Video Models ───────────────

class MiniMaxH3VideoRequest(BaseModel):
    prompt: str
    reference_image: Optional[str] = None
    duration_sec: Optional[float] = 10.0
    camera_movement: Optional[str] = "Slow cinematic push-in dolly track forward"
    lighting: Optional[str] = "Volumetric cinematic rim lighting, atmospheric shadows, 2.39:1 letterbox"
    use_runninghub: Optional[bool] = True


class MiniMaxH3VideoResponse(BaseModel):
    success: bool
    message: str
    video_file: Optional[str] = None
    video_url: Optional[str] = None
    duration_sec: Optional[float] = None
    engine: Optional[str] = None
    size_bytes: Optional[int] = None
    has_watermark: bool = False
    has_audio: bool = False
    audio_codec: Optional[str] = None


# ── HyperFrames & YouTube Closed-Loop Models ────────

class MotionOverlayRequest(BaseModel):
    template: str = "tactical_hud"
    title: str
    subtitle: Optional[str] = ""
    duration_sec: float = Field(default=5.0, ge=0.5, le=60.0)
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=240, le=2160)
    fps: int = Field(default=30, ge=1, le=60)
    preview_gate_20s: bool = False
    force_procedural: bool = True
    use_hyperframes_cli: bool = False
    muted: bool = True
    components: Optional[List[str]] = None
    seed: Optional[int] = None
    personality: Optional[str] = None
    run_qa_gate: bool = False
    image_path: Optional[str] = None


class MotionOverlayResponse(BaseModel):
    success: bool
    template: str
    category: str
    output_video_path: Optional[str] = None
    html_path: Optional[str] = None
    svg_path: Optional[str] = None
    duration_sec: float
    width: int
    height: int
    fps: int
    render_backend: str
    is_preview_gate: bool = False
    has_audio: bool = False
    error: Optional[str] = None
    seed: Optional[int] = None
    personality: Optional[str] = None
    contact_sheet_path: Optional[str] = None
    qa_report: Optional[Dict[str, Any]] = None


class MotionQARequest(BaseModel):
    video_path: str
    bg_hex: str = "#070D17"
    fg_hex: str = "#F1F5F9"
    accent_hex: Optional[str] = "#38BDF8"
    personality: str = "cold_war_noir"
    generate_sheet: bool = True
    vision_critique: bool = False


class MotionQAResponse(BaseModel):
    passed: bool
    score: float
    video_path: str
    contact_sheet_path: Optional[str] = None
    contrast_ratio: float
    min_motion_delta: float
    max_motion_delta: float
    frozen_frame_pairs: int
    safe_margin_ok: bool
    sampled_frame_count: int
    findings: List[Dict[str, Any]] = []
    vision_critique: Optional[str] = None


class CadenceBlueprintRequest(BaseModel):
    video_path: str
    audio_path: Optional[str] = None
    snap_tolerance_sec: float = Field(default=0.18, ge=0.02, le=1.0)
    save_json: bool = False


class CadenceBlueprintResponse(BaseModel):
    source_video: str
    pacing_archetype: str
    total_duration_sec: float
    target_msl_sec: float
    tension_score: int
    rehook_timestamps_sec: List[float] = []
    normalized_beats: List[Dict[str, Any]] = []
    estimated_bpm: Optional[float] = None
    audio_beats: List[float] = []
    blueprint_json_path: Optional[str] = None


class SVGDeconstructRequest(BaseModel):
    image_path: str
    title: str = "DECLASSIFIED ARTIFACT"
    subtitle: str = "SEMANTIC VECTOR RECONSTRUCTION"
    max_paths: int = Field(default=48, ge=1, le=200)
    duration_sec: float = Field(default=4.0, ge=0.5, le=30.0)


class SVGDeconstructResponse(BaseModel):
    success: bool
    source_image_path: str
    svg_path: Optional[str] = None
    html_path: Optional[str] = None
    semantic_groups: List[str] = []
    path_count: int = 0
    total_vertices: int = 0
    faithful_landing_iou: float = 0.0
    smoothness_gate_passed: bool = False
    svg_markup: str = ""
    error: Optional[str] = None


class YouTubeLintRequest(BaseModel):
    title: str
    thumbnail_text: str
    chapters: Optional[Any] = None
    total_duration_sec: float = 300.0
    retention_csv: Optional[str] = None
    description: Optional[str] = ""


class YouTubeLintResponse(BaseModel):
    title_thumbnail_lint: Dict[str, Any]
    chapters_audit: Optional[Dict[str, Any]] = None
    retention_audit: Optional[Dict[str, Any]] = None
    shorts_candidates: List[Dict[str, Any]] = []



# ── Sprint 7-9: Documentary Map Sync, Foley & Storyboard Schemas ──


class MapPinInput(BaseModel):
    label: str = Field(..., min_length=1, max_length=64)
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    timestamp_sec: float = Field(0.3, ge=0.0, le=120.0)
    color_hex: str = Field("#EF4444", pattern=r"^#[0-9a-fA-F]{6}$")


class MapRouteInput(BaseModel):
    origin_lat: float = Field(..., ge=-90.0, le=90.0)
    origin_lon: float = Field(..., ge=-180.0, le=180.0)
    dest_lat: float = Field(..., ge=-90.0, le=90.0)
    dest_lon: float = Field(..., ge=-180.0, le=180.0)
    label: str = Field("", max_length=64)
    start_sec: float = Field(0.5, ge=0.0, le=120.0)
    duration_sec: float = Field(1.5, ge=0.1, le=120.0)
    color_hex: str = Field("#38BDF8", pattern=r"^#[0-9a-fA-F]{6}$")


class MapAnimateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    subtitle: str = Field("", max_length=140)
    theater: str = Field("europe_cold_war", min_length=1, max_length=60)
    pins: List[MapPinInput] = Field(default_factory=list)
    routes: List[MapRouteInput] = Field(default_factory=list)
    duration_sec: float = Field(4.0, ge=0.5, le=60.0)
    width: int = Field(1280, ge=320, le=3840)
    height: int = Field(720, ge=240, le=2160)
    fps: int = Field(24, ge=12, le=60)
    editorial_12fps: bool = True


class MapAnimateResponse(BaseModel):
    success: bool
    theater: str
    title: str
    video_path: Optional[str] = None
    svg_path: Optional[str] = None
    html_path: Optional[str] = None
    duration_sec: float = 0.0
    width: int = 1280
    height: int = 720
    fps: int = 24
    editorial_12fps: bool = True
    error: Optional[str] = None


class ComposeDossierRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=160)
    script: str = Field(..., min_length=1, max_length=20000)
    narration_audio_path: str = Field(..., min_length=1, max_length=512)
    theater: str = Field("europe_cold_war", min_length=1, max_length=60)
    trigger_keywords: Optional[List[str]] = None
    width: int = Field(1280, ge=320, le=3840)
    height: int = Field(720, ge=240, le=2160)
    fps: int = Field(24, ge=12, le=60)


class ComposeDossierResponse(BaseModel):
    success: bool
    topic: str
    slug: str
    duration_sec: float = 0.0
    master_video_path: Optional[str] = None
    map_video_path: Optional[str] = None
    otio_path: Optional[str] = None
    subtitles_path: Optional[str] = None
    manifest_path: Optional[str] = None
    word_triggers: List[Dict[str, Any]] = Field(default_factory=list)
    facts_count: int = 0
    pd_assets_count: int = 0
    error: Optional[str] = None


class FoleyCueInput(BaseModel):
    sfx_name: str = Field(..., min_length=1, max_length=64)
    timestamp_sec: float = Field(..., ge=0.0, le=3600.0)
    gain_db: float = Field(-8.0, ge=-48.0, le=6.0)
    pan: float = Field(0.0, ge=-1.0, le=1.0)
    duration_sec: Optional[float] = Field(None, ge=0.05, le=30.0)


class FoleyTrackRequest(BaseModel):
    total_duration_sec: float = Field(..., ge=0.5, le=3600.0)
    cues: List[FoleyCueInput] = Field(default_factory=list)
    sample_rate: int = Field(44100, ge=16000, le=96000)


class FoleyTrackResponse(BaseModel):
    success: bool
    sfx_track_path: Optional[str] = None
    duration_sec: float = 0.0
    cues_applied: int = 0
    catalog_used: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class VideoReverseRequest(BaseModel):
    video_path: str = Field(..., min_length=1, max_length=512)
    topic: Optional[str] = Field(None, max_length=160)
    mode: str = Field("AUTO", max_length=16)
    use_vision: bool = False


class VideoReverseResponse(BaseModel):
    success: bool
    video_path: str
    topic: str
    mode: str
    total_duration_sec: float
    mean_shot_length: float
    shots: List[Dict[str, Any]] = Field(default_factory=list)
    story_audit: Dict[str, Any] = Field(default_factory=dict)
    manifest_path: Optional[str] = None
    error: Optional[str] = None


class StoryboardCompileRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=160)
    script: str = Field(..., min_length=1, max_length=30000)
    target_niche: str = Field("industrial_automation", min_length=1, max_length=80)
    target_duration_sec: float = Field(20.0, ge=4.0, le=3600.0)
    theater: str = Field("europe_cold_war", min_length=1, max_length=60)


class StoryboardCompileResponse(BaseModel):
    success: bool
    title: str
    slug: str
    target_niche: str
    total_duration_sec: float
    scenes: List[Dict[str, Any]] = Field(default_factory=list)
    hook_audit: Dict[str, Any] = Field(default_factory=dict)
    story_audit: Dict[str, Any] = Field(default_factory=dict)
    overlap_audit: Dict[str, Any] = Field(default_factory=dict)
    budget_estimate: Dict[str, Any] = Field(default_factory=dict)
    manifest_path: Optional[str] = None
    error: Optional[str] = None


class MonetizationPackRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=1, max_length=140)
    subtitle: str = Field("DECLASSIFIED ARCHIVE", max_length=100)
    backdrop_path: Optional[str] = Field(None, max_length=512)
    master_video_path: Optional[str] = Field(None, max_length=512)
    broll_count: int = Field(3, ge=3, le=12)
    target_width: int = Field(3840, ge=640, le=3840)
    target_height: int = Field(2160, ge=360, le=2160)


class MonetizationPackResponse(BaseModel):
    success: bool
    project_id: str
    thumbnails: List[Dict[str, Any]] = Field(default_factory=list)
    master_context: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ShortsRepurposeRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    script: str = Field(default="", max_length=5000)
    source_video_path: Optional[str] = Field(default=None, max_length=320)
    audio_path: Optional[str] = Field(default=None, max_length=320)
    style: str = Field(default="editorial_karaoke", max_length=40)
    safe_zone_profile: str = Field(default="youtube_shorts", max_length=40)
    target_duration_sec: float = Field(default=15.0, ge=3.0, le=60.0)
    width: int = Field(default=1080, ge=360, le=2160)
    height: int = Field(default=1920, ge=640, le=3840)
    fps: int = Field(default=24, ge=12, le=60)
    export_clean_broll: bool = True


class ShortsRepurposeResponse(BaseModel):
    success: bool
    title: str
    style: str
    safe_zone_profile: str
    short_video_path: Optional[str] = None
    ass_path: Optional[str] = None
    clean_broll_path: Optional[str] = None
    clean_broll_muted: bool = True
    manifest_path: Optional[str] = None
    width: int = 1080
    height: int = 1920
    duration_sec: float = 0.0
    window_start_sec: float = 0.0
    window_end_sec: float = 0.0
    salient_center_x: float = 0.5
    safe_zone_passed: bool = False
    overlap_audit: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ── Extracted DarkFactory Routes ──


# --- app.py L1004-L1457 ---

@router.post("/api/v1/narrate", response_model=NarrationResponse)
@router.post("/api/narration/generate", response_model=NarrationResponse)
async def generate_narration_endpoint(req: NarrationRequest):
    """Gera áudio de narração via Deepgram Aura API (instantâneo) ou CosyVoice no RunningHub."""
    import time

    start_time = time.time()
    engine_choice = (getattr(req, "engine", "auto") or "auto").lower()
    has_deepgram_key = bool(os.getenv("DEEPGRAM_API_KEY", "").strip())
    use_deepgram = engine_choice == "deepgram" or (engine_choice == "auto" and has_deepgram_key)

    if use_deepgram:
        try:
            from src.video.voice_engine import DeepgramVoiceEngine
            engine = DeepgramVoiceEngine(output_dir=readers.FINAL_AUDIO_DIR)
            if engine.is_available:
                synth = await asyncio.to_thread(
                    engine.synthesize,
                    text=req.script,
                    voice=getattr(req, "voice", "aura-helios-en") or "aura-helios-en",
                    speed=req.speed or 1.0,
                )
                return NarrationResponse(
                    success=True,
                    message=f"Narração gerada com sucesso via Deepgram Aura ({synth.voice_used})",
                    audio_file=synth.filename,
                    audio_url=f"/api/audio/file/{synth.filename}",
                    duration_sec=synth.duration_seconds,
                    size_bytes=synth.filesize_bytes,
                    provider="deepgram",
                    cost_usd=synth.estimated_cost_usd,
                )
        except Exception as dg_err:
            logger.warning("Deepgram synthesis failed: %s. Tentando fallback...", dg_err)
            if engine_choice == "deepgram":
                return NarrationResponse(
                    success=False,
                    message=f"Erro na geração Deepgram: {str(dg_err)}",
                    duration_sec=time.time() - start_time,
                )

    # Fallback ou execução explícita via RunningHub CosyVoice
    from src.factory.runninghub_bot import run_narration_bot
    try:
        res = await asyncio.to_thread(
            run_narration_bot,
            script=req.script,
            emotion=req.emotion,
            speed=req.speed or 1.0,
        )
        saved_files = res.get("saved_files", [])
        if saved_files:
            fn = saved_files[-1]
            dur = time.time() - start_time
            file_path = readers.FINAL_AUDIO_DIR / fn
            sz = file_path.stat().st_size if file_path.exists() else 0
            return NarrationResponse(
                success=True,
                message="Narração gerada com sucesso via CosyVoice (SaveAudio #346)",
                audio_file=fn,
                audio_url=f"/api/audio/file/{fn}",
                duration_sec=dur,
                size_bytes=sz,
            )
        else:
            return NarrationResponse(
                success=False,
                message="Nenhum áudio salvo durante a execução do workflow CosyVoice.",
                duration_sec=time.time() - start_time,
            )
    except Exception as e:
        logger.error("Erro na geração de narração CosyVoice: %s", e)
        return NarrationResponse(
            success=False,
            message=f"Erro na geração de áudio: {str(e)}",
            duration_sec=time.time() - start_time,
        )


@router.post("/api/narration/task")
async def trigger_narration_task(req: NarrationRequest):
    """Enfileira tarefa de narração em background subprocess."""
    return await runner.run_narration_task(
        script=req.script,
        emotion=req.emotion,
        speed=req.speed or 1.0,
    )


@router.get("/api/narration/items", response_model=List[NarrationItem])
async def list_narration_items():
    """Lista todos os arquivos de áudio de narração salvos em data/final/audio/."""
    return readers.get_audio_items()


ALLOWED_AUDIO_EXTS = {".mp3", ".flac", ".wav", ".m4a", ".ogg", ".aac"}
ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv"}


@router.get("/api/audio/file/{filename}")
async def get_audio_file(filename: str):
    """Serve o arquivo de áudio para streaming ou download (protegido contra path traversal)."""
    safe_name = Path(filename).name
    if not filename or safe_name != filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    if Path(safe_name).suffix.lower() not in ALLOWED_AUDIO_EXTS:
        raise HTTPException(status_code=400, detail="Formato de áudio não suportado")
    path = readers.FINAL_AUDIO_DIR / safe_name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo de áudio não encontrado")
    ext = path.suffix.lower()
    media_type = "audio/mpeg" if ext == ".mp3" else ("audio/flac" if ext == ".flac" else "audio/wav")
    return FileResponse(path, media_type=media_type, filename=path.name)


@router.get("/api/video/file/{filename}")
async def get_video_file(filename: str):
    """Serve vídeo renderizado (MiniMax H3 / HyperFrames / Shorts) com proteção contra path traversal."""
    safe_name = Path(filename).name
    if not filename or safe_name != filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    if Path(safe_name).suffix.lower() not in ALLOWED_VIDEO_EXTS:
        raise HTTPException(status_code=400, detail="Formato de vídeo não suportado")
    for base_dir in (readers.FINAL_VIDEOS_DIR, readers.OUTPUT_DIR, readers.DATA_DIR / "final" / "shorts"):
        candidate = base_dir / safe_name
        if candidate.is_file():
            media = "video/quicktime" if candidate.suffix.lower() == ".mov" else "video/mp4"
            return FileResponse(str(candidate), media_type=media, filename=candidate.name)
    raise HTTPException(status_code=404, detail="Arquivo de vídeo não encontrado")


# ── MiniMax Music 3 & Soundtrack Endpoints ──────────

@router.post("/api/v1/music/generate", response_model=MusicResponse)
@router.post("/api/music/generate", response_model=MusicResponse)
async def generate_music_endpoint(req: MusicRequest):
    """Gera trilha sonora orquestral via MiniMax Music 3 (RunningHub) ou fallback procedural."""
    from src.video.minimax_music_engine import MiniMaxMusicEngine

    engine = MiniMaxMusicEngine(output_dir=readers.FINAL_AUDIO_DIR)
    try:
        track = await asyncio.to_thread(
            engine.generate_soundtrack,
            preset_name=req.preset or "hans_zimmer_tension",
            custom_style=req.style,
            custom_structure=req.structure,
            duration_sec=req.duration_sec or 180.0,
            force_procedural=not req.use_runninghub,
        )
        return MusicResponse(
            success=True,
            message=f"Trilha sonora gerada com sucesso via {track.engine}",
            audio_file=track.filename,
            audio_url=f"/api/audio/file/{track.filename}",
            duration_sec=track.duration_seconds,
            style_used=track.style[:120],
            engine=track.engine,
            size_bytes=track.filesize_bytes,
        )
    except Exception as e:
        logger.error(f"Erro na geração de trilha sonora: {e}")
        return MusicResponse(
            success=False,
            message=f"Erro na geração de trilha sonora: {str(e)}",
        )


# ── 3-Stem Multitrack Documentary Audio Mix ─────────

@router.post("/api/v1/audio/mix", response_model=AudioMixResponse)
@router.post("/api/audio/mix", response_model=AudioMixResponse)
async def mix_audio_endpoint(req: AudioMixRequest):
    """Realiza mixagem 3-stem (voz + música + foley) via FFmpeg com sidechain ducking."""
    from src.video.audio_engine import DarkFactoryAudioEngine

    audio_engine = DarkFactoryAudioEngine()
    v_path = readers.FINAL_AUDIO_DIR / req.voice_file
    if not v_path.exists():
        staging_v = Path(readers.BASE_DIR) / "data" / "staging" / "narration" / req.voice_file
        if staging_v.exists():
            v_path = staging_v
        else:
            raise HTTPException(status_code=404, detail=f"Arquivo de narração não encontrado: {req.voice_file}")

    m_path = (readers.FINAL_AUDIO_DIR / req.soundtrack_file) if req.soundtrack_file else None
    if m_path and not m_path.exists():
        staging_m = Path(readers.BASE_DIR) / "data" / "staging" / "soundtracks" / req.soundtrack_file
        if staging_m.exists():
            m_path = staging_m

    f_path = (readers.FINAL_AUDIO_DIR / req.foley_file) if req.foley_file else None

    out_name = req.output_filename or f"master_mix_{int(time.time())}.mp3"
    out_path = readers.FINAL_AUDIO_DIR / out_name

    try:
        mixed_path = await asyncio.to_thread(
            audio_engine.mix_multitrack_documentary,
            voice_path=v_path,
            soundtrack_path=m_path,
            foley_path=f_path,
            output_path=out_path,
            music_volume=req.music_volume or 0.15,
            foley_volume=req.foley_volume or 0.35,
            ducking=req.ducking if req.ducking is not None else True,
        )
        return AudioMixResponse(
            success=True,
            message="Mixagem multitrack 3-stem criada com sucesso!",
            mix_file=mixed_path.name,
            mix_url=f"/api/audio/file/{mixed_path.name}",
            size_bytes=mixed_path.stat().st_size if mixed_path.exists() else 0,
        )
    except Exception as e:
        logger.error(f"Erro na mixagem de áudio: {e}")
        return AudioMixResponse(
            success=False,
            message=f"Erro na mixagem de áudio: {str(e)}",
        )


# ── MiniMax H3 Cinematic V2 Turbo Endpoint ──────────

@router.post("/api/v1/video/minimax_h3", response_model=MiniMaxH3VideoResponse)
@router.post("/api/video/minimax_h3", response_model=MiniMaxH3VideoResponse)
async def generate_minimax_h3_endpoint(req: MiniMaxH3VideoRequest):
    """Gera vídeo cinemático via MiniMax H3 Cinematic V2 Turbo (Workflow 2118560390471745537)
    com extração direta sem marca d'água no Nó #107 FeiHou e fallback procedural.
    """
    from src.video.minimax_h3_engine import MiniMaxH3VideoEngine

    engine = MiniMaxH3VideoEngine()
    formatted_prompt = engine.build_cinematic_prompt(
        subject=req.prompt,
        camera_movement=req.camera_movement or "Slow cinematic push-in dolly track forward",
        lighting=req.lighting or "Volumetric cinematic rim lighting, atmospheric shadows, 2.39:1 letterbox",
    )
    try:
        res = await asyncio.to_thread(
            engine.generate_video,
            prompt=formatted_prompt,
            reference_image_path=req.reference_image,
            duration_sec=req.duration_sec or 10.0,
            force_procedural=not req.use_runninghub,
        )
        return MiniMaxH3VideoResponse(
            success=True,
            message=f"Vídeo cinemático MiniMax H3 gerado com sucesso via {res.engine} (sem marca d'água)",
            video_file=res.filename,
            video_url=f"/api/video/file/{res.filename}",
            duration_sec=res.duration_seconds,
            engine=res.engine,
            size_bytes=res.filesize_bytes,
            has_watermark=res.has_watermark,
            has_audio=res.has_audio,
            audio_codec=res.audio_codec,
        )
    except Exception as e:
        logger.error(f"Erro na geração de vídeo MiniMax H3: {e}")
        return MiniMaxH3VideoResponse(
            success=False,
            message=f"Erro na geração de vídeo MiniMax H3: {str(e)}",
        )


# ── HyperFrames Motion Overlay & YouTube Lint ───────

def _validate_workspace_file(path_str: str, allowed_exts: set[str], label: str = "path") -> Path:
    """Restrict user-supplied API file paths strictly inside workspace data/safe boundaries."""
    if not path_str or not str(path_str).strip():
        raise HTTPException(status_code=400, detail=f"Missing {label}.")
    base = readers.BASE_DIR.resolve()
    target = Path(path_str).resolve()
    try:
        rel = target.relative_to(base)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Path traversal forbidden for {label}: path must reside inside workspace.",
        )
    if rel.parts and rel.parts[0].lower() in {"src", ".git", ".agents", "venv", ".venv"}:
        raise HTTPException(
            status_code=400,
            detail=f"Access forbidden for {label}: protected directory '{rel.parts[0]}'.",
        )
    if not target.is_file() or target.suffix.lower() not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Invalid or missing {label}.")
    return target


@router.post("/api/v1/video/motion-overlay", response_model=MotionOverlayResponse)
async def render_motion_overlay_endpoint(req: MotionOverlayRequest):
    """Renderiza overlay HyperFrames / Isometric CAD com envelope determinístico e gate 20s."""
    from src.video.hyperframes_engine import HyperFramesMotionEngine, MOTION_TEMPLATES

    if req.template not in MOTION_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown motion template '{req.template}'. Valid: {sorted(MOTION_TEMPLATES)}",
        )

    overlay_dir = (readers.BASE_DIR / "data" / "final" / "motion_overlays").resolve()
    engine = HyperFramesMotionEngine(output_dir=overlay_dir)
    data: dict = {}
    if req.components:
        data["components"] = req.components
    if req.image_path:
        img_target = _validate_workspace_file(
            req.image_path, {".png", ".jpg", ".jpeg", ".webp", ".bmp"}, "image_path"
        )
        data["image_path"] = img_target.as_posix()

    if req.preview_gate_20s:
        res = await asyncio.to_thread(
            engine.render_preview_gate,
            template=req.template,
            title=req.title,
            subtitle=req.subtitle or "",
            duration_sec=req.duration_sec,
            width=req.width,
            height=req.height,
            fps=req.fps,
            data=data or None,
            use_hyperframes_cli=req.use_hyperframes_cli,
            force_procedural=req.force_procedural,
            seed=req.seed,
            personality=req.personality,
            run_qa_gate=True if req.run_qa_gate else False,
        )
    else:
        res = await asyncio.to_thread(
            engine.render_motion_clip,
            template=req.template,
            title=req.title,
            subtitle=req.subtitle or "",
            duration_sec=req.duration_sec,
            width=req.width,
            height=req.height,
            fps=req.fps,
            data=data or None,
            use_hyperframes_cli=req.use_hyperframes_cli,
            force_procedural=req.force_procedural,
            muted=req.muted,
            seed=req.seed,
            personality=req.personality,
            run_qa_gate=req.run_qa_gate,
        )
    return MotionOverlayResponse(**{
        k: v
        for k, v in res.to_dict().items()
        if k in MotionOverlayResponse.model_fields
    })


@router.post("/api/v1/video/motion-qa", response_model=MotionQAResponse)
async def audit_motion_qa_endpoint(req: MotionQARequest):
    """Audita vídeo renderizado com Contact Sheet 3x3, contraste WCAG e detecção de congelamento."""
    from src.video.motion_qa import MotionQAInspector

    target = _validate_workspace_file(
        req.video_path, {".mp4", ".mov", ".webm", ".mkv", ".avi"}, "video_path for Motion QA"
    )
    telemetry_dir = (readers.BASE_DIR / "data" / "staging" / "telemetry").resolve()
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    sheet_path = (telemetry_dir / f"{target.stem}_qa_sheet.png") if req.generate_sheet else None

    inspector = MotionQAInspector()
    report = await asyncio.to_thread(
        inspector.audit_video,
        video_path=target,
        bg_hex=req.bg_hex,
        fg_hex=req.fg_hex,
        accent_hex=req.accent_hex,
        personality=req.personality,
        generate_sheet=req.generate_sheet,
        contact_sheet_path=sheet_path,
        vision_critique=req.vision_critique,
    )
    payload = report.to_dict()
    payload["findings"] = [asdict(f) for f in report.findings]
    return MotionQAResponse(**payload)


@router.post("/api/v1/video/cadence-blueprint", response_model=CadenceBlueprintResponse)
async def build_cadence_blueprint_endpoint(req: CadenceBlueprintRequest):
    """Extrai Cadence Blueprint rítmico e transientes musicais para alinhamento de cortes."""
    from src.video.audio_engine import DarkFactoryAudioEngine
    from src.video.pacing_analyzer import CinematicPacingAnalyzer

    vid_target = _validate_workspace_file(
        req.video_path, {".mp4", ".mov", ".webm", ".mkv", ".avi"}, "video_path for Cadence Blueprint"
    )

    beats: list[float] = []
    est_bpm: Optional[float] = None
    if req.audio_path:
        aud_target = _validate_workspace_file(
            req.audio_path, {".wav", ".mp3", ".flac", ".aac", ".m4a"}, "audio_path for transient extraction"
        )
        audio_analysis = await asyncio.to_thread(DarkFactoryAudioEngine().analyze_audio_transients, aud_target)
        beats = audio_analysis.beat_timestamps
        est_bpm = audio_analysis.estimated_bpm

    analyzer = CinematicPacingAnalyzer()
    report = await asyncio.to_thread(analyzer.analyze_pacing, vid_target)
    telemetry_dir = (readers.BASE_DIR / "data" / "staging" / "telemetry").resolve()
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    out_json = (telemetry_dir / f"{vid_target.stem}.cadence.json") if req.save_json else None
    blueprint = await asyncio.to_thread(
        analyzer.export_cadence_blueprint,
        report=report,
        output_json_path=out_json,
        beat_timestamps=beats or None,
        snap_tolerance_sec=req.snap_tolerance_sec,
    )
    data = blueprint.to_dict()
    data["estimated_bpm"] = est_bpm
    data["audio_beats"] = beats
    data["blueprint_json_path"] = out_json.as_posix() if out_json else None
    return CadenceBlueprintResponse(**data)


@router.post("/api/v1/video/svg-deconstruct", response_model=SVGDeconstructResponse)
async def svg_deconstruct_endpoint(req: SVGDeconstructRequest):
    """Converte emblemas ou diagramas raster em SVG semântico animável com Faithful Landing IoU."""
    from src.video.svg_deconstructor import RasterToAnimatedSVG

    img_target = _validate_workspace_file(
        req.image_path, {".png", ".jpg", ".jpeg", ".webp", ".bmp"}, "image_path for SVG deconstruction"
    )
    telemetry_dir = (readers.BASE_DIR / "data" / "staging" / "telemetry").resolve()
    telemetry_dir.mkdir(parents=True, exist_ok=True)

    res = await asyncio.to_thread(
        RasterToAnimatedSVG().deconstruct_raster,
        image_path=img_target,
        output_svg_path=telemetry_dir / f"{img_target.stem}.semantic.svg",
        output_html_path=telemetry_dir / f"{img_target.stem}.semantic.html",
        title=req.title,
        subtitle=req.subtitle,
        max_paths=req.max_paths,
        duration_sec=req.duration_sec,
    )
    return SVGDeconstructResponse(**res.to_dict())


@router.post("/api/v1/youtube/lint-package", response_model=YouTubeLintResponse)
async def lint_youtube_package_endpoint(req: YouTubeLintRequest):
    """Audita par Título+Thumbnail, capítulos, retenção CSV e janelas Shorts."""
    from src.video.youtube_booster import YouTubeAlgorithmBoosterBridge

    bridge = YouTubeAlgorithmBoosterBridge()
    lint_res = bridge.lint_title_thumbnail_pair(title=req.title, thumbnail_text=req.thumbnail_text)
    chapters_res = (
        bridge.validate_youtube_chapters(req.chapters, total_duration_sec=req.total_duration_sec)
        if req.chapters is not None
        else None
    )
    retention_res = bridge.parse_retention_csv(req.retention_csv) if req.retention_csv else None
    shorts = bridge.extract_shorts_candidates(
        retention_report=retention_res,
        total_duration_sec=req.total_duration_sec,
    )
    return YouTubeLintResponse(
        title_thumbnail_lint=lint_res,
        chapters_audit=chapters_res,
        retention_audit=retention_res,
        shorts_candidates=shorts,
    )


# --- app.py L1489-L1752 ---

@router.post("/api/v1/video/map-animate", response_model=MapAnimateResponse)
async def map_animate_endpoint(req: MapAnimateRequest):
    """Renderiza mapa vetorial editorial (SVG + HTML/GSAP + MP4) em modo offline."""
    from src.video.map_animator import MapAnimator, MapPin, MapRoute, THEATER_PRESETS

    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespace-only.")
    if req.theater not in THEATER_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown theater '{req.theater}'. Valid: {sorted(THEATER_PRESETS)}",
        )

    map_dir = (readers.BASE_DIR / "data" / "final" / "motion_overlays" / "maps").resolve()
    animator = MapAnimator(output_dir=map_dir)
    pins = [
        MapPin(
            label=p.label,
            lat=p.lat,
            lon=p.lon,
            timestamp_sec=p.timestamp_sec,
            color_hex=p.color_hex,
        )
        for p in req.pins
    ]
    routes = [
        MapRoute(
            origin_lat=r.origin_lat,
            origin_lon=r.origin_lon,
            dest_lat=r.dest_lat,
            dest_lon=r.dest_lon,
            label=r.label,
            start_sec=r.start_sec,
            duration_sec=r.duration_sec,
            color_hex=r.color_hex,
        )
        for r in req.routes
    ]

    result = await asyncio.to_thread(
        animator.render_map_animation,
        title=req.title,
        subtitle=req.subtitle,
        theater=req.theater,
        pins=pins,
        routes=routes,
        duration_sec=req.duration_sec,
        width=req.width,
        height=req.height,
        fps=req.fps,
        editorial_12fps=req.editorial_12fps,
    )
    return MapAnimateResponse(**result.to_dict())


@router.post("/api/v1/video/compose-dossier", response_model=ComposeDossierResponse)
async def compose_dossier_endpoint(req: ComposeDossierRequest):
    """Orquestra episódio documental sincronizado palavra-a-palavra com mapa e selos."""
    from src.video.documentary_composer import DocumentaryComposer
    from src.video.map_animator import THEATER_PRESETS

    if not req.topic.strip() or not req.script.strip():
        raise HTTPException(status_code=400, detail="Topic and script cannot be empty or whitespace-only.")
    audio_target = _validate_workspace_file(
        req.narration_audio_path,
        {".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg"},
        "narration_audio_path",
    )
    if req.theater not in THEATER_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown theater '{req.theater}'. Valid: {sorted(THEATER_PRESETS)}",
        )

    episodes_dir = (readers.BASE_DIR / "data" / "final" / "episodes").resolve()
    composer = DocumentaryComposer(output_dir=episodes_dir)
    try:
        result = await asyncio.to_thread(
            composer.compose_episode,
            topic=req.topic,
            script=req.script,
            narration_audio_path=audio_target,
            theater=req.theater,
            trigger_keywords=req.trigger_keywords,
            width=req.width,
            height=req.height,
            fps=req.fps,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ComposeDossierResponse(**result.to_dict())


# ── Sprint 8: CC0 Foley Stem & Video Reverse-Engineer ───────


@router.post("/api/v1/audio/foley-track", response_model=FoleyTrackResponse)
async def build_foley_track_endpoint(req: FoleyTrackRequest):
    """Sintetiza e mixa efeitos sonoros CC0 locais num stem WAV sincronizado."""
    from src.video.foley_library import FoleyCue, FoleyLibrary

    foley_dir = (readers.BASE_DIR / "data" / "final" / "audio" / "foley_stems").resolve()
    lib = FoleyLibrary(output_dir=foley_dir)
    catalog = lib.list_catalog()

    cues: list[FoleyCue] = []
    for item in req.cues:
        key = item.sfx_name.strip().lower()
        if key not in catalog:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown SFX '{item.sfx_name}'. Valid CC0 catalog: {sorted(catalog)}",
            )
        cues.append(
            FoleyCue(
                sfx_name=key,
                timestamp_sec=item.timestamp_sec,
                gain_db=item.gain_db,
                pan=item.pan,
                duration_sec=item.duration_sec,
            )
        )

    res = await asyncio.to_thread(
        lib.build_foley_stem,
        cues=cues,
        total_duration_sec=req.total_duration_sec,
        sample_rate=req.sample_rate,
    )
    return FoleyTrackResponse(**res.to_dict())


@router.post("/api/v1/video/reverse-engineer", response_model=VideoReverseResponse)
async def reverse_engineer_video_endpoint(req: VideoReverseRequest):
    """Engenharia reversa multimodal de clipe existente para prompts MiniMax H3 / Veo 2."""
    from src.video.video_reverse_engineer import VideoReverseEngineer

    video_target = _validate_workspace_file(
        req.video_path,
        {".mp4", ".mov", ".mkv", ".webm", ".avi"},
        "video_path for reverse engineering",
    )
    out_dir = (readers.BASE_DIR / "data" / "processed" / "reverse_engineered").resolve()
    engine = VideoReverseEngineer(output_dir=out_dir)
    res = await asyncio.to_thread(
        engine.reverse_engineer_video,
        video_path=video_target,
        topic=req.topic,
        mode=req.mode,
        use_vision=req.use_vision,
    )
    return VideoReverseResponse(**res.to_dict())


# ── Sprint 9: Storyboard Compiler & Dual Monetization Pack ─


@router.post("/api/v1/video/storyboard-compile", response_model=StoryboardCompileResponse)
async def compile_storyboard_endpoint(req: StoryboardCompileRequest):
    """Compila roteiro em storyboard auditado com colisão 0.5s e orçamento unit economics."""
    from src.video.map_animator import THEATER_PRESETS
    from src.video.storyboard_compiler import StoryboardCompiler

    if not req.title.strip() or not req.script.strip():
        raise HTTPException(status_code=400, detail="Title and script cannot be empty or whitespace-only.")
    if req.theater not in THEATER_PRESETS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown theater '{req.theater}'. Valid: {sorted(THEATER_PRESETS)}",
        )

    sb_dir = (readers.BASE_DIR / "data" / "processed" / "storyboards").resolve()
    compiler = StoryboardCompiler(output_dir=sb_dir)
    try:
        res = await asyncio.to_thread(
            compiler.compile_storyboard,
            title=req.title,
            script=req.script,
            target_niche=req.target_niche,
            target_duration_sec=req.target_duration_sec,
            theater=req.theater,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return StoryboardCompileResponse(**res.to_dict())


@router.post("/api/v1/youtube/render-monetization-pack", response_model=MonetizationPackResponse)
async def render_monetization_pack_endpoint(req: MonetizationPackRequest):
    """Renderiza 3 thumbnails JPEG 1280x720 otimizadas para CTR no YouTube."""
    from src.video.youtube_booster import YouTubeAlgorithmBoosterBridge

    if not req.project_id.strip() or not req.title.strip():
        raise HTTPException(status_code=400, detail="project_id and title cannot be empty or whitespace-only.")

    backdrop_target = None
    if req.backdrop_path:
        backdrop_target = _validate_workspace_file(
            req.backdrop_path,
            {".jpg", ".jpeg", ".png", ".webp"},
            "backdrop_path",
        )

    master_target = None
    if req.master_video_path:
        master_target = _validate_workspace_file(
            req.master_video_path,
            {".mp4", ".mov", ".mkv", ".webm"},
            "master_video_path",
        )

    yt_dir = (readers.BASE_DIR / "data" / "processed" / "youtube_packages").resolve()
    bridge = YouTubeAlgorithmBoosterBridge(output_dir=yt_dir)

    thumbs = await asyncio.to_thread(
        bridge.render_tri_variant_thumbnails,
        project_id=req.project_id,
        title=req.title,
        subtitle=req.subtitle,
        backdrop_path=backdrop_target,
    )

    master_ctx = {"master_video_path": master_target.as_posix()} if master_target is not None else None

    return MonetizationPackResponse(
        success=True,
        project_id=req.project_id,
        thumbnails=thumbs,
        master_context=master_ctx,
    )


_VIDEO_RENDER_SEMAPHORES: dict[int, object] = {}


def _get_video_render_semaphore():
    """Bound concurrent DarkFactory FFmpeg/OpenCV render jobs per event loop."""

    loop = asyncio.get_running_loop()
    loop_id = id(loop)
    sem = _VIDEO_RENDER_SEMAPHORES.get(loop_id)
    if sem is None:
        if len(_VIDEO_RENDER_SEMAPHORES) > 16:
            _VIDEO_RENDER_SEMAPHORES.clear()
        sem = asyncio.Semaphore(2)
        _VIDEO_RENDER_SEMAPHORES[loop_id] = sem
    return sem



# --- app.py L1753-L1820 ---

@router.post("/api/v1/video/repurpose-short", response_model=ShortsRepurposeResponse)
async def repurpose_short_endpoint(req: ShortsRepurposeRequest):
    """Repurposes a 16:9 master or script into a vertical 9:16 kinetic-captioned Short + clean muted B-roll."""
    from src.video.kinetic_captions import CAPTION_STYLES
    from src.video.motion_qa import PLATFORM_SAFE_ZONES
    from src.video.shorts_repurposer import ShortsRepurposerEngine

    if not req.title.strip():
        raise HTTPException(status_code=400, detail="title cannot be empty or whitespace-only.")

    style_key = (req.style or "editorial_karaoke").strip().lower()
    if style_key not in CAPTION_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown caption style '{req.style}'. Valid: {sorted(CAPTION_STYLES)}",
        )

    zone_key = (req.safe_zone_profile or "youtube_shorts").strip().lower()
    if zone_key not in PLATFORM_SAFE_ZONES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown safe_zone_profile '{req.safe_zone_profile}'. Valid: {sorted(PLATFORM_SAFE_ZONES)}",
        )

    src_target = None
    if req.source_video_path:
        src_target = _validate_workspace_file(
            req.source_video_path,
            {".mp4", ".mov", ".mkv", ".webm"},
            "source_video_path",
        )

    audio_target = None
    if req.audio_path:
        audio_target = _validate_workspace_file(
            req.audio_path,
            {".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"},
            "audio_path",
        )

    shorts_dir = (readers.BASE_DIR / "data" / "final" / "shorts").resolve()
    engine = ShortsRepurposerEngine(output_dir=shorts_dir)
    try:
        async with _get_video_render_semaphore():
            res = await asyncio.to_thread(
                engine.repurpose_to_vertical_short,
                title=req.title,
                script=req.script,
                source_video_path=src_target,
                audio_path=audio_target,
                output_dir=shorts_dir,
                style=style_key,
                safe_zone_profile=zone_key,
                target_duration_sec=req.target_duration_sec,
                width=req.width,
                height=req.height,
                fps=req.fps,
                export_clean_broll=req.export_clean_broll,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("repurpose_short_endpoint failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Video engine error: {exc}")

    return ShortsRepurposeResponse(**res.to_dict())

