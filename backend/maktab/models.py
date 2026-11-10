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
    vaqt = models.CharField('Dars vaqti (matn)', max_length=20, blank=True,
                            help_text="Bo'sh qoldirilsa smena soatlaridan olinadi")
    kunlar = models.CharField('Kunlar (matn)', max_length=60, default='Har kuni (7 kun)')
    xona = models.CharField('Xona', max_length=30, blank=True)
    # Jurnal uchun jadval: smena va hafta kunlari
    boshlanish = models.TimeField('Smena boshlanishi', null=True, blank=True, help_text='Masalan 18:00')
    tugash = models.TimeField('Smena tugashi', null=True, blank=True, help_text='Masalan 20:00')
    hafta_kunlari = models.CharField(
        'Dars kunlari', max_length=7, default='1234567',
        help_text='Raqamlar: 1=Dush, 2=Sesh, 3=Chor, 4=Pay, 5=Juma, 6=Shan, 7=Yak. Masalan: 135 yoki 1234567')
    faol = models.BooleanField('Faol', default=True)

    class Meta:
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'
        ordering = ['boshlanish', 'nom']

    def __str__(self):
        return f'{self.nom} · {self.filial}'

    @property
    def smena(self):
        if self.boshlanish:
            t = f'{self.boshlanish:%H:%M}'
            return t + (f'–{self.tugash:%H:%M}' if self.tugash else '')
        return self.vaqt

    def dars_bormi(self, sana):
        return self.faol and str(sana.isoweekday()) in (self.hafta_kunlari or '')


class Xodim(models.Model):
    """Markaz xodimi (ustoz / direktor) — botga va mini ilovaga login bilan kiradi."""
    ism = models.CharField('F.I.Sh.', max_length=120)
    tel = models.CharField('Telefon', max_length=30, blank=True)
    login = models.CharField('Login', max_length=40, unique=True)
    parol = models.CharField('Parol (hash)', max_length=128, editable=False)
    direktor = models.BooleanField('Direktor', default=False,
                                   help_text="Barcha filial, xodim, guruh va hisobotlarni ko'radi")
    ustoz = models.OneToOneField(Ustoz, on_delete=models.SET_NULL, null=True, blank=True, related_name='xodim',
                                 verbose_name='Ustoz profili',
                                 help_text="Dars beradigan bo'lsa — shu ustozning guruhlari jurnalida ishlaydi")
    ariza_oladi = models.BooleanField(
        'Arizalarni oladi', default=True,
        help_text="Yangi arizalar (saytdan/botdan) botga login qilgan xodimga yuboriladi. Olib tashlasangiz — kelmaydi "
                  "(direktorlarga doim boradi)")
    ariza_filiallar = models.ManyToManyField(
        Filial, blank=True, related_name='ariza_oluvchilar', verbose_name='Qaysi filial arizalari',
        help_text="Bo'sh qoldirilsa — barcha filiallar arizalari keladi")
    faol = models.BooleanField('Faol', default=True)
    telegram_id = models.BigIntegerField('Telegram ID', null=True, blank=True, unique=True)
    telegram_username = models.CharField('Telegram username', max_length=64, blank=True)

    class Meta:
        verbose_name = 'Xodim (ustoz/direktor)'
        verbose_name_plural = 'Xodimlar (ustoz/direktor)'

    def __str__(self):
        return f'{self.ism} ({self.login})'

    def parol_qoy(self, xom):
        self.parol = make_password(xom)

    def parol_tekshir(self, xom):
        return bool(self.parol) and check_password(xom, self.parol)

    @property
    def rol(self):
        if self.direktor:
            return 'direktor' + ('+ustoz' if self.ustoz_id else '')
        return 'ustoz' if self.ustoz_id else 'xodim'

    def guruhlar(self):
        qs = Guruh.objects.select_related('kurs', 'filial', 'ustoz')
        if self.direktor:
            return qs
        if self.ustoz_id:
            return qs.filter(ustoz_id=self.ustoz_id)
        return qs.none()

    def guruhga_ruxsat(self, guruh):
        return self.direktor or (self.ustoz_id is not None and guruh.ustoz_id == self.ustoz_id)


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
    """Jurnal qatori: o'quvchining shu kungi davomati, bahosi va izohi."""
    HOLATLAR = [('keldi', 'Keldi'), ('kechikdi', 'Kechikdi'), ('sababli', 'Sababli'), ('kelmadi', 'Kelmadi')]
    oquvchi = models.ForeignKey(Oquvchi, on_delete=models.CASCADE, related_name='davomatlar', verbose_name="O'quvchi")
    guruh = models.ForeignKey(Guruh, on_delete=models.SET_NULL, null=True, blank=True, related_name='davomatlar',
                              verbose_name='Guruh')
    sana = models.DateField('Sana', default=timezone.localdate)
    holat = models.CharField('Holat', max_length=10, choices=HOLATLAR, default='keldi')
    keldi = models.BooleanField('Keldi', default=True, editable=False)
    baho = models.PositiveSmallIntegerField('Baho (1–10)', null=True, blank=True)
    izoh = models.CharField('Izoh', max_length=200, blank=True)
    belgiladi = models.ForeignKey('Xodim', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Belgiladi')
    yangilandi = models.DateTimeField('Yangilandi', auto_now=True, null=True)

    class Meta:
        verbose_name = 'Davomat (jurnal)'
        verbose_name_plural = 'Davomat (jurnal)'
        ordering = ['-sana']
        unique_together = ('oquvchi', 'sana')

    def __str__(self):
        return f'{self.oquvchi.ism} — {self.sana}'

    def save(self, *args, **kwargs):
        self.keldi = self.holat in ('keldi', 'kechikdi')
        super().save(*args, **kwargs)


class Dars(models.Model):
    """Guruhning shu kungi darsi: mavzu va uy vazifasi (jurnal sarlavhasi)."""
    guruh = models.ForeignKey(Guruh, on_delete=models.CASCADE, related_name='darslar', verbose_name='Guruh')
    sana = models.DateField('Sana', default=timezone.localdate)
    mavzu = models.CharField('Mavzu', max_length=200, blank=True)
    uy_vazifa = models.CharField('Uy vazifasi', max_length=300, blank=True)
    xodim = models.ForeignKey(Xodim, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="To'ldirdi")
    yangilandi = models.DateTimeField('Yangilandi', auto_now=True)

    class Meta:
        verbose_name = 'Dars (jurnal)'
        verbose_name_plural = 'Darslar (jurnal)'
        ordering = ['-sana']
        unique_together = ('guruh', 'sana')

    def __str__(self):
        return f'{self.guruh.nom} — {self.sana}'


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
