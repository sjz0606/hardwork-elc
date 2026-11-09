"""Statik saytni (repo ildizidagi index.html, css/, js/, vendor/, media/) shu Django ilova orqali beradi.

Faqat ro'yxatdagi papka/fayllar qo'shiladi — backend/ (.env, db.sqlite3) hech qachon internetga chiqmaydi.
"""
from pathlib import Path

from django.conf import settings
from whitenoise.middleware import WhiteNoiseMiddleware

SAYT_PAPKALAR = ('css', 'js', 'vendor', 'media')
SAYT_FAYLLAR = ('index.html',)


class SaytMiddleware(WhiteNoiseMiddleware):
    def __init__(self, get_response=None, settings_=None):
        super().__init__(get_response)
        ildiz = Path(settings.SAYT_ILDIZ)
        for p in SAYT_PAPKALAR:
            if (ildiz / p).is_dir():
                self.add_files(str(ildiz / p), prefix=f'{p}/')
        for f in SAYT_FAYLLAR:
            if (ildiz / f).is_file():
                # index_file=True bo'lgani uchun /index.html "/" manzilida ham beriladi
                self.add_file_to_dictionary(f'/{f}', str(ildiz / f))
