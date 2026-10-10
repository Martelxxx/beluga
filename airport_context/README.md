# Beluga airport context buckets

Each reviewed airport bucket is stored as `<IATA>.json` and is loaded only by the Beluga backend. The browser does not assemble its own airport knowledge prompt.

V46 contains one detailed bucket: `IAD.json` for Washington Dulles International Airport.

A bucket should separate stable airport facts from live values. Security wait times, current gates, concession open/closed state, transit departure times, baggage carousels, prices, and similar volatile facts must not be invented from static context. Those values belong to current provider feeds or should be described as unavailable.

Every maintained bucket should retain its reviewed source list and review date so a later ingestion/update workflow can identify what needs refreshing.
