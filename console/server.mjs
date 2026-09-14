import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { loadConfig, snapshot, demoSnapshot } from './model.mjs';

const ASSETS = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/favicon.svg', ['favicon.svg', 'image/svg+xml']],
  ['/style.css', ['style.css', 'text/css; charset=utf-8']]
]);

export function createConsoleServer(getSnapshot) {
  let pending;
  let cached;
  let cachedAt = 0;
  const server = createServer(async (req, res) => {
    const host = `127.0.0.1:${server.address().port}`;
    const origin = `http://${host}`;
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
    res.setHeader('Content-Security-Policy', "default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
    const send = (status, type, body) => { res.writeHead(status, { 'Content-Type': type }); res.end(body); };
    if (req.headers.host !== host || (req.headers.origin && req.headers.origin !== origin) ||
        (req.headers['sec-fetch-site'] && !['same-origin', 'none'].includes(req.headers['sec-fetch-site']))) {
      return send(403, 'text/plain', 'Use the local Console address printed at startup.');
    }
    if (req.method !== 'GET') return send(405, 'text/plain', 'Read-only Console: GET only.');
    // Exact routes only: no filesystem paths or project selections come from a request.
    if (req.url === '/api/snapshot') {
      if (req.headers['x-herdr-console'] !== '1') return send(403, 'text/plain', 'Open the local Console to read project data.');
      try {
        if (!cached || Date.now() - cachedAt >= 5000) {
          pending ||= Promise.resolve().then(getSnapshot).then(value => {
            cached = value; cachedAt = Date.now(); return value;
          }).finally(() => { pending = undefined; });
          await pending;
        }
        return send(200, 'application/json; charset=utf-8', JSON.stringify(cached));
      } catch { return send(503, 'application/json', JSON.stringify({ error: 'Snapshot unavailable. Check configured tools and files, then refresh.' })); }
    }
    const asset = ASSETS.get(req.url);
    if (!asset) return send(404, 'text/plain', 'Not found');
    try { send(200, asset[1], await readFile(new URL(`public/${asset[0]}`, import.meta.url))); }
    catch { send(500, 'text/plain', 'Console asset unavailable'); }
  });
  server.requestTimeout = 10000;
  server.headersTimeout = 10000;
  server.timeout = 30000;
  return server;
}

export function parseArgs(args) {
  const result = { port: 4317, demo: false, check: false };
  const seen = new Set();
  for (let i = 0; i < args.length; i++) {
    const key = args[i];
    if (seen.has(key)) throw new Error(`Duplicate option ${key}`);
    seen.add(key);
    if (key === '--help') return { help: true };
    if (key === '--demo' || key === '--check') result[key.slice(2)] = true;
    else if (key === '--config' || key === '--port') {
      const value = args[++i];
      if (!value || value.startsWith('--')) throw new Error(`${key} requires a value`);
      result[key.slice(2)] = key === '--port' ? Number(value) : value;
    } else throw new Error(`Unknown option ${key}`);
  }
  if (!Number.isInteger(result.port) || result.port < 1024 || result.port > 65535) throw new Error('Port must be 1024–65535');
  if (Boolean(result.config) === result.demo) throw new Error('Choose either --config <file> or --demo');
  return result;
}

async function main() {
  if (Number(process.versions.node.split('.')[0]) < 20) throw new Error('Node 20 or newer is required');
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log('Herdr Console (Node 20+)\n  npm run console -- --config /private/console.json [--port 4317] [--check]\n  npm run console -- --demo\nRead-only. Binds to 127.0.0.1 only. No plugin operations or remote requests.');
    return;
  }
  const config = options.demo ? null : await loadConfig(options.config);
  const get = options.demo ? demoSnapshot : () => snapshot(config);
  if (options.check) { console.log(JSON.stringify(await get(), null, 2)); return; }
  const server = createConsoleServer(get);
  server.on('error', error => { console.error(`Console could not start (${error.code || 'server error'}). Try another --port.`); process.exitCode = 1; });
  server.listen(options.port, '127.0.0.1', () => console.log(`Herdr Console${options.demo ? ' — DEMO DATA' : ''}\nhttp://127.0.0.1:${options.port}\nRead-only. Press Ctrl+C to stop.`));
  const stop = () => { server.close(); server.closeAllConnections(); };
  process.once('SIGINT', stop);
  process.once('SIGTERM', stop);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => { console.error(`Console: ${error.message}`); process.exitCode = 1; });
}
