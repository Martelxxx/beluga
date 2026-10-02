# Beluga / iAirport — V41 Exact-Reconstruction Repository

This repository is the canonical source for **iAirport V41**, a standalone, simulated airport-assistant frontend. The project is intentionally self-contained: the full working demo, visual assets, flight fixtures, service fixtures, state machine, animations, transitions, settings, and interaction logic live inside a single HTML file.

> **Primary source of truth:** `iairport_full_demo_v41.html`  
> **Convenience entry point:** `index.html` (byte-for-byte equivalent at this snapshot)  
> **Architecture handoff:** `docs/FRONTEND_HANDOFF_V41.md`  
> **Verification:** `docs/VERIFICATION_V41.md`

The goal of this README is not merely to explain how to run the app. It is a reconstruction specification: a developer or AI coding agent should be able to reproduce the current V41 experience without inventing new UI, changing interaction patterns, or flattening the motion system.

---

## 1. What iAirport is

iAirport is a mobile-first airport companion built around one conversational surface. It combines:

- airport context;
- a linked-flight/trip model;
- airport status and weather tiles;
- food, ride, metro, hotel, rental-car, lounge, and recovery flows;
- connected-service/provider concepts;
- simulated announcements and alerts;
- light/dark presentation with separate day/night airport artwork;
- contextual chat task handling;
- persistent user preferences;
- a compact, image-led home screen with deliberately unused negative space.

**V41 is a demo.** No live airline, airport, rideshare, transit, hotel, rental, payment, auth, booking, or purchasing API is connected. Every flight, quote, order, booking, announcement, transaction, and recovery action is simulated.

Do not convert simulated behavior into a claim of real-world completion when reconstructing this version.

---

## 2. Non-negotiable visual constraints

These decisions define the product identity and must be preserved unless a later product decision explicitly changes them:

1. **Do not enlarge connector logos, connector coins, or the add-connector `+` control.**
2. **Do not fill the empty Home area.** It is intentional negative space, not unfinished UI.
3. Preserve the airport photography and the curved overlapping panel geometry.
4. Preserve the glass/translucent treatment where it is currently used.
5. Preserve the restrained blue/white palette and the dark navy night palette.
6. Preserve compact status tiles and large airport-code hierarchy.
7. Preserve rotating Home prompt verbs and the conversational interaction model.
8. Keep transport controls visually small and decorative but still tappable.
9. Do not replace specific working flows with generic placeholders.
10. Open airport/service/detail surfaces must visually own the viewport; Home may remain mounted for state continuity but must be hidden and non-interactive behind the active surface.
11. On the Home destination tile, show **airport code only**. City/name metadata belongs inside detail screens.
12. The rental inventory is a structured offer list, not a stock-photo gallery.

---

## 3. Repository layout

```text
/
├── README.md
├── index.html
├── iairport_full_demo_v41.html
└── docs/
    ├── FRONTEND_HANDOFF_V41.md
    └── VERIFICATION_V41.md
```

There is intentionally no build system required for the current snapshot.

---

## 4. Run it locally

The file can be opened directly in a modern browser, but using a local HTTP server is preferred because browser security behavior around `file://` URLs varies.

### Python

```bash
python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080/
```

### Node

```bash
npx serve .
```

No environment variables or secret keys are required for the V41 demo.

---

## 5. Canonical viewport and composition

The application shell is deliberately constrained to a mobile canvas:

```css
.app {
  position: relative;
  width: min(100vw, 460px);
  height: 100dvh;
  overflow: hidden;
  isolation: isolate;
}
```

The approved reference artwork was composed at **707 × 1536** and is stretched to the app viewport with `object-fit: fill`, not `cover`.

That distinction matters. A recreation that uses `cover` will crop and shift interactive geometry relative to the art.

Primary responsive review sizes used in V41:

- `390 × 844`
- `360 × 640`

The app should also remain usable from roughly 320 px through the 460 px shell maximum.

---

## 6. Visual system

### Typography

Primary family:

```css
font-family: "Imprima", sans-serif;
```

Core ink and brand blue start from:

```css
--ink: #21354b;
--blue: #4278b9;
```

Do not substitute a dramatically different geometric or corporate sans-serif. Typography is intentionally soft and compact.

### Home image treatment

The airport artwork is not a generic hero banner. It is part of the full-screen composition and lines up with measured hotspot coordinates.

The day and night experiences use **separate raster layers**. Dark mode must not be created by simply inverting or heavily filtering the day photo.

The night raster should read as the same airport after dark, including:

- darkened sky/environment;
- warm terminal/window illumination;
- ramp/road light points;
- subtle tower/airfield illumination;
- preserved architecture and camera angle.

### Dark-mode lower surface

In V41 the curved lower Home shoulder, tile-stage surface, and composer are treated as **one continuous dark material**. Do not independently tint the curve, lower panel, and composer; that recreates the visible seam that V41 removed.

### Status tiles

The Home status row is compact and image-led.

Representative sizing:

```css
:root { --home-tile: clamp(58px, 16vw, 64px); }
```

The row uses four equal compact tiles. Cards use approximately 15 px radii, restrained shadows, image backgrounds, and a lower dark gradient for text legibility.

Airport-code values are intentionally much larger than supporting labels.

### Connector controls

Connector controls are deliberately small. In the final review pass, connector coins measured **25 × 25 px** at the 390 px viewport. Preserve their visual footprint. Accessible naming may change; visual dimensions should not.

---

## 7. Layering model

The app is a stack of surfaces rather than a conventional multi-page website.

Conceptually:

```text
z0   reference/day-night art
z2   measured Home hotspots
z3   lower Home tile stage
z5   Home status / flight context / indicator
z30  transient toast
z40+ chat / feature surfaces
z50+ rental / hotel / settings / airport-detail surfaces
zTop global composer when required by active route
```

The exact z-index values in the source file are authoritative.

### Critical rule

When a detail surface is open:

- Home remains mounted so state and transition continuity are preserved;
- Home tiles and controls are hidden from view;
- Home controls do not receive pointer interaction;
- only the active screen is accessible to assistive technology;
- back navigation restores the prior visible surface rather than rebuilding Home from scratch.

---

## 8. Authoritative application state

V41 centralizes current product state under:

```js
window.iAirportV41.state
```

Persisted browser key:

```text
iairport.v41.state
```

Do **not** use `localStorage.clear()`. Only iAirport-owned keys may be removed.

Canonical shape:

```js
{
  version: 41,
  airport: "IAD",
  flightNumber: null | "DL1247" | "UA2398" | "AF55",
  scenario: "onTime" | "delayed" | "cancelled" | "boarding",
  demoClock: ISODateString,
  demoClockStartedAt: Number,
  task: null | { type, stage, data },
  orders: { food, ride, rental, hotel, lounge },
  connectedServices: [],
  settings: {
    theme,
    textSize,
    language,
    currency,
    reduceMotion,
    airportAnnouncements,
    gateAlerts,
    disruptionAssistance,
    confirmBeforePurchase,
    rememberPreferences,
    tripHistory,
    vehiclePreference
  },
  screen: "home" | screenId,
  history: [],
  chatHistory: []
}
```

### State rule

Every trip-aware screen must derive from the same selected-flight selector/service path. Never hardcode an airline, gate, city, or boarding time inside a reusable component.

---

## 9. Canonical demo flights

| Flight | Airline | Route | Gate | Boarding | Arrival |
|---|---|---|---|---|---|
| DL1247 | Delta | IAD → ATL | B72 | 3:42 PM | 6:10 PM |
| UA2398 | United | IAD → ORD | C4 | 4:18 PM | 6:14 PM |
| AF55 | Air France | IAD → CDG | A19 | 5:47 PM | 8:20 AM +1 |

The shared initial demo clock is:

```text
2026-10-02T19:00:00Z
```

which is 3:00 PM at IAD for the demo date.

Unknown flight numbers must throw/return an explicit unsupported-demo condition. They must **not** fabricate a fallback itinerary, and a failed lookup must not erase the previously selected valid flight.

---

## 10. Scenario model

V41 supports four reviewable flight scenarios:

### `onTime`
Uses scheduled timestamps.

### `delayed`
Moves relevant times together by 75 minutes so status, countdown, announcements, and revised schedule remain coherent.

### `cancelled`
No active boarding countdown. No boarding announcement scheduling.

### `boarding`
The demo clock advances to just after the boarding timestamp and card language changes to a boarding-now state.

### Timing rule

Never reset a generic countdown when linking a flight. Countdown values are derived from the selected flight's actual `boardingAt` timestamp relative to the shared demo clock.

---

## 11. Simulated service boundary

The UI calls:

```js
window.iAirportV41.services
```

Primary methods:

```ts
getAirportSnapshot(code)
searchFlights(query)
getFlight(number)
linkFlight(number)
getAnnouncements()
getMetroRoute({ airportCode, destination })
quoteRide({ airportCode, destination, type })
quoteFood({ venue, item })
quoteRental({ airportCode, provider, vehicle, dates })
quoteHotel({ airportCode, property, dates, adults, children, rooms })
confirmBooking(kind, quote)
recoverTrip(option)
```

In V41 these return local/demo values. A production implementation should preserve these UI-facing contracts and replace the method bodies with backend calls.

Never place provider secrets in browser code.

---

## 12. Conversation task machines

Conversation is stateful. Do not implement the assistant as an unordered list of keywords.

Canonical task state:

```js
state.task = {
  type,
  stage,
  data
}
```

### Metro

```text
needDestination → quoted
```

Retain departure airport and destination. Results include service, station access, route, sample fare, and ticket-acquisition instructions.

A phrase such as “I need a hotel” while metro context is active is a **task switch**, not a destination called “I need a hotel.”

### Rental cars

```text
browse → needDates → needTimes → quote → confirmed
```

Retain:

- airport;
- provider;
- vehicle/class;
- dates;
- pickup time;
- return time;
- daily rate;
- estimated fees;
- provider connection/handoff status;
- confirmation state.

### Hotels

```text
browse → needDetails → quote → confirmed
```

Retain:

- selected property;
- airport;
- dates;
- adults;
- children;
- rooms;
- preferences;
- nightly rate;
- estimated fees;
- confirmation state.

### Food and rides

Use:

```text
selection → quote → confirmation → active status
```

When **Confirm before purchase** is enabled, the user must explicitly confirm before simulated completion.

### Recovery

Recovery changes the actual simulated itinerary/scenario and dependent booking state. Do not add a generic “recovered” record while leaving ride, food, or hotel state unchanged.

---

## 13. Composer behavior

There is one global composer: `#homeForm`.

Do not create a second composer for service pages.

Rules:

- Home: composer remains in its established lower position.
- Connector page: the same composer moves to the **top** of the screen.
- Service/detail screens: the same composer remains reachable and must not be covered by the active page.
- Content surfaces need enough scroll padding to clear the composer.
- Opening chat from Settings must not leave stale Settings-active state.
- Mobile keyboard/viewport changes must not create duplicate inputs.
- Returning Home clears route-specific guidance when appropriate.

Contextual placeholders and rotating Home prompt verbs are part of the design and should remain.

---

## 14. Rental inventory design

V41 intentionally does **not** rely on external vehicle photography.

Each rental offer includes:

- compact provider logo/brand;
- vehicle class;
- model wording using **“or similar”**;
- neutral line/silhouette vehicle art;
- sample daily rate;
- seats;
- bags;
- automatic transmission indicator;
- mileage indicator;
- provider connection or handoff state;
- one primary **Choose** action.

The page is an offer list, not a photo gallery.

Selecting an offer must feed the existing rental task machine. Do not create a second booking state inside the rental page component.

For unconnected providers, show an in-demo handoff surface that:

1. preserves the selected offer;
2. explains that real completion would happen with the provider;
3. lists what data would be passed;
4. provides Continue, Back, and Cancel;
5. explicitly says no real reservation was made.

---

## 15. Motion system

Motion is part of the product identity. Recreating the static geometry but replacing transitions with generic fades is not equivalent.

### Day/night crossfade

The day and night image layers crossfade over approximately:

```text
1.15 s
```

The transition is reversible. Theme changes must preserve current flight, task, and active screen.

### Major sheet/page slide

Rental and other full-height sheets use the characteristic long easing:

```css
transition:
  transform .68s cubic-bezier(.18,.82,.16,1),
  visibility .68s step-end;
```

Open state changes visibility immediately and animates transform:

```css
transition:
  transform .68s cubic-bezier(.18,.82,.16,1),
  visibility 0s step-start;
```

Typical closed transform:

```css
transform: translateY(104%);
```

### Home linked-flight row

The secondary flight-context row appears with approximately:

```css
opacity .36s ease,
transform .45s cubic-bezier(...)
```

starting slightly translated downward.

### Reference-art reset

Measured artwork movement/reset uses approximately:

```css
transform 420ms cubic-bezier(.18,.85,.26,1)
```

### Press feedback

Compact cards and buttons generally use fast physical feedback in the `140–180 ms` range, including small scale/translate changes and restrained shadow changes.

Example status-card active treatment:

```css
transform: scale(.96);
```

### Legacy geometry transitions

The monolithic V41 file contains a small number of longer geometry transitions inherited from the approved prototype, generally between roughly `0.52 s` and `1.12 s`, using custom cubic-bezier curves. **Do not normalize these blindly.** When reconstructing a specific surface, copy the selector's exact duration and easing from `iairport_full_demo_v41.html`.

### Reduced motion

Both the in-app preference and operating-system preference should reduce motion. V41's app-level reduction effectively collapses durations:

```css
.v41-reduce-motion * {
  transition-duration: .01ms !important;
  animation-duration: .01ms !important;
}
```

A modular production rewrite may implement this more selectively, but perceived behavior should be equivalent.

---

## 16. Navigation transition philosophy

Routine repeated navigation should feel quicker than the day/night environmental transition.

Use this hierarchy:

1. **Press response:** immediate / ~0.14–0.18 s.
2. **Routine small UI transitions:** ~0.2–0.45 s.
3. **Page/sheet ownership transitions:** ~0.52–0.72 s.
4. **Large compositional/legacy geometry movements:** up to ~1.12 s where the source specifies it.
5. **Day/night environment transition:** ~1.15 s.

Do not add gratuitous bouncing, spring overshoot, parallax, or glow effects that are not present in the source.

---

## 17. Settings contract

Frontend settings in V41 include:

- appearance: light/dark;
- text size: Default / Large / Extra large;
- app language;
- preferred currency;
- reduce motion;
- airport announcements;
- gate and boarding alerts;
- disruption assistance;
- confirm before purchase;
- remember travel preferences;
- trip history;
- rental/vehicle preference;
- demo flight scenario selector.

Demo currency conversion values are fixed:

```text
USD 1.00
EUR 0.93
GBP 0.80
CAD 1.36
```

Do not present these as live FX rates.

Text-size changes must not enlarge connector coins or the add-connector control.

Hardware/integration-dependent controls must describe their demo limitation honestly.

---

## 18. Alerts, announcements, and transient notifications

Simulated alerts are controlled by the relevant settings.

Flight announcements must derive from the selected flight and scenario. Cancelled flights do not continue to emit boarding announcements.

### Toast lifecycle requirement

Transient trip-link messages such as:

```text
DL1247 added to your trip
```

use a dedicated transient dismissal timer. That timer must **not** be placed in the flight/scenario timer pool, because rescheduling announcements can clear that pool.

This is a specific V41 hotfix: trip-link toasts must auto-dismiss and must not become pinned when flight timers are refreshed.

---

## 19. Theme behavior

Theme changes are state changes, not reloads.

Switching between light and dark must preserve:

- selected flight;
- current airport;
- current task and stage;
- collected task data;
- current screen;
- active orders/bookings;
- navigation history as appropriate.

Dark mode should be applied consistently across:

- Home lower material;
- global composer;
- chat;
- announcements;
- utility cards;
- menus;
- service/detail pages;
- settings;
- inputs;
- confirmation surfaces;
- provider handoff surfaces.

Avoid excessive neon outlines or generic “dark mode glow.”

---

## 20. Accessibility rules

Preserve these behaviors in any rewrite:

- connector controls have accessible names;
- visible screen state and `aria-hidden` state agree;
- only the intended active surface receives interaction;
- focus-visible states remain clearly visible;
- user-entered chat text is inserted through `textContent` or safely escaped;
- generated dynamic markup escapes user-controlled values;
- one global composer prevents duplicate focus targets during mobile keyboard changes;
- large-text modes adapt layout rather than clipping critical labels.

---

## 21. Production architecture target

The current HTML is intentionally self-contained. A production rewrite should preserve behavior while splitting responsibilities approximately as follows:

```text
src/
├── state/
│   ├── appStore.ts
│   └── selectors.ts
├── routing/
│   └── navigation.ts
├── conversation/
│   └── taskMachine.ts
├── services/
│   ├── flights.ts
│   ├── airports.ts
│   ├── announcements.ts
│   ├── transit.ts
│   ├── rides.ts
│   ├── food.ts
│   ├── rentals.ts
│   ├── hotels.ts
│   └── recovery.ts
├── preferences/
│   └── settings.ts
├── assets/
│   ├── airportArtwork.ts
│   └── brandAssets.ts
└── rendering/
    ├── home.ts
    ├── trip.ts
    ├── chat.ts
    └── servicePages.ts
```

### Important

A modular rewrite is only equivalent if it preserves:

- the same visible hierarchy;
- same negative space;
- same interaction outcomes;
- same task retention;
- same flight propagation;
- same dark/light behavior;
- same sheet ownership;
- same approximate timings and exact critical easing curves;
- same connector dimensions;
- same composer movement rules;
- same fallback behavior when images or browser capabilities are unavailable.

---

## 22. Future API boundaries

The frontend is ready to replace demo services with backend-backed implementations for:

- airport snapshot / operational data;
- weather;
- security wait times;
- flight search and status;
- airport announcements;
- directory/search;
- indoor navigation;
- metro/transit routing;
- rideshare quote/request;
- food menu/order/status;
- rental inventory/quote/handoff;
- hotel availability/quote/handoff;
- translation;
- user preferences;
- auth/profile;
- payments and confirmations.

Provider keys, auth tokens, payment credentials, and secret API keys belong behind a server boundary. Do not embed them in `index.html`, bundled frontend JS, or public environment variables.

---

## 23. Exact-reconstruction workflow for a developer or AI agent

If you are rebuilding iAirport from this repository rather than modifying the existing file, follow this order:

### Step 1 — Freeze the source snapshot

Treat `iairport_full_demo_v41.html` as read-only reference during the first reconstruction pass.

### Step 2 — Recreate shell geometry first

Match:

- 460 px max-width mobile shell;
- 100dvh behavior;
- full-screen reference artwork placement;
- curved Home panel geometry;
- empty Home negative space;
- four-tile status row;
- linked-flight secondary row;
- composer geometry;
- safe-area handling.

Do not build feature flows until this matches visually.

### Step 3 — Recreate motion before adding data complexity

Match the critical transitions in Section 15 and copy exact selector timings from the HTML for any surface being ported.

### Step 4 — Implement one authoritative state store

Port the V41 state shape before implementing screens.

### Step 5 — Implement selectors and demo services

All screens should read selected-flight/trip values through the same selector/service layer.

### Step 6 — Implement route ownership

Make sure opening IAD, rentals, hotels, connectors, settings, or other detail pages visually hides Home while preserving Home state underneath.

### Step 7 — Implement the single global composer

Do not create route-specific duplicate inputs. Move/reposition the same composer based on route.

### Step 8 — Implement task machines

Port metro, rentals, hotels, food, rides, and recovery with explicit stage/data retention.

### Step 9 — Implement settings and persistence

Use only the iAirport storage namespace.

### Step 10 — Verify against the behavioral matrix below

Do not call the recreation complete based on screenshots alone.

---

## 24. Minimum behavioral verification matrix

A faithful reconstruction must verify at least:

### Fresh state

- no fabricated selected flight;
- general airport/service shortcuts work;
- flight-specific features offer linking rather than inventing a flight.

### Flight linking

- DL1247;
- UA2398 → United / IAD→ORD / C4 / 4:18 PM;
- AF55 → Air France / IAD→CDG / A19 / 5:47 PM / next-day arrival;
- invalid flight preserves previous valid selection.

### Scenarios

- on time;
- delayed;
- cancelled;
- boarding.

### Cross-screen consistency

Validate the same selected trip across:

- Home;
- My trip;
- chat responses;
- destination detail;
- navigation;
- announcements;
- boarding/gate guidance;
- recovery.

### Service/task flows

- metro task switch;
- ride quote/confirmation/reopen;
- food quote/confirmation/status/reopen;
- connected rental flow;
- unconnected rental provider handoff;
- hotel detail retention;
- recovery updating dependent bookings.

### Navigation

- service page opened directly;
- same service opened through chat;
- back navigation;
- composer remains reachable;
- connector composer appears at top;
- airport/detail page fully covers Home.

### Settings

- appearance;
- day↔night crossfade both directions;
- large text;
- language;
- currency;
- alert gates;
- confirm-before-purchase;
- reset/clear local iAirport data.

### Regression checks

- no duplicate booking on repeat tap;
- no duplicate timers;
- trip-linked toast dismisses;
- no horizontal overflow at review widths;
- missing external assets do not break layout.

---

## 25. Verification status of this snapshot

The supplied V41 build was reviewed in Chromium responsive browser emulation at 390×844 and 360×640.

This is **not** a claim of physical-device testing.

Physical-device items still requiring real-hardware verification include:

- iOS/Android soft keyboard edge cases;
- native haptics;
- OS notification permission behavior;
- device-specific speech voices;
- real provider/API networking when those integrations exist.

See `docs/VERIFICATION_V41.md` for the detailed test record and hotfix notes.

---

## 26. Source-of-truth priority

When documentation and implementation appear to differ, use this priority order:

1. `iairport_full_demo_v41.html` — executable visual/behavioral truth.
2. `README.md` — reconstruction contract and non-negotiable design intent.
3. `docs/FRONTEND_HANDOFF_V41.md` — state/service/workflow architecture.
4. `docs/VERIFICATION_V41.md` — what was actually checked and known limitations.

Do not “improve” an apparent oddity in the source without first determining whether it is an intentional visual decision or a known limitation.

---

## 27. Current version

**iAirport V41**  
Snapshot date: **October 2, 2026**

The project is ready to be used as the canonical reference for the next implementation phase: replacing simulated service methods with real integrations while preserving the V41 product behavior and visual identity.
