# Beluga V51 — Splash, restaurant ordering, simulated payments, traveler wallet

Scope is limited to:
1. Startup splash overlay using the existing Beluga mark.
2. Realistic demo restaurant menus, cart, totals, pickup confirmation.
3. One reusable simulated payment flow for food, rides, hotels, rentals,
   lounges, and Duffel TEST checkout.
4. Settings traveler credentials and saved demo payment cards.

Saved card storage retains only display/payment-token metadata such as brand,
last4 and expiration; full PAN/CVC are not retained.

Unrelated V50.5 Home, mobility, flight-time, journey-row, composer, prompt-loop,
logo and click-repair behavior was not redesigned in this pass.
