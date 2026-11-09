import json
from unittest import mock

import telebot
from django.core.management import call_command
from django.test import TestCase, override_settings
from telebot import types

from maktab.management.commands import runbot
from maktab.models import Ariza, Oquvchi


@override_settings(BOT_TOKEN='', CORS_ORIGINS=['https://sjz0606.github.io'])
class ArizaApiTest(TestCase):
    def setUp(self):
        call_command('boshlangich', stdout=open('nul' if __import__('os').name == 'nt' else '/dev/null', 'w'))

    def test_ariza_saqlanadi(self):
        r = self.client.post('/api/ariza/', json.dumps({'ism': 'Ali', 'tel': '+998 90 123 45 67', 'kurs': 'IELTS',
                                                        'filial': 'chorsu', 'vaqt': '18:00'}),
                             content_type='application/json', HTTP_ORIGIN='https://sjz0606.github.io')
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r['Access-Control-Allow-Origin'], 'https://sjz0606.github.io')
        a = Ariza.objects.get()
        self.assertEqual((a.filial.kod, a.manba), ('chorsu', 'sayt'))

    def test_notogri(self):
        r = self.client.post('/api/ariza/', '{"ism":""}', content_type='application/json', HTTP_ORIGIN='https://yomon.uz')
        self.assertEqual(r.status_code, 400)
        self.assertNotIn('Access-Control-Allow-Origin', r)

    def test_preflight(self):
        r = self.client.options('/api/ariza/', HTTP_ORIGIN='https://sjz0606.github.io')
        self.assertEqual(r.status_code, 204)


@override_settings(BOT_TOKEN='')
class BotTest(TestCase):
    CHAT = 555

    def setUp(self):
        call_command('boshlangich', '--demo', stdout=open('nul' if __import__('os').name == 'nt' else '/dev/null', 'w'))
        runbot.holat.clear()
        runbot.urinishlar.clear()
        self.bot = telebot.TeleBot('1:test', threaded=False)
        self.yuborilgan = []
        self.bot.send_message = lambda chat, matn, **kw: self.yuborilgan.append(matn)
        self.bot.delete_message = mock.Mock()
        self.bot.edit_message_text = lambda matn, *a, **kw: self.yuborilgan.append(matn)
        self.bot.answer_callback_query = mock.Mock()
        runbot.royxatdan_otkaz(self.bot)
        self.n = 0
        # handlerlar ichidagi close_old_connections test tranzaksiyasini buzmasin
        p = mock.patch.object(runbot, 'close_old_connections', lambda: None)
        p.start()
        self.addCleanup(p.stop)

    def yoz(self, matn):
        self.n += 1
        u = types.Update.de_json({'update_id': self.n, 'message': {
            'message_id': self.n, 'date': 0, 'text': matn,
            'chat': {'id': self.CHAT, 'type': 'private'},
            'from': {'id': self.CHAT, 'is_bot': False, 'first_name': 'T', 'username': 'tester'}}})
        self.bot.process_new_updates([u])
        return self.yuborilgan[-1]

    def bos(self, data):
        self.n += 1
        u = types.Update.de_json({'update_id': self.n, 'callback_query': {
            'id': str(self.n), 'chat_instance': 'x', 'data': data,
            'from': {'id': self.CHAT, 'is_bot': False, 'first_name': 'T'},
            'message': {'message_id': 1, 'date': 0, 'text': '.', 'chat': {'id': self.CHAT, 'type': 'private'}}}})
        self.bot.process_new_updates([u])
        return self.yuborilgan[-1]

    def test_login_va_kabinet(self):
        self.assertIn('xush kelibsiz', self.yoz('/start'))
        self.yoz(runbot.KIRISH)
        self.yoz('demo')
        self.assertIn('noto', self.yoz('xato-parol'))
        self.yoz(runbot.KIRISH)
        self.yoz('DEMO')
        self.assertIn("Demo O'quvchi", self.yoz('demo123'))
        self.assertEqual(Oquvchi.objects.get(login='demo').telegram_id, self.CHAT)
        self.assertIn('18:00', self.yoz(runbot.JADVAL))
        self.assertIn('7.0', self.yoz(runbot.NATIJALAR))
        self.assertIn('Qarzdorlik', self.yoz(runbot.TOLOVLAR))
        self.assertIn('%', self.yoz(runbot.DAVOMAT))
        self.assertIn('IELTS-18', self.yoz(runbot.PROFIL))
        self.yoz(runbot.CHIQISH)
        self.assertIsNone(Oquvchi.objects.get(login='demo').telegram_id)
        self.assertIn('Avval', self.yoz(runbot.JADVAL))

    def test_bloklash(self):
        for _ in range(runbot.MAKS_URINISH):
            self.yoz(runbot.KIRISH)
            self.yoz('demo')
            self.yoz('yomon')
        self.assertIn('daqiqadan', self.yoz(runbot.KIRISH))

    def test_ariza_bot(self):
        self.yoz(runbot.YOZILISH)
        self.yoz('Madina')
        self.assertIn("noto'g'ri", self.yoz('123'))
        self.yoz('+998901112233')
        from maktab.models import Filial, Kurs
        self.bos(f'kurs:{Kurs.objects.get(nom="CEFR").pk}')
        self.bos(f'filial:{Filial.objects.get(kod="beruniy").pk}')
        a = Ariza.objects.get()
        self.assertEqual((a.ism, a.kurs, a.filial.kod, a.manba), ('Madina', 'CEFR', 'beruniy', 'bot'))
