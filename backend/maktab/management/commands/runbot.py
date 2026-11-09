"""Botni lokal kompyuterda long polling bilan ishga tushirish: python manage.py runbot
Serverda (cPanel) bot webhook orqali ishlaydi — manage.py webhook_qoy ga qarang."""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from maktab.bot import bot_yarat, buyruqlarni_qoy


class Command(BaseCommand):
    help = 'HardWork ELC Telegram botini long polling bilan ishga tushiradi (lokal sinov uchun)'

    def handle(self, *args, **opts):
        if not settings.BOT_TOKEN:
            raise CommandError(".env faylida BOT_TOKEN yo'q")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        bot = bot_yarat()
        if bot.get_webhook_info().url:
            raise CommandError('Botga webhook o\'rnatilgan (server ishlayapti). Lokal polling uchun avval: '
                               'manage.py webhook_qoy --ochir')
        buyruqlarni_qoy(bot)
        self.stdout.write(self.style.SUCCESS(f'Bot ishga tushdi: @{bot.get_me().username}'))
        bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
