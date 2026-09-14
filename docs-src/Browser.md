# 🌐 Browser (`structupath.browser`)

**Supporting visibility capability.** Browser lets you launch Chrome or Chromium inside a Herdr pane, attach to an existing automation browser, or share a coding agent's [agent-browser](https://github.com/vercel-labs/agent-browser) session. Choose the connection that matches your workflow; agent-browser is only required for shared sessions and recording.

Repo: [StructuPath/herdr-browser](https://github.com/StructuPath/herdr-browser) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-browser#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.7.0` |
| Minimum Herdr | `0.7.0` |
| Explicitly tested Herdr | `0.7.4` |
| Evidence commit | `5fc6a9a52b4f817f21a531c288f36c3820bf93ca` |

The [pinned source](https://github.com/StructuPath/herdr-browser/tree/952e1601006cce2ca45edef56676d18a1f016151) includes the merged session-preservation and stream-recovery fixes. The manifest version remains 0.7.0; the commit identifies the exact implementation behind this guide.

## Choose a browser connection

| Your goal | Use | Requirements | What happens when you quit the pane |
| --- | --- | --- | --- |
| Browse without an agent session | Press `l` to launch local Chromium | Node 22+ and an installed Chrome or Chromium | The pane closes the browser it launched; its workspace profile remains |
| Watch an existing automation run | Press `a` to attach to its CDP endpoint | Node 22+ and a browser with an accessible debugging endpoint | The pane disconnects; the externally owned browser stays open |
| Share a coding agent's browser | Use the exact agent-browser session shown in the header | Node 20+ and agent-browser with its engine installed; Node 22+ for streaming | An existing agent-owned session stays open; a session created by the pane closes |
| Use a separate interactive terminal browser | Invoke Browse | Carbonyl | This is a separate session, not the coding agent's browser |

`q` closes the viewer. The plugin's **Close** action also ends the workspace agent-browser session, so it has a broader effect than quitting an externally attached viewer.

## First run: local Chromium

With Herdr, Node 22+, and Chrome or Chromium installed:

```bash
herdr plugin install StructuPath/herdr-browser
herdr plugin action invoke structupath.browser.open
```

1. Press `l` in the pane to launch a browser.
2. Press `u`, enter your development URL (for example `http://localhost:3000`), and press Enter.
3. Click the page, use `i` to type, or press `o` to stop forwarding pane input while you watch.
4. Press `q` when finished. The browser launched by this pane closes.

The launcher probes common Chrome/Chromium executables and macOS app bundles. If it cannot find yours, set `HERDR_BROWSER_CHROMIUM` to its executable path in the pane's environment or write the path to the plugin's `chromium` config file. Set `HERDR_BROWSER_LAUNCH=1` (or the `launch` config file to `1`) to launch automatically on open. A configured CDP endpoint takes precedence over launch mode.

No extra bundled Chromium build is needed when a supported browser is already installed. The launched browser uses a persistent per-workspace profile under plugin state.

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.browser.open` | Open the viewer; an unconfigured, URL-less open stays idle until a session exists or you choose launch/attach |
| `structupath.browser.close` | Close browser panes and end the workspace session |
| `structupath.browser.browse` | Open a separate interactive Carbonyl browser |
| `structupath.browser.record-start` | Start an observation bundle for the workspace agent-browser session |
| `structupath.browser.record-stop` | Stop the pinned recording and validate its WebM artifact |

## Share a coding agent's session

```bash
npm install -g agent-browser
agent-browser install
herdr plugin action invoke structupath.browser.open
```

Start agent-browser with the exact session shown in the pane header. Replace the example session below with that name:

```bash
agent-browser --session herdr-ws-w123456 open http://localhost:3000
```

A modified click on a localhost URL in Herdr can route it to the workspace browser. The link handler accepts only HTTP(S) localhost, `127.0.0.1`, or `[::1]` URLs.

The viewer inherits daemon settings unchanged. If you explicitly configure `AGENT_BROWSER_IDLE_TIMEOUT_MS`, use the same value for the agent and pane: changing daemon configuration can restart the session.

## Attach and observe

Press `a` and enter an existing browser's CDP endpoint, such as `http://127.0.0.1:9222`. Your automation client must expose that endpoint first; a browser using only a pipe transport cannot be reached by port. To attach on pane startup, set `HERDR_BROWSER_CDP_URL` or the plugin's `cdp-url` config file.

The pane does not create or close external targets or override their viewport. `t` cycles between page targets. Its console feed is observable by the page, so attachment is not a stealth or zero-footprint operation. Use a local HTTP endpoint or a verified browser WebSocket URL; HTTPS discovery is a known follow-up in the pinned implementation.

For a workspace dedicated to watching an agent, set `HERDR_BROWSER_OBSERVE=1` or write `1` to the `observe` config file before opening the pane. This blocks pane input and link-triggered navigation. The runtime `o` toggle blocks pane input, but in agent-browser mode a modified link click can navigate through the launcher outside the pane. Observe-only is an interaction setting, not an access-control boundary.

## Requirements and rendering

- Herdr `>= 0.7.0`; the pinned README records testing with `0.7.4`.
- Node.js `>= 20` for shared-session polling; Node 22+ enables streaming, CDP attach, and local Chromium launch.
- Chrome/Chromium is required for local launch; agent-browser plus its engine is required for shared sessions and recording.
- `chafa` and `carbonyl@next` are optional rendering/browse dependencies.

```bash
# Optional ANSI image rendering on macOS
brew install chafa
```

The viewer selects Kitty graphics, ANSI symbols through chafa, or text-only mode. Chafa is needed for streamed JPEGs in Kitty mode. Shared sessions fall back to screenshot polling if streaming is unavailable, disconnects, or sends no usable image within five seconds. That startup fallback does not guarantee recovery from every later stream stall.

## Recording and session privacy

Recording actions support **agent-browser sessions only**. They refuse in direct attach/launch mode rather than recording an unrelated browser. Starting a recording creates a fresh browser context and reloads the page while preserving cookies and localStorage; start before the flow you want to capture.

Each recording produces a run-scoped bundle under `<plugin state>/runs/run-<run-id>/browser/`, containing `recording.webm` and `evidence.json`. A successful Stop records the WebM's size and SHA-256. This is an unreviewed observation, not proof that a test passed or a reviewer accepted the result. Interrupted or ambiguous stops require inspection; they are not marked complete automatically.

The default shared session is `herdr-ws-<workspace-id>`. Sessions and persistent launch profiles are trusted local state: same-user processes can access them. Recordings remain in plugin state and may contain sensitive content. Quitting the pane does not delete recordings or the local Chromium profile.

## Viewer controls

| Input | Action |
| --- | --- |
| `l` / `a` | Launch local Chromium / attach to an existing CDP browser |
| `u` | Open the address prompt |
| `o` | Toggle observe-only pane input |
| `t` | Cycle page targets in attach mode |
| Click / `i` | Click page coordinates / type into the focused element |
| `b` / `f` / `r` | Back / forward / reload |
| `j` / `k`, Space, wheel | Scroll |
| Esc / `q` | Cancel the prompt / quit the viewer |

## Troubleshooting and development checks

- **No Chromium found:** install Chrome/Chromium or configure its executable path.
- **Waiting for a session:** press `l`, attach with `a`, or start the exact agent-browser session in the header.
- **Text-only pane:** install chafa or configure a compatible terminal for Kitty graphics.
- **Attach cannot connect:** confirm the automation browser exposes a CDP endpoint and that Node 22+ is available to the pane.
- **A linked plugin still shows old behavior:** close and reopen its pane after updating the checkout.

From a **herdr-browser checkout**, run:

```bash
npm run doctor
npm run build
npm run validate
npm run test:integration
```

Doctor checks prerequisites without launching browsers or contacting endpoints; it does not verify engine downloads, Herdr's version, or endpoint reachability. The integration command requires Node 22+, local Chromium, and agent-browser with its engine installed, and fails rather than skipping missing browser prerequisites. See the pinned [readiness assessment](https://github.com/StructuPath/herdr-browser/blob/952e1601006cce2ca45edef56676d18a1f016151/docs/readiness.md) for remaining recommendations.
