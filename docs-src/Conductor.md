# 🎩 Conductor (`structupath.conductor`)

Conductor runs a role-differentiated team—such as builder, validator, and reviewer—as visible Herdr agent panes. An orchestrating agent drives dispatch; completion is a report-file sentinel, not an agent's `idle` state.

Repo: [StructuPath/herdr-conductor](https://github.com/StructuPath/herdr-conductor) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-conductor#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.1.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `d4c6527e36991b234861781af34fe16c7ef16f4b` |

## All five actions

| Action ID | Behavior |
| --- | --- |
| `structupath.conductor.assemble` | Read `.herdr-conductor.json`, create the declared team, and open the board |
| `structupath.conductor.board` | Open the live board with one row per worker |
| `structupath.conductor.status` | Print the board's role/kind/pane/state/cwd data once |
| `structupath.conductor.harvest` | Merge writing-role branches into a Conductor integration worktree, reporting conflicts without forcing |
| `structupath.conductor.stand-down` | Close verified Conductor-owned worker panes while keeping branches and worktrees |

Conductor currently owns its worktree lifecycle and harvest implementation. It does **not** call Swarm to create worktrees or to harvest branches. Swarm is a separate, independently invoked fan-out tool, not a hidden Conductor runtime dependency.

## Minimal supervised quickstart

> **Supervised/manual today.** This example requires a human or trusted orchestrating agent to inspect reports and diffs, approve reconciliation, and handle conflicts. An autonomous supervisor/approval runtime, cross-plugin delegation to Swarm, and cryptographic worker/report attestation are **not implemented prerequisites** in the pinned runtime. Do not describe this flow as unattended or as a security boundary.

1. Start from a clean Git repository and add a reviewed `.herdr-conductor.json` defining a `builder-engine` writing role (using the shipped `builder-engine` template) and at least one review role.
2. Assemble the team and inspect its state:

   ```bash
   herdr plugin action invoke assemble --plugin structupath.conductor
   herdr plugin action invoke status --plugin structupath.conductor
   herdr plugin action invoke board --plugin structupath.conductor
   ```

3. In a trusted orchestrator pane, source the transport, render role prompts, dispatch work, and wait for freshness-checked `<!-- REPORT-COMPLETE -->` sentinels:

   ```bash
   . /path/to/herdr-conductor/scripts/conductor-lib.sh
   conductor_dispatch builder-engine "$(CONDUCTOR_MISSION='Implement the reviewed task.' conductor_render_role builder-engine)"
   conductor_await builder-engine && conductor_collect builder-engine
   ```

4. Review each report, role branch, and test result. Only then invoke reconciliation:

   ```bash
   herdr plugin action invoke harvest --plugin structupath.conductor
   herdr plugin action invoke stand-down --plugin structupath.conductor
   ```

Use the plugin README for the exact role-template/config schema and transport API before running this flow.

## Trust and completion model

Write-capable workers and the orchestrator are trusted same-user principals. Their worktrees isolate changes for review but do not limit filesystem/process access. `read-only` launch flags or agent-native sandbox controls provide the intended reviewer restriction; Guard drops are an audit trail, not a sandbox.

Workers exchange `.conductor/task.md` and `.conductor/report.md`. A worker becoming `idle` can mean it asked a question or finished any turn; only a fresh report containing the completion sentinel satisfies `conductor_await`.
