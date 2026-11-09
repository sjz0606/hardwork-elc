# cPanel'ga joylash (Ahost, de.ahost.cloud) — hardwork.osonhujjat.uz

Bot cPanel'da **webhook** rejimida ishlaydi (Telegram xabarlarni `https://hardwork.osonhujjat.uz/bot/<maxfiy>/` ga yuboradi) — alohida jarayon kerak emas.

## 1. Subdomen (cPanel → Domains)
- **Create A New Domain** → `hardwork.osonhujjat.uz`, "Share document root" belgisini olib tashlang.
- osonhujjat.uz DNS Ahost'da (ns1–3.ahost.cloud) — A yozuv avtomatik qo'shiladi.
- **SSL/TLS Status** → `hardwork.osonhujjat.uz` → **Run AutoSSL** (bir necha daqiqa).

## 2. Kodni yuklab olish (cPanel → Terminal)
```bash
# backend/ + statik sayt (hardwork.osonhujjat.uz ochilganda sayt chiqadi)
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/sjz0606/hardwork-elc.git ~/hardwork_app
cd ~/hardwork_app && git sparse-checkout set backend css js vendor media && git checkout main
```

## 3. Python ilova (cPanel → Setup Python App → Create Application)
| Maydon | Qiymat |
|---|---|
| Python version | 3.11 (yoki eng yangisi) |
| Application root | `hardwork_app/backend` |
| Application URL | `hardwork.osonhujjat.uz` / (bo'sh) |
| Application startup file | `passenger_wsgi.py` |
| Application Entry point | `application` |

**Create** bosing.

## 4. O'rnatish (Terminal)
```bash
bash ~/hardwork_app/backend/deploy/ornatish.sh <BOT_TOKEN>
```
Skript: kutubxonalar, `.env` (maxfiy kalitlar avtomatik), baza, filiallar/kurslar, admin akkaunt (parolni ekranga chiqaradi).
Keyin Setup Python App sahifasida **Restart** bosing va https://hardwork.osonhujjat.uz/admin/ ochilishini tekshiring.

## 5a. Bot (SSL'siz ham ishlaydi) — cron, har daqiqa
```
* * * * * bash $HOME/hardwork_app/backend/deploy/bot.sh
```
Bot har daqiqada 55 soniya polling qiladi. SSL chiqib webhook o'rnatilgach, bu cron o'zi jim bo'lib qoladi (keyin o'chirib qo'ysa bo'ladi).

## 5. Botni webhook bilan ulash (SSL kerak)
```bash
source ~/virtualenv/hardwork_app/backend/3.*/bin/activate && cd ~/hardwork_app/backend
python manage.py webhook_qoy
python manage.py webhook_qoy --holat     # "oxirgi xato: -" bo'lishi kerak
```

## 6. Avtomatik yangilash (cPanel → Cron Jobs, har 5 daqiqa)
```
*/5 * * * * bash $HOME/hardwork_app/backend/deploy/yangila.sh >> $HOME/hardwork_yangila.log 2>&1
```
Shundan keyin GitHub `main` ga push qilingan har bir o'zgarish ≤5 daqiqada serverga tushadi (migrate + collectstatic + restart).

## Foydali
- Lokal kompyuterda bot sinash: avval `manage.py webhook_qoy --ochir`, keyin `manage.py runbot`; tugagach serverda yana `webhook_qoy`.
- Loglar: `~/hardwork_yangila.log`, `~/hardwork_app/backend/stderr.log` (Passenger).
- `.env` va `db.sqlite3` faqat serverda — git'ga tushmaydi.
