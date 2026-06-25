# Codex Discuss Mode

A public Codex plugin marketplace containing `discuss-mode`, a lightweight
hook bundle for `/discuss` turns.

When a prompt contains `/discuss`, the plugin injects read-only brainstorming
guidance for the current turn and blocks the `apply_patch` tool. Shell commands
are not classified or blocked.

## Install

Add this marketplace:

```bash
codex plugin marketplace add devangb3/codex-discuss-mode
```

Install the plugin:

```bash
codex plugin add discuss-mode@devang
```

Start a new Codex session after installing. Codex may ask you to trust the
plugin hook the first time it is discovered.

## Usage

Include `/discuss` anywhere in your prompt:

```text
Review this design /discuss before we implement it.
```

The marker is case-sensitive and applies only to the current turn.
