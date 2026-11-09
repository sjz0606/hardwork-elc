// HardWork — sahifa interaktivligi
(function () {
  // Arizalar manzili: Django backend (hardwork.osonhujjat.uz). Lokal sinovda — runserver (127.0.0.1:8000).
  var FORMA_MANZIL = location.hostname === 'hardwork.osonhujjat.uz' || location.port === '8000'
    ? '/api/ariza/'                                   // sayt backend bilan bir joyda
    : /^(localhost|127\.0\.0\.1)$/.test(location.hostname)
      ? 'http://127.0.0.1:8000/api/ariza/'
      : 'https://hardwork.osonhujjat.uz/api/ariza/';  // GitHub Pages nusxasi

  var kamHarakat = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sichqonli = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var gs = window.gsap && !kamHarakat;

  // ---------- Ma'lumotlar ----------
  var FILIALLAR = {
    chilonzor: {
      nom: 'Chilonzor', manzil: 'Bunyodkor shoh ko\'chasi 52, Integro binosi, 7–8-qavat', mo: 'Chilonzor metro',
      tel: '(99) 887-40-03', telHref: '+998998874003', tg: 'hardwork_integro', ig: 'hardwork_elc',
      xarita: 'https://maps.google.com/maps?q=41.2764056,69.2050986&z=16&output=embed',
      yol: 'https://www.google.com/maps/dir/?api=1&destination=41.2764056,69.2050986'
    },
    beruniy: {
      nom: 'Beruniy', manzil: '“Belissimo” binosi, 2-qavat', mo: 'Beruniy metro',
      tel: '(94) 101-92-42', telHref: '+998941019242', tg: 'hardwork_beruniy', ig: 'hardwork_beruniy',
      xarita: 'https://maps.google.com/maps?q=' + encodeURIComponent('Belissimo, Beruniy, Tashkent') + '&z=16&output=embed',
      yol: 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent('Belissimo Beruniy Tashkent')
    },
    chorsu: {
      nom: 'Chorsu', manzil: 'Alisher Navoiy ko\'chasi 44 — “Turkuaz” savdo majmuasi ro\'parasidagi bino, 3-qavat', mo: 'Chorsu metro',
      tel: '(77) 362-40-03', telHref: '+998773624003', tg: 'hardwork_chorsu', ig: 'hardwork_chorsu',
      xarita: 'https://maps.google.com/maps?q=' + encodeURIComponent('Alisher Navoiy 44, Tashkent') + '&z=16&output=embed',
      yol: 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent('Alisher Navoiy 44, Tashkent')
    }
  };
  var VIDEOLAR = {
    DOD6uQsjCZD: { ism: 'Hadicha', ball: '8.0' },
    DJEjGJhitzo: { ism: 'E\'zoza · 2011-yilda tug\'ilgan', ball: '7.5' },
    DI2_SooCygq: { ism: 'Ra\'noxon · 15 yoshda', ball: '7.5' },
    C7V2L1NNUGY: { ism: '14 yoshda', ball: '7.5' },
    'DTVKir_DHi-': { ism: 'Kimyoxon', ball: '7.5' },
    DT0hpbqDMrV: { ism: 'Dilafruz', ball: '7.0' }
  };
  var VIDEO_TARTIB = Object.keys(VIDEOLAR);
  var IKON = {
    ig: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/></svg>',
    tg: '<svg viewBox="0 0 24 24"><path d="M21 4 3 11l6 2 2 6 3-4 5 4z"/><path d="m9 13 12-9"/></svg>',
    tel: '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'
  };
  function havolalar(f) {
    return '<div class="havolalar">' +
      '<a class="havola havola--tel" href="tel:' + f.telHref + '">' + IKON.tel + f.tel + '</a>' +
      '<a class="havola havola--tg" href="https://t.me/' + f.tg + '" target="_blank" rel="noopener">' + IKON.tg + '@' + f.tg + '</a>' +
      '<a class="havola havola--ig" href="https://www.instagram.com/' + f.ig + '/" target="_blank" rel="noopener">' + IKON.ig + '@' + f.ig + '</a></div>';
  }

  // ---------- Lenta ----------
  var lenta = document.querySelector('.lenta__ichi');
  lenta.innerHTML += lenta.innerHTML;

  // ---------- Nav ----------
  var nav = document.getElementById('nav');
  addEventListener('scroll', function () { nav.classList.toggle('qotgan', scrollY > 30); }, { passive: true });
  document.getElementById('burger').addEventListener('click', function () { nav.classList.toggle('ochiq'); });
  nav.querySelectorAll('.nav__havola a').forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('ochiq'); }); });

  // ---------- Videolar: faqat ko'rinayotganda yuklanadi va o'ynaydi ----------
  function videoYurgiz(v) {
    if (!v.src && v.dataset.src) v.src = v.dataset.src;
    var p = v.play(); if (p && p.catch) p.catch(function () {});
  }
  var videoKuz = new IntersectionObserver(function (y) {
    y.forEach(function (e) {
      var v = e.target;
      if (v.closest('.stek__karta') && v.closest('.stek__karta').dataset.o !== '0') return;
      if (e.isIntersecting) videoYurgiz(v); else v.pause();
    });
  }, { threshold: 0.25 });
  document.querySelectorAll('.reel video, .stek__karta video').forEach(function (v) { videoKuz.observe(v); });

  // ---------- 3D stek ----------
  var kartalar = [].slice.call(document.querySelectorAll('.stek__karta'));
  var nuqtalar = document.getElementById('stekNuqtalar');
  var stekJoriy = 0, stekTaymer;
  nuqtalar.innerHTML = kartalar.map(function () { return '<i></i>'; }).join('');
  function stekQoy(n) {
    stekJoriy = (n + kartalar.length) % kartalar.length;
    kartalar.forEach(function (k, i) {
      var o = (i - stekJoriy + kartalar.length) % kartalar.length;
      k.dataset.o = o;
      var v = k.querySelector('video');
      if (o === 0) videoYurgiz(v); else v.pause();
    });
    [].forEach.call(nuqtalar.children, function (d, i) { d.classList.toggle('faol', i === stekJoriy); });
  }
  function stekAvto() { clearInterval(stekTaymer); if (!kamHarakat) stekTaymer = setInterval(function () { stekQoy(stekJoriy + 1); }, 4200); }
  kartalar.forEach(function (k, i) {
    k.addEventListener('click', function () {
      if (k.dataset.o === '0') oynaOch(k.dataset.video); else { stekQoy(i); stekAvto(); }
    });
  });
  stekQoy(0); stekAvto();

  // ---------- Video oynasi (ovoz bilan) ----------
  var oyna = document.getElementById('oyna'), oynaVideo = document.getElementById('oynaVideo'), oynaMatn = document.getElementById('oynaMatn');
  var oynaJoriy = 0, oldingiFokus = null;
  function oynaOch(id) {
    oynaJoriy = VIDEO_TARTIB.indexOf(id); if (oynaJoriy < 0) oynaJoriy = 0;
    oldingiFokus = document.activeElement;
    oyna.hidden = false; document.body.style.overflow = 'hidden';
    clearInterval(stekTaymer);
    oynaYukla();
    document.getElementById('oynaYop').focus();
  }
  function oynaYukla() {
    var id = VIDEO_TARTIB[oynaJoriy], m = VIDEOLAR[id];
    oynaVideo.poster = 'media/natija/' + id + '.jpg';
    oynaVideo.src = 'media/natija/' + id + '.mp4';
    oynaMatn.innerHTML = '<b>' + m.ball + '</b><span>' + m.ism + '</span>';
    var p = oynaVideo.play(); if (p && p.catch) p.catch(function () {});
  }
  function oynaYop() {
    oynaVideo.pause(); oynaVideo.removeAttribute('src'); oynaVideo.load();
    oyna.hidden = true; document.body.style.overflow = '';
    stekAvto();
    if (oldingiFokus) oldingiFokus.focus();
  }
  function oynaSur(d) { oynaJoriy = (oynaJoriy + d + VIDEO_TARTIB.length) % VIDEO_TARTIB.length; oynaYukla(); }
  document.getElementById('oynaYop').onclick = oynaYop;
  document.getElementById('oynaOldingi').onclick = function () { oynaSur(-1); };
  document.getElementById('oynaKeyingi').onclick = function () { oynaSur(1); };
  oyna.addEventListener('click', function (e) { if (e.target === oyna) oynaYop(); });
  oynaVideo.addEventListener('ended', function () { oynaSur(1); });
  addEventListener('keydown', function (e) {
    if (oyna.hidden) return;
    if (e.key === 'Escape') oynaYop();
    if (e.key === 'ArrowRight') oynaSur(1);
    if (e.key === 'ArrowLeft') oynaSur(-1);
  });
  // mobil: suring
  var tx = null;
  oyna.addEventListener('touchstart', function (e) { tx = e.touches[0].clientX; }, { passive: true });
  oyna.addEventListener('touchend', function (e) { if (tx === null) return; var d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 60) oynaSur(d < 0 ? 1 : -1); tx = null; });
  document.querySelectorAll('.reel').forEach(function (r) { r.addEventListener('click', function () { oynaOch(r.dataset.video); }); });

  // Ko'rinish/skroll animatsiyalari — js/harakat.js

  // ---------- Ball ustunlari ----------
  var kuz = new IntersectionObserver(function (y) {
    y.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('korindi'); kuz.unobserve(e.target); } });
  }, { threshold: 0.35 });
  document.querySelectorAll('.ball').forEach(function (b) { kuz.observe(b); });

  // ---------- Kompyuter: kursor, 3D egilish, magnit tugmalar ----------
  if (sichqonli && !kamHarakat) {
    document.body.classList.add('kursor-faol');
    var kn = document.getElementById('kursor'), kh = document.getElementById('kursorHalqa');
    var mx = innerWidth / 2, my = innerHeight / 2, hx = mx, hy = my;
    addEventListener('pointermove', function (e) { mx = e.clientX; my = e.clientY; kn.style.transform = 'translate(' + mx + 'px,' + my + 'px)'; }, { passive: true });
    (function sikl() { hx += (mx - hx) * 0.18; hy += (my - hy) * 0.18; kh.style.transform = 'translate(' + hx + 'px,' + hy + 'px)'; requestAnimationFrame(sikl); })();
    var nishon = 'a, button, [data-egilish], select, input';
    document.addEventListener('pointerover', function (e) { if (e.target.closest(nishon)) kh.classList.add('ustida'); });
    document.addEventListener('pointerout', function (e) { if (e.target.closest(nishon)) kh.classList.remove('ustida'); });

    document.querySelectorAll('[data-egilish]').forEach(function (k) {
      k.addEventListener('pointermove', function (e) {
        var r = k.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        k.style.transform = 'rotateY(' + ((x - 0.5) * 10) + 'deg) rotateX(' + ((0.5 - y) * 10) + 'deg) translateZ(8px)';
        k.style.setProperty('--mx', x * 100 + '%'); k.style.setProperty('--my', y * 100 + '%');
      });
      k.addEventListener('pointerleave', function () { k.style.transform = ''; });
    });
    document.querySelectorAll('.hero .tugma, .yozilish .tugma, .nav .tugma').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.22) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.32) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
    // stek sichqonchaga qarab biroz buriladi
    var stek = document.getElementById('stek');
    stek.addEventListener('pointermove', function (e) {
      var r = stek.getBoundingClientRect();
      stek.style.transform = 'rotateY(' + (((e.clientX - r.left) / r.width - 0.5) * 8) + 'deg) rotateX(' + ((0.5 - (e.clientY - r.top) / r.height) * 6) + 'deg)';
    });
    stek.addEventListener('pointerleave', function () { stek.style.transform = ''; });
  }

  // ---------- Narx tugmalari → forma ----------
  var formaKurs = document.getElementById('formaKurs');
  document.querySelectorAll('[data-kurs]').forEach(function (b) { b.addEventListener('click', function () { formaKurs.value = b.dataset.kurs; }); });

  // ---------- Vaqt → forma ----------
  var formaVaqt = document.getElementById('formaVaqt'), vaqtIzoh = document.getElementById('vaqtIzoh');
  document.querySelectorAll('.vaqt').forEach(function (v) {
    v.setAttribute('role', 'radio'); v.setAttribute('aria-checked', 'false');
    v.addEventListener('click', function () {
      document.querySelectorAll('.vaqt').forEach(function (x) { x.classList.remove('tanlangan'); x.setAttribute('aria-checked', 'false'); });
      v.classList.add('tanlangan'); v.setAttribute('aria-checked', 'true');
      formaVaqt.value = v.dataset.vaqt;
      vaqtIzoh.innerHTML = '✓ <b>' + v.dataset.vaqt + '</b> tanlandi — <a href="#yozilish" style="color:var(--sariq);font-weight:600">yozilish formasiga o\'tish →</a>';
    });
  });

  // ---------- Filiallar ----------
  var malumot = document.getElementById('filialMalumot'), xarita = document.getElementById('filialXarita');
  var formaFilial = document.getElementById('formaFilial'), mobilTel = document.getElementById('mobilTel');
  function filialKorsat(k, formagaHam) {
    var f = FILIALLAR[k];
    document.querySelectorAll('.filial__tab').forEach(function (t) { var faol = t.dataset.filial === k; t.classList.toggle('faol', faol); t.setAttribute('aria-selected', faol); });
    malumot.innerHTML = '<dl><dt>Manzil</dt><dd>' + f.manzil + '</dd><dt>Mo\'ljal</dt><dd>Ⓜ ' + f.mo + '</dd>' +
      '<dt>Darslar</dt><dd>Haftada 7 kun</dd></dl>' + havolalar(f) +
      '<div class="tugmalar"><a class="tugma tugma--kichik" target="_blank" rel="noopener" href="' + f.yol + '">Yo\'nalish olish ↗</a>' +
      '<a class="tugma tugma--chiziq tugma--kichik" href="#yozilish">Shu filialga yozilish</a></div>';
    if (xarita.dataset.joriy !== k) { xarita.src = f.xarita; xarita.dataset.joriy = k; }
    if (formagaHam !== false) { formaFilial.value = k; formaFilialYangila(); }
  }
  document.querySelectorAll('.filial__tab').forEach(function (t) { t.addEventListener('click', function () { filialKorsat(t.dataset.filial); }); });

  // Yozilish bo'limi: tanlangan filial admini
  var yozilishTg = document.getElementById('yozilishTg');
  function formaFilialYangila() {
    var f = FILIALLAR[formaFilial.value];
    yozilishTg.innerHTML = '<p style="margin:0 0 4px;font-size:13px;color:var(--kul)">' + f.nom + ' filiali bilan to\'g\'ridan-to\'g\'ri:</p>' + havolalar(f);
    mobilTel.href = 'tel:' + f.telHref;
  }
  formaFilial.addEventListener('change', function () { filialKorsat(formaFilial.value, false); formaFilialYangila(); });
  filialKorsat('chilonzor');

  // Pastki qism: uchala filial
  document.getElementById('pastkiFiliallar').innerHTML = Object.keys(FILIALLAR).map(function (k) {
    var f = FILIALLAR[k];
    return '<div><b>Ⓜ ' + f.nom + '</b><span>' + f.manzil + '</span><a href="tel:' + f.telHref + '">' + f.tel + '</a>' +
      '<span><a href="https://t.me/' + f.tg + '" target="_blank" rel="noopener">Telegram</a> · <a href="https://www.instagram.com/' + f.ig + '/" target="_blank" rel="noopener">Instagram</a></span></div>';
  }).join('');

  // ---------- Daraja testi ----------
  var savollar = [
    { s: 'She ___ a student.', v: ['is', 'are', 'am', 'be'], t: 0 },
    { s: 'I ___ English every day.', v: ['studies', 'study', 'studying', 'studied'], t: 1 },
    { s: 'Last summer we ___ to Samarkand.', v: ['go', 'have gone', 'went', 'going'], t: 2 },
    { s: 'There aren\'t ___ chairs in the room.', v: ['some', 'any', 'much', 'a'], t: 1 },
    { s: 'If I study every day, I ___ get 7.5.', v: ['would', 'will', 'am', 'did'], t: 1 },
    { s: 'She has studied here ___ three months.', v: ['since', 'for', 'during', 'from'], t: 1 },
    { s: 'By the time we arrived, the lesson ___.', v: ['had already started', 'has started', 'starts', 'was start'], t: 0 },
    { s: 'Not only ___ the exam, but she also got 8.0 in Listening.', v: ['she passed', 'did she pass', 'she did pass', 'passed she'], t: 1 },
  ];
  var darajalar = [
    { min: 0, d: 'A1', n: 'Beginner', m: '“Nol”dan boshlaymiz — Beginner guruhi siz uchun.', k: 'Beginner (noldan)' },
    { min: 3, d: 'A2', n: 'Elementary', m: 'Poydevor bor. General English bilan har kuni o\'sasiz.', k: 'General English' },
    { min: 5, d: 'B1', n: 'Intermediate', m: 'Yaxshi! General English → IELTS yo\'li.', k: 'General English' },
    { min: 6, d: 'B2', n: 'Upper-Intermediate', m: 'IELTS 6.5–7.5 ga tayyor zamin. IELTS yoki CEFR guruhi.', k: 'IELTS' },
    { min: 8, d: 'C1', n: 'Advanced', m: 'Ajoyib! IELTS Intensive bilan 8.0 ni nishonga oling.', k: 'IELTS' },
  ];
  var ichi = document.getElementById('testIchi'), chiziq = document.getElementById('testChiziq'), joriy = 0, ball = 0;
  function jonlantir() { if (gs) gsap.from(ichi.children, { y: 22, opacity: 0, duration: 0.45, stagger: 0.05, ease: 'power2.out' }); }
  function boshlash() {
    joriy = 0; ball = 0; chiziq.style.width = '0';
    ichi.innerHTML = '<div class="natija"><div class="natija__daraja" style="font-size:72px">A1 → C1</div><h3>Darajangizni bilib oling</h3>' +
      '<p>Ro\'yxatdan o\'tmasdan, 8 ta savol. Natija darhol chiqadi.</p><div class="tugmalar"><button class="tugma" id="testBosh">Testni boshlash →</button></div></div>';
    document.getElementById('testBosh').onclick = savol;
  }
  function savol() {
    var q = savollar[joriy];
    chiziq.style.width = (joriy / savollar.length * 100) + '%';
    ichi.innerHTML = '<div class="test__raqam">Savol ' + (joriy + 1) + ' / ' + savollar.length + '</div><div class="test__savol">' +
      q.s.replace('___', '<u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u>') + '</div><div class="variantlar">' +
      q.v.map(function (v, i) { return '<button class="variant" data-i="' + i + '">' + v + '</button>'; }).join('') + '</div>';
    jonlantir();
    ichi.querySelectorAll('.variant').forEach(function (b) {
      b.onclick = function () {
        var i = +b.dataset.i;
        ichi.querySelectorAll('.variant').forEach(function (x) { x.disabled = true; });
        if (i === q.t) { ball++; b.classList.add('togri'); } else { b.classList.add('notogri'); ichi.querySelector('[data-i="' + q.t + '"]').classList.add('togri'); }
        setTimeout(function () { joriy++; joriy < savollar.length ? savol() : natija(); }, 750);
      };
    });
  }
  function natija() {
    chiziq.style.width = '100%';
    var d = darajalar[0];
    darajalar.forEach(function (x) { if (ball >= x.min) d = x; });
    document.getElementById('formaDaraja').value = d.d + ' (' + ball + '/8)';
    formaKurs.value = d.k;
    ichi.innerHTML = '<div class="natija"><div class="test__raqam">' + ball + ' / 8 to\'g\'ri</div><div class="natija__daraja">' + d.d + '</div>' +
      '<h3>' + d.n + '</h3><p>' + d.m + '</p><div class="tugmalar"><a href="#yozilish" class="tugma">' + d.k + ' — 3 ta bepul dars →</a>' +
      '<button class="tugma tugma--chiziq" id="testQayta">Qayta ishlash</button></div>' +
      '<p style="margin-top:18px;font-size:13px">Tezkor test. Aniq darajani sinov darsida ustoz aniqlaydi.</p></div>';
    document.getElementById('testQayta').onclick = boshlash;
    jonlantir();
  }
  boshlash();

  // ---------- Forma ----------
  var forma = document.getElementById('forma'), xabar = document.getElementById('formaXabar');
  forma.addEventListener('submit', function (e) {
    e.preventDefault();
    var m = Object.fromEntries(new FormData(forma));
    m.yuborildi = new Date().toISOString();
    var f = FILIALLAR[m.filial] || FILIALLAR.chilonzor;
    var tugma = forma.querySelector('button');
    tugma.disabled = true;
    function tayyor(ok) {
      tugma.disabled = false;
      xabar.style.color = ok ? '#b8ff2c' : '#d2ff74';
      xabar.innerHTML = ok
        ? 'Rahmat, ' + m.ism + '! ' + f.nom + ' filiali administratori tez orada qo\'ng\'iroq qiladi.'
        : 'Arizangiz saqlandi. Tezroq javob uchun: <a href="https://t.me/' + f.tg + '" target="_blank" rel="noopener" style="text-decoration:underline">@' + f.tg + '</a> yoki <a href="tel:' + f.telHref + '" style="text-decoration:underline">' + f.tel + '</a>';
      if (ok) forma.reset();
    }
    function lokalSaqla() {
      try {
        var arr = JSON.parse(localStorage.getItem('hardwork_arizalar') || '[]');
        arr.push(m); localStorage.setItem('hardwork_arizalar', JSON.stringify(arr));
      } catch (x) {}
      tayyor(false);
    }
    if (FORMA_MANZIL) {
      fetch(FORMA_MANZIL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(m) })
        .then(function (r) { if (r.ok) tayyor(true); else lokalSaqla(); }).catch(lokalSaqla);
    } else {
      lokalSaqla();
    }
  });

  // ---------- Mobil pastki panel ----------
  var panel = document.getElementById('mobilPanel'), yozilish = document.getElementById('yozilish');
  addEventListener('scroll', function () {
    var r = yozilish.getBoundingClientRect();
    panel.classList.toggle('korinadi', scrollY > innerHeight * 0.8 && !(r.top < innerHeight && r.bottom > 0));
  }, { passive: true });
})();
