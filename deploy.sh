#!/usr/bin/env bash
# =============================================================================
#  SISUSETH – one-command deploy for a fresh Ubuntu/Debian server
#
#  From your computer (copies this script to the server and runs it there):
#      ./deploy.sh root@SERVER_IP
#  Or directly on the server:
#      sudo ./deploy.sh
#
#  First run: installs Docker, firewall, swap, a GitHub deploy key, clones the
#  repo, asks for the domain + e-mail, creates .env, builds and starts the site
#  with automatic HTTPS (Caddy), creates the CMS admin user and nightly backups.
#  Every later run: pulls the latest code and rebuilds – content is kept.
#
#  Settings can be passed as environment variables to skip the questions:
#      DOMAIN=sisuseth.com ACME_EMAIL=you@example.com ./deploy.sh root@1.2.3.4
#  Optional: BRANCH (default master), REPO (default the GitHub SSH URL),
#            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SKIP_DNS_CHECK=1
#  Full guide: docs/DEPLOY.md
# =============================================================================
set -euo pipefail

REPO="${REPO:-git@github.com:AymanRefat/sisuseth.git}"
BRANCH="${BRANCH:-master}"
APP_DIR="${APP_DIR:-/opt/sisuseth}"
DEPLOY_KEY="/root/.ssh/sisuseth_deploy"
PASS_VARS=(DOMAIN ACME_EMAIL BRANCH REPO APP_DIR TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID SKIP_DNS_CHECK)

bold() { printf '\n\033[1;33m==> %s\033[0m\n' "$*"; }
ok()   { printf '    \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '    \033[31m!\033[0m %s\n' "$*"; }
die()  { printf '\n\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }
is_tty() { [[ -t 0 ]]; }
ask() {  # ask VAR "Question" [default]
  local var="$1" question="$2" default="${3:-}" answer
  [[ -n "${!var:-}" ]] && return
  is_tty || die "$var is not set. Run interactively or pass $var=... as an environment variable."
  read -r -p "    $question${default:+ [$default]}: " answer
  printf -v "$var" '%s' "${answer:-$default}"
}

# -----------------------------------------------------------------------------
# Remote mode: ./deploy.sh user@host  → copy this script over and run it there.
# -----------------------------------------------------------------------------
if [[ "${1:-}" == *@* ]]; then
  target="$1"
  env_args=()
  for v in "${PASS_VARS[@]}"; do [[ -n "${!v:-}" ]] && env_args+=("$v=$(printf '%q' "${!v}")"); done
  bold "Copying deploy script to $target"
  scp -q "$0" "$target:/tmp/sisuseth-deploy.sh"
  sudo_cmd="sudo"; [[ "$target" == root@* ]] && sudo_cmd=""
  exec ssh -t "$target" "$sudo_cmd env ${env_args[*]:-} bash /tmp/sisuseth-deploy.sh"
fi

[[ $EUID -eq 0 ]] || die "Run as root (sudo ./deploy.sh) or from your computer: ./deploy.sh root@SERVER_IP"
command -v apt-get >/dev/null || die "This script supports Ubuntu/Debian servers."
export DEBIAN_FRONTEND=noninteractive

# -----------------------------------------------------------------------------
bold "1/9  System packages"
apt-get update -qq
apt-get install -y -qq git curl ca-certificates openssl ufw dnsutils cron >/dev/null
ok "git, curl, ufw, cron installed"

# -----------------------------------------------------------------------------
bold "2/9  Docker"
if ! command -v docker >/dev/null; then
  curl -fsSL https://get.docker.com | sh >/dev/null
  systemctl enable --now docker >/dev/null
  ok "Docker installed"
else
  ok "Docker already installed ($(docker --version | cut -d, -f1))"
fi
docker compose version >/dev/null 2>&1 || die "docker compose plugin missing"

# -----------------------------------------------------------------------------
bold "3/9  Swap + firewall"
mem_mb=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
if [[ $mem_mb -lt 2048 ]] && ! swapon --show | grep -q .; then
  fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
  ok "Added 2 GB swap (server has ${mem_mb} MB RAM; the build needs more)"
else
  ok "Memory OK (${mem_mb} MB RAM)"
fi
ufw allow OpenSSH >/dev/null; ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null; ufw allow 443/udp >/dev/null
ufw --force enable >/dev/null
ok "Firewall: only SSH, HTTP and HTTPS are open"

# -----------------------------------------------------------------------------
bold "4/9  GitHub access (read-only deploy key)"
mkdir -p /root/.ssh && chmod 700 /root/.ssh
if [[ ! -f "$DEPLOY_KEY" ]]; then
  ssh-keygen -t ed25519 -N "" -C "sisuseth-deploy@$(hostname)" -f "$DEPLOY_KEY" >/dev/null
fi
if ! grep -q "sisuseth_deploy" /root/.ssh/config 2>/dev/null; then
  printf 'Host github.com\n  IdentityFile %s\n  IdentitiesOnly yes\n' "$DEPLOY_KEY" >> /root/.ssh/config
  chmod 600 /root/.ssh/config
fi
ssh-keygen -F github.com >/dev/null 2>&1 || ssh-keyscan -t ed25519 github.com >> /root/.ssh/known_hosts 2>/dev/null
github_ok() { ssh -o BatchMode=yes -T git@github.com 2>&1 | grep -q "successfully authenticated"; }
if [[ "$REPO" == git@* ]] && ! github_ok; then
  echo
  echo "    Add this key to GitHub so the server can download the (private) code:"
  echo "    GitHub → AymanRefat/sisuseth → Settings → Deploy keys → Add deploy key"
  echo "    (title: $(hostname), leave 'Allow write access' OFF)"
  echo
  echo "    $(cat "$DEPLOY_KEY.pub")"
  echo
  is_tty || die "Add the deploy key above, then run the script again."
  until github_ok; do read -r -p "    Press Enter after adding the key… "; done
fi
ok "Server can read the repository"

# -----------------------------------------------------------------------------
bold "5/9  Code ($BRANCH)"
if [[ -d "$APP_DIR/.git" ]]; then
  git -C "$APP_DIR" fetch -q origin "$BRANCH"
  git -C "$APP_DIR" checkout -q "$BRANCH"
  git -C "$APP_DIR" reset -q --hard "origin/$BRANCH"   # .env and data are not in git, so they are kept
  ok "Updated to $(git -C "$APP_DIR" log -1 --format='%h %s')"
else
  git clone -q --branch "$BRANCH" "$REPO" "$APP_DIR"
  ok "Cloned into $APP_DIR"
fi
cd "$APP_DIR"
COMPOSE=(docker compose -f deploy/docker-compose.prod.yml --env-file .env)

# -----------------------------------------------------------------------------
bold "6/9  Configuration (.env)"
if [[ ! -f .env ]]; then
  ask DOMAIN "Domain name (without www)" "sisuseth.com"
  DOMAIN="${DOMAIN#www.}"; DOMAIN="${DOMAIN#https://}"; DOMAIN="${DOMAIN%%/*}"
  ask ACME_EMAIL "E-mail for HTTPS certificate notices"
  if is_tty && [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    read -r -p "    Telegram bot token for booking alerts (optional, Enter to skip): " TELEGRAM_BOT_TOKEN
    [[ -n "$TELEGRAM_BOT_TOKEN" ]] && read -r -p "    Telegram chat id: " TELEGRAM_CHAT_ID
  fi
  umask 077
  cat > .env <<ENV
# Created by deploy.sh on $(date -I). Edit and re-run ./deploy.sh to apply.
DOMAIN=$DOMAIN
ACME_EMAIL=$ACME_EMAIL
DJANGO_SECRET_KEY=$(openssl rand -base64 48 | tr -d '\n/+=')
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID:-}
ENV
  ok "Created .env (secret key generated; file readable by root only)"
else
  ok "Keeping existing .env"
fi
DOMAIN=$(grep -E '^DOMAIN=' .env | cut -d= -f2)
[[ -n "$DOMAIN" ]] || die ".env has no DOMAIN=… line"

# -----------------------------------------------------------------------------
bold "7/9  DNS check for $DOMAIN"
server_ip=$(curl -fsS4 --max-time 5 https://api.ipify.org || hostname -I | awk '{print $1}')
if [[ "${SKIP_DNS_CHECK:-0}" != 1 ]]; then
  for host in "$DOMAIN" "www.$DOMAIN"; do
    resolved=$(dig +short A "$host" | tail -n1)
    if [[ "$resolved" == "$server_ip" ]]; then ok "$host → $server_ip"
    else warn "$host points to '${resolved:-nothing}', expected $server_ip. Add an A record at Namecheap (docs/DEPLOY.md). HTTPS starts working once it is correct."
    fi
  done
fi

# -----------------------------------------------------------------------------
bold "8/9  Build and start (first build takes a few minutes)"
"${COMPOSE[@]}" up -d --build --remove-orphans
printf '    Waiting for the site to become healthy'
for _ in $(seq 1 60); do
  status=$(docker inspect -f '{{.State.Health.Status}}' "$("${COMPOSE[@]}" ps -q web)" 2>/dev/null || echo starting)
  [[ "$status" == healthy ]] && break
  printf '.'; sleep 3
done
echo
[[ "$status" == healthy ]] || { "${COMPOSE[@]}" logs --tail 50 web; die "The site did not start. Logs are shown above."; }
ok "Site is running"
docker image prune -f >/dev/null
ok "Removed old Docker images"

if ! "${COMPOSE[@]}" exec -T web python manage.py shell -c \
     "from django.contrib.auth import get_user_model as U; import sys; sys.exit(0 if U().objects.filter(is_superuser=True).exists() else 1)"; then
  echo "    No CMS admin yet – create the login for https://$DOMAIN/admin"
  if is_tty; then
    "${COMPOSE[@]}" exec web python manage.py createsuperuser
  else
    warn "Run later: cd $APP_DIR && ${COMPOSE[*]} exec web python manage.py createsuperuser"
  fi
fi

# -----------------------------------------------------------------------------
bold "9/9  Nightly backups"
cat > /etc/cron.d/sisuseth-backup <<CRON
# Database + uploaded media, every night at 03:30, kept for 14 days in /var/backups/sisuseth
30 3 * * * root APP_DIR=$APP_DIR $APP_DIR/deploy/backup.sh >> /var/log/sisuseth-backup.log 2>&1
CRON
chmod 644 /etc/cron.d/sisuseth-backup
ok "Backups at 03:30 → /var/backups/sisuseth (log: /var/log/sisuseth-backup.log)"

cat <<DONE

$(printf '\033[1;32m')✔ SISUSETH is deployed$(printf '\033[0m')
    Website:  https://$DOMAIN
    CMS:      https://$DOMAIN/admin
    Server:   $server_ip   ·   code in $APP_DIR
    Update:   run ./deploy.sh again (from your computer: ./deploy.sh root@$server_ip)
    Logs:     cd $APP_DIR && ${COMPOSE[*]} logs -f
DONE
