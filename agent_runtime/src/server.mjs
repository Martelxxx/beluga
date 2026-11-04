import http from 'node:http';
import { timingSafeEqual } from 'node:crypto';
import { TaskQueue } from './tasks.mjs';
import { researchPage } from './browser.mjs';
const queue = new TaskQueue({ runner: researchPage });
function respond(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(body));
}
function auth(req, secret) {
  const bearer = req.headers.authorization || '', expected = 'Bearer ' + secret;
  return bearer.length === expected.length && timingSafeEqual(Buffer.from(bearer), Buffer.from(expected));
}
export function makeServer({ token, tasks = queue } = {}) {
  if (!token || token.length < 32) throw new Error('BELUGA_AGENT_BRIDGE_TOKEN must be >=32 chars');
  return http.createServer(async (req, res) => {
    try {
      const path = new URL(req.url, 'http://127.0.0.1').pathname;
      if (req.method === 'GET' && path === '/health') return respond(res, 200, { ok: true, mode: 'read_only' });
      if (!auth(req, token)) return respond(res, 401, { error: 'Unauthorized' });
      if (req.method === 'POST' && path === '/v1/tasks') {
        if (!req.headers['content-type']?.startsWith('application/json')) return respond(res, 415, { error: 'JSON required' });
        let raw = '';
        for await (const chunk of req) { raw += chunk; if (raw.length > 4096) return respond(res, 413, { error: 'Too large' }); }
        let body; try { body = JSON.parse(raw); } catch { return respond(res, 400, { error: 'Bad JSON' }); }
        try { return respond(res, 202, tasks.create(body)); }
        catch (e) { return respond(res, 400, { error: e.message }); }
      }
      const m = path.match(/^\/v1\/tasks\/([0-9a-f-]{36})$/);
      if (req.method === 'GET' && m) {
        const t = tasks.get(m[1]); return respond(res, t ? 200 : 404, t || { error: 'Not found' });
      }
      return respond(res, 404, { error: 'Not found' });
    } catch { return respond(res, 500, { error: 'Unexpected error' }); }
  });
}
if (process.argv[1] && import.meta.url === new URL('file://' + process.argv[1]).href) {
  const server = makeServer({ token: process.env.BELUGA_AGENT_BRIDGE_TOKEN });
  const port = Number.parseInt(process.env.BELUGA_AGENT_PORT || '8794', 10);
  server.listen(port, '127.0.0.1', () => process.stdout.write('[beluga-agent] read-only on 127.0.0.1:' + port + '\n'));
}
