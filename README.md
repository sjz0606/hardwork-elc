# HardWork ELC — demo sayt (v2)

Sotuv demosi: **HardWork English Learning Centre** (Toshkent). Haqiqiy sayti yo'q — faqat Telegram kanal @HardWorkELC (2 000+ obunachi).

## Ishga tushirish
```
python -m http.server 8078
```
→ http://localhost:8078 (build yo'q, statik — istalgan hostingga yuklanadi)

## v2 (2026-10-31): brend, videolar, 3 filial
- Logo: YouTube kanal avatari (media/logo.png, logo-96.png, apple-touch-icon.png)
- Brend ranglari Instagram postlaridan: ko'k #2f6bff + neon-yashil #b8ff2c + logo binafshasi
- Natija videolari: Instagram @hardwork_elc reels (yt-dlp), media/natija/ — to'liq (540x960, ovozli) + _q preview (6 s, ovozsiz) + jpg poster
  DOD6uQsjCZD Hadicha 8.0 · DJEjGJhitzo E'zoza 7.5 · DI2_SooCygq Ra'noxon 7.5 · C7V2L1NNUGY 14 yoshda 7.5 · DTVKir_DHi- Kimyoxon 7.5 · DT0hpbqDMrV Dilafruz 7.0
  Xom fayllar media/xom/ (gitignore)
- Narxlar (Instagram, ~2026-10-24): IELTS 750 000, General English 650 000, CEFR 670 000 so'm/oy; haftada 7 kun ~2 soat; co-working zona
- Filiallar: Chilonzor (99) 887-40-03 @hardwork_integro, IG @hardwork_elc · Beruniy (94) 101-92-42 @hardwork_beruniy, IG @hardwork_beruniy ·
  Chorsu (77) 362-40-03 @hardwork_chorsu, IG @hardwork_chorsu (Alisher Navoiy 44, Turkuaz ro'parasi, 3-qavat)
- Ustozlar (Instagram postlaridan): Jasurbek Karimov (asoschi, 8.0), Temurbek Akbaraliyev (8.5, 8 yil), Otabek Akramov (8.5), Ilhomjon Ne'matullayev
- ESLATMA: videolar va o'quvchi ismlari markazniki — saytni ommaga chiqarishdan oldin markaz roziligi kerak.
  G'ofur G'ulom (90) 063-40-03 eski postlarda bor, hozirgi bio'da yo'q — saytga qo'yilmadi.

## Ma'lumot manbalari (2026-10-31, v1)
- Google Maps: Bunyodkor shoh ko'chasi 52 (Integro FEC), ★4.1 (10), +998 91 180 19 99
- Telegram kanal t.me/s/HardWorkELC: filiallar, telefonlar, dars vaqtlari (9:30, 14:00, 16:00, 18:00, 20:00),
  3 ta bepul sinov darsi, natijalar (Dilnura 7.0 — L7.5/R7/W7/S7; Sevinch 6.0→7.0 — L8/R6.5/W6/S6.5;
  Mohlaroy 7.0; Shirinkhon 7.0; CEFR C1), ustozlar (Otabek Akramov @otabekakramovs, Ilhomjon @nematullive_me)
- Golden Pages: Chilonzor filiali har kuni 09:00–22:00

## Markaz bilan aniqlashtirish kerak
- Ilhomjonning familiyasi (kanalda "Ne’mayullayev" deb yozilgan, saytda "Ne'matullayev")
- Beruniy filialining aniq manzili/koordinatasi va ish vaqti (xarita hozir "Belissimo, Beruniy metro" qidiruvi bilan)
- Kanal tavsifidagi uchinchi raqam "Ganga" — 90 063 40 03 (saytga qo'shilmadi)
- Kurs narxlari, ustozlar rasmlari, logotip (hozir "HW" belgisi)
- O'quvchilar ismlari va natijalarini saytda ko'rsatishga ruxsat
- Forma: `js/ilova.js` dagi `FORMA_MANZIL` bo'sh → arizalar brauzerda saqlanadi, foydalanuvchiga filial Telegram admini ko'rsatiladi

## Tuzilishi
- `js/sahna.js` — three.js zarrachalar: HARD WORK → 7.0 → globus → C1 (aylantirish bilan)
- `js/ilova.js` — kursor, parallaks chiplar, magnit tugmalar, 3D kartalar, ball ustunlari, vaqt tanlash, filial tablari, test, forma
- AI rasm/video yo'q (Higgsfield krediti tugagan) — vizual to'liq kodda
