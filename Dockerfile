# ---- 1. Build the React app ----
FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- 2. Django serves the API, admin (CMS) and the built React app ----
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_DEBUG=0 \
    SQLITE_PATH=/data/db.sqlite3 MEDIA_ROOT=/data/media
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist
COPY frontend/src/locales /app/frontend/src/locales
RUN DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput
EXPOSE 8000
# /data is a persistent volume holding the SQLite DB and uploaded images.
CMD ["sh", "-c", "mkdir -p /data && python manage.py migrate --noinput && python manage.py seed && gunicorn config.wsgi -b 0.0.0.0:${PORT:-8000} -w 2"]
