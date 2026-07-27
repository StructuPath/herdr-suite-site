# StructuPath Herdr Plugins

Four focused plugins for [Herdr](https://herdr.dev), the terminal agent multiplexer, built and maintained by [StructuPath](https://github.com/StructuPath). This repository is the canonical suite documentation source; each plugin README remains the detailed runtime reference.

| Plugin | ID | Pinned release | Minimum Herdr | Explicitly tested | Purpose |
| --- | --- | --- | --- | --- | --- |
| [Browser](Browser) | `structupath.browser` | `0.5.0` | `0.7.0` | `0.7.4` | View and drive a workspace browser session |
| [Guard](Guard) | `structupath.guard` | `0.1.0` | `0.7.5` | `0.7.5` | Advisory command policy, audit, alert, and best-effort interrupt |
| [Swarm](Swarm) | `structupath.swarm` | `0.1.0` | `0.7.4` | `0.7.4`, `0.7.5` | Parallel worktree-per-agent fan-out and review-first harvest |
| [Conductor](Conductor) | `structupath.conductor` | `0.1.0` | `0.7.5` | `0.7.5` | Role-differentiated workers, run visibility, and reconciliation |

Versions are plugin-specific evidence pinned in [`data/plugins.json`](https://github.com/StructuPath/herdr-suite-site/blob/main/data/plugins.json), not a claim that every plugin was tested on one suite-wide Herdr version.

## How the tools relate

- **Browser** exposes the browser session that an agent or operator drives.
- **Guard** observes terminal text and offers advisory/best-effort policy. It is not an authorization boundary for agent TUIs.
- **Swarm** independently fans out interchangeable agents into Swarm-owned worktrees and supports review-first harvest.
- **Conductor** runs a role-differentiated team. Its current `assemble` and `harvest` implementations create and reconcile Conductor-owned worktrees directly; they do **not** delegate worktree creation or harvest to Swarm.

These plugins can be installed together, but the current runtime is not a single automatic pipeline.

## Trust boundary

Herdr plugins and write-capable agents run as the same operating-system user. Treat write agents as **trusted same-user principals**. Worktrees reduce accidental file collisions and make changes reviewable; they are not sandboxes and do not prevent a worker from accessing other same-user files or processes. Use agent-native sandbox/tool controls where an actual enforcement boundary is required.

## Install

Install commands supported by the plugin READMEs:

```bash
herdr plugin install StructuPath/herdr-browser
herdr plugin install StructuPath/herdr-guard
herdr plugin install StructuPath/herdr-swarm
herdr plugin install StructuPath/herdr-conductor
```

These commands are not a blanket claim about marketplace visibility. Inspect source and manifests before installing local plugins.

## Health checks

```bash
herdr plugin list
herdr plugin action list
herdr plugin log list
herdr status server
```

`plugin list` confirms that a manifest parsed and is enabled; `plugin action list` confirms action registration. See each plugin page for its exact actions and prerequisites.
