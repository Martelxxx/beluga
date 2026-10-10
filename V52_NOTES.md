# Beluga V52 — bot-only transactional pages + RouteStack hotels

Scope:
1. On non-conversational information/transaction pages, the full composer is hidden.
   A floating Beluga bot icon appears above bottom actions. Tapping it opens chat
   and restores the composer. Flight-commerce pages are intentionally excluded so
   their previously approved composer behavior stays unchanged.
2. Hotel search/pricing now uses RouteStack through the local Python server.
   Credentials remain in .env and never enter the browser HTML.
3. RouteStack hotel search dynamically discovers the MCP hotel-search tool, so
   Beluga is not hardcoded to a vendor-specific tool name. Search results are
   normalized into Beluga hotel cards, and returned booking links hand off to
   RouteStack secure checkout.

Required .env fields:
ROUTESTACK_API_KEY=
ROUTESTACK_API_SECRET=
ROUTESTACK_BASE_URL=https://mcp.routestack.ai

Optional:
ROUTESTACK_PARTNER_TOKEN=
ROUTESTACK_TIMEOUT=35

Unrelated protected Home journey, mobility/freedom, and composer prompt-loop
regions were kept byte-identical to V51.
