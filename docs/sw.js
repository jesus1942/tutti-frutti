/* Service worker minimo para Tutti Frutti (PWA instalable).
 * Estrategia: network-first solo para recursos del mismo origen.
 * Las llamadas al backend (otro origen) pasan de largo sin tocarse. */
const CACHE = 'tutti-frutti-v9';
const CORE = [
  './',
  './index.html',
  './site.webmanifest',
  './static/icons/icon-192.png',
  './static/icons/icon-512.png',
  './static/icons/icon-maskable-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(CORE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // dejar pasar el backend/API
  event.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(req).then((m) => m || caches.match('./index.html')))
  );
});
