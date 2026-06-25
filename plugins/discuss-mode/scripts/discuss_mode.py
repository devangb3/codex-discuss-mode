#!/usr/bin/env python3
"""Hook helpers for the discuss-mode Codex plugin."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


DISCUSS_MARKER_RE = re.compile(r"(?:^|\s)/discuss(?:\s|$)")
MARKER_TTL_SECONDS = 24 * 60 * 60

GUIDANCE = (
    "The user used /discuss. This turn is brainstorm-only/read-only. Do not "
    "edit files, apply patches, run codegen, formatters, migrations, or any "
    "command intended to change repo-tracked state. You may inspect, search, "
    "read files, run clearly non-mutating checks, and ask clarifying questions. "
    "If the user wants implementation, they can ask in a later turn without "
    "/discuss."
)

BLOCK_REASON = (
    "Blocked because this turn is in /discuss mode. The user wants "
    "brainstorming/read-only discussion only. Ask questions, inspect files, "
    "or propose a plan instead of modifying files."
)

def handle_user_prompt_submit(payload: dict[str, Any]) -> dict[str, Any] | None:
    cleanup_old_markers()
    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not is_discuss_prompt(prompt):
        return None

    write_marker(payload)
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": GUIDANCE,
        }
    }


def handle_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any] | None:
    cleanup_old_markers()
    if not marker_path(payload).is_file():
        return None

    tool_name = payload.get("tool_name")
    if tool_name == "apply_patch":
        return deny()

    return None


def is_discuss_prompt(prompt: str) -> bool:
    return DISCUSS_MARKER_RE.search(prompt) is not None


def deny() -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": BLOCK_REASON,
        }
    }


def write_marker(payload: dict[str, Any]) -> None:
    path = marker_path(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = {
        "session_id": payload.get("session_id"),
        "turn_id": payload.get("turn_id"),
        "created_at": int(time.time()),
    }
    path.write_text(json.dumps(marker, sort_keys=True), encoding="utf-8")


def marker_path(payload: dict[str, Any]) -> Path:
    session_id = str(payload.get("session_id") or "")
    turn_id = str(payload.get("turn_id") or "")
    digest = hashlib.sha256(f"{session_id}:{turn_id}".encode("utf-8")).hexdigest()
    return state_dir() / f"{digest}.json"


def state_dir() -> Path:
    explicit = os.environ.get("DISCUSS_MODE_STATE_DIR")
    if explicit:
        return Path(explicit)
    plugin_data = os.environ.get("PLUGIN_DATA")
    if plugin_data:
        return Path(plugin_data) / "discuss-turns"
    return Path(tempfile.gettempdir()) / "codex-discuss-mode" / "discuss-turns"


def cleanup_old_markers() -> None:
    root = state_dir()
    if not root.is_dir():
        return
    cutoff = time.time() - MARKER_TTL_SECONDS
    for path in root.glob("*.json"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except OSError:
            pass


def run_hook(handler) -> int:
    payload = json.load(sys.stdin)
    output = handler(payload)
    if output is not None:
        print(json.dumps(output, separators=(",", ":")))
    return 0
