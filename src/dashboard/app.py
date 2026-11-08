"""DarkFactory Cinema Dashboard — FastAPI Web Application.

High-frequency command center for Faceless YouTube Dark Channels,
Christopher Nolan screenplay synthesis, 4-stem audio mixing, visual generation queues,
and 1-Click YouTube approval with EDSA / Green Dollar pre-flight compliance.
"""

from __future__ import annotations

import io
import logging
import os
import sys
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import readers, runner, schemas

# Configure UTF-8 on Windows (ADR-01)
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("DarkFactoryApp")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = Path(__file__).parent / "static"
DATA_DIR = BASE_DIR / "data"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup telemetry and graceful shutdown."""
    runner.broadcast_log("🎬 DarkFactory Cinema Dashboard starting on http://localhost:8502", "SYSTEM")
    yield
    runner.broadcast_log("🛑 DarkFactory Cinema Dashboard shutting down.", "SYSTEM")
    for task_name in list(runner._running_tasks.keys()):
        runner.terminate_task(task_name)


app = FastAPI(
    title="DarkFactory Cinema Dashboard",
    description="High-Retention Faceless YouTube Dark Channel Production Cockpit",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for cross-domain orchestration between StockCont (:8501) and DarkFactory (:8502)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── SPA Entry Point ──────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the Single Page Application."""
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="SPA index.html not found.")
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


# ── Cockpit Status & Telemetry ────────────────────────

@app.get("/api/status")
async def get_status():
    """Full system telemetry: KPIs, daemon state, quota, and active tasks."""
    kpis = readers.get_kpis()
    active_tasks = {
        name: runner._task_meta.get(name, {"status": "running"})
        for name in runner._running_tasks.keys()
    }
    return {
        "kpis": kpis,
        "active_tasks": active_tasks,
        "stockcont_dashboard_url": "http://localhost:8501"
    }


# ── Screenplay & Nolan Director ───────────────────────

@app.get("/api/screenplays")
async def list_screenplays():
    """Retrieves all generated Nolan screenplays and research dossiers."""
    return readers.get_screenplays()


@app.post("/api/screenplay")
async def save_screenplay(req: schemas.ScreenplaySaveRequest):
    """Saves or updates a screenplay JSON file atomically."""
    target_file = DATA_DIR / "scripts" / f"nolan_{req.topic.lower().replace(' ', '_')[:30]}.json"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    import json
    tmp = target_file.with_suffix(f".tmp.{os.getpid()}")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(req.screenplay_data, f, indent=2, ensure_ascii=False)
    tmp.replace(target_file)
    runner.broadcast_log(f"💾 Screenplay for '{req.topic}' saved successfully.", "INFO")
    return {"status": "saved", "file": target_file.name}


# ── Visual Queues & Prompts ───────────────────────────

@app.get("/api/visual-queues")
async def list_visual_queues():
    """Lists prompts queued for Google Flow (Veo 3.1 & Omni 1.2) and RunningHub."""
    return readers.get_visual_queues()


# ── Sound Lab & Audio Library ─────────────────────────

@app.get("/api/audio-library")
async def list_audio_library():
    """Groups available stems (Voice, OST Lyria, Foley, Master) for Web Audio mixer."""
    return readers.get_audio_library()


# ── 1-Click Approval Queue & Lançamento ───────────────

@app.get("/api/approval-queue")
async def list_approval_queue():
    """Lists ready documentaries with A/B/C thumbnails, SEO package, and Green Dollar pre-flight."""
    return readers.get_approval_queue()


@app.post("/api/approval-action")
async def handle_approval_action(req: schemas.ApprovalActionRequest):
    """Executes publication decision: Unlisted, Public, or Quarantine."""
    daemon_state = readers.read_daemon_state()
    queue = daemon_state.get("pending_approval_queue", [])

    if req.action == "publish_unlisted":
        runner.broadcast_log(f"🚀 Publishing episode '{req.video_id}' as UNLISTED on YouTube...", "ACTION")
        # Update state
        daemon_state["completed_episodes"].append({
            "video_id": req.video_id,
            "published_at": str(os.path.getmtime(DATA_DIR / "output")),
            "visibility": "unlisted",
            "selected_thumbnail": req.selected_thumbnail
        })
        if req.video_id in queue:
            queue.remove(req.video_id)
        readers.save_daemon_state(daemon_state)
        return {"status": "success", "action": "published_unlisted", "video_id": req.video_id}

    elif req.action == "publish_public":
        runner.broadcast_log(f"🌟 Publishing episode '{req.video_id}' as PUBLIC on YouTube!", "ACTION")
        daemon_state["completed_episodes"].append({
            "video_id": req.video_id,
            "visibility": "public",
            "selected_thumbnail": req.selected_thumbnail
        })
        if req.video_id in queue:
            queue.remove(req.video_id)
        readers.save_daemon_state(daemon_state)
        return {"status": "success", "action": "published_public", "video_id": req.video_id}

    elif req.action == "reject_quarantine":
        runner.broadcast_log(f"⚠️ Moving '{req.video_id}' to Quarantine. Notes: {req.quarantine_notes}", "WARN")
        q_dir = DATA_DIR / "quarantine" / f"rejected_{req.video_id}"
        q_dir.mkdir(parents=True, exist_ok=True)
        import json
        with open(q_dir / "quarantine_report.json", "w", encoding="utf-8") as f:
            json.dump({
                "video_id": req.video_id,
                "reason": req.quarantine_notes or "Rejected by human reviewer via Dashboard",
                "timestamp": str(os.path.getmtime(q_dir))
            }, f, indent=2)
        if req.video_id in queue:
            queue.remove(req.video_id)
        readers.save_daemon_state(daemon_state)
        return {"status": "quarantined", "video_id": req.video_id}

    raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}")


@app.get("/api/download-package/{video_id}")
async def download_package(video_id: str):
    """Generates an in-memory ZIP package containing the master video, subtitles, thumbnails, and SEO."""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_STORED) as zf:
        # Add video if exists
        vid_path = DATA_DIR / "output" / f"{video_id}.mp4"
        if not vid_path.exists():
            matches = list((DATA_DIR / "output").glob(f"*{video_id}*.mp4"))
            if matches:
                vid_path = matches[0]

        if vid_path.exists():
            zf.write(vid_path, arcname=f"video/{vid_path.name}")

        # Add Subtitles
        sub_dir = DATA_DIR / "subtitles"
        if sub_dir.exists():
            for s in sub_dir.glob("*.srt"):
                zf.write(s, arcname=f"subtitles/{s.name}")

        # Add SEO Package
        pkg_dir = DATA_DIR / "processed" / "algorithm_packages"
        if pkg_dir.exists():
            for p in pkg_dir.glob("*.json"):
                zf.write(p, arcname=f"seo/{p.name}")

        # Add Dispute Kit
        dk_dir = DATA_DIR / "processed" / "dispute_kits"
        if dk_dir.exists():
            for dk in dk_dir.glob("*.txt"):
                zf.write(dk, arcname=f"compliance/{dk.name}")

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=darkfactory_{video_id}_package.zip"}
    )


# ── Quarantine & Discard Inspection ───────────────────

@app.get("/api/quarantine")
async def list_quarantine():
    """Returns quarantined items with detailed diagnosis."""
    return readers.get_quarantine_reports()


# ── Modular Execution & Daemon Control ────────────────

@app.post("/api/run-phase")
async def run_phase(req: schemas.PhaseRunRequest):
    """Executes an individual pipeline phase."""
    res = runner.execute_phase(req.phase, req.topic)
    return res


@app.post("/api/trigger-topic")
async def trigger_topic(req: schemas.TopicTriggerRequest):
    """Initiates a full autonomous production cycle on a given topic."""
    res = runner.execute_topic_production(req.topic, dry_run=req.dry_run)
    return res


@app.post("/api/daemon-control")
async def daemon_control(req: schemas.DaemonControlRequest):
    """Controls the 24/7 background supervisor daemon."""
    res = runner.control_daemon(req.action)
    return res


# ── Real-Time SSE Log Streaming ───────────────────────

@app.get("/api/stream-logs")
async def stream_logs():
    """Streams live log events to the frontend console."""
    return StreamingResponse(
        runner.log_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# ── Media Serving Endpoints ───────────────────────────

@app.get("/api/media/audio/{filename}")
async def serve_audio(filename: str):
    """Streams audio stem files."""
    path = DATA_DIR / "audio" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio stem not found.")
    return FileResponse(path)


@app.get("/api/media/audio/mastered/{filename}")
async def serve_audio_mastered(filename: str):
    """Streams mastered audio stem files."""
    path = DATA_DIR / "audio" / "mastered" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Mastered audio not found.")
    return FileResponse(path)


@app.get("/api/media/video/{filename}")
async def serve_video(filename: str, request: Request):
    """Streams video file with support for HTTP partial content (Range requests)."""
    path = DATA_DIR / "output" / filename
    if not path.exists():
        # Fallback to broll if found
        path = DATA_DIR / "broll" / filename
        if not path.exists():
            raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(path, media_type="video/mp4")


@app.get("/api/media/subtitles/{filename}")
async def serve_subtitles(filename: str):
    """Serves SRT subtitle tracks."""
    path = DATA_DIR / "subtitles" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Subtitle file not found.")
    return FileResponse(path, media_type="text/plain; charset=utf-8")


@app.get("/api/media/broll/{filename}")
async def serve_broll(filename: str):
    """Serves b-roll preview frames and thumbnail candidates."""
    path = DATA_DIR / "broll" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="B-roll frame not found.")
    media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(path, media_type=media_type)
