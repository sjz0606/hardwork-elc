// HardWork — 3D zarracha sahnasi.
// Hikoya: "HARD WORK" (mehnat) → "7.0" (IELTS natija) → globus (dunyo tili) → "C1" (CEFR).
// Sahifa aylantirilganda zarrachalar bir shakldan ikkinchisiga "portlab" o'tadi.
import * as THREE from '../vendor/three.module.min.js';

const kanvas = document.getElementById('sahna');
const mobil = matchMedia('(max-width: 760px)').matches;
const kamHarakat = matchMedia('(prefers-reduced-motion: reduce)').matches;
const N = mobil ? 4000 : 8500;

const renderer = new THREE.WebGLRenderer({ canvas: kanvas, antialias: false, alpha: true, powerPreference: 'high-performance' });
const pr = Math.min(devicePixelRatio || 1, 1.5);
renderer.setPixelRatio(pr);
renderer.setClearColor(0x000000, 0);

const sahna = new THREE.Scene();
const kamera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
kamera.position.set(0, 0, 14);
const guruh = new THREE.Group();
sahna.add(guruh);

const tasodif = (a, b) => a + Math.random() * (b - a);

// ---------- Shakllar ----------
async function matnNuqtalari(qatorlar, n, kenglik) {
  try { await document.fonts.load('400 200px Anton'); } catch (e) { /* zaxira */ }
  const W = 1200, H = 300 * qatorlar.length + 40;
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const x = c.getContext('2d');
  x.fillStyle = '#fff'; x.textAlign = 'center'; x.textBaseline = 'middle';
  let o = 300;
  const shrift = (k) => `400 ${k}px Anton, Impact, "Arial Black", sans-serif`;
  x.font = shrift(o);
  const engKeng = () => Math.max(...qatorlar.map((q) => x.measureText(q).width));
  while (engKeng() > W * 0.92 && o > 40) { o -= 10; x.font = shrift(o); }
  qatorlar.forEach((q, i) => x.fillText(q, W / 2, H / 2 + (i - (qatorlar.length - 1) / 2) * o * 0.95));
  const d = x.getImageData(0, 0, W, H).data;
  const p = [];
  for (let y = 0; y < H; y += 2) for (let i = 0; i < W; i += 2) if (d[(y * W + i) * 4 + 3] > 128) p.push(i, y);
  const m = kenglik / W, soni = p.length / 2, out = new Float32Array(n * 3);
  for (let k = 0; k < n; k++) {
    const j = (Math.random() * soni) | 0;
    out[k * 3] = (p[j * 2] - W / 2 + tasodif(-1, 1)) * m;
    out[k * 3 + 1] = -(p[j * 2 + 1] - H / 2 + tasodif(-1, 1)) * m;
    out[k * 3 + 2] = tasodif(-0.15, 0.15);
  }
  return out;
}

function globus(n) {
  const out = new Float32Array(n * 3);
  const halqa = Math.floor(n * 0.2), sfera = n - halqa, oltin = Math.PI * (3 - Math.sqrt(5)), R = 3.2;
  for (let i = 0; i < sfera; i++) {
    const y = 1 - (i / (sfera - 1)) * 2, r = Math.sqrt(1 - y * y), t = oltin * i;
    out[i * 3] = Math.cos(t) * r * R; out[i * 3 + 1] = y * R; out[i * 3 + 2] = Math.sin(t) * r * R;
  }
  for (let i = sfera; i < n; i++) {
    const a = Math.random() * Math.PI * 2, rr = 4.9 + tasodif(-0.1, 0.1), z = Math.sin(a) * rr;
    out[i * 3] = Math.cos(a) * rr; out[i * 3 + 1] = z * Math.sin(0.45); out[i * 3 + 2] = z * Math.cos(0.45);
  }
  return out;
}

function sochilgan(n) {
  const out = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { out[i * 3] = tasodif(-24, 24); out[i * 3 + 1] = tasodif(-15, 15); out[i * 3 + 2] = tasodif(-20, 6); }
  return out;
}

// ---------- Geometriya ----------
const geo = new THREE.BufferGeometry();
const joy = new Float32Array(N * 3), rang = new Float32Array(N * 3), olchamlar = new Float32Array(N), faza = new Float32Array(N * 2);
const sariq = new THREE.Color('#ffc21a'), kok = new THREE.Color('#5f8dff'), oq = new THREE.Color('#f4f6fb');
for (let i = 0; i < N; i++) {
  const r = Math.random();
  const c = r < 0.22 ? sariq : r < 0.32 ? kok : oq.clone().multiplyScalar(tasodif(0.6, 1));
  rang.set([c.r, c.g, c.b], i * 3);
  olchamlar[i] = tasodif(0.6, 1.6);
  faza[i * 2] = Math.random() * Math.PI * 2; faza[i * 2 + 1] = Math.random() * Math.PI * 2;
}
geo.setAttribute('position', new THREE.BufferAttribute(joy, 3).setUsage(THREE.DynamicDrawUsage));
geo.setAttribute('aRang', new THREE.BufferAttribute(rang, 3));
geo.setAttribute('aOlcham', new THREE.BufferAttribute(olchamlar, 1));

const mat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  uniforms: { uPiksel: { value: pr }, uXiralik: { value: 3 } },
  vertexShader: /* glsl */`
    attribute vec3 aRang; attribute float aOlcham;
    uniform float uPiksel, uXiralik;
    varying vec3 vRang; varying float vAlfa;
    void main(){
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      float chuqur = -mv.z;
      float xira = abs(chuqur - 14.0) * 0.12 * uXiralik + uXiralik * 0.25;
      gl_PointSize = aOlcham * uPiksel * (24.0 / chuqur) * (1.0 + xira * 2.2);
      vAlfa = 0.95 / (1.0 + xira * xira * 3.0);
      vRang = aRang;
      gl_Position = projectionMatrix * mv;
    }`,
  fragmentShader: /* glsl */`
    varying vec3 vRang; varying float vAlfa;
    void main(){
      float d = length(gl_PointCoord - 0.5);
      if (d > 0.5) discard;
      gl_FragColor = vec4(vRang, smoothstep(0.5, 0.0, d) * vAlfa);
    }`,
});
guruh.add(new THREE.Points(geo, mat));

// Orbitadagi halqa — "harakat" ramzi
const halqa = new THREE.Mesh(new THREE.TorusGeometry(6.2, 0.01, 8, 240), new THREE.MeshBasicMaterial({ color: 0xffc21a, transparent: true, opacity: 0.3 }));
const halqa2 = new THREE.Mesh(new THREE.TorusGeometry(6.9, 0.006, 8, 240), new THREE.MeshBasicMaterial({ color: 0x5f8dff, transparent: true, opacity: 0.22 }));
guruh.add(halqa, halqa2);

// ---------- Holat ----------
let nishonlar = null;
const boshlangich = sochilgan(N);
joy.set(boshlangich);
let introBosh = -1, bosqich = 0, bosqichMaqsad = 0, globusBurchak = 0;
const sichqon = { x: 0, y: 0, sx: 0, sy: 0 };
const joyMaqsad = new THREE.Vector3(), joyHozir = new THREE.Vector3();
let sahnaShaffof = 1;
const heroOyna = document.querySelector('.hero__sahna');

addEventListener('pointermove', (e) => {
  sichqon.x = (e.clientX / innerWidth) * 2 - 1;
  sichqon.y = (e.clientY / innerHeight) * 2 - 1;
}, { passive: true });

function korinishBalandligi() { return 2 * kamera.position.z * Math.tan(THREE.MathUtils.degToRad(kamera.fov / 2)); }

function aylantirishniOlchash() {
  const h = innerHeight;
  const max = document.documentElement.scrollHeight - h;
  const p = max > 0 ? scrollY / max : 0;
  bosqichMaqsad = Math.min(3, Math.max(0, (p - 0.04) * 3.5));
  const vh = korinishBalandligi(), vw = vh * kamera.aspect;
  if (mobil && heroOyna) {
    // Mobil: hero ichidagi "oyna" markazida turadi, keyin yuqoriga — fon bo'lib qoladi
    const r = heroOyna.getBoundingClientRect();
    const cy = r.top + r.height / 2;
    if (r.bottom > 40) { joyMaqsad.set(0, (0.5 - cy / h) * vh, 0); sahnaShaffof = 1; }
    else { joyMaqsad.set(0, vh * 0.22, -2); sahnaShaffof = 0.45; }
  } else {
    // Kompyuter: hero'da o'ngda, keyin o'ngda fon bo'lib qoladi
    const heroTugadi = Math.min(1, scrollY / (h * 0.8));
    joyMaqsad.set(vw * 0.22, 0.2 + heroTugadi * 0.6, -heroTugadi * 2);
    sahnaShaffof = 1 - heroTugadi * 0.5;
  }
}
addEventListener('scroll', aylantirishniOlchash, { passive: true });

function oynaOlchami() {
  renderer.setSize(innerWidth, innerHeight, false);
  kamera.aspect = innerWidth / innerHeight;
  kamera.updateProjectionMatrix();
  guruh.scale.setScalar(mobil ? 0.62 : Math.min(1, Math.max(0.65, kamera.aspect / 1.9)));
  aylantirishniOlchash();
}
addEventListener('resize', oynaOlchami);
oynaOlchami();
joyHozir.copy(joyMaqsad);

const silliq = (t) => t * t * (3 - 2 * t);
const A = [0, 0, 0], B = [0, 0, 0];
function nuqta(k, i, out) {
  const a = nishonlar[k];
  let x = a[i * 3], y = a[i * 3 + 1], z = a[i * 3 + 2];
  if (k === 2) { const c = Math.cos(globusBurchak), s = Math.sin(globusBurchak), nx = x * c + z * s; z = -x * s + z * c; x = nx; }
  out[0] = x; out[1] = y; out[2] = z;
}

const soat = new THREE.Clock();
function kadr() {
  const dt = Math.min(soat.getDelta(), 0.05), t = soat.elapsedTime;
  if (nishonlar) {
    if (introBosh < 0) introBosh = performance.now();
    const intro = kamHarakat ? 1 : Math.min(1, (performance.now() - introBosh) / 2600);
    const ie = 1 - Math.pow(1 - intro, 3);
    bosqich += (bosqichMaqsad - bosqich) * Math.min(1, dt * 3.2);
    const bi = Math.min(2, Math.floor(bosqich));
    const f = silliq(Math.min(1, Math.max(0, bosqich - bi)));
    globusBurchak += dt * (0.15 + Math.max(0, 1 - Math.abs(bosqich - 2)) * 0.4);
    const portlash = Math.sin(f * Math.PI) * 1.1;
    for (let i = 0; i < N; i++) {
      nuqta(bi, i, A); nuqta(bi + 1, i, B);
      const f1 = faza[i * 2], f2 = faza[i * 2 + 1];
      const x = A[0] + (B[0] - A[0]) * f + Math.sin(f1) * portlash + Math.sin(t * 0.9 + f1) * 0.03;
      const y = A[1] + (B[1] - A[1]) * f + Math.cos(f2) * portlash + Math.cos(t * 0.8 + f2) * 0.03;
      const z = A[2] + (B[2] - A[2]) * f + Math.sin(f1 + f2) * portlash;
      const j = i * 3;
      joy[j] = boshlangich[j] + (x - boshlangich[j]) * ie;
      joy[j + 1] = boshlangich[j + 1] + (y - boshlangich[j + 1]) * ie;
      joy[j + 2] = boshlangich[j + 2] + (z - boshlangich[j + 2]) * ie;
    }
    geo.attributes.position.needsUpdate = true;
    mat.uniforms.uXiralik.value = 0.22 + (1 - ie) * 3 + Math.sin(f * Math.PI) * 0.7;
  }
  joyHozir.lerp(joyMaqsad, Math.min(1, dt * 4));
  guruh.position.copy(joyHozir);
  kanvas.style.opacity = (parseFloat(kanvas.style.opacity || 1) + (sahnaShaffof - parseFloat(kanvas.style.opacity || 1)) * 0.1).toFixed(3);

  sichqon.sx += (sichqon.x - sichqon.sx) * 0.05;
  sichqon.sy += (sichqon.y - sichqon.sy) * 0.05;
  guruh.rotation.y = sichqon.sx * 0.35 + (mobil ? Math.sin(t * 0.4) * 0.25 : 0);
  guruh.rotation.x = sichqon.sy * 0.2;
  halqa.rotation.set(1.15 + sichqon.sy * 0.3, t * 0.18, 0);
  halqa2.rotation.set(1.3, -t * 0.12, t * 0.05);
  kamera.position.x = sichqon.sx * 0.5;
  kamera.position.y = -sichqon.sy * 0.35;
  kamera.lookAt(0, 0, 0);
  renderer.render(sahna, kamera);
  requestAnimationFrame(kadr);
}

(async () => {
  const k = 8.2;
  const [hw, yetti, c1] = await Promise.all([
    matnNuqtalari(['HARD', 'WORK'], N, k * 1.05),
    matnNuqtalari(['7.0'], N, k * 0.95),
    matnNuqtalari(['C1'], N, k * 0.75),
  ]);
  nishonlar = [hw, yetti, globus(N), c1];
  aylantirishniOlchash();
  bosqich = bosqichMaqsad;
  dispatchEvent(new Event('sahna-tayyor'));
})();
requestAnimationFrame(kadr);
