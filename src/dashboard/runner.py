"""Process runner and real-time SSE task orchestrator for the DarkFactory Dashboard.

Spawns non-blocking asynchronous pipeline jobs, captures stdout/stderr,
and streams live log events to the frontend via Server-Sent Events (SSE).
"""

from __future__ import annotations

import asyncio
import collections
import datetime
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

logger = logging.getLogger("DarkFactoryRunner")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"
PYTHON_EXE = sys.executable

# In-memory log buffer holding recent events
_log_history: collections.deque = collections.deque(maxlen=1000)
_log_listeners: List[asyncio.Queue] = []
_running_tasks: Dict[str, subprocess.Popen] = {}
_task_meta: Dict[str, Dict] = {}


def broadcast_log(message: str, level: str = "INFO") -> None:
    """Stores log entry and broadcasts to all active SSE queues."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{now}] [{level}] {message}"
    _log_history.append(entry)

    # Deliver to connected SSE clients
    for q in list(_log_listeners):
        try:
            q.put_nowait(entry)
        except Exception:
            pass


async def log_stream_generator() -> AsyncGenerator[str, None]:
    """Yields recent history followed by real-time log events."""
    q: asyncio.Queue = asyncio.Queue()
    _log_listeners.append(q)

    try:
        # Replay past logs
        for prev in list(_log_history):
            yield f"data: {prev}\n\n"

        while True:
            msg = await q.get()
            yield f"data: {msg}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        if q in _log_listeners:
            _log_listeners.remove(q)


def is_task_running(task_name: str) -> bool:
    """Checks if a named task is currently executing."""
    proc = _running_tasks.get(task_name)
    if not proc:
        return False
    if proc.poll() is None:
        return True
    return False


def terminate_task(task_name: str) -> bool:
    """Terminates an active task."""
    proc = _running_tasks.get(task_name)
    if proc and proc.poll() is None:
        try:
            proc.terminate()
            broadcast_log(f"Process {task_name} received terminate signal.", "WARN")
            time.sleep(0.5)
            if proc.poll() is None:
                proc.kill()
            return True
        except Exception as e:
            logger.error(f"Failed to terminate task {task_name}: {e}")
    return False


def _run_cmd_background(task_name: str, cmd: List[str], cwd: Optional[Path] = None) -> None:
    """Internal target for threading to spawn and monitor process output."""
    broadcast_log(f"🚀 Spawning [{task_name}]: {' '.join(cmd)}", "INFO")
    _task_meta[task_name] = {
        "command": cmd,
        "started_at": datetime.datetime.now().isoformat(),
        "status": "running"
    }

    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd or BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env
        )
        _running_tasks[task_name] = proc

        # Stream lines in real-time
        if proc.stdout:
            for line in iter(proc.stdout.readline, ""):
                if not line:
                    break
                broadcast_log(line.rstrip(), "OUTPUT")

        proc.wait()
        exit_code = proc.returncode
        _task_meta[task_name]["status"] = "success" if exit_code == 0 else "failed"
        _task_meta[task_name]["exit_code"] = exit_code

        if exit_code == 0:
            broadcast_log(f"✅ [{task_name}] Completed successfully.", "SUCCESS")
        else:
            broadcast_log(f"❌ [{task_name}] Exited with code {exit_code}.", "ERROR")

    except Exception as e:
        broadcast_log(f"💥 [{task_name}] Exception during execution: {e}", "CRITICAL")
        _task_meta[task_name]["status"] = "error"
    finally:
        _running_tasks.pop(task_name, None)


def execute_topic_production(topic: str, dry_run: bool = False) -> Dict[str, Any]:
    """Launches full episode production cycle for a chosen topic."""
    task_name = "full_production_cycle"
    if is_task_running(task_name):
        return {"status": "error", "message": "A production cycle is already in progress."}

    # Use run_pilot_pipeline or daemon cycle
    script_path = BASE_DIR / "run_pilot_pipeline.py"
    if not script_path.exists():
        script_path = SRC_DIR / "daemon_darkfactory.py"

    cmd = [PYTHON_EXE, str(script_path)]
    if dry_run:
        cmd.append("--dry-run")

    t = threading.Thread(target=_run_cmd_background, args=(task_name, cmd), daemon=True)
    t.start()
    return {"status": "started", "task_name": task_name, "topic": topic}


def execute_phase(phase: int, topic: Optional[str] = None) -> Dict[str, Any]:
    """Executes a single modular pipeline phase."""
    task_name = f"phase_{phase}_execution"
    if is_task_running(task_name):
        return {"status": "error", "message": f"Phase {phase} is already executing."}

    default_topic = topic or "1983 Soviet nuclear false alarm incident"

    if phase == 1:
        # Research
        cmd = [PYTHON_EXE, str(SRC_DIR / "research_engine.py"), "--topic", default_topic]
    elif phase == 2:
        # Nolan Screenplay
        cmd = [PYTHON_EXE, str(SRC_DIR / "nolan_director.py"), "--topic", default_topic]
    elif phase == 3:
        # Video Render
        cmd = [PYTHON_EXE, str(SRC_DIR / "render_pilot_video.py")]
    elif phase == 4:
        # Audio Stem Mixing & Master
        cmd = [PYTHON_EXE, str(SRC_DIR / "audio_mixer_master.py")]
    elif phase == 5:
        # Algorithm Booster & SEO
        cmd = [PYTHON_EXE, str(SRC_DIR / "youtube_algorithm_booster.py"), "--topic", default_topic]
    else:
        return {"status": "error", "message": f"Invalid phase {phase}"}

    t = threading.Thread(target=_run_cmd_background, args=(task_name, cmd), daemon=True)
    t.start()
    return {"status": "started", "task_name": task_name, "phase": phase}


def control_daemon(action: str) -> Dict[str, Any]:
    """Controls the 24/7 background supervisor daemon."""
    task_name = "supervisor_daemon_24_7"

    if action == "start":
        if is_task_running(task_name):
            return {"status": "already_running", "message": "Daemon 24/7 is already active."}
        cmd = [PYTHON_EXE, str(SRC_DIR / "daemon_darkfactory.py")]
        t = threading.Thread(target=_run_cmd_background, args=(task_name, cmd), daemon=True)
        t.start()
        return {"status": "started", "message": "Daemon 24/7 launched in continuous mode."}

    elif action == "stop":
        if not is_task_running(task_name):
            return {"status": "not_running", "message": "Daemon 24/7 is not currently running."}
        success = terminate_task(task_name)
        return {"status": "stopped" if success else "failed", "message": "Daemon termination requested."}

    elif action == "run_once":
        if is_task_running(task_name):
            return {"status": "error", "message": "Daemon is already running."}
        cmd = [PYTHON_EXE, str(SRC_DIR / "daemon_darkfactory.py"), "--once"]
        t = threading.Thread(target=_run_cmd_background, args=(task_name, cmd), daemon=True)
        t.start()
        return {"status": "started", "message": "Daemon single-cycle execution started."}

    return {"status": "error", "message": f"Unknown action: {action}"}


async def run_narration_task(
    script: str,
    emotion: Optional[str] = None,
    speed: float = 1.0,
) -> Dict[str, Any]:
    """Starts CosyVoice Account 4 narration generation in a background thread."""
    import uuid

    task_name = f"narration-{uuid.uuid4().hex[:8]}"
    cmd = [PYTHON_EXE, "-m", "src.factory.runninghub_bot", "--account", "4", "--script", script]
    if emotion:
        cmd.extend(["--emotion", emotion])
    if speed != 1.0:
        cmd.extend(["--speed", str(speed)])
    t = threading.Thread(target=_run_cmd_background, args=(task_name, cmd), daemon=True)
    t.start()
    return {"success": True, "message": "CosyVoice narration task started", "task_id": task_name}
