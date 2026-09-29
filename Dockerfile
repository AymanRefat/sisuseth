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
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv PATH="/opt/venv/bin:$PATH"
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock backend/.python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY backend/ ./
COPY --from=frontend /app/frontend/dist /app/frontend/dist
COPY frontend/src/locales /app/frontend/src/locales
RUN DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput
EXPOSE 8000
# /data is a persistent volume holding the SQLite DB and uploaded images.
CMD ["sh", "-c", "mkdir -p /data && python manage.py migrate --noinput && python manage.py seed && gunicorn config.wsgi -b 0.0.0.0:${PORT:-8000} -w 2"]
