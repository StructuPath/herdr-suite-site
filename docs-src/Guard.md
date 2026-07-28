# 🛡️ Guard (`structupath.guard`)

**Supporting text-policy capability.** Guard is an **advisory, best-effort** cross-agent command policy layer for Herdr. It audits and alerts on matching terminal text and may interrupt visible shell input, but it is not a sandbox or authorization boundary for agent TUIs.

Repo: [StructuPath/herdr-guard](https://github.com/StructuPath/herdr-guard) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-guard#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.1.1` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `7327dc4f310987e05059a20cec7d8fc50bbf0cc5` |

The `v0.1.1` tag target passed sequential one-shot RPC, dedicated subscription, reconnect, terminal rendering, replay suppression, and default/named-session recovery checks on Herdr 0.7.5/protocol 17. Guard records an interrupt request as accepted or failed; neither result proves command prevention.

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.guard.open` | Open the policy/activity dashboard |
| `structupath.guard.pause` | Pause policy actions for 15 minutes while continuing to audit |
| `structupath.guard.resume` | Resume policy actions immediately |
| `structupath.guard.test` | Dry-run text against the active policy without executing it |
| `structupath.guard.reset-rules` | Back up and reseed the default rules |

## Honest coverage contract

| Pane | Guard sees | Interrupt guarantee |
| --- | --- | --- |
| Interactive zsh/bash | Typed, unsubmitted input | Best-effort `ctrl+c` request; prevention unknown |
| Raw/no-echo shell | No typed input | None; `stty -echo` can be alerted |
| Agent TUIs (Pi/Claude/Codex) | Rendered terminal text only | Usually none; native harness controls remain authoritative |
| Logs/builds | Printed output | None unless the pane is classified as a shell |
| Herdr popups | Nothing in the pinned release | Blind spot |

Guard performs text matching, not intent analysis. An agent running as the same user can disable the plugin, use unseen channels, or act outside observed terminal text. Use native agent hooks, sandboxing, and operating-system controls for authoritative enforcement.

## Policy and trust

Rules live at `$HERDR_PLUGIN_CONFIG_DIR/rules.json` and support `audit`, `alert`, and `interrupt` severities with regex or substring matching. Workspace `.herdr-guard.json` rules are capped at `alert`; repository-controlled regex and interrupt rules are rejected.

The plugin itself is ordinary local code with the user's privileges. Review the source and policy before use, and protect audit logs because they can contain sensitive metadata even after redaction.
