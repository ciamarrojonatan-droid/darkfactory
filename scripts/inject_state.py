#!/usr/bin/env python3
"""PreInvocation hook: inject pipeline state context before each model turn.

Reads state.md from the project root and injects it as an ephemeral message
so the model always has fresh pipeline status without permanently bloating
the conversation history.

Contract: PreInvocation -> input has invocationNum, common fields.
           Output: { "injectSteps": [...] }
"""
import json
import os
import sys


def find_project_root() -> str:
    """Find the project root by locating state.md or package.json or walking up."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current and os.path.dirname(current) != current:
        if os.path.isfile(os.path.join(current, "state.md")) or os.path.isfile(os.path.join(current, "package.json")):
            return current
        current = os.path.dirname(current)
    # Default fallback: two levels up from .agents/scripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))


PROJECT_ROOT = find_project_root()
STATE_FILE = os.path.join(PROJECT_ROOT, "state.md")


def read_state() -> str:
    """Read state.md, returning a fallback message if missing."""
    if not os.path.isfile(STATE_FILE):
        return "⚠️ state.md not found. Run /status to generate pipeline state."

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return "⚠️ state.md is empty. Run /status to populate."
        return content
    except Exception as exc:
        return f"⚠️ Error reading state.md: {exc}"


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            print(json.dumps({}))
            return
        payload = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        print(json.dumps({}))
        return

    invocation_num = payload.get("invocationNum", 0)

    # Only inject state on the first few invocations to avoid noise
    # After invocation 5, skip injection unless state changed
    if invocation_num > 5:
        print(json.dumps({}))
        return

    state_content = read_state()

    # Truncate if too long (keep under 2000 chars for ephemeral)
    if len(state_content) > 2000:
        state_content = state_content[:1997] + "..."

    result = {
        "injectSteps": [
            {
                "ephemeralMessage": (
                    f"📊 **Pipeline State** (auto-injected):\n\n{state_content}"
                )
            }
        ]
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
