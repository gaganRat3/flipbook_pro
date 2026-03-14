// Service Worker for bhudevstore PWA
const CACHE_NAME = 'bhudevstore-v1';
const STATIC_CACHE = 'bhudevstore-static-v1';
const DYNAMIC_CACHE = 'bhudevstore-dynamic-v1';
const IMAGE_CACHE = 'bhudevstore-images-v1';

// Files to cache on install
const STATIC_FILES = [
  '/',
  '/offline/',
  '/static/manifest.json',
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('Service Worker: Caching static files');
      return cache.addAll(STATIC_FILES).catch((error) => {
        console.error('Service Worker: Error caching files:', error);
      });
    })
  );
  self.skipWaiting(); // Activate immediately
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (
            cacheName !== STATIC_CACHE &&
            cacheName !== DYNAMIC_CACHE &&
            cacheName !== IMAGE_CACHE
          ) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - do not cache auth/admin routes; keep logout/login always network-backed.
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Never intercept non-GET requests.
  if (request.method !== 'GET') {
    return;
  }

  // Ignore cross-origin requests.
  if (url.origin !== self.location.origin) {
    return;
  }

  // Auth/admin/session-sensitive routes must always hit network.
  const bypassPrefixes = [
    '/login/',
    '/logout/',
    '/register/',
    '/admin/',
    '/active-sessions/',
    '/unlock-request/',
    '/debug/',
  ];
  if (bypassPrefixes.some((prefix) => url.pathname.startsWith(prefix))) {
    event.respondWith(fetch(request));
    return;
  }

  // Network-first for HTML documents.
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match('/offline/')))
    );
    return;
  }

  // Cache-first for static assets only.
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/media/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Default network-first fallback.
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});
