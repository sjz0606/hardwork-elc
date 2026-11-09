# HardWork ELC — backend (Django) + Telegram bot

Bot: **@hardworkschool_bot**

## Nima qiladi
- **Telegram bot** (login bilan kirish):
  - Mehmon: 🔐 Kirish · 📝 Sinov darsiga yozilish · 💰 Kurslar va narxlar · 📍 Filiallar
  - O'quvchi (login + parol bilan kirgach): 👤 Profilim · 📅 Dars jadvali · 📊 Natijalarim · ✅ Davomat · 💳 To'lovlar · 🚪 Chiqish
  - Parol xabari chatdan avtomatik o'chiriladi; 5 marta noto'g'ri parol → 10 daqiqa blok
  - Bitta login faqat bitta Telegram akkauntga ulanadi (admin paneldan "Telegram akkauntdan uzish" mumkin)
- **Admin panel** `/admin/`: filiallar, kurslar, ustozlar, guruhlar, o'quvchilar (login/parol), to'lovlar, davomat, natijalar, arizalar
- **API** `POST /api/ariza/` — saytdagi yozilish formasi shu yerga yuboradi; yangi ariza adminlarga Telegramda keladi

## Ishga tushirish (Windows)
```
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env          # BOT_TOKEN ni yozing
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py boshlangich        # filiallar, kurslar, ustozlar (--demo: login demo / demo123)
.venv\Scripts\python manage.py createsuperuser
```
Ikki oynada:
```
.venv\Scripts\python manage.py runserver      # admin: http://127.0.0.1:8000/admin/
.venv\Scripts\python manage.py runbot         # Telegram bot
```

## O'quvchiga login berish
Admin → O'quvchilar → Qo'shish: ism, login, guruh. Parolni yozing yoki bo'sh qoldiring — avtomatik yaratiladi
va sahifa tepasida ko'rsatiladi. Tanlangan o'quvchilarga "yangi parol yaratish" amali ham bor.

## Arizalar Telegramga kelishi
1. Botga `/myid` yozing → chat ID chiqadi
2. `.env` → `ADMIN_CHAT_IDS=123456789` (bir nechta bo'lsa vergul bilan)
3. Har bir filial uchun alohida chat: Admin → Filiallar → "Admin chat ID"

Guruh chatiga yuborish uchun botni guruhga qo'shing va guruhda `/myid` yozing (ID minus bilan boshlanadi).

## Serverga joylash
- `.env`: `DEBUG=0`, `ALLOWED_HOSTS=api.domen.uz`, yangi `DJANGO_SECRET_KEY`, `CORS_ORIGINS` ga sayt manzili
- `python manage.py collectstatic`, Django'ni gunicorn/Passenger orqali ishga tushiring
- Bot alohida doimiy jarayon: `python manage.py runbot` (systemd / supervisor / pm2)
- Saytdagi `js/ilova.js` → `FORMA_MANZIL` ga `https://api.domen.uz/api/ariza/` yozing

## Testlar
```
.venv\Scripts\python manage.py test maktab
```

## Server
https://hardwork.osonhujjat.uz — cPanel (Ahost). `main` ga push qilingan o'zgarish cron orqali ≤5 daqiqada serverga tushadi (`deploy/yangila.sh`, log: `~/hardwork_yangila.log`).
