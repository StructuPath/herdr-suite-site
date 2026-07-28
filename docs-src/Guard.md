# 🛡️ Guard (`structupath.guard`)

**Supporting text-policy capability.** Guard is an **advisory, best-effort** cross-agent command policy layer for Herdr. It audits and alerts on matching terminal text and may interrupt visible shell input, but it is not a sandbox or authorization boundary for agent TUIs.

Repo: [StructuPath/herdr-guard](https://github.com/StructuPath/herdr-guard) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-guard#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.1.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `pending transport hotfix` |
| Evidence commit | `fa8ebcaaf6731976b9c208ebb4bcd61339deac97` |

> **Compatibility evidence withdrawn:** the pinned `0.1.0` client was later shown to fail a second Herdr 0.7.5 RPC because it reused a socket that Herdr closes after one response. The preserved one-shot RPC repair must be committed, live-smoked, and released before 0.7.5 is listed as explicitly tested again.

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.guard.open` | Open the policy/activity dashboard |
| `structupath.guard.pause` | Pause enforcement for 15 minutes while continuing to audit |
| `structupath.guard.resume` | Resume enforcement immediately |
| `structupath.guard.test` | Dry-run text against the active policy without executing it |
| `structupath.guard.reset-rules` | Back up and reseed the default rules |

## Honest coverage contract

| Pane | Guard sees | Interrupt guarantee |
| --- | --- | --- |
| Interactive zsh/bash | Typed, unsubmitted input | Strong pre-execution `ctrl+c` attempt |
| Raw/no-echo shell | No typed input | None; `stty -echo` can be alerted |
| Agent TUIs (Pi/Claude/Codex) | Rendered terminal text only | Incidental and best-effort; native harness controls remain authoritative |
| Logs/builds | Printed output | Best-effort while the process runs |
| Herdr popups | Nothing in the pinned release | Blind spot |

Guard performs text matching, not intent analysis. An agent running as the same user can disable the plugin, use unseen channels, or act outside observed terminal text. Use native agent hooks, sandboxing, and operating-system controls for authoritative enforcement.

## Policy and trust

Rules live at `$HERDR_PLUGIN_CONFIG_DIR/rules.json` and support `audit`, `alert`, and `interrupt` severities with regex or substring matching. Workspace `.herdr-guard.json` rules are capped at `alert`; repository-controlled regex and interrupt rules are rejected.

The plugin itself is ordinary local code with the user's privileges. Review the source and policy before use, and protect audit logs because they can contain sensitive metadata even after redaction.
