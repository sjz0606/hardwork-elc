#!/bin/bash
# BIR MARTA: cPanel'da "Setup Python App" yaratilgandan keyin ishga tushiriladi.
#   bash ~/hardwork_app/backend/deploy/ornatish.sh <BOT_TOKEN>
set -e
ILOVA="$HOME/hardwork_app/backend"
VENV=$(ls -d "$HOME"/virtualenv/hardwork_app/backend/3.*/ 2>/dev/null | tail -1)
[ -z "$VENV" ] && { echo "XATO: virtualenv topilmadi — avval cPanel > Setup Python App da ilova yarating (root: hardwork_app/backend)"; exit 1; }
source "$VENV/bin/activate"
cd "$ILOVA"

echo "== Kutubxonalar o'rnatilmoqda..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  [ -z "$1" ] && { echo "Foydalanish: bash deploy/ornatish.sh <BOT_TOKEN>"; exit 1; }
  echo "== .env yaratilmoqda (maxfiy kalitlar avtomatik)"
  cat > .env <<EOT
BOT_TOKEN=$1
ADMIN_CHAT_IDS=5268013950
DJANGO_SECRET_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(50))')
DEBUG=0
ALLOWED_HOSTS=hardwork.osonhujjat.uz
CORS_ORIGINS=https://sjz0606.github.io
SITE_URL=https://hardwork.osonhujjat.uz
WEBHOOK_SECRET=$(python -c 'import secrets;print(secrets.token_urlsafe(32))')
EOT
  chmod 600 .env
fi

echo "== Baza..."
python manage.py migrate --noinput
python manage.py createcachetable
python manage.py boshlangich
python manage.py collectstatic --noinput -v0

if ! python manage.py shell -c "from django.contrib.auth.models import User;import sys;sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
  PAROL=$(python -c 'import secrets;print(secrets.token_urlsafe(9))')
  DJANGO_SUPERUSER_PASSWORD="$PAROL" python manage.py createsuperuser --noinput --username admin --email admin@hardwork.local
  echo "== ADMIN PANEL: login admin, parol $PAROL  (yozib oling!)"
fi

mkdir -p tmp && touch tmp/restart.txt
echo "== TAYYOR. Keyingi qadam (SSL ishlagach): python manage.py webhook_qoy"
