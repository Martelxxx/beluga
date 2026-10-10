# Beluga V52.1 — Hotel natural language + restaurant logo correction

Only two requested areas changed:

1. Restaurant hero logos now explicitly override the historical global square-image
   rule so their 14px corner radius renders correctly.
2. RouteStack Hotels are airport-context-first and composer-first:
   - no destination/IAD input on the hotel page
   - direct hotel route searches the current airport area immediately
   - default stay is tonight → tomorrow, 1 adult, 1 room
   - the remaining stay controls are optional refinements
   - the existing AI composer router semantically extracts hotel dates, guests,
     rooms, budget, named hotel, and first/second/third result selection
   - natural-language hotel requests search RouteStack directly in chat
   - external RouteStack checkout still requires a user click on its booking link

No mobility, journey-row, prompt-loop, bot-only surface behavior, flight booking,
restaurant menu/cart/payment behavior, or unrelated visual component was changed.
