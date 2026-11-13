#!/usr/bin/env python3
"""Stop hook: enforce mandatory git commit and git push before agent completes.

Contract: Stop -> input has executionNum, terminationReason, fullyIdle, error.
          Output: { "decision": "continue"|"stop", "reason": "..." }
"""
import json
import os
import subprocess
import sys


# Reasons where we should NOT force continuation
TERMINAL_REASONS = {
    "USER_CANCELED",
    "MAX_TOKEN_BUDGET_EXCEEDED",
    "MAX_FORCED_INVOCATIONS",
    "TERMINAL_CUSTOM_HOOK",
}


def find_project_root() -> str:
    """Find the project root by locating package.json or walking up."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current and os.path.dirname(current) != current:
        if os.path.isfile(os.path.join(current, "package.json")) or os.path.isdir(os.path.join(current, ".git")):
            return current
        current = os.path.dirname(current)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({"decision": "stop"}))
            return
        payload = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        print(json.dumps({"decision": "stop"}))
        return

    termination_reason = payload.get("terminationReason", "")
    execution_num = payload.get("executionNum", 0)

    # Never override user cancellation or hard limits
    if termination_reason in TERMINAL_REASONS:
        print(json.dumps({"decision": "stop"}))
        return

    # Safety: don't loop forever — cap forced continuations
    if execution_num > 10:
        print(
            json.dumps(
                {
                    "decision": "stop",
                    "reason": "Reached max execution count (10). Stopping.",
                }
            )
        )
        return

    # Mandato Permanente de Git Push (AGENTS.md & GEMINI.md)
    # Verifica se há arquivos modificados/untracked ou commits locais não enviados
    project_root = find_project_root()
    if execution_num < 3:
        try:
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            has_uncommitted = bool(status_proc.stdout and status_proc.stdout.strip())

            cherry_proc = subprocess.run(
                ["git", "cherry", "-v", "origin/main"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            has_unpushed = bool(cherry_proc.stdout and cherry_proc.stdout.strip())

            if has_uncommitted or has_unpushed:
                issues = []
                if has_uncommitted:
                    issues.append("arquivos não commitados no working tree")
                if has_unpushed:
                    issues.append("commits locais pendentes de git push")
                reason = (
                    f"⚠️ [HOOK GATE - GIT PUSH MANDATÓRIO] Detectado: {', '.join(issues)}. "
                    "Conforme diretiva mandatória permanente de AGENTS.md e GEMINI.md, "
                    "você DEVE rodar 'git add .', 'git commit' e 'git push origin main' antes de encerrar."
                )
                print(json.dumps({"decision": "continue", "reason": reason}))
                return
        except Exception:
            pass

    # Normal completion — allow stop
    print(json.dumps({"decision": "stop"}))


if __name__ == "__main__":
    main()
