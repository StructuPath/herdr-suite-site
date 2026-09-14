# 🛡️ Guard (`structupath.guard`)

**Supporting text-policy capability.** Guard has two paths: an advisory pane watcher that audits, alerts, and attempts interrupts, and an optional harness reporter that evaluates reported Bash commands before execution. Neither path is a sandbox or a same-user security boundary.

Repo: [StructuPath/herdr-guard](https://github.com/StructuPath/herdr-guard) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-guard#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.2.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `12e3fd6f7d65bd4c846f5da23cb2f24ee617cd48` |

Historical `v0.1.1` evidence covers sequential one-shot RPC, dedicated subscription, reconnect, terminal rendering, replay suppression, and default/named-session recovery on Herdr 0.7.5/protocol 17. It does not certify the new reporter in a live Herdr session. Guard records an interrupt request as accepted or failed; neither result proves command prevention.

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.guard.open` | Open the policy/activity dashboard |
| `structupath.guard.pause` | Pause policy actions for 15 minutes while continuing to audit |
| `structupath.guard.resume` | Resume policy actions immediately |
| `structupath.guard.test` | Dry-run text against the active policy without executing it |
| `structupath.guard.reset-rules` | Back up and reseed the default rules |

## First run

Use Herdr `>=0.7.5`, Node.js `>=20.10`, Python `>=3.11`, and Bash. Locking uses `lockf` on macOS or `flock` on Linux. Check which executable your shell selects before installing:

```bash
command -v herdr
herdr --version
herdr plugin install StructuPath/herdr-guard
herdr plugin list
herdr plugin action list
```

Open Guard and use its Test action to evaluate sample text without executing it. Installation does not automatically configure a harness hook. The source checkout also provides `npm run build`, `npm run validate`, and the read-only `npm run doctor` setup check.

## Honest pane coverage contract

| Pane | Guard sees | Interrupt guarantee |
| --- | --- | --- |
| Interactive zsh/bash | Typed, unsubmitted input | Best-effort `ctrl+c` request; prevention unknown |
| Raw/no-echo shell | No typed input | None; `stty -echo` can be alerted |
| Agent TUIs (Pi/Claude/Codex) | Rendered terminal text only | Usually none; native harness controls remain authoritative |
| Logs/builds | Printed output | None unless the pane is classified as a shell |
| Herdr popups | Nothing in the pinned release | Blind spot |

Guard performs text matching, not intent analysis. An agent running as the same user can disable the plugin, use unseen channels, or act outside observed terminal text. Use native agent hooks, sandboxing, and operating-system controls for authoritative enforcement.

## Optional harness reporter

Version 0.2.0 includes a Claude `PreToolUse` Bash hook adapter. Wire it explicitly using the repository README instructions. The hook reports raw command text and its working directory to Guard's local Unix socket; policy uses the reported directory. Interrupt-tier matches return a deny decision, alert-tier matches request permission, and other commands are allowed.

The adapter fails open if the socket is missing, times out, or returns an invalid response. Audit records cannot prove the harness honored a decision. This is a command-text policy check, not prompt analysis or a substitute for native enforcement.

The socket defaults to `$XDG_STATE_HOME/herdr-guard/reporter.sock`, falling back to `~/.local/state/herdr-guard/reporter.sock`, separate from plugin state, in a private directory. Run only one owner per socket; a `HERDR_GUARD_REPORTER_SOCKET` override must agree between Guard and the hook.

## Policy and trust

Rules live at `$HERDR_PLUGIN_CONFIG_DIR/rules.json` and support `audit`, `alert`, and `interrupt` severities with regex or substring matching. Workspace `.herdr-guard.json` rules are capped at `alert`; repository-controlled regex and interrupt rules are rejected.

The plugin itself is ordinary local code with the user's privileges. Review the source and policy before use, and protect audit logs because they can contain sensitive metadata even after redaction.

## Upgrading

Upgrades preserve existing `rules.json`. New default patterns therefore do not silently replace a reviewed policy. To adopt the defaults, review them first, then explicitly use Reset rules, which backs up the existing file before reseeding. Version 0.2.0 includes broader destructive-command, exfiltration, tampering, and evasion patterns. A force-with-lease push is audit-tier in the defaults, not silently ignored.
