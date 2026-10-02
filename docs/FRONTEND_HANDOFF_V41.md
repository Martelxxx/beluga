# iAirport V41 — Frontend Handoff

## Scope

`iairport_full_demo_v41.html` is a standalone simulated frontend. It contains no live airline, airport, weather, transit, hotel, rental-car, rideshare, payment, authentication, or purchasing integration. Every quote, status, booking, announcement, recovery action, and confirmation is demo data.

## V41 state model

V41 adds one authoritative application state under `window.iAirportV41.state` and persists only the namespaced demo snapshot `iairport.v41.state`.

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
    theme, textSize, language, currency, reduceMotion,
    airportAnnouncements, gateAlerts, disruptionAssistance,
    confirmBeforePurchase, rememberPreferences, tripHistory,
    vehiclePreference
  },
  screen: "home" | screenId,
  history: [],
  chatHistory: []
}
```

Every V41 trip-aware render reads the current flight through `scenarioFlight()`. Flight search and the flight-link sheet call the same `services.linkFlight()` path.

### Supported flight fixtures

| Flight | Airline | Route | Gate | Boarding | Arrival |
|---|---|---|---|---|---|
| DL1247 | Delta | IAD → ATL | B72 | 3:42 PM | 6:10 PM |
| UA2398 | United | IAD → ORD | C4 | 4:18 PM | 6:14 PM |
| AF55 | Air France | IAD → CDG | A19 | 5:47 PM | 8:20 AM +1 |

Unknown numbers throw `UNSUPPORTED_DEMO_FLIGHT`. The previous valid flight remains selected.

## Shared demo clock and scenarios

The initial demo clock is `2026-10-02T19:00:00Z` (3:00 PM at IAD). Countdown cards derive minutes from the selected flight's `boardingAt` value. Switching flights does not create a hard-coded 42-minute timer.

- `onTime`: scheduled timestamps.
- `delayed`: timestamps shift 75 minutes together.
- `cancelled`: no active boarding countdown and no flight announcements.
- `boarding`: demo clock moves just after boarding and the card reads `Boarding now`.

The Settings page includes a demo-only scenario selector so these states can be reviewed without live operations data.

## Simulated service boundary

The UI calls `window.iAirportV41.services` rather than manufacturing transaction state directly.

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

All methods return local fixtures/promises. A production implementation can retain the UI state contract and replace the method bodies with authenticated backend calls.

## Conversation task state

Conversation flows use `state.task = { type, stage, data }`.

### Metro

`needDestination → quoted`

The departure airport is retained. A request such as “I need a hotel” is interpreted as a task switch rather than a transit destination. Metro results include service, route, sample fare, station access, and ticket-acquisition instructions.

### Rental cars

`browse → needDates → needTimes → quote → confirmed`

Retained fields: airport, provider, vehicle, dates, pickup/return time text, daily rate, fees, status, and demo confirmation.

Unconnected providers use an in-demo handoff showing what would be sent to the provider, plus Continue, Back, and Cancel. It explicitly states that no reservation has been made.

### Hotels

`browse → needDetails → quote → confirmed`

Retained fields: property, airport, dates/guest input, parsed adults/children/rooms, preferences, nightly rate, fees, status, and demo confirmation.

### Ride and food

Both use selection → quote → confirmation. When **Confirm before purchase** is on, the explicit confirmation control is required. Active home cards reopen the saved order/ride rather than starting a second transaction.

### Recovery

Recovery changes the actual simulated itinerary scenario and updates dependent food/ride/hotel state where applicable. Repeated recovery interaction renders from the same state rather than creating generic duplicate entries.

## Navigation and composer

V41 owns `state.screen` and `state.history` and keeps the single `#homeForm` composer above service screens. The composer is never duplicated.

Opening the composer from a service or Settings route moves into chat while retaining task state and removing stale Settings screen state. Back uses the recorded screen history. Scrollable service surfaces reserve bottom clearance for the composer.

## Settings behavior

Implemented frontend effects:

- Light/dark appearance, preserving current state.
- Separate day/night raster crossfade (1.15 s, reversible).
- Reduced motion from both the app setting and system preference.
- Default/Large/Extra large readable text sizing without resizing connector coins.
- App language selection changes `document.lang`, common conversation controls, task prompt language, and simulated announcement language.
- Currency selection uses fixed demo conversion values: USD 1.00, EUR 0.93, GBP 0.80, CAD 1.36.
- Alert toggles gate simulated announcements/boarding alerts.
- Confirm-before-purchase changes transaction completion flow.
- Rental preference is retained in state for future recommendation scoring.
- Preference/history toggles persist inside the V41 namespace.
- Clear local data removes iAirport-prefixed storage only; it does not clear unrelated browser storage.

Hardware-dependent features such as haptics, OS notifications, precise location, and speech synthesis remain browser/device dependent and are not represented as live capabilities.

## Theme and imagery

The existing day and night airport rasters remain separate layers. V41 keeps the reversible opacity crossfade and removes the bright lower dark-mode panel by theming the tile-stage gradient. Dark tiles use restrained shadows rather than bright glow outlines.

Destination cards continue to use the prototype's destination artwork where available. A missing external rental/hotel image is replaced by an intentional in-app fallback rather than a broken image or a misleading exact vehicle photograph.

## Accessibility and safety

- Connector controls receive accessible names without changing their visual dimensions.
- User-entered conversation text is inserted with `textContent`.
- Generated feature markup escapes dynamic strings before insertion.
- Screen `aria-hidden` values follow V41 navigation state.
- The single composer avoids duplicate inputs during mobile viewport/keyboard changes.

## Future integration boundaries

A production rebuild should preserve the V41 state/service contracts but split the standalone file into modules:

```text
state/
  appStore.ts
  selectors.ts
routing/
  navigation.ts
conversation/
  taskMachine.ts
services/
  flights.ts
  airports.ts
  announcements.ts
  transit.ts
  rides.ts
  food.ts
  rentals.ts
  hotels.ts
  recovery.ts
preferences/
  settings.ts
assets/
  airportArtwork.ts
  brandAssets.ts
rendering/
  home.ts
  trip.ts
  chat.ts
  servicePages.ts
```

Provider secrets, payment credentials, airline tokens, and API keys must live behind a server boundary, never in the browser demo.

## Remaining limitations

V41 is a production-handoff-quality interactive prototype, not a production booking client. Network integrations, authentication, payment authorization, live maps, real ticketing, push notifications, native haptics, and real provider handoffs are intentionally absent. Speech synthesis depends on browser support. Browser responsive emulation was used for verification; no physical-device test was performed in this build pass.

## Review-pass layout decisions

The final V41 review pass adds several explicit presentation contracts that should be preserved in a production rebuild:

- **Home dark surface:** the curved lower Home shoulder, tile-stage background, and global composer form one continuous dark material. Do not independently tint the curve or composer.
- **Connector route:** the existing global composer is repositioned to the top while the connector sheet is active. Connector coins, provider marks, and the add-connector control retain their established compact dimensions.
- **Modal/detail ownership:** an airport or service surface owns the visible content viewport while open. Home content remains mounted for state continuity, but is hidden from view and pointer interaction until the surface closes.
- **Destination tile:** the Home destination tile displays the airport code only. City/name metadata belongs inside the destination-detail surface, not below the code on Home.
- **Rental inventory:** rental browsing is a structured offer list, not a photo gallery. Each offer carries provider branding, class, `or similar` model language, neutral vehicle silhouette, sample daily rate, capacity facts, connection/handoff state, and one primary selection action. This keeps the demo complete offline and avoids presenting a stock photograph as an exact vehicle.

The rental renderer should continue to route selection into the existing V41 rental task machine (`browse → needDates → needTimes → quote → confirmed`) rather than maintaining a second booking state inside the page component.
