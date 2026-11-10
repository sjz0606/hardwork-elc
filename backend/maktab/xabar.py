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


def ariza_oluvchilar(a):
    """Ariza kimlarga borishi: .env ADMIN_CHAT_IDS, filial guruhi, direktorlar va «Arizalarni oladi» xodimlar."""
    from django.db.models import Q

    from .models import BotKirish

    chatlar = set(settings.ADMIN_CHAT_IDS)
    if a.filial and a.filial.admin_chat_id:
        chatlar.add(a.filial.admin_chat_id)
    xodim_kirishlar = (BotKirish.objects.filter(xodim__faol=True)
                       .filter(Q(xodim__direktor=True) | Q(xodim__ariza_oladi=True))
                       .select_related('xodim').prefetch_related('xodim__ariza_filiallar'))
    for k in xodim_kirishlar:
        filiallar = {f.id for f in k.xodim.ariza_filiallar.all()}
        # direktor hammasini oladi; boshqalar — tanlangan filiallar (bo'sh = hammasi)
        if k.xodim.direktor or not filiallar or a.filial_id in filiallar:
            chatlar.add(k.telegram_id)
    if settings.ARIZA_OQUVCHILARGA:
        # botga login qilgan barcha o'quvchilarga ham (egasi talabi; .env ARIZA_OQUVCHILARGA=0 bilan o'chadi)
        chatlar.update(BotKirish.objects.filter(oquvchi__faol=True).values_list('telegram_id', flat=True))
    return chatlar


def ariza_xabari(a):
    """Yangi arizani barcha mas'ullarga botda yuboradi."""
    if not settings.BOT_TOKEN:
        return
    chatlar = ariza_oluvchilar(a)
    matn = ariza_matni(a)
    # Sinxron: cPanel/Passenger fon oqimlarini so'rov tugagach to'xtatishi mumkin. Har biri ko'pi bilan 10 s.
    for c in chatlar:
        yubor(c, matn)
