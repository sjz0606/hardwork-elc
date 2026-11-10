from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from maktab import miniapp, views

admin.site.site_header = 'HardWork ELC — boshqaruv'
admin.site.site_title = 'HardWork admin'
admin.site.index_title = 'Markaz ma\'lumotlari'

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/ariza/', views.ariza_qabul, name='ariza'),
    path('api/salomatlik/', views.salomatlik),
    path('bot/<str:maxfiy>/', views.bot_webhook),
    # Telegram Mini App — jurnal va hisobot
    path('app/', miniapp.sahifa, name='miniapp'),
    path('app/api/men', miniapp.men),
    path('app/api/darslar', miniapp.darslar),
    path('app/api/jurnal/<int:guruh_id>', miniapp.jurnal),
    path('app/api/hisobot', miniapp.hisobot),
    path('app/api/xodimlar', miniapp.xodimlar),
    path('app/api/mening', miniapp.mening_jurnalim),
]
