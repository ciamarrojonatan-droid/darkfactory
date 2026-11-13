#!/usr/bin/env python3
"""SessionStart hook: show pipeline status and pending tasks at session start.

Reads state.md and key DarkFactory directories to build a telemetry summary.
Injected as a systemMessage so it persists in conversation history for the full session.

Contract: SessionStart -> input has common fields.
           Output: { "injectSteps": [...] }
"""
import json
import os
import socket
import sys
from datetime import datetime


def find_project_root() -> str:
    """Find the project root by locating state.md or package.json or walking up."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current and os.path.dirname(current) != current:
        if os.path.isfile(os.path.join(current, "state.md")) or os.path.isfile(os.path.join(current, "package.json")):
            return current
        current = os.path.dirname(current)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))


PROJECT_ROOT = find_project_root()
STATE_FILE = os.path.join(PROJECT_ROOT, "state.md")
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "data", "scripts")
AUDIO_DIR = os.path.join(PROJECT_ROOT, "data", "audio")
FINAL_DIR = os.path.join(PROJECT_ROOT, "data", "final")
QUARANTINE_DIR = os.path.join(PROJECT_ROOT, "data", "quarantine")


def check_dashboard_status(host: str = "127.0.0.1", port: int = 8502) -> str:
    """Check if Cinema Dashboard FastAPI server is responding on port 8502."""
    try:
        with socket.create_connection((host, port), timeout=0.8):
            return "🟢 Online (http://localhost:8502)"
    except Exception:
        return "⚪ Offline (iniciar via run_dashboard.bat)"


def count_files_with_exts(directory: str, extensions: tuple) -> int:
    """Count files with given extensions recursively."""
    if not os.path.isdir(directory):
        return 0
    count = 0
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(extensions):
                count += 1
    return count


def count_directories(directory: str) -> int:
    """Count top-level directories in a path."""
    if not os.path.isdir(directory):
        return 0
    try:
        return len([d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))])
    except Exception:
        return 0


def read_state_summary() -> str:
    """Read the first section of state.md for quick context."""
    if not os.path.isfile(STATE_FILE):
        return "No state.md found."
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[:15]).strip()
    except Exception:
        return "Error reading state.md."


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if raw_input.strip():
            _payload = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        pass

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    dashboard_status = check_dashboard_status()
    scripts_count = count_files_with_exts(SCRIPTS_DIR, (".json", ".txt"))
    audio_count = count_files_with_exts(AUDIO_DIR, (".mp3", ".wav", ".raw"))
    final_videos = count_files_with_exts(FINAL_DIR, (".mp4", ".mov", ".mkv"))
    quarantine_items = count_directories(QUARANTINE_DIR)

    welcome = (
        f"🎬 **DarkFactory Cinema Pipeline Session Started** — {now}\n\n"
        f"## 📊 Telemetria da Esteira Documental\n"
        f"| Métrica / Serviço | Status / Quantidade |\n"
        f"|:---|:---|\n"
        f"| Cinema Dashboard (:8502) | {dashboard_status} |\n"
        f"| Roteiros & Queues (`data/scripts/`) | **{scripts_count}** arquivos |\n"
        f"| Acervo de Áudio & Masters (`data/audio/`) | **{audio_count}** arquivos (narração, Foley, trilhas) |\n"
        f"| Vídeos Renderizados (`data/final/`) | **{final_videos}** renders finais |\n"
        f"| Quarentena QC (`data/quarantine/`) | **{quarantine_items}** ocorrências rastreadas |\n"
        f"| Direção Autoral & Showrunner | Christopher Nolan (`nolan-director.md` ativo) |\n\n"
        f"**Modo Operacional**: Autonomia Total — execução de ponta a ponta, validação contínua e persistência no Git.\n\n"
        f"Use `/status` para inspecionar, `/pipeline` para rodar fases cinematográficas, "
        f"`/deploy` para subir o Dashboard :8502 e `/review` para auditoria de áudio/vídeo."
    )

    result = {
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": welcome
                }
            }
        ]
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
