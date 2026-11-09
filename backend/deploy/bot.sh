#!/bin/bash
# Bot serverda cron orqali (HTTPS kerak emas). cPanel > Cron Jobs, har daqiqa:
#   * * * * * bash $HOME/hardwork_app/backend/deploy/bot.sh
# Bir vaqtda faqat bitta nusxa ishlaydi (flock). Webhook o'rnatilsa, o'zi jim chiqib ketadi.
exec 9>"$HOME/.hardwork_bot.lock"
flock -n 9 || exit 0
VENV=$(ls -d "$HOME"/virtualenv/hardwork_app/backend/3.*/ | tail -1)
cd "$HOME/hardwork_app/backend" || exit 1
"$VENV/bin/python" manage.py runbot --muddat 55 >> "$HOME/hardwork_bot.log" 2>&1
