// HardWork — professional harakat qatlami: silliq skroll, matn ochilishi, sanoqlar, parallaks, tezlikka javob beruvchi lenta
(function () {
  var kamHarakat = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (kamHarakat || !window.gsap || !window.ScrollTrigger) {
    document.documentElement.classList.add('harakatsiz');
    return;
  }
  gsap.registerPlugin(ScrollTrigger);
  var sichqonli = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var html = document.documentElement;
  html.classList.add('harakat');

  // ================= 1. Silliq skroll (faqat sichqoncha bilan) =================
  var lenis = null;
  if (sichqonli && window.Lenis) {
    lenis = new Lenis({ lerp: 0.085, wheelMultiplier: 1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
    gsap.ticker.lagSmoothing(0);
    // ichki havolalar silliq
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href');
      var nishon = id.length > 1 && document.querySelector(id);
      if (!nishon) return;
      e.preventDefault();
      lenis.scrollTo(nishon, { offset: id === '#bosh' ? 0 : -70, duration: 1.4 });
    });
    // video oynasi ochilganda skroll to'xtaydi
    var oyna = document.getElementById('oyna');
    if (oyna) new MutationObserver(function () { oyna.hidden ? lenis.start() : lenis.stop(); })
      .observe(oyna, { attributes: true, attributeFilter: ['hidden'] });
  }

  // ================= 2. Yordamchilar =================
  // Matnni so'zlarga bo'ladi (em/br va boshqa teglar saqlanadi), har so'z niqob ichida
  function sozlarga(el) {
    var natija = [];
    (function yur(tugun) {
      Array.prototype.slice.call(tugun.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var qism = n.textContent.split(/(\s+)/), frag = document.createDocumentFragment();
          qism.forEach(function (s) {
            if (!s) return;
            if (/^\s+$/.test(s)) { frag.appendChild(document.createTextNode(s)); return; }
            var t = document.createElement('span'), i = document.createElement('span');
            t.className = 'soz'; i.className = 'soz__i'; i.textContent = s;
            t.appendChild(i); frag.appendChild(t); natija.push(i);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') {
          yur(n);
        }
      });
    })(el);
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    return natija;
  }

  // Matnni harflarga bo'ladi
  function harflarga(el) {
    var natija = [];
    (function yur(tugun) {
      Array.prototype.slice.call(tugun.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split('').forEach(function (c) {
            var s = document.createElement('span'); s.className = 'harf'; s.textContent = c;
            frag.appendChild(s); natija.push(s);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) yur(n);
      });
    })(el);
    return natija;
  }

  // Raqamni 0 dan sanaydi: "650 000", "8.0", "7", "7.5"
  function sanash(el, kechikish) {
    var asl = el.textContent.trim(), toza = asl.replace(/\s/g, '');
    if (!/^\d+(\.\d+)?$/.test(toza)) return false;
    var son = parseFloat(toza), kasr = (toza.split('.')[1] || '').length, boshliq = /\s/.test(asl);
    var o = { v: 0 };
    el.style.minWidth = el.offsetWidth + 'px';
    gsap.to(o, {
      v: son, duration: son > 1000 ? 1.8 : 1.4, delay: kechikish || 0, ease: 'power3.out',
      onUpdate: function () {
        var t = kasr ? o.v.toFixed(kasr) : String(Math.round(o.v));
        if (boshliq) t = t.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        el.textContent = t;
      },
      onComplete: function () { el.textContent = asl; el.style.minWidth = ''; }
    });
    return true;
  }
  function sanashKorinsa(sel) {
    gsap.utils.toArray(sel).forEach(function (el) {
      if (!/^\d[\d\s]*(\.\d+)?$/.test(el.textContent.trim())) return;
      var asl = el.textContent;
      el.textContent = asl.replace(/\d/g, '0');
      ScrollTrigger.create({ trigger: el, start: 'top 92%', once: true, onEnter: function () { el.textContent = asl; sanash(el); } });
    });
  }

  // Harflarni "shifrlab" ochish (bo'lim teglari uchun)
  var BELGILAR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789—·';
  function shifr(el) {
    var asl = el.textContent, uz = asl.length, q = { p: 0 };
    gsap.to(q, {
      p: 1, duration: 0.9, ease: 'power2.out',
      onUpdate: function () {
        var ochiq = Math.floor(q.p * uz), s = asl.slice(0, ochiq);
        for (var i = ochiq; i < uz; i++) s += asl[i] === ' ' ? ' ' : BELGILAR[(Math.random() * BELGILAR.length) | 0];
        el.textContent = s;
      },
      onComplete: function () { el.textContent = asl; }
    });
  }

  // ================= 3. Skroll progress chizig'i =================
  var bar = document.createElement('div');
  bar.className = 'progress'; bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  gsap.to(bar, { scaleX: 1, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: 0.3 } });

  // ================= 4. Hero: kirish va skrollda chiqish =================
  // har bir qator ichini o'raymiz — qator niqob, ichki qism ko'tariladi
  gsap.utils.toArray('.hero__sarlavha .qator').forEach(function (q) {
    var i = document.createElement('span'); i.className = 'qator__i';
    while (q.firstChild) i.appendChild(q.firstChild);
    q.appendChild(i);
  });
  var heroTl = gsap.timeline({ defaults: { ease: 'expo.out' } });
  heroTl
    .from('.nav', { y: -40, opacity: 0, duration: 1.1 }, 0)
    .from('.hero__sarlavha .qator__i', { yPercent: 115, rotate: 3, duration: 1.4, stagger: 0.12, transformOrigin: '0 100%' }, 0.1)
    .from('.belgi', { y: 20, opacity: 0, duration: 1 }, 0.2)
    .from('.hero__matn', { y: 30, opacity: 0, filter: 'blur(10px)', duration: 1.2 }, 0.45)
    .from('.hero__tugmalar > *', { y: 30, opacity: 0, scale: 0.94, duration: 1.1, stagger: 0.08 }, 0.55)
    .from('.hero__fakt li', { y: 26, opacity: 0, duration: 1, stagger: 0.08 }, 0.7)
    .from('.stek', { y: 120, rotateX: 26, rotateY: -14, scale: 0.86, opacity: 0, duration: 1.8, transformPerspective: 1400 }, 0.25)
    .from('.pastga', { opacity: 0, duration: 1 }, 1.2);
  heroTl.add(function () { gsap.utils.toArray('.hero__fakt b').forEach(function (b, i) { sanash(b, i * 0.08); }); }, 0.75);

  var hero = document.querySelector('.hero');
  if (hero) {
    gsap.to('.hero__ichi', { yPercent: -18, opacity: 0.15, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('.stek', { yPercent: -10, rotateX: 14, scale: 0.92, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
    gsap.to('.pastga', { opacity: 0, ease: 'none', scrollTrigger: { trigger: hero, start: 'top top', end: '15% top', scrub: true } });
  }

  // ================= 5. Bo'lim sarlavhalari =================
  gsap.utils.toArray('.bolim h2').forEach(function (h) {
    var sozlar = sozlarga(h);
    gsap.set(sozlar, { yPercent: 115, rotate: 4, transformOrigin: '0 100%' });
    ScrollTrigger.create({
      trigger: h, start: 'top 88%', once: true,
      onEnter: function () {
        gsap.to(sozlar, { yPercent: 0, rotate: 0, duration: 1.2, stagger: 0.045, ease: 'expo.out',
          onComplete: function () { h.classList.add('ochildi'); } });
      }
    });
  });

  gsap.utils.toArray('.bolim__teg').forEach(function (t) {
    gsap.set(t, { opacity: 0 });
    ScrollTrigger.create({ trigger: t, start: 'top 90%', once: true, onEnter: function () { gsap.to(t, { opacity: 1, duration: 0.2 }); shifr(t); } });
  });

  gsap.utils.toArray('.bolim__bosh > p, .bolim__p, .bolim__bosh--qator > a, .narxlar__izoh, .vaqtlar__izoh').forEach(function (p) {
    gsap.from(p, { y: 30, opacity: 0, filter: 'blur(8px)', duration: 1.1, ease: 'power3.out', scrollTrigger: { trigger: p, start: 'top 92%' } });
  });

  // ================= 6. Kartalar to'plami (batch) =================
  function toplam(sel, sozlama) {
    var el = gsap.utils.toArray(sel);
    if (!el.length) return;
    gsap.set(el, Object.assign({ opacity: 0, y: 80, rotateX: -18, scale: 0.96, transformPerspective: 1100, transformOrigin: '50% 0%' }, sozlama.dan || {}));
    ScrollTrigger.batch(el, {
      start: 'top 90%', once: true,
      onEnter: function (b) {
        gsap.to(b, Object.assign({ opacity: 1, y: 0, x: 0, rotateX: 0, rotateY: 0, scale: 1, duration: 1.2, stagger: 0.09, ease: 'expo.out', clearProps: 'transform,opacity' }, sozlama.ga || {}));
      }
    });
  }
  toplam('.nega__karta', {});
  toplam('.narx', { dan: { y: 120, rotateX: -24 } });
  toplam('.ustoz', { dan: { y: 90, rotateY: 12 } });
  toplam('.devor', {});
  toplam('.vaqt', { dan: { y: 40, rotateX: -50, transformOrigin: '50% 100%' }, ga: { duration: 0.9, stagger: 0.06 } });
  toplam('.nega__katta', { dan: { rotateX: 0, y: 50 } });

  // Reels: pastdan "parda" bilan ochiladi + ichki video parallaksi
  var reels = gsap.utils.toArray('.reel');
  if (reels.length) {
    gsap.set(reels, { clipPath: 'inset(100% 0% 0% 0% round 18px)', y: 60 });
    ScrollTrigger.batch(reels, {
      start: 'top 92%', once: true,
      onEnter: function (b) {
        gsap.to(b, { clipPath: 'inset(0% 0% 0% 0% round 18px)', y: 0, duration: 1.4, stagger: 0.08, ease: 'expo.out',
          onComplete: function () { gsap.set(this.targets(), { clearProps: 'clipPath,transform' }); } });
      }
    });
    reels.forEach(function (r, i) {
      var v = r.querySelector('video');
      if (v) gsap.fromTo(v, { yPercent: -6, scale: 1.14 }, { yPercent: 6, scale: 1.14, ease: 'none',
        scrollTrigger: { trigger: r, start: 'top bottom', end: 'bottom top', scrub: true } });
    });
  }

  // Boshqa bloklar
  [['.test', { y: 80, scale: 0.94 }], ['.filial__tablar', { y: 40 }], ['.filial__malumot', { x: -60 }],
   ['.filial__xarita', { x: 60, scale: 0.96 }], ['.yozilish__chap', { y: 60 }], ['.forma', { y: 90, rotateX: -10, transformPerspective: 1200 }]]
    .forEach(function (j) {
      gsap.utils.toArray(j[0]).forEach(function (el) {
        gsap.from(el, Object.assign({ opacity: 0, duration: 1.3, ease: 'expo.out', clearProps: 'transform,opacity', scrollTrigger: { trigger: el, start: 'top 90%' } }, j[1]));
      });
    });

  // Ustoz ballari "sakrab" chiqadi
  gsap.utils.toArray('.ustoz__ball').forEach(function (b) {
    gsap.from(b, { scale: 0, rotate: -30, duration: 0.9, ease: 'back.out(2.2)', scrollTrigger: { trigger: b, start: 'top 90%' }, delay: 0.35 });
  });

  // Sanoqlar
  sanashKorinsa('.narx__summa b, .devor b, .ustoz__ball, .reel__ball');

  // ================= 7. Lenta: skroll tezligiga javob beradi =================
  var lenta = document.querySelector('.lenta__ichi');
  if (lenta) {
    var yarim = 0, x = 0, yon = 1, kuch = 0;
    function olch() { yarim = lenta.scrollWidth / 2; }
    olch(); addEventListener('resize', olch); addEventListener('load', olch);
    if (document.fonts) document.fonts.ready.then(olch);
    ScrollTrigger.create({
      trigger: '.lenta', start: 'top bottom', end: 'bottom top',
      onUpdate: function (s) { yon = s.direction; kuch = Math.min(Math.abs(s.getVelocity()) / 180, 14); }
    });
    var sk = 0;
    gsap.ticker.add(function (t, dt) {
      if (!yarim) return;
      x -= yon * (1 + kuch) * dt * 0.06;
      kuch *= 0.93;
      if (x <= -yarim) x += yarim;
      if (x > 0) x -= yarim;
      sk += (-yon * kuch * 0.9 - sk) * 0.12;
      lenta.style.transform = 'translate3d(' + x.toFixed(2) + 'px,0,0) skewX(' + sk.toFixed(2) + 'deg)';
    });
  }

  // ================= 8. Navigatsiya: yashirinish va faol havola =================
  var nav = document.getElementById('nav');
  if (nav) {
    ScrollTrigger.create({
      start: 400, end: 'max',
      onUpdate: function (s) { if (!nav.classList.contains('ochiq')) nav.classList.toggle('yashirin', s.direction === 1); },
      onLeaveBack: function () { nav.classList.remove('yashirin'); }
    });
    nav.querySelectorAll('.nav__havola a').forEach(function (a) {
      var bolim = document.querySelector(a.getAttribute('href'));
      if (!bolim) return;
      ScrollTrigger.create({ trigger: bolim, start: 'top 55%', end: 'bottom 55%',
        onToggle: function (s) { a.classList.toggle('faol', s.isActive); } });
    });
  }

  // ================= 9. Pastki ulkan logo: harflar ko'tariladi =================
  var plogo = document.querySelector('.pastki__logo');
  if (plogo) {
    var harflar = harflarga(plogo);
    gsap.from(harflar, { yPercent: 100, opacity: 0, rotate: 8, stagger: 0.05, ease: 'power3.out',
      scrollTrigger: { trigger: '.pastki', start: 'top 85%', end: 'bottom bottom', scrub: 1 } });
  }

  // Fon "aurora" skroll bilan siljiydi
  gsap.to('.aurora', { yPercent: 20, ease: 'none', scrollTrigger: { start: 0, end: 'max', scrub: true } });

  // ================= 10. Sichqoncha: yorug'lik va tugma effektlari =================
  if (sichqonli) {
    document.querySelectorAll('.narx, .nega__karta, .ustoz, .devor, .vaqt, .forma, .filial__malumot').forEach(function (k) {
      k.classList.add('nurli');
      k.addEventListener('pointermove', function (e) {
        var r = k.getBoundingClientRect();
        k.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        k.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    });
    // Kursor halqasi interaktiv elementlar ustida kattalashadi
    var halqa = document.getElementById('kursorHalqa');
    if (halqa) {
      document.addEventListener('pointerover', function (e) {
        halqa.classList.toggle('video', !!e.target.closest('.reel, .stek__karta[data-o="0"]'));
      });
    }
  }

  // Shriftlar yuklangach o'lchamlarni yangilash
  if (document.fonts) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  addEventListener('load', function () { ScrollTrigger.refresh(); });
})();
