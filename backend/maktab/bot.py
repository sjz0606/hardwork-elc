"""HardWork ELC Telegram bot mantiqi — polling (manage.py runbot) va webhook (/bot/<maxfiy>/) uchun umumiy."""
import functools
import html
import logging
import time
from datetime import timedelta

import telebot
from django.conf import settings
from django.core.cache import cache
from django.db import close_old_connections
from django.utils import timezone
from telebot import types

from maktab.models import Ariza, Filial, Kurs, Oquvchi
from maktab.xabar import ariza_xabari

log = logging.getLogger('hardwork.bot')
def e(s):
    return html.escape(str(s), quote=False)

# --- Tugma matnlari ---
KIRISH = '🔐 Kirish'
YOZILISH = '📝 Sinov darsiga yozilish'
NARXLAR = '💰 Kurslar va narxlar'
FILIALLAR = '📍 Filiallar'
PROFIL = '👤 Profilim'
JADVAL = '📅 Dars jadvali'
NATIJALAR = '📊 Natijalarim'
DAVOMAT = '✅ Davomat'
TOLOVLAR = "💳 To'lovlar"
CHIQISH = '🚪 Chiqish'
BEKOR = '❌ Bekor qilish'

MAKS_URINISH = 5          # ketma-ket noto'g'ri parol
BLOK_SONIYA = 10 * 60     # shundan keyin bloklash muddati



class Ombor:
    """Chat holatini Django keshida saqlaydi — webhookda har so'rov alohida jarayonda bo'lishi mumkin."""

    def __init__(self, prefiks, muddat):
        self.prefiks, self.muddat = prefiks, muddat

    def _k(self, chat):
        return f'hwbot:{self.prefiks}:{chat}'

    def get(self, chat, standart=None):
        v = cache.get(self._k(chat))
        return standart if v is None else v

    def __setitem__(self, chat, qiymat):
        cache.set(self._k(chat), qiymat, self.muddat)

    def pop(self, chat, standart=None):
        v = self.get(chat, standart)
        cache.delete(self._k(chat))
        return v

    def yangila(self, chat, **kw):
        h = self.get(chat, {})
        h.update(kw)
        self[chat] = h
        return h

    def clear(self):
        cache.clear()


holat = Ombor('holat', 60 * 60)            # chat_id -> {'qadam': ..., ...}
urinishlar = Ombor('urinish', BLOK_SONIYA)  # chat_id -> (soni, blok_tugash_vaqti)


def som(n):
    return f'{n:,}'.replace(',', ' ') + " so'm"


def mehmon_klaviatura():
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(KIRISH)
    if not settings.BOT_FAQAT_LOGIN:
        k.row(YOZILISH)
        k.row(NARXLAR, FILIALLAR)
    return k


LOGIN_KERAK = ("🔐 Botdan foydalanish uchun markaz bergan <b>login va parol</b> bilan kiring.\n"
               "Login yo'q bo'lsa — filial administratoriga murojaat qiling.")


def oquvchi_klaviatura():
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.row(PROFIL, JADVAL)
    k.row(NATIJALAR, DAVOMAT)
    k.row(TOLOVLAR, FILIALLAR)
    k.row(CHIQISH)
    return k


def bekor_klaviatura(kontakt=False):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=kontakt)
    if kontakt:
        k.row(types.KeyboardButton('📱 Raqamni yuborish', request_contact=True))
    k.row(BEKOR)
    return k


def joriy_oquvchi(chat_id):
    return Oquvchi.objects.select_related('guruh__kurs', 'guruh__filial', 'guruh__ustoz') \
        .filter(telegram_id=chat_id, faol=True).first()


def asosiy_menyu(chat_id):
    return oquvchi_klaviatura() if joriy_oquvchi(chat_id) else mehmon_klaviatura()


BUYRUQLAR = [
    ('start', 'Bosh menyu'),
    ('kirish', 'Login bilan kirish'),
    ('chiqish', 'Akkauntdan chiqish'),
    ('myid', 'Telegram ID ni bilish'),
]


def bot_yarat(token=None, threaded=True):
    """Handlerlari ulangan TeleBot qaytaradi."""
    bot = telebot.TeleBot(token or settings.BOT_TOKEN, parse_mode='HTML', threaded=threaded)
    royxatdan_otkaz(bot)
    return bot


def buyruqlarni_qoy(bot):
    bot.set_my_commands([types.BotCommand(k, t) for k, t in BUYRUQLAR])


def royxatdan_otkaz(bot):
    def db(f):
        """Har bir handlerdan oldin eskirgan DB ulanishlarini yopadi, xatolarni yutadi."""
        @functools.wraps(f)
        def w(*a, **kw):
            close_old_connections()
            try:
                return f(*a, **kw)
            except Exception:
                log.exception('Handler xatosi')
                obj = a[0]
                chat = obj.message.chat.id if isinstance(obj, types.CallbackQuery) else obj.chat.id
                bot.send_message(chat, "Kechirasiz, xatolik yuz berdi. Qaytadan urinib ko'ring.")
            finally:
                close_old_connections()
        return w

    shaxsiy = lambda m: m.chat.type == 'private'  # noqa: E731

    def mehmonga_yopiq(m):
        """Faqat-login rejimida kirmagan foydalanuvchini to'xtatadi."""
        if settings.BOT_FAQAT_LOGIN and not joriy_oquvchi(m.chat.id):
            bot.send_message(m.chat.id, LOGIN_KERAK, reply_markup=mehmon_klaviatura())
            return True
        return False

    # ---------------- Umumiy ----------------
    @bot.message_handler(commands=['start'], func=shaxsiy)
    @db
    def start(m):
        holat.pop(m.chat.id, None)
        o = joriy_oquvchi(m.chat.id)
        if o:
            matn = f'Salom, <b>{e(o.ism)}</b>! 👋\nHardWork o\'quvchi kabinetiga xush kelibsiz.'
        elif settings.BOT_FAQAT_LOGIN:
            bot.send_message(m.chat.id, 'Assalomu alaykum! 👋\n<b>HardWork English Learning Centre</b> boti.\n\n'
                             + LOGIN_KERAK, reply_markup=mehmon_klaviatura())
            return kirish(m)
        else:
            matn = ('Assalomu alaykum! 👋\n<b>HardWork English Learning Centre</b> botiga xush kelibsiz.\n\n'
                    "• O'quvchilar — <b>🔐 Kirish</b> tugmasi orqali markaz bergan login va parol bilan kiring.\n"
                    '• Yangi bo\'lsangiz — <b>3 ta bepul sinov darsiga</b> yoziling.')
        bot.send_message(m.chat.id, matn, reply_markup=asosiy_menyu(m.chat.id))

    @bot.message_handler(commands=['myid'])
    @db
    def myid(m):
        bot.send_message(m.chat.id, f'Chat ID: <code>{m.chat.id}</code>')

    @bot.message_handler(func=lambda m: shaxsiy(m) and m.text == BEKOR)
    @db
    def bekor(m):
        holat.pop(m.chat.id, None)
        bot.send_message(m.chat.id, 'Bekor qilindi.', reply_markup=asosiy_menyu(m.chat.id))

    @bot.message_handler(func=lambda m: shaxsiy(m) and m.text == NARXLAR)
    @db
    def narxlar(m):
        if mehmonga_yopiq(m):
            return
        qatorlar = ['<b>Kurslar va narxlar</b>\n']
        for k in Kurs.objects.order_by('narx'):
            qatorlar.append(f'📚 <b>{e(k.nom)}</b>' + (f' — {e(k.tavsif)}' if k.tavsif else '') + f'\n     {som(k.narx)}/oy')
        qatorlar.append('\n✦ Darslar haftada 7 kun, ~2 soatdan\n✦ 3 marta bepul sinov darsi')
        bot.send_message(m.chat.id, '\n'.join(qatorlar))

    @bot.message_handler(func=lambda m: shaxsiy(m) and m.text == FILIALLAR)
    @db
    def filiallar(m):
        if mehmonga_yopiq(m):
            return
        qatorlar = ['<b>Filiallarimiz</b>']
        for f in Filial.objects.order_by('pk'):
            q = f'\n📍 <b>{e(f.nom)}</b>'
            if f.manzil:
                q += f'\n{e(f.manzil)}'
            if f.tel:
                q += f'\n📞 {e(f.tel)}'
            if f.tg:
                q += f'\n💬 @{e(f.tg)}'
            qatorlar.append(q)
        bot.send_message(m.chat.id, '\n'.join(qatorlar), disable_web_page_preview=True)

    # ---------------- Login ----------------
    @bot.message_handler(commands=['kirish'], func=shaxsiy)
    @bot.message_handler(func=lambda m: shaxsiy(m) and m.text == KIRISH)
    @db
    def kirish(m):
        if joriy_oquvchi(m.chat.id):
            bot.send_message(m.chat.id, 'Siz allaqachon kirgansiz.', reply_markup=oquvchi_klaviatura())
            return
        soni, blok = urinishlar.get(m.chat.id, (0, 0))
        if blok > time.time():
            daq = int((blok - time.time()) // 60) + 1
            bot.send_message(m.chat.id, f"Ko'p marta noto'g'ri parol kiritildi. {daq} daqiqadan keyin urinib ko'ring.")
            return
        holat[m.chat.id] = {'qadam': 'login'}
        bot.send_message(m.chat.id, '🔐 <b>Loginingizni</b> kiriting:', reply_markup=bekor_klaviatura())

    @bot.message_handler(func=lambda m: shaxsiy(m) and holat.get(m.chat.id, {}).get('qadam') == 'login',
                         content_types=['text'])
    @db
    def login_qabul(m):
        holat[m.chat.id] = {'qadam': 'parol', 'login': m.text.strip()}
        bot.send_message(m.chat.id, '🔑 Endi <b>parolni</b> kiriting:\n<i>(xavfsizlik uchun xabaringiz o\'chiriladi)</i>')

    @bot.message_handler(func=lambda m: shaxsiy(m) and holat.get(m.chat.id, {}).get('qadam') == 'parol',
                         content_types=['text'])
    @db
    def parol_qabul(m):
        try:
            bot.delete_message(m.chat.id, m.message_id)
        except Exception:
            pass
        login = holat.pop(m.chat.id, {}).get('login', '')
        o = Oquvchi.objects.filter(login__iexact=login, faol=True).first()
        if not o or not o.parol_tekshir(m.text):
            soni, _ = urinishlar.get(m.chat.id, (0, 0))
            soni += 1
            if soni >= MAKS_URINISH:
                urinishlar[m.chat.id] = (0, time.time() + BLOK_SONIYA)
                matn = "❌ Login yoki parol noto'g'ri. Urinishlar tugadi — 10 daqiqadan keyin qayta urinib ko'ring."
            else:
                urinishlar[m.chat.id] = (soni, 0)
                matn = f"❌ Login yoki parol noto'g'ri. (qolgan urinish: {MAKS_URINISH - soni})"
            bot.send_message(m.chat.id, matn, reply_markup=mehmon_klaviatura())
            return
        if o.telegram_id and o.telegram_id != m.chat.id:
            bot.send_message(m.chat.id, "Bu akkaunt boshqa Telegram profilga ulangan. Filial administratoriga murojaat qiling.",
                             reply_markup=mehmon_klaviatura())
            return
        urinishlar.pop(m.chat.id, None)
        # Shu Telegramga avval boshqa o'quvchi ulangan bo'lsa — uzamiz
        Oquvchi.objects.filter(telegram_id=m.chat.id).exclude(pk=o.pk).update(telegram_id=None, telegram_username='')
        o.telegram_id = m.chat.id
        o.telegram_username = m.from_user.username or ''
        o.save(update_fields=['telegram_id', 'telegram_username'])
        bot.send_message(m.chat.id, f'✅ Xush kelibsiz, <b>{e(o.ism)}</b>!', reply_markup=oquvchi_klaviatura())

    @bot.message_handler(commands=['chiqish'], func=shaxsiy)
    @bot.message_handler(func=lambda m: shaxsiy(m) and m.text == CHIQISH)
    @db
    def chiqish(m):
        n = Oquvchi.objects.filter(telegram_id=m.chat.id).update(telegram_id=None, telegram_username='')
        holat.pop(m.chat.id, None)
        bot.send_message(m.chat.id, 'Akkauntdan chiqdingiz.' if n else 'Siz tizimga kirmagansiz.',
                         reply_markup=mehmon_klaviatura())

    # ---------------- O'quvchi kabineti ----------------
    def oquvchi_kerak(f):
        @functools.wraps(f)
        def w(m):
            o = joriy_oquvchi(m.chat.id)
            if not o:
                bot.send_message(m.chat.id, 'Avval tizimga kiring.', reply_markup=mehmon_klaviatura())
                return
            return f(m, o)
        return w

    def tugma(matn):
        return lambda m: shaxsiy(m) and m.text == matn

    @bot.message_handler(func=tugma(PROFIL))
    @db
    @oquvchi_kerak
    def profil(m, o):
        g = o.guruh
        qatorlar = [f'👤 <b>{e(o.ism)}</b>', f'Login: <code>{e(o.login)}</code>']
        if o.tel:
            qatorlar.append(f'Telefon: {e(o.tel)}')
        if g:
            qatorlar += [f'Kurs: {e(g.kurs.nom)}', f'Guruh: {e(g.nom)}', f'Filial: {e(g.filial.nom)}']
            if g.ustoz:
                qatorlar.append(f'Ustoz: {e(g.ustoz.ism)}' + (f' (@{e(g.ustoz.tg)})' if g.ustoz.tg else ''))
        else:
            qatorlar.append('Guruh: hali biriktirilmagan')
        qatorlar.append(f'Markazda: {o.qoshilgan:%d.%m.%Y} dan')
        bot.send_message(m.chat.id, '\n'.join(qatorlar))

    @bot.message_handler(func=tugma(JADVAL))
    @db
    @oquvchi_kerak
    def jadval(m, o):
        g = o.guruh
        if not g:
            bot.send_message(m.chat.id, "Siz hali guruhga biriktirilmagansiz. Administrator bilan bog'laning.")
            return
        matn = (f'📅 <b>Dars jadvali</b>\n\nGuruh: {e(g.nom)}\nKunlar: {e(g.kunlar)}\nVaqt: <b>{e(g.vaqt)}</b>\n'
                f'Filial: {e(g.filial.nom)}' + (f'\nXona: {e(g.xona)}' if g.xona else '') +
                (f'\n📍 {e(g.filial.manzil)}' if g.filial.manzil else ''))
        bot.send_message(m.chat.id, matn)

    @bot.message_handler(func=tugma(NATIJALAR))
    @db
    @oquvchi_kerak
    def natijalar(m, o):
        nlar = list(o.natijalar.all()[:8])
        if not nlar:
            bot.send_message(m.chat.id, "Hozircha natijalar kiritilmagan.")
            return
        qatorlar = ['📊 <b>Natijalarim</b>']
        for n in nlar:
            q = f'\n<b>{n.sana:%d.%m.%Y}</b> · {e(n.get_turi_display())} — <b>{e(n.umumiy)}</b>'
            qism = [f'{b}{v}' for b, v in (('L', n.listening), ('R', n.reading), ('W', n.writing), ('S', n.speaking))
                    if v is not None]
            if qism:
                q += '\n' + ' · '.join(qism)
            if n.izoh:
                q += f'\n<i>{e(n.izoh)}</i>'
            qatorlar.append(q)
        bot.send_message(m.chat.id, '\n'.join(qatorlar))

    @bot.message_handler(func=tugma(DAVOMAT))
    @db
    @oquvchi_kerak
    def davomat(m, o):
        dan = timezone.localdate() - timedelta(days=30)
        oxirgi = list(o.davomatlar.filter(sana__gte=dan))
        if not oxirgi:
            bot.send_message(m.chat.id, "So'nggi 30 kunda davomat yozuvlari yo'q.")
            return
        keldi = sum(1 for d in oxirgi if d.keldi)
        foiz = round(keldi * 100 / len(oxirgi))
        qatorlar = [f'✅ <b>Davomat (30 kun)</b>\nKeldi: {keldi} / {len(oxirgi)} dars — <b>{foiz}%</b>\n']
        qatorlar += [f'{d.sana:%d.%m} — ' + ('✅ keldi' if d.keldi else '❌ kelmadi') for d in oxirgi[:10]]
        bot.send_message(m.chat.id, '\n'.join(qatorlar))

    @bot.message_handler(func=tugma(TOLOVLAR))
    @db
    @oquvchi_kerak
    def tolovlar(m, o):
        tlar = list(o.tolovlar.all()[:6])
        if not tlar:
            bot.send_message(m.chat.id, "To'lovlar haqida ma'lumot yo'q.")
            return
        qarz = sum(t.summa for t in o.tolovlar.filter(tolandi=False))
        qatorlar = ["💳 <b>To'lovlar</b>\n"]
        for t in tlar:
            belgi = f"✅ to'langan ({t.sana:%d.%m})" if t.tolandi and t.sana else ("✅ to'langan" if t.tolandi else "⏳ to'lanmagan")
            qatorlar.append(f'{t.oy:%m.%Y} — {som(t.summa)} — {belgi}')
        qatorlar.append(f'\nQarzdorlik: <b>{som(qarz)}</b>' if qarz else "\nQarzdorlik yo'q 👍")
        bot.send_message(m.chat.id, '\n'.join(qatorlar))

    # ---------------- Sinov darsiga yozilish ----------------
    @bot.message_handler(func=tugma(YOZILISH))
    @db
    def yozilish(m):
        if mehmonga_yopiq(m):
            return
        holat[m.chat.id] = {'qadam': 'a_ism'}
        bot.send_message(m.chat.id, '📝 Ismingizni yozing:', reply_markup=bekor_klaviatura())

    @bot.message_handler(func=lambda m: shaxsiy(m) and holat.get(m.chat.id, {}).get('qadam') == 'a_ism',
                         content_types=['text'])
    @db
    def a_ism(m):
        holat.yangila(m.chat.id, qadam='a_tel', ism=m.text.strip()[:120])
        bot.send_message(m.chat.id, '📞 Telefon raqamingizni yuboring (tugma orqali yoki yozib):',
                         reply_markup=bekor_klaviatura(kontakt=True))

    @bot.message_handler(func=lambda m: shaxsiy(m) and holat.get(m.chat.id, {}).get('qadam') == 'a_tel',
                         content_types=['text', 'contact'])
    @db
    def a_tel(m):
        tel = m.contact.phone_number if m.content_type == 'contact' else m.text.strip()
        raqamlar = ''.join(c for c in tel if c.isdigit())
        if not 9 <= len(raqamlar) <= 15:
            bot.send_message(m.chat.id, "Raqam noto'g'ri. Masalan: +998 90 123 45 67")
            return
        holat.yangila(m.chat.id, qadam='a_kurs', tel=tel[:30])
        k = types.InlineKeyboardMarkup()
        for kurs in Kurs.objects.order_by('narx'):
            k.add(types.InlineKeyboardButton(f'{kurs.nom} — {som(kurs.narx)}', callback_data=f'kurs:{kurs.pk}'))
        bot.send_message(m.chat.id, '👍', reply_markup=bekor_klaviatura())
        bot.send_message(m.chat.id, '📚 Qaysi kurs qiziqtiradi?', reply_markup=k)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('kurs:'))
    @db
    def a_kurs(c):
        h = holat.get(c.message.chat.id)
        if not h or h.get('qadam') != 'a_kurs':
            bot.answer_callback_query(c.id)
            return
        kurs = Kurs.objects.filter(pk=c.data.split(':')[1]).first()
        h = holat.yangila(c.message.chat.id, qadam='a_filial', kurs=kurs.nom if kurs else '')
        k = types.InlineKeyboardMarkup()
        for f in Filial.objects.order_by('pk'):
            k.add(types.InlineKeyboardButton(f.nom, callback_data=f'filial:{f.pk}'))
        bot.answer_callback_query(c.id)
        bot.edit_message_text(f'📚 Kurs: <b>{e(h["kurs"])}</b>\n\n📍 Qaysi filial qulay?',
                              c.message.chat.id, c.message.message_id, reply_markup=k)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('filial:'))
    @db
    def a_filial(c):
        chat = c.message.chat.id
        h = holat.get(chat)
        if not h or h.get('qadam') != 'a_filial':
            bot.answer_callback_query(c.id)
            return
        holat.pop(chat, None)
        f = Filial.objects.filter(pk=c.data.split(':')[1]).first()
        a = Ariza.objects.create(ism=h['ism'], tel=h['tel'], kurs=h.get('kurs', ''), filial=f,
                                 manba='bot', telegram_id=chat)
        ariza_xabari(a)
        bot.answer_callback_query(c.id, 'Qabul qilindi!')
        bot.edit_message_text(
            f'✅ Rahmat, <b>{e(a.ism)}</b>! Arizangiz qabul qilindi.\n'
            f'{e(f.nom if f else "Filial")} administratori tez orada qo\'ng\'iroq qiladi.'
            + (f'\n\nTezroq javob uchun: @{e(f.tg)}' if f and f.tg else ''),
            chat, c.message.message_id)
        bot.send_message(chat, 'Bosh menyu:', reply_markup=asosiy_menyu(chat))

    # ---------------- Qolgan hammasi ----------------
    @bot.message_handler(func=shaxsiy, content_types=['text'])
    @db
    def boshqa(m):
        if mehmonga_yopiq(m):
            return
        bot.send_message(m.chat.id, 'Menyudan tanlang 👇', reply_markup=asosiy_menyu(m.chat.id))


_webhook_bot = None


def webhook_bot():
    """Webhook uchun bitta (jarayon ichida qayta ishlatiladigan) sinxron bot."""
    global _webhook_bot
    if _webhook_bot is None:
        _webhook_bot = bot_yarat(threaded=False)
    return _webhook_bot
