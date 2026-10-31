// HardWork — sahifa interaktivligi
(function () {
  // Arizalar manzili (backend yoki Telegram bot proksisi). Bo'sh bo'lsa — brauzerda saqlanadi.
  var FORMA_MANZIL = '';

  var kamHarakat = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sichqonli = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var mobil = matchMedia('(max-width: 760px)').matches;
  var gs = window.gsap && !kamHarakat;

  // ---------- Yuklanish ----------
  var yuklash = document.getElementById('yuklash'), ochildi = false;
  function och() {
    if (ochildi) return; ochildi = true;
    yuklash.classList.add('tayyor');
    if (gs) {
      gsap.from('.hero__sarlavha .qator', { yPercent: 105, duration: 1.2, stagger: 0.1, ease: 'expo.out', delay: 0.35 });
      gsap.from('.belgi, .hero__matn, .hero__tugmalar, .hero__fakt li, .hero__sahna', { y: 28, opacity: 0, duration: 1, stagger: 0.07, ease: 'power3.out', delay: 0.6 });
      gsap.from('.chip', { scale: 0.6, opacity: 0, duration: 1.1, stagger: 0.15, ease: 'back.out(1.7)', delay: 1 });
    }
  }
  addEventListener('sahna-tayyor', function () { setTimeout(och, 1300); });
  setTimeout(och, 3800);

  // ---------- Lenta (uzluksiz) ----------
  var lenta = document.querySelector('.lenta__ichi');
  lenta.innerHTML += lenta.innerHTML;

  // ---------- Nav ----------
  var nav = document.getElementById('nav');
  addEventListener('scroll', function () { nav.classList.toggle('qotgan', scrollY > 30); }, { passive: true });
  document.getElementById('burger').addEventListener('click', function () { nav.classList.toggle('ochiq'); });
  nav.querySelectorAll('.nav__havola a').forEach(function (a) { a.addEventListener('click', function () { nav.classList.remove('ochiq'); }); });

  // ---------- Ko'rinish animatsiyalari ----------
  if (gs && window.ScrollTrigger) {
    gsap.registerPlugin(ScrollTrigger);
    gsap.utils.toArray('.bolim__bosh, .test, .yozilish, .jadval > div:first-child, .filial__tablar, .filial__malumot, .filial__xarita').forEach(function (el) {
      gsap.from(el, { y: 50, opacity: 0, duration: 1, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 88%' } });
    });
    gsap.utils.toArray('.natijalar, .kurslar, .ustozlar, .vaqtlar, .natijalar__kichik').forEach(function (g) {
      gsap.from(g.children, { y: 70, opacity: 0, rotateX: -18, duration: 1, stagger: 0.08, ease: 'power3.out', scrollTrigger: { trigger: g, start: 'top 85%' } });
    });
    gsap.to('.lenta__ichi', { xPercent: -8, ease: 'none', scrollTrigger: { trigger: '.lenta', scrub: 1 } });
  }

  // ---------- Ball ustunlari ----------
  var kuz = new IntersectionObserver(function (yozuvlar) {
    yozuvlar.forEach(function (y) { if (y.isIntersecting) { y.target.classList.add('korindi'); kuz.unobserve(y.target); } });
  }, { threshold: 0.35 });
  document.querySelectorAll('.ball').forEach(function (b) { kuz.observe(b); });

  // ---------- Kompyuter: maxsus kursor, 3D egilish, magnit, parallaks ----------
  if (sichqonli && !kamHarakat) {
    document.body.classList.add('kursor-faol');
    var nuqta = document.getElementById('kursor'), halqa = document.getElementById('kursorHalqa');
    var mx = innerWidth / 2, my = innerHeight / 2, hx = mx, hy = my;
    addEventListener('pointermove', function (e) { mx = e.clientX; my = e.clientY; nuqta.style.transform = 'translate(' + mx + 'px,' + my + 'px)'; }, { passive: true });
    (function sikl() { hx += (mx - hx) * 0.18; hy += (my - hy) * 0.18; halqa.style.transform = 'translate(' + hx + 'px,' + hy + 'px)'; requestAnimationFrame(sikl); })();
    document.addEventListener('pointerover', function (e) { if (e.target.closest('a, button, [data-egilish], select, input')) halqa.classList.add('ustida'); });
    document.addEventListener('pointerout', function (e) { if (e.target.closest('a, button, [data-egilish], select, input')) halqa.classList.remove('ustida'); });

    document.querySelectorAll('[data-egilish]').forEach(function (k) {
      k.addEventListener('pointermove', function (e) {
        var r = k.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        k.style.transform = 'rotateY(' + ((x - 0.5) * 12) + 'deg) rotateX(' + ((0.5 - y) * 12) + 'deg) translateZ(8px)';
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

    var chiplar = document.querySelectorAll('.chip');
    addEventListener('pointermove', function (e) {
      var px = e.clientX / innerWidth - 0.5, py = e.clientY / innerHeight - 0.5;
      chiplar.forEach(function (c) { var d = +c.dataset.chuqurlik; c.style.transform = 'translate(' + (-px * d) + 'px,' + (-py * d) + 'px)'; });
    }, { passive: true });
  }

  // ---------- Vaqt tanlash → forma ----------
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
  var filiallar = {
    chilonzor: {
      manzil: 'Bunyodkor shoh ko\'chasi 52, Integro binosi, 7–8-qavat', mo: 'Chilonzor metro',
      tel: '+998 99 887 40 03', telHref: '+998998874003', tg: 'hardwork_integro',
      xarita: 'https://maps.google.com/maps?q=41.2764056,69.2050986&z=16&output=embed',
      yol: 'https://www.google.com/maps/dir/?api=1&destination=41.2764056,69.2050986'
    },
    beruniy: {
      manzil: '“Belissimo” binosi, 2-qavat', mo: 'Beruniy metro',
      tel: '+998 94 101 92 42', telHref: '+998941019242', tg: 'hardwork_beruniy',
      xarita: 'https://maps.google.com/maps?q=' + encodeURIComponent('Belissimo, Beruniy metro, Tashkent') + '&z=16&output=embed',
      yol: 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent('Belissimo Beruniy Tashkent')
    }
  };
  var malumot = document.getElementById('filialMalumot'), xarita = document.getElementById('filialXarita');
  var formaFilial = document.getElementById('formaFilial');
  function filialKorsat(k) {
    var f = filiallar[k];
    document.querySelectorAll('.filial__tab').forEach(function (t) { var faol = t.dataset.filial === k; t.classList.toggle('faol', faol); t.setAttribute('aria-selected', faol); });
    malumot.innerHTML = '<dl><dt>Manzil</dt><dd>' + f.manzil + '</dd><dt>Mo\'ljal</dt><dd>' + f.mo + '</dd>' +
      '<dt>Telefon</dt><dd><a href="tel:' + f.telHref + '">' + f.tel + '</a></dd><dt>Telegram</dt><dd><a href="https://t.me/' + f.tg + '" target="_blank" rel="noopener">@' + f.tg + '</a></dd>' +
      '<dt>Ish vaqti</dt><dd>Har kuni · 09:00 – 22:00</dd></dl>' +
      '<div class="tugmalar"><a class="tugma tugma--kichik" target="_blank" rel="noopener" href="' + f.yol + '">Yo\'nalish olish ↗</a>' +
      '<a class="tugma tugma--chiziq tugma--kichik" href="tel:' + f.telHref + '">Qo\'ng\'iroq</a></div>';
    if (xarita.dataset.joriy !== k) { xarita.src = f.xarita; xarita.dataset.joriy = k; }
    formaFilial.value = k === 'beruniy' ? 'Beruniy' : 'Chilonzor';
  }
  document.querySelectorAll('.filial__tab').forEach(function (t) { t.addEventListener('click', function () { filialKorsat(t.dataset.filial); }); });
  filialKorsat('chilonzor');

  // ---------- Daraja testi ----------
  var savollar = [
    { s: 'She ___ a student.', v: ['is', 'are', 'am', 'be'], t: 0 },
    { s: 'I ___ English every day.', v: ['studies', 'study', 'studying', 'studied'], t: 1 },
    { s: 'Last summer we ___ to Samarkand.', v: ['go', 'have gone', 'went', 'going'], t: 2 },
    { s: 'There aren\'t ___ chairs in the room.', v: ['some', 'any', 'much', 'a'], t: 1 },
    { s: 'If I study hard, I ___ get 7.0.', v: ['would', 'will', 'am', 'did'], t: 1 },
    { s: 'She has worked here ___ three years.', v: ['since', 'for', 'during', 'from'], t: 1 },
    { s: 'By the time we arrived, the lesson ___.', v: ['had already started', 'has started', 'starts', 'was start'], t: 0 },
    { s: 'Not only ___ the exam, but she also got 8.0 in Listening.', v: ['she passed', 'did she pass', 'she did pass', 'passed she'], t: 1 },
  ];
  var darajalar = [
    { min: 0, d: 'A1', n: 'Beginner', m: 'Noldan boshlaymiz — Beginner guruhi siz uchun.', k: 'Beginner' },
    { min: 3, d: 'A2', n: 'Elementary', m: 'Poydevor bor. General English bilan tez o\'sasiz.', k: 'General English' },
    { min: 5, d: 'B1', n: 'Intermediate', m: 'Yaxshi! General English + IELTS Standard yo\'li.', k: 'IELTS Standard' },
    { min: 6, d: 'B2', n: 'Upper-Intermediate', m: 'IELTS 6.5–7.0 ga tayyor zamin. IELTS Standard yoki CEFR.', k: 'IELTS Standard' },
    { min: 8, d: 'C1', n: 'Advanced', m: 'Ajoyib! IELTS Intensive bilan 7.0+ ni nishonga oling.', k: 'IELTS Intensive' },
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
    document.getElementById('formaKurs').value = d.k;
    ichi.innerHTML = '<div class="natija"><div class="test__raqam">' + ball + ' / 8 to\'g\'ri</div><div class="natija__daraja">' + d.d + '</div>' +
      '<h3>' + d.n + '</h3><p>' + d.m + '</p><div class="tugmalar"><a href="#yozilish" class="tugma">' + d.k + ' — bepul sinov darsi →</a>' +
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
    m.vaqt_yuborildi = new Date().toISOString();
    var tg = m.filial === 'Beruniy' ? 'hardwork_beruniy' : 'hardwork_integro';
    var tugma = forma.querySelector('button');
    tugma.disabled = true;
    function tayyor(ok) {
      tugma.disabled = false;
      xabar.style.color = ok ? '#4ade80' : '#ffd75e';
      xabar.innerHTML = ok
        ? 'Rahmat, ' + m.ism + '! Administrator tez orada qo\'ng\'iroq qiladi.'
        : 'Arizangiz saqlandi. Tezroq javob uchun yozing: <a href="https://t.me/' + tg + '" target="_blank" rel="noopener" style="text-decoration:underline">@' + tg + '</a>';
      if (ok) forma.reset();
    }
    if (FORMA_MANZIL) {
      fetch(FORMA_MANZIL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(m) })
        .then(function (r) { tayyor(r.ok); }).catch(function () { tayyor(false); });
    } else {
      var arr = JSON.parse(localStorage.getItem('hardwork_arizalar') || '[]');
      arr.push(m); localStorage.setItem('hardwork_arizalar', JSON.stringify(arr));
      tayyor(false);
    }
  });

  // ---------- Mobil pastki panel ----------
  var panel = document.getElementById('mobilPanel'), yozilish = document.getElementById('yozilish');
  addEventListener('scroll', function () {
    var r = yozilish.getBoundingClientRect();
    panel.classList.toggle('korinadi', scrollY > innerHeight * 0.8 && !(r.top < innerHeight && r.bottom > 0));
  }, { passive: true });
})();
