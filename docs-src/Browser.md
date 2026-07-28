# 🌐 Browser (`structupath.browser`)

**Supporting visibility capability.** Browser supplies a drivable Herdr pane around [agent-browser](https://github.com/vercel-labs/agent-browser). It can show and control the same workspace browser session used by a coding agent, or open a separate interactive Carbonyl browser.

Repo: [StructuPath/herdr-browser](https://github.com/StructuPath/herdr-browser) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-browser#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.5.0` |
| Minimum Herdr | `0.7.0` |
| Explicitly tested Herdr | `0.7.4` |
| Evidence commit | `72b986e3a0233b938b0046806bc2aaeefb56e12e` |

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.browser.open` | Open the shared workspace viewer; with no URL it attaches view-only |
| `structupath.browser.close` | Close browser panes and end the workspace session |
| `structupath.browser.browse` | Open a separate interactive Carbonyl browser |
| `structupath.browser.record-start` | Start WebM recording for the workspace session |
| `structupath.browser.record-stop` | Stop and save the active recording |

## Quick start

```bash
herdr plugin action invoke open --plugin structupath.browser
```

With no URL, use `u` in the pane or start agent-browser with the exact session shown in the pane header:

```bash
agent-browser --session herdr-ws-<workspace-id> open http://localhost:3000
```

A modified click on a localhost URL in Herdr can route it to the workspace browser. The link handler accepts only HTTP(S) localhost, `127.0.0.1`, or `[::1]` URLs.

## Requirements and session model

- Herdr `>= 0.7.0`; the pinned README records testing with `0.7.4`.
- Node.js `>= 20`; Node 22+ enables live WebSocket streaming.
- `agent-browser` plus its browser engine is required.
- `chafa` and `carbonyl@next` are optional rendering/browse dependencies.

```bash
npm install -g agent-browser
agent-browser install
```

The default session is `herdr-ws-<workspace-id>`, isolating browser state by Herdr workspace. Browser sessions remain a trusted local boundary: another same-user process that knows the session name can drive it. Recordings are retained in plugin state and may contain sensitive content.

## Viewer controls

`u` opens the address prompt; click sends real Chrome mouse events; `i` types into the focused element; `b`/`f` navigate history; `r` reloads; `j`/`k`, Space, and the wheel scroll; `q` closes the viewer pane.
