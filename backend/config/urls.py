from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from maktab import views

admin.site.site_header = 'HardWork ELC — boshqaruv'
admin.site.site_title = 'HardWork admin'
admin.site.index_title = 'Markaz ma\'lumotlari'

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/ariza/', views.ariza_qabul, name='ariza'),
    path('api/salomatlik/', views.salomatlik),
    path('bot/<str:maxfiy>/', views.bot_webhook),
]
