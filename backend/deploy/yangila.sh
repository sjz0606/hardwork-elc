#!/bin/bash
# AVTOMATIK YANGILASH: GitHub main'ga push qilinsa, server 5 daqiqa ichida o'zi oladi.
# cPanel > Cron Jobs:
#   */5 * * * * bash $HOME/hardwork_app/backend/deploy/yangila.sh >> $HOME/hardwork_yangila.log 2>&1
cd "$HOME/hardwork_app" || exit 1
exec 9>"$HOME/.hardwork_yangila.lock"
flock -n 9 || exit 0

# serverda: backend + statik sayt (index.html ildizda, cone rejimida o'zi keladi)
git sparse-checkout set backend css js vendor media 2>/dev/null
git fetch -q origin main || exit 1
ESKI=$(git rev-parse HEAD)
[ "$ESKI" = "$(git rev-parse origin/main)" ] && exit 0

# .env, db.sqlite3 va staticfiles gitignore'da — reset ularga tegmaydi
git reset -q --hard origin/main

VENV=$(ls -d "$HOME"/virtualenv/hardwork_app/backend/3.*/ | tail -1)
source "$VENV/bin/activate"
git diff --quiet "$ESKI" HEAD -- backend/requirements.txt || { pip install -q --no-cache-dir -r backend/requirements.txt; bash backend/deploy/ixchamla.sh; }

cd backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput -v0
mkdir -p tmp && touch tmp/restart.txt
echo "$(date '+%F %T') yangilandi: $(git log --oneline -1)"
