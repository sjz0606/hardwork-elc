import hashlib
import hmac
import json
import time
from datetime import date, time as soat, timedelta
from unittest import mock
from urllib.parse import urlencode

from django.test import TestCase, override_settings
from django.utils import timezone

from maktab.miniapp import init_data_tekshir
from maktab.models import Dars, Davomat, Filial, Guruh, Kurs, Oquvchi, Ustoz, Xodim

TOKEN = '123:ABC'


def imzola(user, token=TOKEN, auth_date=None):
    maydon = {'auth_date': str(auth_date or int(time.time())), 'query_id': 'q1', 'user': json.dumps(user)}
    satr = '\n'.join(f'{k}={v}' for k, v in sorted(maydon.items()))
    kalit = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    maydon['hash'] = hmac.new(kalit, satr.encode(), hashlib.sha256).hexdigest()
    return urlencode(maydon)


@override_settings(BOT_TOKEN=TOKEN, DEBUG=False)
class MiniAppTest(TestCase):
    def setUp(self):
        self.f1 = Filial.objects.create(kod='chilonzor', nom='Chilonzor')
        self.f2 = Filial.objects.create(kod='chorsu', nom='Chorsu')
        k = Kurs.objects.create(nom='IELTS', narx=750000)
        self.u1 = Ustoz.objects.create(ism='Otabek')
        self.u2 = Ustoz.objects.create(ism='Temurbek')
        hk = str(timezone.localdate().isoweekday())
        self.g1 = Guruh.objects.create(nom='IELTS-18', kurs=k, filial=self.f1, ustoz=self.u1,
                                       boshlanish=soat(18), tugash=soat(20), hafta_kunlari=hk)
        self.g2 = Guruh.objects.create(nom='IELTS-9', kurs=k, filial=self.f2, ustoz=self.u2,
                                       boshlanish=soat(9, 30), tugash=soat(11, 30), hafta_kunlari=hk)
        self.o1 = Oquvchi.objects.create(ism='Ali', login='ali', guruh=self.g1, telegram_id=301)
        self.o2 = Oquvchi.objects.create(ism='Vali', login='vali', guruh=self.g1)
        self.o3 = Oquvchi.objects.create(ism='Hasan', login='hasan', guruh=self.g2)
        self.ustoz = Xodim.objects.create(ism='Otabek', login='otabek', ustoz=self.u1, telegram_id=101)
        self.direktor = Xodim.objects.create(ism='Jasurbek', login='jasur', direktor=True, telegram_id=201)
        self.bugun = timezone.localdate().isoformat()

    def get(self, url, tid):
        return self.client.get(url, HTTP_X_INIT_DATA=imzola({'id': tid}) if tid else '')

    def post(self, url, tid, data):
        return self.client.post(url, json.dumps(data), content_type='application/json',
                                HTTP_X_INIT_DATA=imzola({'id': tid}))

    # --- imzo
    def test_imzo(self):
        self.assertEqual(init_data_tekshir(imzola({'id': 5}))['id'], 5)
        self.assertIsNone(init_data_tekshir(imzola({'id': 5}, token='999:XYZ')))
        self.assertIsNone(init_data_tekshir(imzola({'id': 5}, auth_date=int(time.time()) - 2 * 86400)))
        self.assertIsNone(init_data_tekshir(imzola({'id': 5}).replace('5', '6', 1)))
        self.assertIsNone(init_data_tekshir(''))

    def test_kirmagan_403(self):
        self.assertEqual(self.get('/app/api/men', None).status_code, 403)
        self.assertEqual(self.get('/app/api/men', 999).status_code, 403)  # imzo to'g'ri, lekin botda login yo'q

    def test_sahifa(self):
        r = self.client.get('/app/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'telegram-web-app.js')

    # --- ustoz
    def test_ustoz_faqat_oz_guruhi(self):
        j = self.get('/app/api/darslar', 101).json()
        self.assertEqual([d['nom'] for d in j['darslar']], ['IELTS-18'])
        self.assertEqual(self.get(f'/app/api/jurnal/{self.g2.id}', 101).status_code, 403)
        self.assertEqual(self.get('/app/api/hisobot', 101).status_code, 403)
        self.assertEqual(self.get('/app/api/men', 101).json()['rol'], 'ustoz')

    def test_jurnal_saqlash(self):
        r = self.post(f'/app/api/jurnal/{self.g1.id}', 101, {
            'sana': self.bugun, 'mavzu': 'Writing Task 2', 'uy_vazifa': 'Test 2',
            'qatorlar': [{'id': self.o1.id, 'holat': 'keldi', 'baho': 8, 'izoh': 'zo\'r'},
                         {'id': self.o2.id, 'holat': 'kelmadi'},
                         {'id': self.o3.id, 'holat': 'keldi'}]})  # boshqa guruh o'quvchisi — e'tiborsiz
        self.assertEqual(r.json()['saqlandi'], 2)
        self.assertEqual(Davomat.objects.get(oquvchi=self.o1).baho, 8)
        self.assertTrue(Davomat.objects.get(oquvchi=self.o1).keldi)
        self.assertFalse(Davomat.objects.get(oquvchi=self.o2).keldi)
        self.assertFalse(Davomat.objects.filter(oquvchi=self.o3).exists())
        d = Dars.objects.get(guruh=self.g1)
        self.assertEqual((d.mavzu, d.xodim), ('Writing Task 2', self.ustoz))
        j = self.get(f'/app/api/jurnal/{self.g1.id}?sana={self.bugun}', 101).json()
        self.assertEqual({q['ism']: q['holat'] for q in j['qatorlar']}, {'Ali': 'keldi', 'Vali': 'kelmadi'})
        self.assertTrue(self.get('/app/api/darslar', 101).json()['darslar'][0]['toldirilgan'])
        # belgini olib tashlash
        self.post(f'/app/api/jurnal/{self.g1.id}', 101, {'sana': self.bugun, 'qatorlar': [{'id': self.o2.id, 'holat': None}]})
        self.assertFalse(Davomat.objects.filter(oquvchi=self.o2).exists())

    def test_jurnal_xato_kiritish(self):
        ertaga = (timezone.localdate() + timedelta(days=1)).isoformat()
        self.assertEqual(self.post(f'/app/api/jurnal/{self.g1.id}', 101, {'sana': ertaga}).status_code, 400)
        r = self.post(f'/app/api/jurnal/{self.g1.id}', 101,
                      {'sana': self.bugun, 'qatorlar': [{'id': self.o1.id, 'holat': 'keldi', 'baho': 15}]})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Davomat.objects.exists())  # tranzaksiya qaytarildi

    def test_dars_kuni_boyicha(self):
        ertaga = timezone.localdate() + timedelta(days=1)
        self.assertEqual(self.get(f'/app/api/darslar?sana={ertaga}', 101).json()['darslar'], [])

    # --- direktor
    def test_direktor_hammasini_koradi(self):
        j = self.get('/app/api/darslar', 201).json()
        self.assertEqual([d['nom'] for d in j['darslar']], ['IELTS-9', 'IELTS-18'])  # smena tartibida
        j = self.get(f'/app/api/darslar?filial={self.f2.id}', 201).json()
        self.assertEqual([d['nom'] for d in j['darslar']], ['IELTS-9'])
        self.assertEqual(self.get(f'/app/api/jurnal/{self.g2.id}', 201).status_code, 200)
        self.assertEqual(self.post(f'/app/api/jurnal/{self.g2.id}', 201, {
            'sana': self.bugun, 'qatorlar': [{'id': self.o3.id, 'holat': 'kechikdi'}]}).status_code, 200)

    def test_hisobot(self):
        self.post(f'/app/api/jurnal/{self.g1.id}', 101, {'sana': self.bugun, 'qatorlar': [
            {'id': self.o1.id, 'holat': 'keldi'}, {'id': self.o2.id, 'holat': 'kelmadi'}]})
        j = self.get(f'/app/api/hisobot?dan={self.bugun}&gacha={self.bugun}', 201).json()
        self.assertEqual(j['davomat']['foiz'], 50)
        self.assertEqual(j['jami']['rejadagi_darslar'], 2)
        self.assertEqual(j['jami']['yozilgan_darslar'], 1)
        self.assertEqual([y['guruh'] for y in j['yozilmagan']], ['IELTS-9'])
        self.assertEqual({u['ism']: u['jurnal'] for u in j['ustozlar']}, {'Otabek': 100, 'Temurbek': 0})
        j = self.get(f'/app/api/hisobot?filial={self.f2.id}', 201).json()
        self.assertEqual([f['nom'] for f in j['filiallar']], ['Chorsu'])

    def test_xodimlar(self):
        j = self.get('/app/api/xodimlar', 201).json()
        ismlar = [x['ism'] for x in j['xodimlar']]
        self.assertIn('Jasurbek', ismlar)
        self.assertIn('Temurbek', ismlar)  # login berilmagan ustoz ham ko'rinadi

    def test_direktor_ham_ustoz(self):
        self.direktor.ustoz = self.u2
        self.direktor.save()
        j = self.get('/app/api/darslar?meniki=1', 201).json()
        self.assertEqual([d['nom'] for d in j['darslar']], ['IELTS-9'])
        self.assertEqual(self.get('/app/api/men', 201).json()['rol'], 'direktor+ustoz')

    # --- o'quvchi
    def test_oquvchi(self):
        self.post(f'/app/api/jurnal/{self.g1.id}', 101, {'sana': self.bugun, 'mavzu': 'Speaking',
                                                         'qatorlar': [{'id': self.o1.id, 'holat': 'keldi', 'baho': 9}]})
        j = self.get('/app/api/mening', 301).json()
        self.assertEqual(j['qatorlar'][0]['mavzu'], 'Speaking')
        self.assertEqual(self.get('/app/api/darslar', 301).status_code, 403)


@override_settings(BOT_TOKEN='', MINIAPP_URL='https://hw.test/app/', MINIAPP_SSL_TEKSHIR=False)
class XodimBotTest(TestCase):
    def setUp(self):
        import telebot

        from maktab import bot as b
        b.holat.clear()
        self.b = b
        self.x = Xodim(ism='Jasurbek', login='jasur', direktor=True)
        self.x.parol_qoy('sir123')
        self.x.save()
        self.bot = telebot.TeleBot('1:test', threaded=False)
        self.yuborilgan = []
        self.bot.send_message = lambda chat, matn, **kw: self.yuborilgan.append((matn, kw.get('reply_markup')))
        self.bot.delete_message = mock.Mock()
        self.bot.set_chat_menu_button = mock.Mock()
        b.royxatdan_otkaz(self.bot)
        p = mock.patch.object(b, 'close_old_connections', lambda: None)
        p.start()
        self.addCleanup(p.stop)
        self.n = 0

    def yoz(self, matn):
        from telebot import types
        self.n += 1
        self.bot.process_new_updates([types.Update.de_json({'update_id': self.n, 'message': {
            'message_id': self.n, 'date': 0, 'text': matn, 'chat': {'id': 77, 'type': 'private'},
            'from': {'id': 77, 'is_bot': False, 'first_name': 'J'}}})])
        return self.yuborilgan[-1]

    def test_direktor_login_va_miniapp_tugmasi(self):
        self.yoz(self.b.KIRISH)
        self.yoz('JASUR')
        matn, klav = self.yoz('sir123')
        self.assertIn('direktor', matn)
        self.x.refresh_from_db()
        self.assertEqual(self.x.telegram_id, 77)
        tugmalar = [t for qator in klav.keyboard for t in qator]
        web = {t['text']: t['web_app']['url'] for t in tugmalar if t.get('web_app')}
        self.assertEqual(web, {self.b.JURNAL: 'https://hw.test/app/', self.b.HISOBOT: 'https://hw.test/app/?tab=hisobot'})
        self.bot.set_chat_menu_button.assert_called_once()
        self.yoz(self.b.CHIQISH)
        self.x.refresh_from_db()
        self.assertIsNone(self.x.telegram_id)

    @override_settings(MINIAPP_URL='http://hw.test/app/')
    def test_https_yoq_bolsa_oddiy_tugma(self):
        self.yoz(self.b.KIRISH)
        self.yoz('jasur')
        _, klav = self.yoz('sir123')
        self.assertFalse(any(t.get('web_app') for q in klav.keyboard for t in q))
        matn, _ = self.yoz(self.b.JURNAL)
        self.assertIn('SSL', matn)

    def test_login_yagona(self):
        from maktab.admin import OquvchiForma, XodimForma
        Oquvchi.objects.create(ism='A', login='band')
        f = XodimForma(data={'ism': 'X', 'login': 'BAND', 'faol': True})
        self.assertFalse(f.is_valid())
        self.assertIn('login', f.errors)
        f = OquvchiForma(data={'ism': 'Y', 'login': 'jasur', 'faol': True, 'qoshilgan': date.today()})
        self.assertFalse(f.is_valid())
        self.assertIn('login', f.errors)
