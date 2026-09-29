# API

Built with Django REST Framework (`backend/content/views.py` and `serializers.py`). It is JSON only and needs no authentication. Every endpoint that returns text accepts `?lang=fi|sv|en`. The default is `fi`, and any text without a translation falls back to English.

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/content/?lang=fi` | Everything the page needs in one request: `settings` (contact, prices, `features` flags, …), `texts` (CMS text overrides), `packages`, `calculator`, `testimonials`, `faq`, `gallery`, `products`, `beforeAfter`, `videos`. Only active items are included. |
| POST | `/api/bookings/` | Booking form. Body: `name`*, `phone`*, `furniture`*, `city`, `preferred_date` (YYYY-MM-DD), `language`, `referral_code`. Returns `201 {id, …}`, or `400 {field: [errors]}` if something is missing or invalid. Sends a Telegram alert if configured. |
| GET | `/api/google-reviews/?lang=fi` | `{enabled: false}` or `{enabled, rating, count, url, reviews: [{author, photo, rating, text, when}]}`. Cached for 6 h. |
| POST | `/api/referrals/` | Body `{name, phone}` → `201 {code}`. The same phone number always gets the same code. Returns `404` when the feature is off. |
| GET | `/api/referrals/<code>/` | `{valid: true/false}`. Case-insensitive. |

The POST endpoints are limited to **20 requests per hour per IP address** (`FormThrottle`).

Tests: `cd backend && uv run pytest` (see `backend/tests/`).
