"""Telegram'ga xabar yuborish (bot jarayonidan tashqarida ham ishlaydi)."""
import html
import json
import logging
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def yubor(chat_id, matn):
    url = f'https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage'
    data = json.dumps({'chat_id': chat_id, 'text': matn, 'parse_mode': 'HTML'}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:  # tarmoq xatosi arizani saqlashga xalaqit bermasin
        log.warning('Telegram xabar yuborilmadi (%s): %s', chat_id, e)


def ariza_matni(a):
    e = lambda s: html.escape(str(s), quote=False)  # noqa: E731
    qatorlar = [
        '🆕 <b>Yangi ariza</b> (' + a.get_manba_display() + ')',
        f'👤 {e(a.ism)}',
        f'📞 {e(a.tel)}',
        f'📚 {e(a.kurs or "—")}',
        f'📍 {e(a.filial.nom if a.filial else "—")}',
    ]
    if a.vaqt:
        qatorlar.append(f'🕒 {e(a.vaqt)}')
    if a.daraja:
        qatorlar.append(f'📝 Test: {e(a.daraja)}')
    qatorlar.append(f'#ariza{a.pk}')
    return '\n'.join(qatorlar)


def ariza_xabari(a):
    """Arizani umumiy adminlarga va filial chatiga yuboradi."""
    if not settings.BOT_TOKEN:
        return
    chatlar = set(settings.ADMIN_CHAT_IDS)
    if a.filial and a.filial.admin_chat_id:
        chatlar.add(a.filial.admin_chat_id)
    matn = ariza_matni(a)
    # Sinxron: cPanel/Passenger fon oqimlarini so'rov tugagach to'xtatishi mumkin. Har biri ko'pi bilan 10 s.
    for c in chatlar:
        yubor(c, matn)
