# API

Built with Django REST Framework (`backend/content/views.py` and `serializers.py`). It is JSON only and needs no authentication. Every endpoint that returns text accepts `?lang=fi|sv|en`. The default is `fi`, and any text without a translation falls back to English.

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/content/?lang=fi` | Everything the page needs in one request: `settings` (contact, prices, `features` flags, …), `texts` (CMS text overrides), `packages`, `calculator`, `testimonials`, `faq`, `pains`, `steps`, `timeline`, `products`, `beforeAfter`, `videos`, `galleryCount`. Only active items are included. |
| GET | `/api/gallery/?page=1` | Gallery photos, 9 per page (`page_size` up to 48): `{count, next, previous, results: [{id, src, caption}]}`. The site shows the first page and loads more with a "Show more" button. |
| POST | `/api/bookings/` | Booking form. Body: `name`*, `phone`*, `furniture`*, `city`, `preferred_date` (YYYY-MM-DD), `language`. Returns `201 {id, …}`, or `400 {field: [errors]}` if something is missing or invalid. Sends a Telegram alert if configured. |

The booking endpoint is limited to **20 requests per hour per IP address** (`FormThrottle`).

Tests: `cd backend && uv run pytest` (see `backend/tests/`).
