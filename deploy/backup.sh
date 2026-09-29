#!/usr/bin/env bash
# Nightly backup of the database and uploaded media (installed as a cron job by deploy.sh).
# Keeps the last $KEEP_DAYS days in $BACKUP_DIR. Restore instructions: docs/DEPLOY.md
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/sisuseth}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/sisuseth}"
KEEP_DAYS="${KEEP_DAYS:-14}"
STAMP="$(date +%Y-%m-%d_%H%M)"
COMPOSE=(docker compose -f "$APP_DIR/deploy/docker-compose.prod.yml" --env-file "$APP_DIR/.env")

mkdir -p "$BACKUP_DIR"
# Consistent SQLite copy (safe while the site is running), then archive it together with the media folder.
"${COMPOSE[@]}" exec -T web python -c "
import sqlite3
src = sqlite3.connect('/data/db.sqlite3'); dst = sqlite3.connect('/data/backup.sqlite3')
src.backup(dst); dst.close(); src.close()"
"${COMPOSE[@]}" exec -T web tar -C /data -czf - backup.sqlite3 media > "$BACKUP_DIR/sisuseth_$STAMP.tar.gz"
"${COMPOSE[@]}" exec -T web rm -f /data/backup.sqlite3
find "$BACKUP_DIR" -name 'sisuseth_*.tar.gz' -mtime +"$KEEP_DAYS" -delete
echo "Backup written: $BACKUP_DIR/sisuseth_$STAMP.tar.gz ($(du -h "$BACKUP_DIR/sisuseth_$STAMP.tar.gz" | cut -f1))"
