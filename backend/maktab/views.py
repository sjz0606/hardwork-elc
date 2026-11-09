import json
import re

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Ariza, Filial
from .xabar import ariza_xabari

TEL_RE = re.compile(r'^\+?[\d\s()\-]{7,20}$')


def _cors(request, javob):
    origin = request.headers.get('Origin', '')
    if origin in settings.CORS_ORIGINS:
        javob['Access-Control-Allow-Origin'] = origin
        javob['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        javob['Access-Control-Allow-Headers'] = 'Content-Type'
        javob['Vary'] = 'Origin'
    return javob


@csrf_exempt
def ariza_qabul(request):
    """Saytdagi yozilish formasi shu yerga JSON yuboradi."""
    if request.method == 'OPTIONS':
        return _cors(request, HttpResponse(status=204))
    if request.method != 'POST':
        return _cors(request, JsonResponse({'ok': False, 'xato': 'Faqat POST'}, status=405))
    try:
        m = json.loads(request.body or b'{}')
        if not isinstance(m, dict):
            raise ValueError
    except ValueError:
        return _cors(request, JsonResponse({'ok': False, 'xato': "JSON noto'g'ri"}, status=400))

    ism = str(m.get('ism', '')).strip()[:120]
    tel = str(m.get('tel', '')).strip()[:30]
    if not ism or not TEL_RE.match(tel):
        return _cors(request, JsonResponse({'ok': False, 'xato': 'Ism va telefon kerak'}, status=400))

    a = Ariza.objects.create(
        ism=ism, tel=tel,
        kurs=str(m.get('kurs', '')).strip()[:80],
        filial=Filial.objects.filter(kod=str(m.get('filial', ''))).first(),
        vaqt=str(m.get('vaqt', '')).strip()[:20],
        daraja=str(m.get('daraja', '')).strip()[:60],
        manba='sayt',
    )
    ariza_xabari(a)
    return _cors(request, JsonResponse({'ok': True, 'id': a.pk}, status=201))


def salomatlik(request):
    return JsonResponse({'ok': True})


@csrf_exempt
def bot_webhook(request, maxfiy):
    """Telegram yangilanishlari (cPanel'da bot shu orqali ishlaydi)."""
    import hmac

    from telebot import types

    from .bot import webhook_bot

    kalit = settings.WEBHOOK_SECRET.encode()
    sarlavha = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '').encode()
    if (request.method != 'POST' or not kalit
            or not hmac.compare_digest(maxfiy.encode(), kalit) or not hmac.compare_digest(sarlavha, kalit)):
        return HttpResponse(status=403)
    try:
        update = types.Update.de_json(request.body.decode('utf-8'))
    except Exception:
        return HttpResponse(status=400)
    webhook_bot().process_new_updates([update])
    return HttpResponse('ok')
