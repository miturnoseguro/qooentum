// sw.js – Service Worker para cachear mapa y assets

const CACHE_NAME = 'qooentum-map-v3';
const STATIC_CACHE = 'qooentum-static-v1';

// Archivos estáticos de la app (ajusta según tu estructura)
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logo.png',
  '/bright_patched.json',        // Estilo del mapa (debe existir)
  // Si usas sprites/fuentes locales, agrégalos aquí
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_FILES)),
      caches.open(CACHE_NAME)
    ])
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME && key !== STATIC_CACHE)
          .map(key => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 1. TESELAS DEL MAPA (tiles, sprites, fuentes)
  const isMapTile =
    url.pathname.endsWith('.pbf') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.webp') ||
    url.pathname.includes('/tiles/') ||
    url.hostname.includes('tiles.openstreetmap') ||
    url.hostname.includes('maptiler') ||
    url.hostname.includes('openstreetmap') ||
    url.pathname.includes('/sprites/') ||
    url.pathname.includes('/fonts/') ||
    url.pathname.includes('/glyphs/');

  if (isMapTile) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        }).catch(() => new Response('', { status: 404 }));
      })
    );
    return;
  }

  // 2. ARCHIVOS ESTÁTICOS DE LA APP
  if (STATIC_FILES.some(file => url.pathname === file || url.pathname.endsWith(file))) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        return cached || fetch(event.request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(STATIC_CACHE).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // 3. API Y DATOS DINÁMICOS (NO CACHEAR)
  // Dejamos que pasen directamente
  event.respondWith(
    fetch(event.request).catch(() => new Response('Sin conexión', { status: 503 }))
  );
});
