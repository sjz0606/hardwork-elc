"""Saytdagi ma'lumotlarni bazaga yozadi: python manage.py boshlangich [--demo]"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from maktab.models import Davomat, Filial, Guruh, Kurs, Natija, Oquvchi, Tolov, Ustoz

FILIALLAR = [
    ('chilonzor', 'Chilonzor', "Bunyodkor shoh ko'chasi 52, Integro binosi, 7–8-qavat (Chilonzor metro)",
     '+998 99 887 40 03', 'hardwork_integro'),
    ('beruniy', 'Beruniy', '“Belissimo” binosi, 2-qavat (Beruniy metro)', '+998 94 101 92 42', 'hardwork_beruniy'),
    ('chorsu', 'Chorsu', "Alisher Navoiy ko'chasi 44 — “Turkuaz” ro'parasi, 3-qavat (Chorsu metro)",
     '+998 77 362 40 03', 'hardwork_chorsu'),
]
KURSLAR = [
    ('General English', 'Noldan → B2', 650000),
    ('CEFR', 'B2 · C1', 670000),
    ('IELTS', 'Band 6.5 – 8.0', 750000),
]
USTOZLAR = [
    ('Jasurbek Karimov', '8.0', ''),
    ('Temurbek Akbaraliyev', '8.5', ''),
    ('Otabek Akramov', '8.5', 'otabekakramovs'),
    ("Ilhomjon Ne'matullayev", '', 'nematullive_me'),
]


class Command(BaseCommand):
    help = "Filiallar, kurslar va ustozlarni yaratadi; --demo bilan sinov o'quvchisi (demo / demo123)"

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true')

    def handle(self, *args, demo=False, **opts):
        for kod, nom, manzil, tel, tg in FILIALLAR:
            Filial.objects.update_or_create(kod=kod, defaults=dict(nom=nom, manzil=manzil, tel=tel, tg=tg))
        for nom, tavsif, narx in KURSLAR:
            Kurs.objects.update_or_create(nom=nom, defaults=dict(tavsif=tavsif, narx=narx))
        for ism, ball, tg in USTOZLAR:
            Ustoz.objects.update_or_create(ism=ism, defaults=dict(ball=ball, tg=tg))
        self.stdout.write(self.style.SUCCESS('Filiallar, kurslar, ustozlar tayyor.'))

        if not demo:
            return
        g, _ = Guruh.objects.get_or_create(
            nom='IELTS-18', defaults=dict(kurs=Kurs.objects.get(nom='IELTS'), filial=Filial.objects.get(kod='chilonzor'),
                                          ustoz=Ustoz.objects.get(ism='Otabek Akramov'), vaqt='18:00–20:00', xona='7-12'))
        o, yangi = Oquvchi.objects.get_or_create(login='demo', defaults=dict(ism="Demo O'quvchi", tel='+998 90 000 00 00', guruh=g))
        o.parol_qoy('demo123')
        o.save()
        if yangi:
            bugun = date.today()
            for i in range(14):
                Davomat.objects.get_or_create(oquvchi=o, sana=bugun - timedelta(days=i), defaults={'keldi': i % 6 != 3})
            Natija.objects.create(oquvchi=o, sana=bugun - timedelta(days=20), listening=6.5, reading=6.0,
                                  writing=5.5, speaking=6.0, umumiy='6.0')
            Natija.objects.create(oquvchi=o, sana=bugun - timedelta(days=3), listening=7.5, reading=7.0,
                                  writing=6.0, speaking=6.5, umumiy='7.0', izoh='Writing Task 2 ustida ishlash kerak')
            oy = bugun.replace(day=1)
            Tolov.objects.create(oquvchi=o, oy=(oy - timedelta(days=1)).replace(day=1), summa=750000, tolandi=True,
                                 sana=(oy - timedelta(days=25)))
            Tolov.objects.create(oquvchi=o, oy=oy, summa=750000, tolandi=False)
        self.stdout.write(self.style.SUCCESS("Demo o'quvchi: login demo, parol demo123"))
