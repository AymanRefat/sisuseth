# SISUSETH – Furniture assembly website

Landing page and CMS for SISUSETH Furniture Assembly (Helsinki, Espoo, Vantaa).

- **Frontend:** React (Vite) with a language switcher for Finnish, Swedish and English
- **Backend:** Django and Django REST Framework, with dependencies managed by [uv](https://docs.astral.sh/uv/). It serves the JSON API, the built React app, and the admin panel, which is the CMS
- **Database:** SQLite, stored on a persistent volume. Set `DATABASE_URL` to use Postgres instead
- **Deploy:** one Docker image containing one process

**Docs:** [Optional features and their on/off switches](docs/FEATURES.md) · [API](docs/API.md)

## Project structure

```
backend/
  config/            Django settings and URLs (serves /api, /admin, /media and the React build)
  content/
    models.py        Everything editable in the CMS, including the FEATURES on/off list
    serializers.py   DRF serializers (picks the right language)
    views.py         API endpoints
    services.py      Telegram alerts, Google reviews, referral codes
    admin.py         CMS screens
    management/commands/seed.py   Starting content
    seed_images/     Starting photos (gallery, logo, hero)
    tests.py
frontend/src/
  App.jsx            Page sections
  features/          One file per optional feature (docs/FEATURES.md)
  i18n.jsx           Language switching + CMS text overrides
  locales/           Default texts in fi / sv / en
docs/                Documentation
```

## What the owner can edit in the CMS (`/admin`)

| Section | Contents |
|---|---|
| Site settings | Logo, hero image, phone, WhatsApp number, email, social links, service areas, brand list, "500+ customers", starting price, hourly rate, price per extra item |
| Text blocks | Every heading and paragraph on the page, in EN, FI and SV. If a block is empty, the site uses the default text built into the frontend |
| Pricing packages / Calculator options | Names, prices, hours, referral bonus, which package is marked "most popular" |
| Gallery images | Photos uploaded to this server (stored in `/data/media`). Large uploads are resized to 1600px automatically. Includes 15 starting photos from `backend/content/seed_images` |
| Testimonials, FAQ | Add, reorder and hide items, in EN, FI and SV |
| Features | On/off switch for each optional section. See [docs/FEATURES.md](docs/FEATURES.md) |
| Products | Price search and quiz: product, brand, price, assembly time |
| Before/after photos, Videos | Uploaded to this server and shown in their own sections |
| Referrals | Customers' referral codes and how many bookings each one brought |
| Booking requests | Leads sent from the website form, with a status field (new, contacted, done) |

## Local development

```bash
cd backend
uv sync                                   # creates backend/.venv (Python 3.13)
uv run python manage.py migrate
uv run python manage.py seed              # prototype content, starting photos, all texts
uv run python manage.py createsuperuser
uv run python manage.py runserver         # API + CMS on :8000

cd ../frontend && npm install && npm run dev   # site on :5173 (proxies /api and /media to Django)
```

Add a Python dependency with `uv add <package>`.

Run the tests with `cd backend && uv run pytest`. They are in `backend/tests/`.

The logo is also the favicon. `frontend/public/favicon.png` is the default, and the site switches to the logo uploaded in the CMS as soon as the page loads.

## Run with Docker

```bash
cp .env.example .env    # then edit the values
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000 for the site and http://localhost:8000/admin for the CMS.

## How translations work

Finnish is the default language. Visitors can switch to Swedish or English, and the choice is remembered.

1. The default UI text is in `frontend/src/locales/{en,fi,sv}.json`, so the site works even if the API is down.
2. `python manage.py seed` copies every key into the **Text blocks** table in the CMS.
3. Text edited in the CMS overrides the bundled default for that language.
4. Content stored in the database (packages, FAQ, testimonials) has separate `_en`, `_fi` and `_sv` fields. If a translation is missing, the English text is shown.

To add a language, add a locale JSON file, add the code to `LANGS` in `content/models.py`, and run `makemigrations`.
