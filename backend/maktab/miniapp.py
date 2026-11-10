"""Telegram Mini App (jurnal + direktor hisoboti) — API.

Kirish: Telegram WebApp `initData` bot tokeni bilan imzolanadi (HMAC). Imzo to'g'ri bo'lsa, foydalanuvchi
telegram_id orqali botda login qilgan Xodim yoki O'quvchiga bog'lanadi. Botga login qilmagan odam kira olmaydi.
"""
import hashlib
import hmac
import json
import time
from datetime import date, timedelta
from functools import wraps
from urllib.parse import parse_qsl

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Dars, Davomat, Filial, Guruh, Oquvchi, Tolov, Ustoz, Xodim

INIT_DATA_MUDDAT = 24 * 3600
HOLATLAR = dict(Davomat.HOLATLAR)
KUNLAR = ['', 'Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']


# ---------------------------------------------------------------- kirish
def init_data_tekshir(init_data, token=None):
    """Telegram WebApp initData imzosini tekshiradi. To'g'ri bo'lsa user dict, aks holda None."""
    token = token or settings.BOT_TOKEN
    if not init_data or not token:
        return None
    try:
        juftlar = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    except ValueError:
        return None
    imzo = juftlar.pop('hash', '')
    tekshiruv = '\n'.join(f'{k}={v}' for k, v in sorted(juftlar.items()))
    kalit = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    kutilgan = hmac.new(kalit, tekshiruv.encode(), hashlib.sha256).hexdigest()
    if not imzo or not hmac.compare_digest(kutilgan, imzo):
        return None
    try:
        if time.time() - int(juftlar.get('auth_date', 0)) > INIT_DATA_MUDDAT:
            return None
        return json.loads(juftlar.get('user', '{}'))
    except (ValueError, TypeError):
        return None


def foydalanuvchi(request):
    """(xodim, oquvchi) — ikkalasidan biri yoki ikkalasi None."""
    if settings.DEBUG and request.headers.get('X-Dev-Login'):  # faqat lokal sinov uchun
        login = request.headers['X-Dev-Login']
        return (Xodim.objects.filter(login__iexact=login, faol=True).first(),
                Oquvchi.objects.filter(login__iexact=login, faol=True).first())
    user = init_data_tekshir(request.headers.get('X-Init-Data', ''))
    if not user or not user.get('id'):
        return None, None
    tid = int(user['id'])
    x = Xodim.objects.select_related('ustoz').filter(telegram_id=tid, faol=True).first()
    if x:
        return x, None
    return None, Oquvchi.objects.select_related('guruh').filter(telegram_id=tid, faol=True).first()


def api(rollar=('xodim', 'oquvchi')):
    def dek(f):
        @csrf_exempt
        @wraps(f)
        def w(request, *a, **kw):
            x, o = foydalanuvchi(request)
            if not ((x and 'xodim' in rollar) or (x and x.direktor and 'direktor' in rollar)
                    or (o and 'oquvchi' in rollar)):
                return JsonResponse({'xato': "Ruxsat yo'q. Botga login bilan kiring."}, status=403)
            request.xodim, request.oquvchi = x, o
            try:
                return f(request, *a, **kw)
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
                return JsonResponse({'xato': f"Noto'g'ri so'rov: {e}"}, status=400)
        return w
    return dek


def _sana(s, standart=None):
    return date.fromisoformat(s) if s else (standart or timezone.localdate())


def _int(s):
    return int(s) if s not in (None, '', 'null') else None


# ---------------------------------------------------------------- sahifa
def sahifa(request):
    return render(request, 'maktab/app.html')


# ---------------------------------------------------------------- umumiy
@api()
def men(request):
    x, o = request.xodim, request.oquvchi
    if x:
        d = {'tur': 'xodim', 'ism': x.ism, 'rol': x.rol, 'direktor': x.direktor, 'ustoz_id': x.ustoz_id}
        if x.direktor:
            d['filiallar'] = list(Filial.objects.order_by('pk').values('id', 'nom'))
            d['ustozlar'] = list(Ustoz.objects.order_by('ism').values('id', 'ism'))
        return JsonResponse(d)
    g = o.guruh
    return JsonResponse({'tur': 'oquvchi', 'ism': o.ism, 'guruh': g.nom if g else None,
                         'smena': g.smena if g else None})


def _guruh_json(g, sana=None, darslar=None, belgilar=None):
    d = {'id': g.id, 'nom': g.nom, 'kurs': g.kurs.nom, 'filial': g.filial.nom, 'filial_id': g.filial_id,
         'ustoz': g.ustoz.ism if g.ustoz else None, 'ustoz_id': g.ustoz_id, 'smena': g.smena,
         'kunlar': ''.join(KUNLAR[int(c)] + ' ' for c in g.hafta_kunlari if c.isdigit()).strip(),
         'xona': g.xona, 'oquvchilar': getattr(g, 'soni', None)}
    if sana is not None:
        d['toldirilgan'] = g.id in (darslar or set()) or g.id in (belgilar or set())
    return d


@api(rollar=('xodim',))
def darslar(request):
    """Tanlangan kunda darsi bor guruhlar (smena bo'yicha tartibda)."""
    x = request.xodim
    sana = _sana(request.GET.get('sana'))
    qs = x.guruhlar().filter(faol=True).annotate(soni=Count('oquvchilar', filter=Q(oquvchilar__faol=True)))
    if x.direktor:
        if _int(request.GET.get('filial')):
            qs = qs.filter(filial_id=_int(request.GET['filial']))
        if _int(request.GET.get('ustoz')):
            qs = qs.filter(ustoz_id=_int(request.GET['ustoz']))
        if request.GET.get('meniki') == '1':
            qs = qs.filter(ustoz_id=x.ustoz_id) if x.ustoz_id else qs.none()
    hammasi = request.GET.get('hammasi') == '1'
    guruhlar = [g for g in qs.order_by('boshlanish', 'nom') if hammasi or g.dars_bormi(sana)]
    ids = [g.id for g in guruhlar]
    toldi_d = set(Dars.objects.filter(guruh_id__in=ids, sana=sana).values_list('guruh_id', flat=True))
    toldi_b = set(Davomat.objects.filter(guruh_id__in=ids, sana=sana).values_list('guruh_id', flat=True))
    return JsonResponse({'sana': sana.isoformat(), 'hafta_kuni': KUNLAR[sana.isoweekday()],
                         'darslar': [_guruh_json(g, sana, toldi_d, toldi_b) for g in guruhlar]})


@csrf_exempt
@api(rollar=('xodim',))
def jurnal(request, guruh_id):
    x = request.xodim
    g = Guruh.objects.select_related('kurs', 'filial', 'ustoz').get(pk=guruh_id)
    if not x.guruhga_ruxsat(g):
        return JsonResponse({'xato': "Bu guruh jurnaliga ruxsat yo'q"}, status=403)
    if request.method == 'POST':
        return _jurnal_saqla(request, x, g)
    sana = _sana(request.GET.get('sana'))
    oquvchilar = list(g.oquvchilar.filter(faol=True).order_by('ism'))
    yozuvlar = {d.oquvchi_id: d for d in Davomat.objects.filter(oquvchi__in=oquvchilar, sana=sana)}
    dars = Dars.objects.filter(guruh=g, sana=sana).select_related('xodim').first()
    # oxirgi 7 dars kuni — tez almashtirish uchun
    kunlar, k = [], sana
    for _ in range(60):
        if g.dars_bormi(k):
            kunlar.append(k.isoformat())
            if len(kunlar) == 7:
                break
        k -= timedelta(days=1)
    return JsonResponse({
        'guruh': _guruh_json(g), 'sana': sana.isoformat(), 'dars_kuni': g.dars_bormi(sana),
        'tahrir': True, 'oxirgi_kunlar': kunlar,
        'dars': {'mavzu': dars.mavzu, 'uy_vazifa': dars.uy_vazifa,
                 'xodim': dars.xodim.ism if dars and dars.xodim else None} if dars else None,
        'qatorlar': [{'id': o.id, 'ism': o.ism,
                      'holat': yozuvlar[o.id].holat if o.id in yozuvlar else None,
                      'baho': yozuvlar[o.id].baho if o.id in yozuvlar else None,
                      'izoh': yozuvlar[o.id].izoh if o.id in yozuvlar else ''} for o in oquvchilar],
    })


def _jurnal_saqla(request, x, g):
    m = json.loads(request.body or b'{}')
    sana = _sana(m.get('sana'))
    if sana > timezone.localdate():
        return JsonResponse({'xato': 'Kelajak sanasiga jurnal yozib bo\'lmaydi'}, status=400)
    ruxsatli = set(g.oquvchilar.filter(faol=True).values_list('id', flat=True))
    with transaction.atomic():
        Dars.objects.update_or_create(guruh=g, sana=sana, defaults={
            'mavzu': str(m.get('mavzu', ''))[:200], 'uy_vazifa': str(m.get('uy_vazifa', ''))[:300], 'xodim': x})
        n = 0
        for q in m.get('qatorlar', []):
            oid = int(q['id'])
            if oid not in ruxsatli:
                continue
            holat = q.get('holat')
            if holat not in HOLATLAR:
                Davomat.objects.filter(oquvchi_id=oid, sana=sana).delete()
                continue
            baho = _int(q.get('baho'))
            if baho is not None and not 1 <= baho <= 10:
                raise ValueError('baho 1–10 oralig\'ida bo\'lishi kerak')
            Davomat.objects.update_or_create(oquvchi_id=oid, sana=sana, defaults={
                'guruh': g, 'holat': holat, 'baho': baho, 'izoh': str(q.get('izoh', ''))[:200], 'belgiladi': x})
            n += 1
    return JsonResponse({'ok': True, 'saqlandi': n})


# ---------------------------------------------------------------- direktor
def _davr(request):
    bugun = timezone.localdate()
    dan = _sana(request.GET.get('dan'), bugun.replace(day=1))
    gacha = _sana(request.GET.get('gacha'), bugun)
    if gacha < dan:
        dan, gacha = gacha, dan
    if (gacha - dan).days > 370:
        raise ValueError('davr 1 yildan oshmasin')
    return dan, gacha


def _rejadagi(guruhlar, dan, gacha):
    """Har guruh uchun davrdagi rejadagi dars kunlari soni."""
    kunlar = [dan + timedelta(days=i) for i in range((gacha - dan).days + 1)]
    return {g.id: sum(1 for k in kunlar if g.dars_bormi(k)) for g in guruhlar}


def _foiz(a, b):
    return round(a * 100 / b) if b else None


@api(rollar=('direktor',))
def hisobot(request):
    dan, gacha = _davr(request)
    filial = _int(request.GET.get('filial'))
    guruhlar = list(Guruh.objects.select_related('filial', 'ustoz').filter(faol=True)
                    .filter(**({'filial_id': filial} if filial else {})))
    gids = [g.id for g in guruhlar]
    reja = _rejadagi(guruhlar, dan, gacha)
    dav = Davomat.objects.filter(sana__range=(dan, gacha), guruh_id__in=gids)
    dars_qs = Dars.objects.filter(sana__range=(dan, gacha), guruh_id__in=gids)
    # jurnali yozilgan (guruh, kun) juftliklari: Dars yoki Davomat bor
    yozilgan = set(dars_qs.values_list('guruh_id', 'sana')) | set(dav.values_list('guruh_id', 'sana').distinct())

    def dav_stat(qs):
        s = qs.aggregate(jami=Count('id'), keldi=Count('id', filter=Q(holat='keldi')),
                         kechikdi=Count('id', filter=Q(holat='kechikdi')),
                         sababli=Count('id', filter=Q(holat='sababli')), kelmadi=Count('id', filter=Q(holat='kelmadi')))
        s['foiz'] = _foiz(s['keldi'] + s['kechikdi'], s['jami'])
        return s

    oquvchilar = Oquvchi.objects.filter(faol=True, guruh_id__in=gids)
    tolov = Tolov.objects.filter(oquvchi__guruh_id__in=gids, oy__lte=gacha)
    tolandi = tolov.filter(tolandi=True, oy__gte=dan.replace(day=1)).aggregate(s=Sum('summa'))['s'] or 0
    qarz = tolov.filter(tolandi=False).aggregate(s=Sum('summa'))['s'] or 0

    # filiallar kesimi
    filiallar = []
    for f in Filial.objects.order_by('pk'):
        fg = [g for g in guruhlar if g.filial_id == f.id]
        if filial and f.id != filial:
            continue
        ids = [g.id for g in fg]
        rj = sum(reja[i] for i in ids)
        yz = sum(1 for (gi, _) in yozilgan if gi in ids)
        filiallar.append({'id': f.id, 'nom': f.nom, 'guruhlar': len(fg),
                          'oquvchilar': oquvchilar.filter(guruh__filial=f).count(),
                          'davomat': dav_stat(dav.filter(guruh__filial=f))['foiz'],
                          'jurnal': _foiz(yz, rj),
                          'qarz': tolov.filter(tolandi=False, oquvchi__guruh__filial=f).aggregate(s=Sum('summa'))['s'] or 0})

    # ustozlar kesimi
    ustozlar = []
    for u in Ustoz.objects.order_by('ism'):
        ug = [g for g in guruhlar if g.ustoz_id == u.id]
        if not ug:
            continue
        ids = [g.id for g in ug]
        rj = sum(reja[i] for i in ids)
        yz = sum(1 for (gi, _) in yozilgan if gi in ids)
        ustozlar.append({'id': u.id, 'ism': u.ism, 'guruhlar': len(ug), 'rejadagi': rj, 'yozilgan': yz,
                         'jurnal': _foiz(yz, rj), 'davomat': dav_stat(dav.filter(guruh_id__in=ids))['foiz']})

    # jurnali yozilmagan darslar (o'tgan kunlar, eng yangisi birinchi)
    yozilmagan = []
    k = min(gacha, timezone.localdate())
    while k >= dan and len(yozilmagan) < 30:
        for g in sorted(guruhlar, key=lambda g: (g.boshlanish is None, g.boshlanish)):
            if g.dars_bormi(k) and (g.id, k) not in yozilgan:
                yozilmagan.append({'guruh_id': g.id, 'guruh': g.nom, 'sana': k.isoformat(), 'smena': g.smena,
                                   'filial': g.filial.nom, 'ustoz': g.ustoz.ism if g.ustoz else None})
        k -= timedelta(days=1)

    return JsonResponse({
        'dan': dan.isoformat(), 'gacha': gacha.isoformat(),
        'jami': {'filiallar': len({g.filial_id for g in guruhlar}), 'guruhlar': len(guruhlar),
                 'oquvchilar': oquvchilar.count(), 'xodimlar': Xodim.objects.filter(faol=True).count(),
                 'rejadagi_darslar': sum(reja.values()), 'yozilgan_darslar': len(yozilgan),
                 'jurnal': _foiz(len(yozilgan), sum(reja.values())),
                 'tolandi': tolandi, 'qarz': qarz},
        'davomat': dav_stat(dav), 'filiallar': filiallar, 'ustozlar': ustozlar, 'yozilmagan': yozilmagan[:30],
    })


@api(rollar=('direktor',))
def xodimlar(request):
    filial = _int(request.GET.get('filial'))
    natija = []
    for x in Xodim.objects.select_related('ustoz').order_by('-direktor', 'ism'):
        gs = Guruh.objects.filter(ustoz_id=x.ustoz_id, faol=True) if x.ustoz_id else Guruh.objects.none()
        if filial:
            gs = gs.filter(filial_id=filial)
            if not gs.exists() and not x.direktor:
                continue
        natija.append({'id': x.id, 'ism': x.ism, 'rol': x.rol, 'faol': x.faol, 'botda': x.telegram_id is not None,
                       'ustoz_id': x.ustoz_id, 'guruhlar': [{'id': g.id, 'nom': g.nom, 'smena': g.smena,
                                                            'filial': g.filial.nom} for g in gs.select_related('filial')]})
    # login berilmagan ustozlar ham ko'rinsin
    bor = {x['ustoz_id'] for x in natija if x['ustoz_id']}
    for u in Ustoz.objects.exclude(id__in=bor).order_by('ism'):
        gs = Guruh.objects.filter(ustoz=u, faol=True).select_related('filial')
        if filial:
            gs = gs.filter(filial_id=filial)
        if gs.exists():
            natija.append({'id': None, 'ism': u.ism, 'rol': 'ustoz (login yo\'q)', 'faol': True, 'botda': False,
                           'ustoz_id': u.id, 'guruhlar': [{'id': g.id, 'nom': g.nom, 'smena': g.smena,
                                                          'filial': g.filial.nom} for g in gs]})
    return JsonResponse({'xodimlar': natija})


# ---------------------------------------------------------------- o'quvchi
@api(rollar=('oquvchi',))
def mening_jurnalim(request):
    o = request.oquvchi
    dav = list(o.davomatlar.select_related('guruh').order_by('-sana')[:40])
    mavzular = {(d.guruh_id, d.sana): d for d in Dars.objects.filter(
        guruh_id__in={d.guruh_id for d in dav if d.guruh_id}, sana__in={d.sana for d in dav})}
    jami = len(dav)
    keldi = sum(1 for d in dav if d.holat in ('keldi', 'kechikdi'))
    return JsonResponse({'foiz': _foiz(keldi, jami), 'qatorlar': [{
        'sana': d.sana.isoformat(), 'holat': d.holat, 'baho': d.baho, 'izoh': d.izoh,
        'mavzu': getattr(mavzular.get((d.guruh_id, d.sana)), 'mavzu', ''),
        'uy_vazifa': getattr(mavzular.get((d.guruh_id, d.sana)), 'uy_vazifa', '')} for d in dav]})
