# SISUSETH – Furniture assembly website

Landing page and CMS for SISUSETH Furniture Assembly (Helsinki, Espoo, Vantaa).

- **Frontend:** React (Vite) with a language switcher for Finnish, Swedish and English
- **Backend:** Django. It serves the JSON API, the built React app, and the admin panel, which is the CMS
- **Database:** SQLite, stored on a persistent volume. Set `DATABASE_URL` to use Postgres instead
- **Deploy:** one Docker image containing one process

## What the owner can edit in the CMS (`/admin`)

| Section | Contents |
|---|---|
| Site settings | Phone, WhatsApp number, email, social links, service areas, "500+ customers", starting price, hourly rate |
| Text blocks | Every heading and paragraph on the page, in EN, FI and SV. If a block is empty, the site uses the default text built into the frontend |
| Pricing packages / Calculator options | Names, prices, hours, referral bonus, which package is marked "most popular" |
| Testimonials, FAQ, Gallery images | Add, reorder and hide items; upload photos |
| Booking requests | Leads sent from the website form, with a status field (new, contacted, done) |

## Local development

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && python manage.py migrate && python manage.py seed && python manage.py createsuperuser
python manage.py runserver            # API + admin on :8000
cd ../frontend && npm install && npm run dev   # site on :5173 (proxies /api to Django)
```

## Run with Docker

```bash
cp .env.example .env    # then edit the values
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000 for the site and http://localhost:8000/admin for the CMS.

## How translations work

1. The default UI text is in `frontend/src/locales/{en,fi,sv}.json`, so the site works even if the API is down.
2. `python manage.py seed` copies every key into the **Text blocks** table in the CMS.
3. Text edited in the CMS overrides the bundled default for that language.
4. Content stored in the database (packages, FAQ, testimonials) has separate `_en`, `_fi` and `_sv` fields. If a translation is missing, English is shown.

To add a language, add a locale JSON file, add the code to `LANGS` in `content/models.py`, and run `makemigrations`.
