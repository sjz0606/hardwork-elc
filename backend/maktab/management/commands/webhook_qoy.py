"""Telegram webhookni serverga ulaydi: python manage.py webhook_qoy
.env: SITE_URL=https://hardwork.osonhujjat.uz va WEBHOOK_SECRET=uzun-tasodifiy-satr"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from maktab.bot import bot_yarat, buyruqlarni_qoy


class Command(BaseCommand):
    help = "Telegram webhookni SITE_URL/bot/<WEBHOOK_SECRET>/ ga o'rnatadi (--ochir: o'chiradi, --holat: ko'rsatadi)"

    def add_arguments(self, parser):
        parser.add_argument('--ochir', action='store_true', help="Webhookni o'chirish (lokal polling uchun)")
        parser.add_argument('--holat', action='store_true', help="Joriy webhook holatini ko'rsatish")

    def handle(self, *args, ochir=False, holat=False, **opts):
        if not settings.BOT_TOKEN:
            raise CommandError(".env faylida BOT_TOKEN yo'q")
        bot = bot_yarat(threaded=False)
        if holat:
            i = bot.get_webhook_info()
            self.stdout.write(f'url: {i.url or "-"}\nkutilayotgan: {i.pending_update_count}\n'
                              f'oxirgi xato: {i.last_error_message or "-"}')
            return
        if ochir:
            bot.remove_webhook()
            self.stdout.write(self.style.SUCCESS("Webhook o'chirildi."))
            return
        if not settings.SITE_URL.startswith('https://') or not settings.WEBHOOK_SECRET:
            raise CommandError(".env da SITE_URL (https://...) va WEBHOOK_SECRET bo'lishi kerak")
        url = f'{settings.SITE_URL.rstrip("/")}/bot/{settings.WEBHOOK_SECRET}/'
        bot.remove_webhook()
        bot.set_webhook(url=url, secret_token=settings.WEBHOOK_SECRET, drop_pending_updates=True,
                        allowed_updates=['message', 'callback_query'])
        buyruqlarni_qoy(bot)
        self.stdout.write(self.style.SUCCESS(f'Webhook o\'rnatildi: {settings.SITE_URL.rstrip("/")}/bot/***/'))
