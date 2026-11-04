/** Phase 1 only permits read-only research on explicitly approved public hosts. */
export const TASK_KIND = 'web_research';
export function allowedHosts(raw = '') {
  if (!raw.trim()) return ['example.com', 'books.toscrape.com'];
  const hosts = raw.split(',').map(x => x.trim().toLowerCase()).filter(Boolean);
  if (!hosts.length || hosts.some(h => !/^(?!-)[a-z0-9.-]+$/.test(h) || h.includes('..') || h.startsWith('.'))) throw new Error('Invalid allowlist');
  return hosts;
}
export function validateTarget(input, hosts = allowedHosts(process.env.BELUGA_AGENT_ALLOWED_HOSTS || '')) {
  if (typeof input !== 'string' || input.length > 2048) throw new Error('Invalid URL');
  let url; try { url = new URL(input); } catch { throw new Error('Invalid URL'); }
  if (url.protocol !== 'https:' || url.username || url.password || url.port || url.hash) throw new Error('Clean HTTPS URL required');
  if (!hosts.includes(url.hostname.toLowerCase())) throw new Error('Target host is not approved');
  return url.toString();
}
export function validateRequest(body, hosts) {
  if (!body || typeof body !== 'object' || Array.isArray(body) || body.kind !== TASK_KIND) throw new Error('Only read-only web research is enabled');
  if (typeof body.passenger_id !== 'string' || !/^[a-zA-Z0-9_-]{1,100}$/.test(body.passenger_id)) throw new Error('Invalid passenger ID');
  return { kind: TASK_KIND, passenger_id: body.passenger_id, url: validateTarget(body.url, hosts) };
}
