# Herdr Suite: supervised AgentOps

Herdr-native tools for human-supervised agent work, built and maintained by
[StructuPath](https://github.com/StructuPath). **Explore** is the ready first
workflow. **Deliver** is an attended Stage 3 lifecycle with strict task/report
contracts and approved single-ref apply. Browser and Guard provide supporting visibility and text-policy capabilities.

This repository is the canonical suite documentation source; each plugin README remains the detailed runtime reference.

## See your projects locally

[Console](Console) is a read-only local app for project Git state, tool health, saved run observations, Browser QA summaries, and copyable next commands. From the suite site checkout, run `npm run console -- --demo` for labeled fixtures or `npm run console -- --config /absolute/private/console.json` for explicitly configured projects. It requires Node.js 20 or newer and binds to loopback only.

The public website serves documentation, not a remote controller. Console is separate from the four plugins and does not launch agents, approve work, push, or create pull requests.

## Start with Explore

[Explore with Swarm](Swarm) when you have one bounded coding task and want to compare several implementations. Swarm records a base SHA, gives each agent a separate worktree and branch, reports concrete change counts, and lets the operator preview and harvest a selected candidate.

The operator defines the comparison criterion, reviews diffs and tests, and chooses what lands. Agents commit locally; the operator can explicitly publish a candidate branch or request the GitHub draft PR handoff with SHA-bound validation evidence. PR and CI observation does not approve a merge.

## Deliver is attended

[Deliver with Conductor](Conductor) is an attended Stage 3 workflow: visible
role panes, repository/workspace-bound strict state, immutable task contracts,
private report outboxes, deterministic one-CAS integration, exact-SHA reviewer
and validator gates, operator approval receipts, single-ref apply, and archival stand-down.

Apply receipts are unauthenticated same-user operator records. The pinned runtime
does not provide suite adapters, unattended automation, general automatic recovery,
cryptographic report attestation, or protection against malicious same-UID processes.
Conductor requires exactly Herdr 0.7.5; its manifest minimum is not a promise of
compatibility with later versions.

## Supporting trust capabilities

- [Browser](Browser) launches local Chromium, attaches to an existing automation browser, or shares an agent-browser session. Attach and launch modes offer explicit tab selection and stop forwarding input when the selected tab disappears. The text prompt supports verbatim multiline paste. Its standalone QA runner repeats saved assertions at desktop and mobile viewport sizes with private evidence. Recording is available for agent-browser sessions only. Sessions are a trusted same-user boundary, and artifacts may contain sensitive content.
- [Guard](Guard) observes rendered terminal text with best-effort interrupts and offers an optional pre-execution harness reporter. Its Claude Code hook can deny reported Bash calls but fails open when unavailable; Guard is not a sandbox or protection against same-user bypass.

## Pinned compatibility evidence

| Plugin | ID | Pinned release | Minimum Herdr | Explicitly tested | Purpose |
| --- | --- | --- | --- | --- | --- |
| [Browser](Browser) | `structupath.browser` | `0.8.0` | `0.7.0` | `0.7.4` | Chromium launch, CDP attach, shared sessions, recording, and repeatable QA |
| [Guard](Guard) | `structupath.guard` | `0.2.0` | `0.7.5` | `0.7.5` | Text policy plus optional fail-open harness reporter |
| [Swarm](Swarm) | `structupath.swarm` | `0.5.0` | `0.7.4` | `0.7.4`, `0.7.5` | Parallel candidates, per-slot checks, compare and merge the winner, conflict resolver, and PR publication |
| [Conductor](Conductor) | `structupath.conductor` | `0.4.0` | `0.7.5` | `0.7.5` | Attended Stage 3: exact-SHA gates, preview, approval receipts, and single-ref apply |

Versions are plugin-specific source evidence pinned in [`data/plugins.json`](https://github.com/StructuPath/herdr-suite-site/blob/main/data/plugins.json), not a claim that every plugin was tested on one suite-wide Herdr version. Recorded Herdr versions include retained historical compatibility evidence; they do not certify every new feature. Guard's accepted interrupt requests and harness verdicts do not prove command prevention.

## Composition and supervision boundaries

These plugins can be installed together, but the current runtime is not a single automatic pipeline.

| Component | System provides | Operator remains responsible for |
| --- | --- | --- |
| Explore / Swarm | Worktree fan-out, change counts, previews, guarded harvest | Task bounds, candidate review, tests, slot selection, cleanup |
| Deliver / Conductor | Task-bound roles, exact-SHA gates, preview, receipt-bound local-ref apply, and stand-down | Work direction, assertion review, operator receipts, conflicts, and ambiguous recovery |
| Browser | Chromium launch, external attach, shared-session recording, and repeatable QA | Session privacy, assertion coverage, served build identity, artifact review |
| Guard | Text matching, audit, interrupt attempts, and optional harness verdicts | Hook wiring, fail-open behavior, sandboxing, access control, log protection |

Herdr plugins and write-capable agents run as the same operating-system user. Treat them as **trusted same-user principals**. Worktrees reduce accidental file collisions and make changes reviewable; they are not sandboxes and do not prevent a worker from accessing other same-user files or processes.

## Install by capability

```bash
# Ready first workflow
herdr plugin install StructuPath/herdr-swarm

# Attended Stage 3 delivery (exactly Herdr 0.7.5)
herdr plugin install StructuPath/herdr-conductor

# Supporting visibility and policy
herdr plugin install StructuPath/herdr-browser
herdr plugin install StructuPath/herdr-guard
```

These commands are not a blanket claim about marketplace visibility. Inspect source and manifests before installing local plugins.

## Health checks

```bash
herdr plugin list
herdr plugin action list
herdr plugin log list
herdr status server
```

`plugin list` confirms that a manifest parsed and is enabled; `plugin action list` confirms action registration. See each plugin page for its exact actions, prerequisites, and limits.

## Keep the suite current

In each source checkout, run `npm run build` and `npm run validate` for Browser, Swarm, and Guard; Conductor uses `npm run check`. Browser, Swarm, and Guard also provide a read-only `npm run doctor` to identify missing prerequisites and the selected Herdr binary. Check `command -v herdr`, `herdr --version`, and `herdr status server` when multiple installations exist. The pinned Conductor release still requires exactly 0.7.5; a bounded, isolated 0.9.3 development smoke does not promote that release pin or the default server.

After an upgrade, verify action registration and run one bounded workflow in a separate test repository before larger work. Preserve reviewed Guard rules, explicitly wire any reporter hook, and review Swarm setup hooks and agent presets. Browser already supports Chromium; add a committed QA scenario for the app's critical flow and run it against the intended candidate build at desktop and mobile viewport sizes.

Use the build → validate → fix loop per candidate. Select one Swarm slot at
a clean committed HEAD. Run the checks and Browser QA against that SHA, save
their separate result files outside the worktree, then record the operator's
approved or rejected review for the exact run, slot, and SHA. Supply
`HERDR_SWARM_CANDIDATE_VALIDATION_FILE`,
`HERDR_SWARM_CANDIDATE_BROWSER_QA_FILE`, and
`HERDR_SWARM_CANDIDATE_REVIEW_FILE`; run `harvest-step.sh candidate-status
<slot>` to inspect missing/stale/failed evidence, then explicitly run
`harvest-step.sh publish-candidate-pr <slot>` only if approved. This strict verb
refuses nonpassing or mismatched inputs and dirty slot work before a push;
legacy `publish-pr` intentionally remains permissive and is not this gate.
Inspect `pr-status <slot>`, the actual GitHub head, and remote CI before any
merge decision. The result files are caller-supplied, not authenticated
attestations; Browser QA's commit field does not prove the served app was built
from it. The local smoke used a bare Git remote and stub GitHub transport, not
a real PR. These are operator-driven steps, not an automatic cross-plugin
pipeline or merge/apply authorization.

For each change, repeat build, relevant tests, and workflow validation until passing, then publish a reviewable PR. Update these guides and the pinned manifest evidence together whenever versions, actions, or supported behavior change.

The suite does not remotely control repositories or automatically update
third-party plugins. Herdr plugins execute as the local user with access to
their environment and Herdr API; a marketplace listing is not a security
review. Any future remote control needs an independently reviewed
authentication/authorization and network exposure design, explicit per-action
approval, scoped credentials, audit and revocation, and a rollback plan.
Automated plugin updates need reviewed, pinned source and artifact provenance,
isolated compatibility checks, and an operator-selected rollout. Console's
copy-only commands and saved observations grant neither capability.

## Optional standalone review companion

[`persiyanov/herdr-reviewr` v0.41.0](https://github.com/persiyanov/herdr-reviewr/tree/f05568594926352196a77c0d15cc07cc259cdf2e)
is **not** a suite dependency or an installed production plugin. The pinned
commit is `f05568594926352196a77c0d15cc07cc259cdf2e`; the macOS
Apple-silicon release archive SHA-256 is
`89f203857a2c6c2be7ad9dc8813f77eafe1ce5051c5156ae414040352c2268d4`.
Its tag and commit are unsigned. An isolated, network-denied disposable-repo
pilot ran the extracted standalone binary, displayed an untracked file's diff,
switched between Changes and Files, and exited cleanly. It did not exercise
review comments, agent send, PR operations, or its plugin install hook. Do not
infer those paths work or that this binary has approval authority. For a
manual review, inspect the pinned source/artifact first and run the standalone
binary against a selected repository without installing the plugin; record an
operator decision separately for Swarm's strict handoff.

The existing `~Agent Harness` workspace demonstrates a useful **role pattern**:
one builder, independent reviewer, QA, research, and adversarial reviewer
report to an orchestrator. A supervised suite run can use a Swarm slot for the
builder, distinct reviewer/validator work, Browser QA for the exact candidate,
and an optional adversarial pass. The orchestrator inspects the reports and
records the operator's decision; agent messages and review UI alone cannot
approve a draft handoff, merge a PR, or authorize Conductor apply. This is a
manual role pattern, not an automatic five-agent launcher.
