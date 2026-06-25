#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from discuss_mode import BLOCK_REASON  # noqa: E402
from discuss_mode import GUIDANCE  # noqa: E402
from discuss_mode import handle_pre_tool_use  # noqa: E402
from discuss_mode import handle_user_prompt_submit  # noqa: E402


class DiscussModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.previous_state_dir = os.environ.get("DISCUSS_MODE_STATE_DIR")
        os.environ["DISCUSS_MODE_STATE_DIR"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.previous_state_dir is None:
            os.environ.pop("DISCUSS_MODE_STATE_DIR", None)
        else:
            os.environ["DISCUSS_MODE_STATE_DIR"] = self.previous_state_dir

    def test_discuss_injects_guidance(self) -> None:
        output = handle_user_prompt_submit(user_prompt("review this /discuss please"))

        self.assertEqual(
            output,
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": GUIDANCE,
                }
            },
        )

    def test_discuss_marker_does_not_match_larger_token(self) -> None:
        output = handle_user_prompt_submit(user_prompt("review /discussion please"))

        self.assertIsNone(output)

    def test_regular_prompt_does_not_inject_guidance(self) -> None:
        output = handle_user_prompt_submit(user_prompt("review this"))

        self.assertIsNone(output)

    def test_discuss_apply_patch_is_blocked(self) -> None:
        handle_user_prompt_submit(user_prompt("/discuss review this"))

        output = handle_pre_tool_use(pre_tool_use("apply_patch", "fake patch"))

        self.assertEqual(output, deny_output())

    def test_discuss_allows_shell_commands(self) -> None:
        handle_user_prompt_submit(user_prompt("/discuss review this"))

        for command in ("rg TODO", "sed -i 's/a/b/' file.txt", "cat notes.md > output.md"):
            with self.subTest(command=command):
                output = handle_pre_tool_use(pre_tool_use("Bash", command))
                self.assertIsNone(output)

    def test_prompt_after_discuss_without_discuss_is_not_blocked(self) -> None:
        handle_user_prompt_submit(user_prompt("/discuss review this", turn_id="turn-1"))
        first_output = handle_pre_tool_use(
            pre_tool_use("apply_patch", "fake patch", turn_id="turn-1")
        )
        handle_user_prompt_submit(user_prompt("now implement it", turn_id="turn-2"))

        second_output = handle_pre_tool_use(
            pre_tool_use("apply_patch", "fake patch", turn_id="turn-2")
        )

        self.assertEqual(first_output, deny_output())
        self.assertIsNone(second_output)


def user_prompt(prompt: str, *, turn_id: str = "turn-1") -> dict[str, object]:
    return {
        "session_id": "session-1",
        "turn_id": turn_id,
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
    }


def pre_tool_use(tool_name: str, command: str, *, turn_id: str = "turn-1") -> dict[str, object]:
    return {
        "session_id": "session-1",
        "turn_id": turn_id,
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"command": command},
        "tool_use_id": "tool-1",
    }


def deny_output() -> dict[str, object]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": BLOCK_REASON,
        }
    }


if __name__ == "__main__":
    unittest.main()
