from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class Filial(models.Model):
    kod = models.SlugField('Kod', unique=True, help_text='Saytdagi qiymat: chilonzor, beruniy, chorsu')
    nom = models.CharField('Nomi', max_length=80)
    manzil = models.CharField('Manzil', max_length=255, blank=True)
    tel = models.CharField('Telefon', max_length=30, blank=True)
    tg = models.CharField('Telegram admin', max_length=64, blank=True, help_text='@ belgisiz')
    admin_chat_id = models.BigIntegerField('Admin chat ID', null=True, blank=True,
                                           help_text='Shu filial arizalari yuboriladigan Telegram chat')

    class Meta:
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiallar'

    def __str__(self):
        return self.nom


class Kurs(models.Model):
    nom = models.CharField('Nomi', max_length=80, unique=True)
    tavsif = models.CharField('Tavsif', max_length=120, blank=True)
    narx = models.PositiveIntegerField("Narx (so'm/oy)", default=0)

    class Meta:
        verbose_name = 'Kurs'
        verbose_name_plural = 'Kurslar'

    def __str__(self):
        return self.nom


class Ustoz(models.Model):
    ism = models.CharField('F.I.Sh.', max_length=120)
    ball = models.CharField('IELTS ball', max_length=10, blank=True)
    tg = models.CharField('Telegram', max_length=64, blank=True)

    class Meta:
        verbose_name = 'Ustoz'
        verbose_name_plural = 'Ustozlar'

    def __str__(self):
        return self.ism


class Guruh(models.Model):
    nom = models.CharField('Guruh nomi', max_length=80)
    kurs = models.ForeignKey(Kurs, on_delete=models.PROTECT, verbose_name='Kurs')
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT, verbose_name='Filial')
    ustoz = models.ForeignKey(Ustoz, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ustoz')
    vaqt = models.CharField('Dars vaqti', max_length=20, help_text='Masalan: 18:00–20:00')
    kunlar = models.CharField('Kunlar', max_length=60, default='Har kuni (7 kun)')
    xona = models.CharField('Xona', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'

    def __str__(self):
        return f'{self.nom} · {self.filial}'


class Oquvchi(models.Model):
    ism = models.CharField('F.I.Sh.', max_length=120)
    tel = models.CharField('Telefon', max_length=30, blank=True)
    login = models.CharField('Login', max_length=40, unique=True)
    parol = models.CharField('Parol (hash)', max_length=128, editable=False)
    guruh = models.ForeignKey(Guruh, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='oquvchilar', verbose_name='Guruh')
    faol = models.BooleanField('Faol', default=True)
    telegram_id = models.BigIntegerField('Telegram ID', null=True, blank=True, unique=True)
    telegram_username = models.CharField('Telegram username', max_length=64, blank=True)
    qoshilgan = models.DateField("Qo'shilgan sana", default=timezone.localdate)

    class Meta:
        verbose_name = "O'quvchi"
        verbose_name_plural = "O'quvchilar"

    def __str__(self):
        return f'{self.ism} ({self.login})'

    def parol_qoy(self, xom):
        self.parol = make_password(xom)

    def parol_tekshir(self, xom):
        return bool(self.parol) and check_password(xom, self.parol)


class Tolov(models.Model):
    oquvchi = models.ForeignKey(Oquvchi, on_delete=models.CASCADE, related_name='tolovlar', verbose_name="O'quvchi")
    oy = models.DateField('Oy', help_text='Oyning istalgan kuni')
    summa = models.PositiveIntegerField("Summa (so'm)")
    tolandi = models.BooleanField("To'landi", default=False)
    sana = models.DateField("To'langan sana", null=True, blank=True)

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-oy']

    def __str__(self):
        return f'{self.oquvchi.ism} — {self.oy:%m.%Y}'


class Davomat(models.Model):
    oquvchi = models.ForeignKey(Oquvchi, on_delete=models.CASCADE, related_name='davomatlar', verbose_name="O'quvchi")
    sana = models.DateField('Sana', default=timezone.localdate)
    keldi = models.BooleanField('Keldi', default=True)

    class Meta:
        verbose_name = 'Davomat'
        verbose_name_plural = 'Davomat'
        ordering = ['-sana']
        unique_together = ('oquvchi', 'sana')

    def __str__(self):
        return f'{self.oquvchi.ism} — {self.sana}'


class Natija(models.Model):
    TURLAR = [('mock', 'Mock IELTS'), ('ielts', 'Rasmiy IELTS'), ('cefr', 'CEFR'), ('test', 'Ichki test')]
    oquvchi = models.ForeignKey(Oquvchi, on_delete=models.CASCADE, related_name='natijalar', verbose_name="O'quvchi")
    turi = models.CharField('Turi', max_length=10, choices=TURLAR, default='mock')
    sana = models.DateField('Sana', default=timezone.localdate)
    listening = models.DecimalField('Listening', max_digits=3, decimal_places=1, null=True, blank=True)
    reading = models.DecimalField('Reading', max_digits=3, decimal_places=1, null=True, blank=True)
    writing = models.DecimalField('Writing', max_digits=3, decimal_places=1, null=True, blank=True)
    speaking = models.DecimalField('Speaking', max_digits=3, decimal_places=1, null=True, blank=True)
    umumiy = models.CharField('Umumiy (band / daraja)', max_length=10)
    izoh = models.CharField('Izoh', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Natija'
        verbose_name_plural = 'Natijalar'
        ordering = ['-sana']

    def __str__(self):
        return f'{self.oquvchi.ism} — {self.umumiy}'


class Ariza(models.Model):
    HOLATLAR = [('yangi', 'Yangi'), ('boglanildi', "Bog'lanildi"), ('yozildi', 'Guruhga yozildi'), ('rad', 'Rad / javobsiz')]
    MANBALAR = [('sayt', 'Sayt'), ('bot', 'Telegram bot')]
    ism = models.CharField('Ism', max_length=120)
    tel = models.CharField('Telefon', max_length=30)
    kurs = models.CharField('Kurs', max_length=80, blank=True)
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Filial')
    vaqt = models.CharField('Qulay vaqt', max_length=20, blank=True)
    daraja = models.CharField('Test darajasi', max_length=60, blank=True)
    manba = models.CharField('Manba', max_length=10, choices=MANBALAR, default='sayt')
    telegram_id = models.BigIntegerField('Telegram ID', null=True, blank=True)
    holat = models.CharField('Holat', max_length=12, choices=HOLATLAR, default='yangi')
    yaratildi = models.DateTimeField('Yaratildi', auto_now_add=True)

    class Meta:
        verbose_name = 'Ariza'
        verbose_name_plural = 'Arizalar'
        ordering = ['-yaratildi']

    def __str__(self):
        return f'{self.ism} · {self.tel}'
