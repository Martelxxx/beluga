# Beluga Agent Runtime — Phase 1 (draft)
Standalone **read-only** Browserbase + Stagehand v4 backend service. No passenger UI, Focus rail, Dynamic Hub styling, navigation or ingestion changes. Do not deploy the older v52.2 GitHub passenger frontend over the newer Beluga build.

## Requirements
Node.js 22.18+, Browserbase key stored in server secrets, and separate random backend-only BELUGA_AGENT_BRIDGE_TOKEN of at least 32 characters. No Browserbase project ID is needed. Free-tier Model Gateway can power the first demo without an extra model key.

## Setup (requires permission before installing dependencies)
- In agent_runtime, run npm install.
- Set BROWSERBASE_API_KEY and BELUGA_AGENT_BRIDGE_TOKEN in the backend environment, not in HTML/Git/chat.
- For first cloud session: npm run smoke.
- For backend task API: npm start (127.0.0.1:8794).
- For tests: npm test (no external packages required).
- View full cloud session links in https://www.browserbase.com/sessions.

## API
POST /v1/tasks from a trusted backend with Authorization: Bearer <bridge token>, Content-Type: application/json and body {"kind":"web_research","passenger_id":"guest_001","url":"https://example.com/"}. Response 202 gives task id. Poll authenticated GET /v1/tasks/{id} for queued/running/completed/failed and a session_url.

**Not production-ready:** in-memory task state, single-process queue, no persistent passenger authentication or durable transaction approvals. No purchases, payments, logins, submissions, rides, cookies or merchant automations enabled. Do not expose directly to the internet.

Next: connect newer Beluga composer backend to this service, add Dynamic Hub progress feedback without changing visuals, and build merchant-approved quote preparation and server-enforced user approval (single-use, price-bound, idempotent), preferring official Uber MCP/partner access.

## macOS guided installation and first session

Run `bash setup_mac.command` from `agent_runtime/` on the networked Mac hosting the Beluga development environment. The script checks for Node.js 22.18+, installs it through nvm or Homebrew if available, installs the Browserbase `browse` CLI if absent, installs Stagehand dependencies, prompts secretly for the Browserbase key if unset, verifies account access, starts a disposable read-only cloud browser, prints the complete session link, and runs tests. It does not write the Browserbase key to disk or modify the passenger UI. No project ID is needed.

The hosted ChatGPT sandbox could not reach registry.npmjs.org (DNS EAI_AGAIN). Local Node security tests pass, but the first live browser session remains unverified until this script runs on a machine with npm/Browserbase network access. The code is Phase 1 research-only; payments, logins and purchases are disabled.
