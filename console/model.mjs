import { open, realpath, readFile, stat } from 'node:fs/promises';
import { constants } from 'node:fs';
import { dirname, resolve, isAbsolute } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { createHash } from 'node:crypto';

const exec = promisify(execFile);
const MAX_BYTES = 2 * 1024 * 1024;
const SHA = /^(?:[a-f0-9]{40}|[a-f0-9]{64})$/;
const text = (v, max = 180) => typeof v === 'string' ? v.replace(/[\x00-\x1f\x7f]/g, ' ').slice(0, max) : '';
const object = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const count = (v) => Number.isSafeInteger(v) && v >= 0 && v <= 1_000_000 ? v : null;

export async function boundedRead(path) {
  const file = await open(path, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const stat = await file.stat();
    if (!stat.isFile() || stat.size > MAX_BYTES) throw new Error('Expected a regular file under 2 MiB');
    const buffer = Buffer.alloc(MAX_BYTES + 1);
    let length = 0;
    while (length < buffer.length) {
      const { bytesRead } = await file.read(buffer, length, buffer.length - length, null);
      if (!bytesRead) break;
      length += bytesRead;
    }
    if (length > MAX_BYTES) throw new Error('File exceeds 2 MiB');
    return { content: buffer.subarray(0, length).toString('utf8'), observedAt: stat.mtime.toISOString() };
  } finally { await file.close(); }
}

export async function loadConfig(path) {
  const base = dirname(resolve(path));
  const config = JSON.parse((await boundedRead(path)).content);
  if (!object(config) || config.schemaVersion !== 1 || !Array.isArray(config.projects) ||
      config.projects.length < 1 || config.projects.length > 20 ||
      Object.keys(config).some(k => !['schemaVersion', 'projects', 'herdrBinary'].includes(k))) {
    throw new Error('Config requires schemaVersion: 1 and 1–20 projects');
  }
  const ids = new Set();
  const paths = ['path', 'swarmManifest', 'conductorStatus', 'guardAudit', 'qaReport', 'pullRequestStatus'];
  const projects = config.projects.map(p => {
    if (!object(p) || !/^[a-z0-9][a-z0-9-]{0,47}$/.test(p.id) || ids.has(p.id) ||
        typeof p.name !== 'string' || !p.name.trim() || p.name.length > 100 ||
        typeof p.path !== 'string' ||
        Object.keys(p).some(k => !['id', 'name', ...paths].includes(k))) {
      throw new Error('Each project needs a unique slug id, name, path, and only supported fields');
    }
    ids.add(p.id);
    const result = { id: p.id, name: text(p.name, 100) };
    for (const key of paths) if (p[key] !== undefined) {
      if (typeof p[key] !== 'string' || !p[key] || p[key].length > 4096 || /[\x00-\x1f\x7f]/.test(p[key])) {
        throw new Error(`Invalid ${key} path`);
      }
      result[key] = resolve(base, p[key]);
    }
    return result;
  });
  if (config.herdrBinary !== undefined && (typeof config.herdrBinary !== 'string' ||
      !isAbsolute(config.herdrBinary) || /[\x00-\x1f\x7f]/.test(config.herdrBinary))) {
    throw new Error('herdrBinary must be an absolute executable path');
  }
  return { projects, herdrBinary: config.herdrBinary || 'herdr' };
}

// Drop inherited Git overrides so a configured project cannot be redirected to another repository.
export function gitEnvironment() {
  return { ...Object.fromEntries(Object.entries(process.env).filter(([k]) => !k.startsWith('GIT_'))),
    GIT_OPTIONAL_LOCKS: '0', GIT_TERMINAL_PROMPT: '0' };
}

async function command(file, args, options = {}) {
  const { stdout } = await exec(file, args, { timeout: 5000, maxBuffer: MAX_BYTES, ...options });
  return stdout;
}

async function git(path, args) {
  return command('git', ['-C', path, '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false', ...args], { env: gitEnvironment() });
}

export async function inspectGit(path) {
  const physical = await realpath(path);
  const root = (await git(physical, ['rev-parse', '--show-toplevel'])).trim();
  if (await realpath(root) !== physical) throw new Error('Project path must be a Git worktree root');
  const [head, branch, status, worktrees, common] = await Promise.all([
    git(physical, ['rev-parse', '--verify', 'HEAD']),
    git(physical, ['branch', '--show-current']),
    git(physical, ['status', '--porcelain=v1', '-z', '--untracked-files=normal']),
    git(physical, ['worktree', 'list', '--porcelain', '-z']),
    git(physical, ['rev-parse', '--path-format=absolute', '--git-common-dir'])
  ]);
  const commit = head.trim();
  if (!SHA.test(commit)) throw new Error('Project has no valid HEAD');
  // Rename records contain a second NUL-delimited path; filenames are deliberately not exposed.
  const records = status.split('\0');
  let changedFiles = 0;
  for (let i = 0; i < records.length; i++) if (records[i]) {
    changedFiles++;
    if (/^[RC]|^.[RC]/.test(records[i])) i++;
  }
  const commonPath = await realpath(common.trim());
  const identity = await stat(commonPath, { bigint: true });
  const repositoryKey = createHash('sha256').update(`herdr-conductor-repository-v1\0${commonPath}\0${identity.dev}\0${identity.ino}`).digest('hex');
  return { commit, branch: text(branch.trim() || 'Detached HEAD'), dirty: Boolean(status), changedFiles,
    worktrees: worktrees.split('\0').filter(s => s.startsWith('worktree ')).length, root: physical, repositoryKey };
}

async function observation(path, parse) {
  if (!path) return { status: 'not_configured' };
  try {
    const { content, observedAt } = await boundedRead(path);
    return { status: 'observed', observedAt, ...await parse(content) };
  } catch {
    return { status: 'unavailable', message: 'Cannot read a supported, bounded observation. Check the configured file.' };
  }
}

export function parseQA(content, current) {
  const q = JSON.parse(content);
  if (!object(q) || q.schemaVersion !== 1 || q.kind !== 'herdr-browser-qa' ||
      !['passed', 'failed'].includes(q.status) || !object(q.git) || !SHA.test(q.git.commit) ||
      typeof q.git.dirty !== 'boolean' || typeof q.git.changedDuringRun !== 'boolean' ||
      !object(q.summary) || !object(q.scenario?.policy) ||
      ['failOnConsoleError','failOnPageError','failOnFailedRequest'].some(k => typeof q.scenario.policy[k] !== 'boolean') ||
      !Array.isArray(q.runs) || q.runs.length > 20 ||
      !Number.isFinite(Date.parse(q.finishedAt))) throw new Error('Unsupported QA report');
  const summary = Object.fromEntries(['viewports', 'passed', 'failed', 'assertions', 'consoleErrors', 'pageErrors', 'failedRequests'].map(k => [k, count(q.summary[k])]));
  if (Object.values(summary).some(n => n === null) || summary.viewports < q.runs.length ||
      summary.passed + summary.failed !== summary.viewports || summary.viewports < 1) throw new Error('Invalid QA summary');
  const policy = q.scenario.policy;
  const strict = policy.failOnConsoleError && policy.failOnPageError && policy.failOnFailedRequest;
  const inconsistent = q.status === 'passed' && (summary.failed > 0 || summary.viewports !== q.runs.length || q.cleanup?.status !== 'passed' ||
    (policy.failOnConsoleError && summary.consoleErrors > 0) ||
    (policy.failOnPageError && summary.pageErrors > 0) ||
    (policy.failOnFailedRequest && summary.failedRequests > 0) || q.runs.some(r => r.status !== 'passed'));
  if (inconsistent) throw new Error('Contradictory QA report');
  const fresh = current && q.git.commit === current.commit && !q.git.dirty && !q.git.changedDuringRun && !current.dirty;
  return { outcome: q.status, commit: q.git.commit, finishedAt: q.finishedAt,
    scenario: text(q.scenario?.name), validationPolicy: strict ? 'strict' : 'relaxed', freshness: fresh ? 'matches_clean_head' : 'not_current_clean_head',
    summary, artifactCount: q.runs.reduce((n, r) => n + (Array.isArray(r.artifacts) ? r.artifacts.length : 0), 0),
    viewports: q.runs.map(r => ({ name: text(r.viewport?.name), status: text(r.status) })) };
}

export function parsePullRequest(content, current) {
  const lines = content.trim().split('\n');
  const records = lines.filter(line => line.startsWith('ci_status\t'));
  if (records.length !== 1) throw new Error('Expected one Swarm CI status record');
  const value = JSON.parse(records[0].slice('ci_status\t'.length));
  if (!object(value) || value.schema_version !== 1 || !SHA.test(value.local_head_sha)) throw new Error('Invalid PR status');
  if (value.status === 'no_pr') return { outcome: 'no_pr' };
  if (!['passed','failed','pending','not_run','unknown'].includes(value.status) ||
      !SHA.test(value.head_sha) || !/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value.repository) ||
      !Number.isSafeInteger(value.number) || value.number < 1 || count(value.check_count) === null ||
      !['OPEN','CLOSED','MERGED'].includes(value.state) || typeof value.draft !== 'boolean') throw new Error('Unsupported PR status');
  const url = `https://github.com/${value.repository}/pull/${value.number}`;
  if (value.url !== url) throw new Error('Foreign PR URL');
  return { outcome:value.status, url, number:value.number, repository:value.repository, draft:value.draft, state:value.state,
    commit:value.head_sha, checks:value.check_count,
    freshness: current && current.commit === value.head_sha && value.local_head_sha === value.head_sha && !current.dirty ? 'matches_clean_head' : 'not_current_clean_head' };
}

export async function inspectProject(p) {
  const result = { id: p.id, name: p.name, path: p.path };
  try { result.git = await inspectGit(p.path); }
  catch { result.error = 'Repository unavailable, uncommitted, or not a worktree root. Check the configured path.'; }
  const [swarm, conductor, guard, qa, pullRequest] = await Promise.all([
    observation(p.swarmManifest, async content => {
      const run = JSON.parse(content);
      if (!object(run) || typeof run.run_id !== 'string' || typeof run.repo_root !== 'string' ||
          !Array.isArray(run.slots) || run.slots.length > 100 || !result.git ||
          await realpath(run.repo_root) !== result.git.root) throw new Error('Foreign Swarm run');
      return { run: text(run.run_id), slots: run.slots.map(s => {
        if (!object(s) || !['pending','running','failed','settled','merged','skipped','archived'].includes(s.status)) throw new Error('Unsupported slot');
        return { slot: text(String(s.slot)), label: text(s.label), state: s.status, branch: text(s.branch) };
      }) };
    }),
    observation(p.conductorStatus, content => {
      const run = JSON.parse(content);
      if (!object(run) || typeof run.run !== 'string' || typeof run.lifecycle !== 'string' ||
          !Array.isArray(run.workers) || run.workers.length > 100 || !SHA.test(run.fork_sha) ||
          !result.git || run.repository_key !== result.git.repositoryKey) throw new Error('Unsupported or foreign Conductor status');
      return { run: text(run.run), lifecycle: text(run.lifecycle), workspace: text(run.workspace_id),
        binding: 'operator_selected_snapshot', workers: run.workers.map(w => ({ role: text(w.role), state: text(w.status) })),
        nextOperations: Array.isArray(run.legal_next_operations) ? run.legal_next_operations.filter(v => ['status','harvest','preview','apply','stand-down'].includes(v)) : [] };
    }),
    observation(p.guardAudit, content => {
      const counts = { audit: 0, alert: 0, interrupt: 0, other: 0 };
      const lines = content.split('\n').filter(line => line.trim());
      if (lines.length > 10000) throw new Error('Audit too large');
      for (const line of lines) {
        const entry = JSON.parse(line);
        if (!object(entry)) throw new Error('Invalid audit entry');
        counts[Object.hasOwn(counts, entry.severity) ? entry.severity : 'other']++;
      }
      return { events: lines.length, counts };
    }),
    observation(p.qaReport, content => parseQA(content, result.git)),
    observation(p.pullRequestStatus, content => parsePullRequest(content, result.git))
  ]);
  return { ...result, swarm, conductor, guard, qa, pullRequest };
}

const parseVersion = (s) => /(?:^|\s|v)(\d+\.\d+\.\d+)(?:\b|$)/.exec(s)?.[1] || null;
export function compatibility(plugin, version) {
  if (!version) return 'unknown';
  if (plugin.slug === 'conductor') return version === '0.7.5' ? 'version_match' : 'incompatible';
  const actual = version.split('.').map(Number), minimum = plugin.min_herdr_version.split('.').map(Number);
  let comparison = 0;
  for (let i = 0; i < 3 && !comparison; i++) comparison = actual[i] - minimum[i];
  if (comparison < 0) return 'incompatible';
  return plugin.tested_herdr_versions.includes(version) ? 'version_match' : 'not_tested';
}

export async function health(herdrBinary) {
  const probes = [['Node', process.execPath], ['Git', 'git'], ['Herdr', herdrBinary], ['agent-browser', 'agent-browser']];
  const tools = await Promise.all(probes.map(async ([name, binary]) => {
    try {
      const version = parseVersion(await command(binary, ['--version']));
      return { name, version, status: version ? 'available' : 'unknown' };
    } catch { return { name, version: null, status: 'unavailable' }; }
  }));
  const evidence = JSON.parse(await readFile(new URL('../data/plugins.json', import.meta.url), 'utf8'));
  const herdr = tools.find(t => t.name === 'Herdr').version;
  return { tools, selectedHerdr: herdrBinary, evidenceDate: evidence.evidence_date,
    plugins: evidence.plugins.map(p => ({ name: p.name, slug: p.slug, version: p.version,
      minimum: p.min_herdr_version, compatibility: compatibility(p, herdr), source: p.repository })) };
}

export async function snapshot(config) {
  const readinessPromise = health(config.herdrBinary);
  const projects = [];
  // Bound both Git process fan-out and observation buffers across large configurations.
  for (let i = 0; i < config.projects.length; i += 4) {
    projects.push(...await Promise.all(config.projects.slice(i, i + 4).map(inspectProject)));
  }
  const readiness = await readinessPromise;
  return { schemaVersion: 1, generatedAt: new Date().toISOString(), demo: false, readiness, projects };
}

export function demoSnapshot() {
  const now = new Date().toISOString(), commit = 'a'.repeat(40);
  return { schemaVersion: 1, generatedAt: now, demo: true,
    readiness: { selectedHerdr: 'Demo runtime', evidenceDate: '2026-09-14',
      tools: ['Node','Git','Herdr','agent-browser'].map(name => ({ name, version: name === 'Herdr' ? '0.7.5' : 'Demo', status: 'available' })),
      plugins: [{name:'Browser',version:'0.8.0',compatibility:'version_match'}, {name:'Swarm',version:'0.4.0',compatibility:'version_match'}, {name:'Guard',version:'0.2.0',compatibility:'version_match'}, {name:'Conductor',version:'0.4.0',compatibility:'version_match'}] },
    projects: [{id:'demo',name:'Checkout improvements',path:'/demo/storefront',
      git:{commit,branch:'feature/checkout',dirty:false,changedFiles:0,worktrees:3},
      swarm:{status:'observed',observedAt:now,run:'demo-run',slots:[{slot:'1',label:'Builder',state:'settled',branch:'swarm/demo/1'},{slot:'2',label:'Alternative',state:'running',branch:'swarm/demo/2'}]},
      conductor:{status:'not_configured'},pullRequest:{status:'not_configured'},guard:{status:'observed',observedAt:now,events:3,counts:{audit:2,alert:1,interrupt:0,other:0}},
      qa:{status:'observed',observedAt:now,outcome:'passed',commit,finishedAt:now,scenario:'Checkout journey',validationPolicy:'strict',freshness:'matches_clean_head',summary:{viewports:2,passed:2,failed:0,assertions:6,consoleErrors:0,pageErrors:0,failedRequests:0},artifactCount:2,viewports:[{name:'desktop',status:'passed'},{name:'mobile',status:'passed'}]}
    }] };
}
