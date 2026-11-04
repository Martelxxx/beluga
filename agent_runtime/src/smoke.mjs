import { researchPage } from './browser.mjs';
if (!process.env.BROWSERBASE_API_KEY) {
  console.error('Configure Browserbase key in backend secrets first.'); process.exit(1);
}
try {
  const data = await researchPage(process.argv[2] || 'https://example.com/', {
    onSession: id => console.log('Cloud session: https://www.browserbase.com/sessions/' + id)
  });
  console.log(JSON.stringify(data, null, 2));
} catch (e) { console.error('Browser smoke test failed: ' + e.name); process.exitCode = 1; }
