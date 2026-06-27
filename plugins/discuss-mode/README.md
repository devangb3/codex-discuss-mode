# Discuss Mode Codex Plugin

This plugin adds a lightweight `/discuss` mode using Codex hooks. When the
latest user prompt contains `/discuss`, the current turn is treated as
brainstorm-only/read-only.

The hook blocks `apply_patch`, which is the primary file-editing path for Codex. Shell
commands are not classified or blocked by this plugin.

This is a guardrail, not a security boundary. The injected `/discuss` guidance
is responsible for steering the agent away from implementation, and the
`apply_patch` block catches the common edit path. Rerun the request without
`/discuss` when you want implementation.

## How It Works

- `UserPromptSubmit` checks whether `prompt` contains `/discuss`.
- If detected, it writes a turn-scoped marker under `PLUGIN_DATA` keyed by
  `session_id` and `turn_id`.
- The same hook injects additional context telling Codex that the turn is
  brainstorming/read-only.
- `PreToolUse` checks the marker for the active `turn_id`.
- If the marker exists, `PreToolUse` blocks `apply_patch` with a JSON
  `permissionDecision: "deny"` response.

The marker is keyed by turn, so a later prompt without `/discuss` is not locked.

## Files

- `.codex-plugin/plugin.json` - plugin manifest
- `hooks/hooks.json` - hook declarations discovered by Codex plugin loading
- `scripts/user_prompt_submit.py` - `UserPromptSubmit` hook entrypoint
- `scripts/pre_tool_use.py` - `PreToolUse` hook entrypoint
- `scripts/discuss_mode.py` - shared hook logic
- `tests/test_discuss_mode.py` - script-level tests

## Install

Install or select this plugin folder as a Codex plugin capability root:

```bash
examples/plugins/discuss-mode
```

Codex discovers `hooks/hooks.json` automatically for plugin-bundled hooks. After
installing, trust/enable the discovered hooks when Codex prompts for hook trust.

For a one-off local hook setup, you can also copy this folder outside the repo
and install that copy as a local plugin.

## Usage

Include `/discuss` as an inline marker in a prompt. Avoid placing it at the
very start of the prompt because Codex reserves leading `/...` input for slash
commands:

```text
Review this module /discuss and tell me the risks before we implement anything.
```

The `/discuss` marker is case-sensitive and only applies to the current turn.
Prefer using it after some leading text, such as `Review this module /discuss`,
rather than starting the prompt with `/discuss`. Use a later prompt without
`/discuss` when you want Codex to implement changes.

## Tests

Run the script tests from the repository root:

```bash
python3 examples/plugins/discuss-mode/tests/test_discuss_mode.py
```

The tests cover guidance injection, non-`/discuss` prompts, blocking
`apply_patch`, allowing shell commands, and ensuring the next non-`/discuss`
turn is not blocked.
