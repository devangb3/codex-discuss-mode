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

Include `/discuss` as an inline marker in your prompt. Avoid placing it at
the very start of the prompt because Codex reserves leading `/...` input for
slash commands:

```text
Review this design /discuss before we implement it.
```

The marker is case-sensitive and applies only to the current turn. Prefer using
it after some leading text, such as `Review this design /discuss`, rather than
starting the prompt with `/discuss`.

## Why this exists

Codex Default Mode is optimized for execution. That is great when the user wants implementation, but there is a common workflow gap: sometimes the user wants to brainstorm, clarify, or review a design without entering full Plan Mode and without letting Codex immediately edit files.

Related community discussions include:

- A request for a clarification-first mode / native ask-human tool for ambiguous or risky work.
- A request for safer structured questions in Default Mode without switching fully into Plan Mode.
- Reports that Default Mode’s “assume and execute” behavior can conflict with “understand first” workflows.
- Reports of Plan Mode being sticky or difficult to exit, which makes a lighter per-turn discuss marker useful.

`/discuss` is a small userland workaround: it marks the current turn as read-only brainstorming and blocks Codex’s primary edit path, `apply_patch`, with feedback telling the model not to mutate and to continue discussion instead.

This is not a full sandbox. It does not guarantee blocking every possible shell-based mutation. It is an intent guardrail for Codex’s normal editing flow.
