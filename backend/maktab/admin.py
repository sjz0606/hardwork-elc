import secrets

from django import forms
from django.contrib import admin, messages

from .models import Ariza, Davomat, Filial, Guruh, Kurs, Natija, Oquvchi, Tolov, Ustoz


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


class OquvchiInline(admin.TabularInline):
    model = Oquvchi
    fields = ('ism', 'login', 'tel', 'faol')
    readonly_fields = ('ism', 'login', 'tel', 'faol')
    extra = 0
    can_delete = False
    show_change_link = True


@admin.register(Guruh)
class GuruhAdmin(admin.ModelAdmin):
    list_display = ('nom', 'kurs', 'filial', 'ustoz', 'vaqt', 'kunlar')
    list_filter = ('filial', 'kurs', 'ustoz')
    inlines = [OquvchiInline]


class OquvchiForma(forms.ModelForm):
    yangi_parol = forms.CharField(
        label='Yangi parol', required=False, min_length=4,
        widget=forms.PasswordInput(render_value=False),
        help_text="Bo'sh qoldirsangiz: yangi o'quvchiga avtomatik parol yaratiladi, mavjudiniki o'zgarmaydi.")

    class Meta:
        model = Oquvchi
        fields = '__all__'


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
    search_fields = ('ism', 'login', 'tel', 'telegram_username')
    readonly_fields = ('telegram_id', 'telegram_username')
    inlines = [TolovInline, NatijaInline]
    actions = ['parol_yangila', 'botdan_uzish']

    @admin.display(boolean=True, description='Botga kirgan')
    def botda(self, obj):
        return obj.telegram_id is not None

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
        n = queryset.update(telegram_id=None, telegram_username='')
        messages.success(request, f'{n} ta o\'quvchi botdan uzildi.')


@admin.register(Tolov)
class TolovAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'oy', 'summa', 'tolandi', 'sana')
    list_filter = ('tolandi', 'oquvchi__guruh__filial')
    search_fields = ('oquvchi__ism', 'oquvchi__login')
    autocomplete_fields = ('oquvchi',)


@admin.register(Davomat)
class DavomatAdmin(admin.ModelAdmin):
    list_display = ('oquvchi', 'sana', 'keldi')
    list_filter = ('keldi', 'sana', 'oquvchi__guruh')
    autocomplete_fields = ('oquvchi',)


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
