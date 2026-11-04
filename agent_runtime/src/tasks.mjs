import { randomUUID } from 'node:crypto';
import { allowedHosts, validateRequest } from './policy.mjs';
export class TaskQueue {
  constructor({ runner, hosts = allowedHosts(process.env.BELUGA_AGENT_ALLOWED_HOSTS || '') } = {}) {
    if (typeof runner !== 'function') throw new Error('Runner required');
    this.runner = runner; this.hosts = hosts; this.tasks = new Map(); this.pending = []; this.busy = false;
  }
  create(body) {
    const req = validateRequest(body, this.hosts);
    if (this.pending.length >= 10) throw new Error('Agent queue is full');
    if ([...this.tasks.values()].filter(t => t.passenger_id === req.passenger_id && ['queued', 'running'].includes(t.status)).length >= 2) throw new Error('Too many active tasks');
    const task = { id: randomUUID(), ...req, status: 'queued', session_url: null, result: null, error: null };
    this.tasks.set(task.id, task); this.pending.push(task.id);
    queueMicrotask(() => void this.drain());
    return structuredClone(task);
  }
  get(id) { return this.tasks.has(id) ? structuredClone(this.tasks.get(id)) : null; }
  async drain() {
    if (this.busy) return; this.busy = true;
    try {
      while (this.pending.length) {
        const task = this.tasks.get(this.pending.shift()); if (!task) continue;
        task.status = 'running';
        try {
          task.result = await this.runner(task.url, { onSession: id => {
            if (/^[0-9a-zA-Z-]{1,128}$/.test(id)) task.session_url = 'https://www.browserbase.com/sessions/' + id;
          } });
          task.status = 'completed';
        } catch (err) {
          task.status = 'failed'; task.error = 'Browser task failed; inspect backend/session logs';
          process.stderr.write('[beluga-agent] failed task ' + task.id + ': ' + (err?.name || 'Error') + '\n');
        }
      }
    } finally { this.busy = false; }
  }
}
