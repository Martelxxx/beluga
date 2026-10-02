# iAirport V41 — Verification Report

## Test method

The final standalone HTML was parsed and executed in headless Chromium with responsive browser emulation. Checks were run against 390×844 and 360×640 viewports. This was **browser emulation, not a physical-device test**.

## Passed

- Fresh start has no fabricated linked flight.
- Service flows can open without a selected flight.
- DL1247, UA2398, and AF55 use the shared selected-flight state.
- UA2398 propagates United, IAD → ORD, Gate C4, boarding 4:18 PM.
- AF55 propagates Air France, IAD → CDG, Gate A19, boarding 5:47 PM, next-day arrival.
- Unknown `BOGUS` input returns an unsupported-demo response and preserves the previous valid flight.
- Flight search and the link sheet use the same V41 link operation.
- Cancelled scenario shows `Cancelled` instead of an active countdown and suppresses scheduled flight announcements.
- Delayed scenario updates status and revised times together.
- Boarding scenario uses `Boarding now` behavior.
- Metro task switches cleanly to hotel when the user says “I need a hotel.”
- Enterprise rental selection retains provider, vehicle, dates, times, rate, estimated fees, quote, and confirmation.
- Unconnected rental handoff exposes passed details and working Continue/Back/Cancel controls.
- Hotel flow retains property, dates, adults, children, rooms, preference text, rate, fees, and quote.
- Food and ride require quote → confirmation when Confirm-before-purchase is enabled.
- Food and ride home cards reopen their saved task/status instead of generating duplicates.
- Recovery updates the itinerary scenario and dependent food/ride booking state.
- Composer remains a single input and is accessible from service routes.
- V41 navigation history returns to the previous screen and clears stale Settings state when appropriate.
- Text size, language, currency, rental preference, alert flags, and confirmation preference are stored in shared settings state.
- Clear local data resets flight, task, orders, preferences, connectors, timers, history, and theme without calling `localStorage.clear()`.
- Day → night and night → day use the separate artwork layers and reversible crossfade.
- Dark mode no longer leaves the abrupt bright lower home panel.
- Rental/hotel fallback art does not depend on an external image URL.
- No horizontal document overflow at 390×844 or 360×640 in tested states.
- No JavaScript page errors in the main trip/task transaction checks.

## Visual inspection

The 390×844 light and dark home states were visually inspected. The home composition, empty central area, curved panel geometry, airport photography, compact transport controls, compact status tiles, connector sizing, and large airport-code hierarchy remain intact.

## Not tested on real hardware

- Physical iPhone/Android keyboard behavior.
- Native haptic feedback.
- OS push notification permissions.
- Device-specific speech voice availability.
- Live provider/API network behavior, because V41 is intentionally offline/simulated.

## Post-build visual correction pass — October 2, 2026

Additional browser-emulation checks were run after the V41 visual-polish corrections requested during review.

Passed:

- Dark Home lower curved surface and the composer now use one continuous dark material; the pale/mismatched tip directly above the composer is no longer exposed.
- The connector sheet keeps the existing connector/logo/+ dimensions while moving the single global composer to the top of the screen. At the 390 px test width its computed top position was 16 px.
- Opening the IAD airport surface hides the Home status row, flight context, connector rail, transport actions, and message chip behind the active page. The underlying Home state remains mounted for return navigation.
- Destination Home tile renders only the airport code. The former city metadata element is empty and hidden.
- The V41 rental page now renders three structured sample offers with provider branding, category, neutral vehicle silhouette, daily sample rate, model-or-similar wording, capacity facts, provider state, and one primary Choose action. It no longer depends on remote vehicle photography.
- Connector coins measured 25 × 25 px in the connector-grid browser check after the composer move; the requested compact connector sizing remains unchanged.
- No script exceptions were observed in the final targeted DOM run.

These checks used Chromium responsive browser emulation and DOM inspection, not physical-device testing.


## Hotfix — trip-link toast lifecycle

Fixed a V41 notification lifecycle defect where `scheduleAnnouncements()` called `clearTimers()` immediately after the trip-added toast was shown, cancelling the toast dismissal callback and leaving messages such as “DL1247 added to your trip” pinned on screen. Toast dismissal now uses a dedicated transient timer outside the managed flight/scenario timer set. A stale toast is also cleared on V41 boot. Static regression assertions passed. A fresh browser replay was attempted but the current execution environment blocked local/localhost Chromium navigation, so this hotfix is not claimed as browser-verified in this pass.
