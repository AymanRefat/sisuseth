# Deploying SISUSETH

One small Linux server runs everything: Django + the React site + the CMS in one container, with **Caddy** in front for automatic HTTPS. The database (SQLite) and uploaded photos live on a Docker volume that survives updates.

**Cost:** about €4–5/month (Hetzner CAX11 in Helsinki) + the domain.

## 1. Create the server (once)
1. Sign up at [Hetzner Cloud](https://console.hetzner.cloud) → *New project* → *Add server*:
   - Location **Helsinki**, image **Ubuntu 24.04**, type **CAX11** (ARM, 2 vCPU / 4 GB), or any Ubuntu/Debian server with ≥ 1 GB RAM
   - Add **your SSH key** (`cat ~/.ssh/id_ed25519.pub` on your Mac)
2. Copy the server's **IPv4 address**.

## 2. Point the Namecheap domain at it (once)
Namecheap → *Domain List* → **Manage** → **Advanced DNS** → delete the default parking records, then add:

| Type | Host | Value | TTL |
|---|---|---|---|
| A Record | `@` | `SERVER_IP` | Automatic |
| A Record | `www` | `SERVER_IP` | Automatic |

DNS usually takes 5–30 minutes to update. The deploy script checks it and warns if it's not ready yet. HTTPS starts working as soon as it is.

## 3. Deploy
From the project folder on your Mac:

```bash
./deploy.sh root@SERVER_IP
```

The first run asks for the **domain** and an **e-mail** (for HTTPS certificate notices). It then:

1. installs git, Docker and cron
2. adds swap on small servers and opens only ports 22, 80 and 443 in the firewall
3. creates a **read-only GitHub deploy key** and shows it. Add it under *GitHub → repo → Settings → Deploy keys* (leave write access off) and press Enter
4. clones the repo to `/opt/sisuseth`
5. writes `.env` with a generated secret key (optional: Telegram bot token for booking alerts)
6. checks the DNS records
7. builds and starts the site. The first `migrate` loads all the starting content
8. asks you to create the **CMS admin login** (username + password for `/admin`). Give these to the owner
9. installs a nightly backup at 03:30

To skip the questions: `DOMAIN=sisuseth.com ACME_EMAIL=you@example.com ./deploy.sh root@SERVER_IP`

## 4. Updating the site
Push to GitHub, then run the same command again:

```bash
./deploy.sh root@SERVER_IP
```

It pulls the latest `master`, rebuilds and restarts in about a minute. The owner's content, photos and settings are kept. Starting content is only loaded on the very first run.

After a release that adds **new text keys**, run once so they appear in the CMS:
```bash
ssh root@SERVER_IP 'cd /opt/sisuseth && docker compose -f deploy/docker-compose.prod.yml --env-file .env exec web python manage.py seed'
```

## Everyday commands (on the server)
```bash
cd /opt/sisuseth
C="docker compose -f deploy/docker-compose.prod.yml --env-file .env"
$C ps                                                   # status
$C logs -f web                                          # Django logs
$C logs -f caddy                                        # HTTPS / traffic logs
$C exec web python manage.py createsuperuser            # another CMS login
$C exec web python manage.py changepassword USERNAME    # reset a password
$C restart                                              # restart everything
```
To change settings, edit `/opt/sisuseth/.env` (for example to add the Telegram token) and run `./deploy.sh` again.

## Backups
- Every night at 03:30 → `/var/backups/sisuseth/sisuseth_YYYY-MM-DD_HHMM.tar.gz` (database + media, kept 14 days). Log: `/var/log/sisuseth-backup.log`.
- Run one now: `/opt/sisuseth/deploy/backup.sh`
- Copy them off the server now and then: `scp root@SERVER_IP:/var/backups/sisuseth/*.tar.gz ~/Backups/`. Hetzner's automatic server backups (+20 % of the server price) are also a good idea.

**Restore** a backup:
```bash
cd /opt/sisuseth && C="docker compose -f deploy/docker-compose.prod.yml --env-file .env"
mkdir -p /tmp/restore && tar -xzf /var/backups/sisuseth/sisuseth_DATE.tar.gz -C /tmp/restore
$C stop web
docker run --rm -v sisuseth_sisuseth-data:/data -v /tmp/restore:/restore alpine \
  sh -c 'cp /restore/backup.sqlite3 /data/db.sqlite3 && rm -rf /data/media && cp -r /restore/media /data/media'
$C start web
```

## Files
| File | Purpose |
|---|---|
| `deploy.sh` | The whole setup and update process (safe to run again and again) |
| `deploy/docker-compose.prod.yml` | Production stack: `web` (Django/gunicorn) + `caddy` (HTTPS) |
| `deploy/Caddyfile` | HTTPS, www → main-domain redirect, compression, security headers, 100 MB upload limit |
| `deploy/backup.sh` | Nightly backup (installed as `/etc/cron.d/sisuseth-backup`) |
| `docker-compose.yml` | Local testing only (`docker compose up --build` → http://localhost:8000) |

## Troubleshooting
- **"The site did not start"**: the script prints the last 50 log lines. It's usually a typo in `.env`.
- **The browser warns about the certificate**: DNS isn't pointing at the server yet, or has only just changed. Check with `dig +short sisuseth.com`, wait, then `$C restart caddy`.
- **Upload fails for a big video**: keep videos under 100 MB (ideally under 10 MB, see docs/FEATURES.md).
- **The server ran out of memory while building**: the script adds swap on small servers. On a 512 MB server, choose a bigger one.
