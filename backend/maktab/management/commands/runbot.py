"""Botni long polling bilan ishga tushirish.

  python manage.py runbot              — lokal kompyuterda, to'xtatilguncha
  python manage.py runbot --muddat 55  — serverda (cPanel) cron orqali: har daqiqada 55 soniya ishlaydi.
                                         HTTPS kerak emas. Webhook o'rnatilgan bo'lsa jim chiqib ketadi.
"""
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from maktab.bot import bot_yarat, buyruqlarni_qoy

log = logging.getLogger('hardwork.bot')
OFFSET_KALIT = 'hwbot:offset'


class Command(BaseCommand):
    help = 'HardWork ELC Telegram botini long polling bilan ishga tushiradi'

    def add_arguments(self, parser):
        parser.add_argument('--muddat', type=int, default=0,
                            help="Shuncha soniya ishlab chiqib ketadi (cron uchun). 0 — cheksiz.")

    def handle(self, *args, muddat=0, **opts):
        if not settings.BOT_TOKEN:
            raise CommandError(".env faylida BOT_TOKEN yo'q")
        if muddat:
            return self.cron_rejimi(muddat)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        bot = bot_yarat()
        if bot.get_webhook_info().url:
            raise CommandError("Botga webhook o'rnatilgan (server ishlayapti). Lokal polling uchun avval: "
                               'manage.py webhook_qoy --ochir')
        buyruqlarni_qoy(bot)
        self.stdout.write(self.style.SUCCESS(f'Bot ishga tushdi: @{bot.get_me().username}'))
        bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)

    def cron_rejimi(self, muddat):
        """Belgilangan vaqt ichida yangilanishlarni oladi va qayta ishlaydi. Offset bazada saqlanadi."""
        bot = bot_yarat(threaded=False)
        if bot.get_webhook_info().url:
            return  # webhook rejimiga o'tilgan — polling kerak emas
        if not cache.get('hwbot:buyruqlar'):
            buyruqlarni_qoy(bot)
            cache.set('hwbot:buyruqlar', 1, 24 * 3600)
        tugash = time.monotonic() + muddat
        while True:
            qoldi = tugash - time.monotonic()
            if qoldi < 3:
                break
            try:
                yangilar = bot.get_updates(offset=cache.get(OFFSET_KALIT), timeout=int(min(25, qoldi - 2)),
                                           allowed_updates=['message', 'callback_query'])
            except Exception as e:
                log.warning('get_updates xatosi: %s', e)
                time.sleep(3)
                continue
            for u in yangilar:
                # avval offset — handler xato bersa ham bir xabar qayta-qayta ishlanmasin
                cache.set(OFFSET_KALIT, u.update_id + 1, None)
                try:
                    bot.process_new_updates([u])
                except Exception:
                    log.exception('Yangilanishni qayta ishlashda xato')
