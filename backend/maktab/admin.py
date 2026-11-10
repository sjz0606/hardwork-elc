import secrets

from django import forms
from django.contrib import admin, messages

from .models import Ariza, BotKirish, Dars, Davomat, Filial, Guruh, Kurs, Natija, Oquvchi, Tolov, Ustoz, Xodim


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('nom', 'kod', 'tel', 'tg', 'admin_chat_id')
    prepopulated_fields = {'kod': ('nom',)}


@admin.register(Kurs)
class KursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tavsif', 'narx')
    list_editable = ('narx',)


@admin.register(Ustoz)
class UstozAdmin(admin.ModelAdmin):
    list_display = ('ism', 'ball', 'tg')


class BotKirishInline(admin.TabularInline):
    model = BotKirish
    fields = ('telegram_id', 'username', 'yaratildi')
    readonly_fields = fields
    extra = 0
    verbose_name_plural = 'Botga shu login bilan kirgan Telegram akkauntlar'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BotKirish)
class BotKirishAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'xodim', 'oquvchi', 'yaratildi')
    search_fields = ('username', 'telegram_id', 'xodim__login', 'oquvchi__login')
    readonly_fields = ('telegram_id', 'username', 'xodim', 'oquvchi', 'yaratildi')

    def has_add_permission(self, request):
        return False


class OquvchiInline(admin.TabularInline):
    model = Oquvchi
    fields = ('ism', 'login', 'tel', 'faol')
    readonly_fields = ('ism', 'login', 'tel', 'faol')
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Guruh)
class GuruhAdmin(admin.ModelAdmin):
    list_display = ('nom', 'kurs', 'filial', 'ustoz', 'smena', 'hafta_kunlari', 'faol')
    list_filter = ('faol', 'filial', 'kurs', 'ustoz')
    search_fields = ('nom',)
    fieldsets = (
        (None, {'fields': ('nom', 'kurs', 'filial', 'ustoz', 'faol')}),
        ("Jadval (jurnal shu bo'yicha ishlaydi)", {'fields': ('boshlanish', 'tugash', 'hafta_kunlari', 'xona')}),
        ("Saytda ko'rinadigan matn (ixtiyoriy)", {'fields': ('vaqt', 'kunlar'), 'classes': ('collapse',)}),
    )
    inlines = [OquvchiInline]


def _login_band(login, model, pk):
    """Login o'quvchilar va xodimlar orasida yagona bo'lishi kerak (bot ikkalasini bir joyda tekshiradi)."""
    for m in (Oquvchi, Xodim):
        qs = m.objects.filter(login__iexact=login)
        if m is model and pk:
            qs = qs.exclude(pk=pk)
        if qs.exists():
            return True
    return False


class XodimForma(forms.ModelForm):
    yangi_parol = forms.CharField(
        label='Yangi parol', required=False, min_length=4,
        widget=forms.PasswordInput(render_value=False),
        help_text="Bo'sh qoldirsangiz: yangi xodimga avtomatik parol yaratiladi, mavjudiniki o'zgarmaydi.")

    class Meta:
        model = Xodim
        fields = '__all__'

    def clean_login(self):
        login = self.cleaned_data['login'].strip()
        if _login_band(login, Xodim, self.instance.pk):
            raise forms.ValidationError("Bu login band (o'quvchi yoki xodimda bor).")
        return login


@admin.register(Xodim)
class XodimAdmin(admin.ModelAdmin):
    form = XodimForma
    list_display = ('ism', 'login', 'direktor', 'ustoz', 'ariza_oladi', 'faol', 'botda')
    list_filter = ('direktor', 'ariza_oladi', 'faol')
    filter_horizontal = ('ariza_filiallar',)
    inlines = [BotKirishInline]
    search_fields = ('ism', 'login', 'tel')
    actions = ['parol_yangila', 'botdan_uzish']

    @admin.display(boolean=True, description='Botga kirgan')
    def botda(self, obj):
        return obj.bot_kirishlar.exists()

    def save_model(self, request, obj, form, change):
        xom = form.cleaned_data.get('yangi_parol')
        if not xom and not obj.parol:
            xom = secrets.token_hex(3)
        if xom:
            obj.parol_qoy(xom)
            messages.success(request, f'{obj.ism}: login «{obj.login}», parol «{xom}». Xodimga yetkazing.')
        super().save_model(request, obj, form, change)

    @admin.action(description='Tanlanganlarga yangi parol yaratish')
    def parol_yangila(self, request, queryset):
        qatorlar = []
        for o in queryset:
            xom = secrets.token_hex(3)
            o.parol_qoy(xom)
            o.save(update_fields=['parol'])
            qatorlar.append(f'{o.login}: {xom}')
        messages.success(request, 'Yangi parollar — ' + '; '.join(qatorlar))

    @admin.action(description='Telegram akkauntdan uzish')
    def botdan_uzish(self, request, queryset):
        n, _ = BotKirish.objects.filter(xodim__in=queryset).delete()
        messages.success(request, f'{n} ta Telegram akkaunt botdan uzildi.')


class OquvchiForma(forms.ModelForm):
    yangi_parol = forms.CharField(
        label='Yangi parol', required=False, min_length=4,
        widget=forms.PasswordInput(render_value=False),
        help_text="Bo'sh qoldirsangiz: yangi o'quvchiga avtomatik parol yaratiladi, mavjudiniki o'zgarmaydi.")

    class Meta:
        model = Oquvchi
        fields = '__all__'

    def clean_login(self):
        login = self.cleaned_data['login'].strip()
        if _login_band(login, Oquvchi, self.instance.pk):
            raise forms.ValidationError("Bu login band (o'quvchi yoki xodimda bor).")
        return login


class TolovInline(admin.TabularInline):
    model = Tolov
    extra = 0


class NatijaInline(admin.TabularInline):
    model = Natija
    extra = 0


@admin.register(Oquvchi)
class OquvchiAdmin(admin.ModelAdmin):
    form = OquvchiForma
    list_display = ('ism', 'login', 'guruh', 'tel', 'faol', 'botda')
    list_filter = ('faol', 'guruh__filial', 'guruh')
    search_fields = ('ism', 'login', 'tel', 'bot_kirishlar__username')
    inlines = [TolovInline, NatijaInline, BotKirishInline]
    actions = ['parol_yangila', 'botdan_uzish']

    @admin.display(boolean=True, description='Botga kirgan')
    def botda(self, obj):
        return obj.bot_kirishlar.exists()

    def save_model(self, request, obj, form, change):
        xom = form.cleaned_data.get('yangi_parol')
        if not xom and not obj.parol:
            xom = secrets.token_hex(3)  # 6 belgili parol
        if xom:
            obj.parol_qoy(xom)
            messages.success(request, f'{obj.ism}: login «{obj.login}», parol «{xom}». O\'quvchiga yetkazing.')
        super().save_model(request, obj, form, change)

    @admin.action(description='Tanlanganlarga yangi parol yaratish')
    def parol_yangila(self, request, queryset):
        qatorlar = []
        for o in queryset:
            xom = secrets.token_hex(3)
            o.parol_qoy(xom)
            o.save(update_fields=['parol'])
            qatorlar.append(f'{o.login}: {xom}')
        messages.success(request, 'Yangi parollar — ' + '; '.join(qatorlar))

    @admin.action(description='Telegram akkauntdan uzish')
    def botdan_uzish(self, request, queryset):
        n, _ = BotKirish.objects.filter(oquvchi__in=queryset).delete()
        messages.success(request, f'{n} ta Telegram akkaunt botdan uzildi.')


@admin.register(Tolov)
class TolovAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'oy', 'summa', 'tolandi', 'sana')
    list_filter = ('tolandi', 'oquvchi__guruh__filial')
    search_fields = ('oquvchi__ism', 'oquvchi__login')
    autocomplete_fields = ('oquvchi',)


@admin.register(Davomat)
class DavomatAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'guruh', 'sana', 'holat', 'baho', 'izoh', 'belgiladi')
    list_filter = ('holat', 'sana', 'guruh__filial', 'guruh')
    search_fields = ('oquvchi__ism', 'oquvchi__login')
    autocomplete_fields = ('oquvchi',)
    date_hierarchy = 'sana'


@admin.register(Dars)
class DarsAdmin(admin.ModelAdmin):
    list_display = ('guruh', 'sana', 'mavzu', 'uy_vazifa', 'xodim')
    list_filter = ('guruh__filial', 'guruh')
    search_fields = ('guruh__nom', 'mavzu')
    date_hierarchy = 'sana'


@admin.register(Natija)
class NatijaAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'turi', 'sana', 'listening', 'reading', 'writing', 'speaking', 'umumiy')
    list_filter = ('turi',)
    autocomplete_fields = ('oquvchi',)


@admin.register(Ariza)
class ArizaAdmin(admin.ModelAdmin):
    list_display = ('ism', 'tel', 'kurs', 'filial', 'vaqt', 'manba', 'holat', 'yaratildi')
    list_filter = ('holat', 'manba', 'filial', 'kurs')
    list_editable = ('holat',)
    search_fields = ('ism', 'tel')
