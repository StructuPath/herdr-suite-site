import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, mkdir, symlink, rm, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';
import { request } from 'node:http';
import { boundedRead, loadConfig, inspectGit, inspectProject, parseQA, parsePullRequest, compatibility, demoSnapshot, gitEnvironment } from '../model.mjs';
import { createConsoleServer, parseArgs } from '../server.mjs';

async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(), 'herdr-console-test-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const repo = join(root, 'repo'); await mkdir(repo);
  const git = (...args) => execFileSync('git', ['-C', repo, ...args], { encoding: 'utf8', env: {
    ...gitEnvironment(), GIT_CONFIG_NOSYSTEM:'1', GIT_CONFIG_GLOBAL:'/dev/null',
    GIT_AUTHOR_NAME:'Console Test',GIT_AUTHOR_EMAIL:'console@example.invalid',
    GIT_COMMITTER_NAME:'Console Test',GIT_COMMITTER_EMAIL:'console@example.invalid'
  }}).trim();
  git('init', '-q'); git('commit','-q','--allow-empty','-m','fixture');
  return { root, repo, git };
}
function qa(commit) {
  return { schemaVersion:1,kind:'herdr-browser-qa',status:'passed',cleanup:{status:'passed'},git:{commit,dirty:false,changedDuringRun:false},
    finishedAt:new Date().toISOString(),scenario:{name:'Homepage',policy:{failOnConsoleError:true,failOnPageError:true,failOnFailedRequest:true}},summary:{viewports:2,passed:2,failed:0,assertions:2,consoleErrors:0,pageErrors:0,failedRequests:0},
    runs:['desktop','mobile'].map(name => ({viewport:{name},status:'passed',steps:[{type:'assertTitle',status:'passed'}],artifacts:[`${name}.png`],consoleErrors:[],pageErrors:[],failedRequests:[],unresolvedRequests:0})) };
}
test('configuration explicitly selects repositories and rejects unknown, duplicate and executable fields', async t => {
  const { root } = await fixture(t); const file = join(root, 'config.json');
  const config = {schemaVersion:1,projects:[{id:'one',name:'First project',path:'repo'}]};
  await writeFile(file, JSON.stringify(config));
  assert.equal((await loadConfig(file)).projects[0].path, join(root, 'repo'));
  for (const bad of [ {...config, command:'rm -rf /'}, {...config, projects:[config.projects[0],config.projects[0]]},
    {...config,projects:[{...config.projects[0],script:'file.mjs'}]}, {...config,herdrBinary:'shell --eval anything'} ]) {
    await writeFile(file,JSON.stringify(bad)); await assert.rejects(loadConfig(file));
  }
});
test('bounded observation refuses symlinks, directories, FIFOs and oversized data', async t => {
  const {root} = await fixture(t); const file=join(root,'data'); await writeFile(file,'{}');
  const link=join(root,'link'); await symlink(file,link);
  await assert.rejects(boundedRead(link)); await assert.rejects(boundedRead(root));
  const fifo=join(root,'pipe'); execFileSync('mkfifo',[fifo]); await assert.rejects(boundedRead(fifo));
  await writeFile(file,Buffer.alloc(2*1024*1024+1)); await assert.rejects(boundedRead(file));
});
test('read-only Git inspection counts changes, handles detached HEAD and leaves index unchanged', async t => {
  const {repo,git}=await fixture(t);
  await writeFile(join(repo,'a.txt'),'one'); git('add','a.txt'); git('commit','-qm','file');
  const index=await readFile(join(repo,'.git/index'));
  let result=await inspectGit(repo); assert.equal(result.dirty,false); assert.equal(result.worktrees,1);
  await writeFile(join(repo,'a.txt'),'two'); await writeFile(join(repo,'new file.txt'),'three');
  result=await inspectGit(repo); assert.equal(result.changedFiles,2); assert.equal(result.dirty,true);
  await mkdir(join(repo,'new-directory'));
  for (const name of ['one','two','three']) await writeFile(join(repo,'new-directory',name),'new');
  assert.equal((await inspectGit(repo)).changedFiles,5);
  assert.deepEqual(await readFile(join(repo,'.git/index')),index);
  git('checkout','--detach','-q'); assert.equal((await inspectGit(repo)).branch,'Detached HEAD');
  await mkdir(join(repo,'child')); await assert.rejects(inspectGit(join(repo,'child')));
});
test('Git environment strips inherited repository and config redirections', () => {
  const old=process.env.GIT_DIR; process.env.GIT_DIR='/foreign';
  try { assert.equal(gitEnvironment().GIT_DIR,undefined); assert.equal(gitEnvironment().GIT_OPTIONAL_LOCKS,'0'); }
  finally { if (old === undefined) delete process.env.GIT_DIR; else process.env.GIT_DIR=old; }
});
test('QA freshness requires exact clean unchanged HEAD and rejects contradictory success', () => {
  const commit='a'.repeat(40), report=qa(commit), current={commit,dirty:false};
  assert.equal(parseQA(JSON.stringify(report),current).freshness,'matches_clean_head');
  for (const git of [{...report.git,dirty:true},{...report.git,commit:'b'.repeat(40)}]) {
    assert.equal(parseQA(JSON.stringify({...report,git}),current).freshness,'not_current_clean_head');
  }
  assert.equal(parseQA(JSON.stringify(report),{...current,dirty:true}).freshness,'not_current_clean_head');
  assert.throws(()=>parseQA(JSON.stringify({...report,summary:{...report.summary,failedRequests:1}}),current));
  assert.throws(()=>parseQA(JSON.stringify({...report,kind:'something-else'}),current));
  const relaxed={...report,scenario:{...report.scenario,policy:{...report.scenario.policy,failOnConsoleError:false}},summary:{...report.summary,consoleErrors:2},runs:report.runs.map(r=>({...r,consoleErrors:[{message:'expected'}]}))};
  assert.equal(parseQA(JSON.stringify(relaxed),current).validationPolicy,'relaxed');
  const earlyFailure={...report,status:'failed',runs:[],summary:{...report.summary,passed:0,failed:2,assertions:0}};
  assert.equal(parseQA(JSON.stringify(earlyFailure),current).outcome,'failed');
  assert.throws(()=>parseQA(JSON.stringify({...report,cleanup:{status:'failed'}}),current));
  assert.throws(()=>parseQA(JSON.stringify({...report,git:{...report.git,changedDuringRun:true}}),current));
  assert.throws(()=>parseQA(JSON.stringify({...report,runs:[]}),current));
  assert.throws(()=>parseQA(JSON.stringify({...report,runs:report.runs.map(r=>({...r,status:'failed'}))}),current));
});
test('observations are projected, repository-bound, missing sources stay unknown', async t => {
  const {root,repo}=await fixture(t), info=await inspectGit(repo);
  const p={id:'one',name:'One',path:repo,swarmManifest:join(root,'swarm.json'),conductorStatus:join(root,'status.json'),guardAudit:join(root,'audit.jsonl'),qaReport:join(root,'qa.json')};
  await writeFile(p.swarmManifest,JSON.stringify({run_id:'r1',repo_root:repo,slots:[{slot:'1',label:'Build',status:'running',branch:'swarm/r1/1',mission:'DO NOT EXPOSE'}]}));
  const conductor={run:'c1',lifecycle:'applied',repository_key:info.repositoryKey,fork_sha:info.commit,workers:[],legal_next_operations:['status','stand-down']};
  await writeFile(p.conductorStatus,JSON.stringify(conductor));
  await writeFile(p.guardAudit,JSON.stringify({severity:'alert',line:'SECRET COMMAND'})+'\n');
  await writeFile(p.qaReport,JSON.stringify(qa(info.commit)));
  const result=await inspectProject(p);
  assert.equal(result.swarm.status,'observed'); assert.equal(result.conductor.lifecycle,'applied');
  assert.equal(result.guard.counts.alert,1); assert.equal(result.qa.freshness,'matches_clean_head');
  assert.ok(!JSON.stringify(result).includes('SECRET COMMAND')); assert.ok(!JSON.stringify(result).includes('DO NOT EXPOSE'));
  await writeFile(p.conductorStatus,JSON.stringify({...conductor,repository_key:'0'.repeat(64)}));
  assert.equal((await inspectProject(p)).conductor.status,'unavailable');
  await writeFile(p.swarmManifest,'{'); assert.equal((await inspectProject(p)).swarm.status,'unavailable');
  assert.equal((await inspectProject({id:'empty',name:'Empty',path:repo})).qa.status,'not_configured');
});
test('version compatibility never infers newer Conductor support', () => {
  const c={slug:'conductor',min_herdr_version:'0.7.5',tested_herdr_versions:['0.7.5']};
  assert.equal(compatibility(c,'0.7.5'),'version_match'); assert.equal(compatibility(c,'0.8.2'),'incompatible');
  assert.equal(compatibility({...c,slug:'swarm'},'0.8.2'),'not_tested');
  assert.equal(compatibility({...c,slug:'swarm'},'0.6.9'),'incompatible');
});
test('PR observations validate links, current SHA and never turn absent checks into pass', () => {
  const commit='a'.repeat(40), current={commit,dirty:false};
  const p={schema_version:1,repository:'StructuPath/example',number:12,url:'https://github.com/StructuPath/example/pull/12',state:'OPEN',draft:true,head_sha:commit,local_head_sha:commit,status:'pending',check_count:1};
  const parse=v=>parsePullRequest(`ci_status\t${JSON.stringify(v)}\n`,current);
  assert.equal(parse(p).freshness,'matches_clean_head'); assert.equal(parse(p).outcome,'pending');
  assert.throws(()=>parse({...p,status:'passed',check_count:0}));
  assert.equal(parse({...p,status:'not_run',check_count:0}).outcome,'not_run');
  assert.equal(parse({...p,repository:'structupath/example'}).number,12);
  assert.equal(parse({...p,head_sha:'b'.repeat(40)}).freshness,'not_current_clean_head');
  assert.throws(()=>parse({...p,url:'javascript:alert(1)'}));
  assert.throws(()=>parse({...p,url:'https://github.com.evil.test/StructuPath/example/pull/12'}));
  assert.throws(()=>parse({...p,url:'https://github.com/StructuPath/example/pull/13'}));
  assert.throws(()=>parsePullRequest(`ci_status\t${JSON.stringify(p)}\nci_status\t${JSON.stringify(p)}`,current));
  assert.equal(parse({schema_version:1,status:'no_pr',local_head_sha:commit}).outcome,'no_pr');
});
test('CLI requires an explicit project configuration or clearly labeled demo', () => {
  assert.throws(()=>parseArgs([])); assert.throws(()=>parseArgs(['--demo','--config','a']));
  assert.throws(()=>parseArgs(['--demo','--port','80'])); assert.throws(()=>parseArgs(['--host','0.0.0.0']));
  assert.equal(parseArgs(['--demo','--check']).check,true); assert.equal(demoSnapshot().demo,true);
});
test('HTTP serves read-only same-origin data, rejects rebinding, traversal and write attempts', async t => {
  let reads=0;
  const server=createConsoleServer(async()=>{reads++; return demoSnapshot();});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  t.after(()=>{server.closeAllConnections();server.close();});
  const port=server.address().port,host=`127.0.0.1:${port}`;
  const get=(path,headers={},method='GET')=>new Promise((resolve,reject)=>{
    const req=request({host:'127.0.0.1',port,path,method,headers:{Host:host,...headers}},res=>{
      let body='';res.on('data',chunk=>body+=chunk);res.on('end',()=>resolve({status:res.statusCode,body,headers:res.headers}));
    });req.on('error',reject);req.end();
  });
  assert.equal((await get('/')).status,200);
  assert.equal((await get('/api/snapshot')).status,403);
  assert.equal((await get('/api/snapshot',{'X-Herdr-Console':'1',Origin:'https://evil.test'})).status,403);
  assert.equal((await get('/api/snapshot',{'X-Herdr-Console':'1',Host:'evil.test'})).status,403);
  assert.equal((await get('/api/snapshot',{'X-Herdr-Console':'1','Sec-Fetch-Site':'cross-site'})).status,403);
  assert.equal((await get('/api/snapshot',{'X-Herdr-Console':'1'},'POST')).status,405);
  assert.equal((await get('/../console/example.json')).status,404);
  assert.equal((await get('/api/snapshot?path=/etc/passwd',{'X-Herdr-Console':'1'})).status,404);
  const r=await get('/api/snapshot',{'X-Herdr-Console':'1'});
  assert.equal(r.status,200); assert.equal(JSON.parse(r.body).demo,true);
  assert.equal(r.headers['access-control-allow-origin'],undefined); assert.equal(r.headers['cache-control'],'no-store');
  await get('/api/snapshot',{'X-Herdr-Console':'1'}); assert.equal(reads,1);
});
