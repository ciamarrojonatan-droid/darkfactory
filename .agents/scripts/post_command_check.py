#!/usr/bin/env python3
"""PostToolUse hook: auto-check run_command exit codes.

Reads the tool call from stdin. If the command failed (error field present),
logs the error to stderr for diagnostics.
Always outputs empty JSON object {} to allow the model to see the error and auto-correct.

Contract: PostToolUse -> input has toolCall, stepIdx, error (optional).
           Output: empty JSON object {}.
"""
import json
import sys


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

    error = payload.get("error", "")

    if error:
        tool_call = payload.get("toolCall", {})
        command = tool_call.get("args", {}).get("CommandLine", "<unknown>")
        print(
            f"[hook:auto-error-recovery] Command failed: {command!r} -> {error}",
            file=sys.stderr,
        )

    print(json.dumps({}))


if __name__ == "__main__":
    main()
