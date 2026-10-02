const $ = selector => document.querySelector(selector);
let data;
const labels = { version_match:'Version match', not_tested:'Not tested on this version', incompatible:'Version mismatch', unknown:'Unknown', available:'Available', unavailable:'Unavailable', not_configured:'Not connected', matches_clean_head:'Matches clean HEAD', not_current_clean_head:'Not current clean HEAD' };
function element(tag, value, className) { const e = document.createElement(tag); if (value !== undefined) e.textContent = value; if (className) e.className = className; return e; }
function badge(value, tone = '') { return element('span', labels[value] || value, `badge ${tone}`); }
function time(value) { const d = new Date(value); return Number.isNaN(d.valueOf()) ? 'Unknown time' : d.toLocaleString(); }
function row(parent, label, value) { const line = element('div', undefined, 'detail-row'); line.append(element('span', label, 'muted'), element('span', String(value))); parent.append(line); }
function panel(title, observation) {
  const p = element('section', undefined, 'panel'); p.append(element('h3', title));
  if (observation.status !== 'observed') p.append(element('p', observation.message || 'Not connected. Add its observation file to your Console configuration.', 'muted'));
  else p.append(element('p', `File updated ${time(observation.observedAt)}`, 'footnote'));
  return p;
}
function command(parent, label, value) {
  const group = element('div', undefined, 'command');
  const code = element('code', value), button = element('button', 'Copy');
  button.type = 'button'; button.setAttribute('aria-label', `Copy ${label} command`);
  button.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(value); button.textContent = 'Copied'; }
    catch { button.textContent = 'Select command to copy'; }
  });
  group.append(element('p', label), code, button); parent.append(group);
}
const suiteComponents = [
  ['site', 'Suite site'],
  ['browser', 'Browser'],
  ['guard', 'Guard'],
  ['swarm', 'Swarm'],
  ['conductor', 'Conductor']
];
const pinRelationLabels = {
  at_pin: 'At reviewed pin',
  ahead_of_pin: 'Ahead of reviewed pin',
  behind_pin: 'Behind reviewed pin',
  diverged: 'Diverged from reviewed pin',
  pin_unavailable: 'Pinned commit unavailable locally',
  not_pinned: 'No suite pin',
  unavailable: 'Checkout unavailable'
};
function renderSuite() {
  const configured = data.projects.filter(project => project.suite);
  const section = $('#suite-section');
  if (!configured.length) {
    section.hidden = true;
    $('#suite-checkouts').replaceChildren();
    return;
  }
  const byComponent = new Map(configured.map(project => [project.suite.component, project]));
  const cards = suiteComponents.map(([component, displayName]) => {
    const project = byComponent.get(component);
    const card = element('article', undefined, `suite-card${project ? '' : ' suite-gap'}`);
    const heading = element('div', undefined, 'suite-card-heading');
    const title = element('div');
    title.append(element('h3', displayName));
    if (!project) {
      heading.append(title, badge('Not configured'));
      card.append(heading, element('p', `Add suiteComponent "${component}" to one project to include this checkout.`, 'muted'));
      return card;
    }
    title.append(element('p', project.name, 'muted'));
    const relation = project.suite.pinRelation;
    heading.append(title, badge(pinRelationLabels[relation] || relation, relation === 'at_pin' || relation === 'not_pinned' ? 'good' : 'warn'));
    card.append(heading, element('p', project.path, 'path'));
    if (project.error) card.append(element('p', project.error, 'error'));
    const facts = element('div', undefined, 'suite-facts');
    if (component === 'site') row(facts, 'Reviewed pin', 'Not applicable — the site is not pinned');
    else row(facts, 'Reviewed pin', project.suite.pinnedCommit ? project.suite.pinnedCommit.slice(0, 12) : 'Unavailable');
    const upstream = project.suite.upstream;
    if (upstream.state === 'tracking') {
      row(facts, 'Configured upstream', 'Local tracking ref');
      const ahead = upstream.ahead === null ? 'unknown' : upstream.ahead;
      const behind = upstream.behind === null ? 'unknown' : upstream.behind;
      row(facts, 'HEAD comparison', `${ahead} ahead · ${behind} behind`);
    } else if (upstream.state === 'no_upstream') {
      row(facts, 'Configured upstream', 'No upstream configured');
    } else {
      row(facts, 'Configured upstream', 'Relation unavailable');
    }
    card.append(facts);
    if (!project.error && relation !== 'unavailable') {
      const commands = element('div', undefined, 'suite-commands');
      commands.append(element('p', `Copy only — run manually from ${project.name} at the checkout path shown above.`, 'footnote'));
      command(commands, `Inspect ${displayName} checkout`, 'git status -sb');
      command(commands, `Refresh ${displayName} remote refs`, 'git fetch --prune');
      card.append(commands);
    }
    return card;
  });
  $('#suite-checkouts').replaceChildren(...cards);
  section.hidden = false;
  const selected = data.readiness.server?.version;
  $('#suite-compatibility').textContent = `Conductor supports exactly Herdr 0.7.5. Running Herdr server ${selected || 'unavailable'} ${selected === '0.7.5' ? 'matches that version; installed-action checks are still required.' : 'is not supported by the pinned Conductor.'}`;
}
function renderHealth() {
  const root = $('#health'); root.replaceChildren();
  for (const tool of data.readiness.tools) {
    const card = element('div', undefined, 'health-card');
    card.append(element('span', tool.name, 'muted'), element('strong', tool.version || 'Not available'), badge(tool.status, tool.status === 'available' ? 'good' : 'warn'));
    root.append(card);
  }
  const server = data.readiness.server;
  const card = element('div', undefined, 'health-card');
  card.append(element('span', 'Running Herdr server', 'muted'), element('strong', server?.version || 'Not available'),
    badge(server?.status || 'unavailable', server?.status === 'running' ? 'good' : 'warn'));
  root.append(card);
  const line = element('div', undefined, 'compatibility');
  for (const plugin of data.readiness.plugins) line.append(badge(`${plugin.name} ${plugin.version} · ${labels[plugin.compatibility]}`, plugin.compatibility === 'version_match' ? '' : 'warn'));
  root.append(line);
  $('#compatibility-note').textContent = `Pinned source versions · evidence ${data.readiness.evidenceDate}. Compatibility compares the running server (protocol ${server?.protocol ?? 'unknown'}), not just the selected CLI binary. It does not verify installed actions or live integration. Selected binary: ${data.readiness.selectedHerdr}`;
}
function projectCard(p) {
  const card = element('article', undefined, 'project-card');
  const heading = element('div', undefined, 'project-heading');
  const title = element('div'); title.append(element('h3', p.name), element('p', p.path, 'path'));
  heading.append(title, badge(p.error ? 'Unavailable' : p.git.dirty ? 'Uncommitted changes' : 'Clean worktree', p.error || p.git.dirty ? 'warn' : 'good')); card.append(heading);
  if (p.error) card.append(element('p', p.error, 'error'));
  else {
    const stats = element('div', undefined, 'stats');
    row(stats, 'Branch', p.git.branch); row(stats, 'Commit', p.git.commit.slice(0, 12)); row(stats, 'Changed files', p.git.changedFiles); row(stats, 'Worktrees', p.git.worktrees); card.append(stats);
  }
  const details = element('details'); details.open = data.projects.length === 1;
  details.append(element('summary', 'Run status & validation evidence'));
  const grid = element('div', undefined, 'evidence-grid');
  const swarm = panel('Swarm', p.swarm);
  if (p.swarm.status === 'observed') {
    row(swarm, 'Run', p.swarm.run);
    for (const slot of p.swarm.slots) row(swarm, `${slot.slot} · ${slot.label || slot.branch}`, slot.state);
    swarm.append(element('p', 'Manifest observations; agent activity may have changed.', 'footnote'));
  }
  const candidate = panel('Swarm candidate handoff', p.candidate);
  if (p.candidate.status === 'observed') {
    candidate.append(badge(p.candidate.freshness !== 'matches_clean_head' ? 'Saved preview: stale checkout' :
      p.candidate.reportedReady ? 'Saved preview: ready' : 'Saved preview: blocked',
      p.candidate.reportedReady && p.candidate.freshness === 'matches_clean_head' ? 'good' : 'warn'));
    candidate.append(badge(p.candidate.freshness, p.candidate.freshness === 'matches_clean_head' ? '' : 'warn'));
    row(candidate, 'Run / slot', `${p.candidate.run} / ${p.candidate.slot}`);
    row(candidate, 'Selected commit', p.candidate.commit.slice(0, 12));
    row(candidate, 'Validation / Browser QA / review', `${p.candidate.validation} / ${p.candidate.browserQA} / ${p.candidate.review}`);
    if (p.candidate.issues.length) row(candidate, 'Reported gaps', p.candidate.issues.join(', '));
    candidate.append(element('p', 'Saved caller-supplied preview, not approval or authorization. Swarm rechecks the selected slot and all evidence before publishing a draft PR.', 'footnote'));
  }
  const conductor = panel('Conductor', p.conductor);
  if (p.conductor.status === 'observed') {
    row(conductor, 'Saved lifecycle', p.conductor.lifecycle); row(conductor, 'Run', p.conductor.run);
    if (p.conductor.nextOperations?.length) row(conductor, 'Recorded next operations', p.conductor.nextOperations.join(', '));
    for (const worker of p.conductor.workers) row(conductor, worker.role, worker.state);
    conductor.append(element('p', 'Operator-selected saved status; refresh Conductor status before acting.', 'footnote'));
  }
  const guard = panel('Guard', p.guard);
  if (p.guard.status === 'observed') {
    row(guard, 'Recorded events', p.guard.events);
    row(guard, 'Alerts / interrupt requests', `${p.guard.counts.alert} / ${p.guard.counts.interrupt}`);
    guard.append(element('p', 'Advisory counts. Raw commands and log messages stay out of this view.', 'footnote'));
  }
  const qa = panel('Browser QA', p.qa);
  if (p.qa.status === 'observed') {
    qa.append(badge(p.qa.outcome, p.qa.outcome === 'passed' && p.qa.freshness === 'matches_clean_head' && p.qa.validationPolicy === 'strict' ? 'good' : 'warn'));
    qa.append(badge(p.qa.freshness, p.qa.freshness === 'matches_clean_head' ? '' : 'warn'));
    if (p.qa.validationPolicy !== 'strict') qa.append(badge('Relaxed failure policy', 'warn'));
    row(qa, 'Scenario', p.qa.scenario); row(qa, 'Tested commit', p.qa.commit.slice(0, 12));
    row(qa, 'Completed', time(p.qa.finishedAt));
    row(qa, 'Viewports / assertions', `${p.qa.summary.viewports} / ${p.qa.summary.assertions}`);
    row(qa, 'Console / page / request errors', `${p.qa.summary.consoleErrors} / ${p.qa.summary.pageErrors} / ${p.qa.summary.failedRequests}`);
    row(qa, 'Artifacts retained', p.qa.artifactCount);
    for (const view of p.qa.viewports) row(qa, view.name, view.status);
    qa.append(element('p', 'Report supplied by the local runner. Screenshots and raw diagnostics remain in its private output directory.', 'footnote'));
  }
  const pr = panel('GitHub handoff', p.pullRequest);
  if (p.pullRequest.status === 'observed') {
    if (p.pullRequest.outcome === 'no_pr') pr.append(element('p', 'No matching pull request in this saved observation.', 'muted'));
    else {
      const link = element('a', `${p.pullRequest.repository} #${p.pullRequest.number}`);
      link.href = p.pullRequest.url; link.target = '_blank'; link.rel = 'noopener noreferrer'; pr.append(link);
      row(pr, 'PR state', `${p.pullRequest.state}${p.pullRequest.draft ? ' · draft' : ''}`);
      row(pr, 'CI / check count', `${p.pullRequest.outcome} / ${p.pullRequest.checks}`);
      pr.append(badge(p.pullRequest.freshness, p.pullRequest.freshness === 'matches_clean_head' ? '' : 'warn'));
      pr.append(element('p', 'Saved GitHub status. Refresh through Swarm before making a merge decision.', 'footnote'));
    }
  }
  grid.append(swarm, candidate, conductor, qa, guard, pr); details.append(grid); card.append(details);
  const next = element('details', undefined, 'next-actions'); next.append(element('summary', 'Next steps in your project workspace'));
  next.append(element('p', 'Copy a command to the intended Herdr workspace. These controls only copy text; commands retain the plugin’s own previews and approvals.', 'muted'));
  command(next, 'Inspect Swarm status', 'herdr plugin action invoke status --plugin structupath.swarm');
  command(next, 'Inspect Conductor status (Herdr 0.7.5)', 'herdr plugin action invoke status --plugin structupath.conductor');
  command(next, 'Review Swarm harvest / GitHub handoff', 'herdr plugin action invoke harvest --plugin structupath.swarm');
  card.append(next); return card;
}
function renderProjects() {
  if (!data) return;
  const query = $('#filter').value.toLowerCase().trim();
  const projects = data.projects.filter(p => `${p.name} ${p.git?.branch || ''}`.toLowerCase().includes(query));
  $('#projects').replaceChildren(...projects.map(projectCard));
  if (!projects.length) $('#projects').append(element('p', 'No projects match your search.', 'muted'));
}
async function refresh() {
  $('#refresh').disabled = true;
  $('#notice').textContent = 'Reading project status…';
  try {
    const response = await fetch('/api/snapshot', { headers: { 'X-Herdr-Console': '1' }, cache: 'no-store' });
    if (!response.ok) throw new Error('Snapshot unavailable. Check the Console terminal and refresh.');
    data = await response.json(); renderHealth(); renderSuite(); renderProjects();
    $('#updated').textContent = `Read ${time(data.generatedAt)}`;
    $('#notice').textContent = data.demo ? 'DEMO — illustrative data only. Restart with --config to view your projects.' : `${data.projects.length} configured project${data.projects.length === 1 ? '' : 's'} · observations refresh when you ask.`;
    $('#notice').className = data.demo ? 'demo' : '';
  } catch (error) {
    $('#notice').textContent = `${error.message} Previously displayed data may be stale.`; $('#notice').className = 'error';
  } finally { $('#refresh').disabled = false; }
}
$('#refresh').addEventListener('click', refresh);
$('#filter').addEventListener('input', renderProjects);
refresh();
