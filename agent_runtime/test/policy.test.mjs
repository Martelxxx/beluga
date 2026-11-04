import test from 'node:test';
import assert from 'node:assert/strict';
import { allowedHosts, validateTarget, validateRequest } from '../src/policy.mjs';
import { TaskQueue } from '../src/tasks.mjs';
const hosts = allowedHosts('example.com,books.toscrape.com');
test('only allowlisted HTTPS destinations', () => {
  assert.equal(validateTarget('https://example.com/',hosts), 'https://example.com/');
  for (const u of ['http://example.com','https://localhost','https://example.com.evil.com','https://example.com:8888','https://a:b@example.com']) assert.throws(() => validateTarget(u,hosts));
});
test('financial actions are disabled', () => {
  for (const kind of ['purchase','checkout','book_uber','login']) assert.throws(() => validateRequest({kind,passenger_id:'guest',url:'https://example.com/'},hosts));
});
test('queue records full browser session and completion', async () => {
  const q = new TaskQueue({hosts,runner:async(url,{onSession}) => {onSession('123e4567-e89b-12d3-a456-426614174000');return {title:'Example',source_url:url};}});
  const t=q.create({kind:'web_research',passenger_id:'guest',url:'https://example.com/'});
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(q.get(t.id).status,'completed');
  assert.equal(q.get(t.id).session_url,'https://www.browserbase.com/sessions/123e4567-e89b-12d3-a456-426614174000');
});
