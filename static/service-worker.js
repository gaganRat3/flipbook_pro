const STATIC_CACHE = "static-v4";
const DYNAMIC_CACHE = "dynamic-v3";
const IMAGE_CACHE = "image-v3";
const OFFLINE_URL = "/offline.html";

// List of core assets to cache for offline
const CORE_ASSETS = [
  '/',
  '/offline.html',
  '/static/css/filters.css',
  '/static/manifest.json',
  // Add more static assets as needed
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
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

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Only handle GET requests
  if (request.method !== 'GET') return;

  // Skip API and auth/admin routes
  if (
    request.url.includes('/api/') ||
    request.url.includes('/admin/') ||
    request.url.includes('/register/') ||
    request.url.includes('/login/')
  ) {
    event.respondWith(fetch(request));
    return;
  }

  // Images: cache first, then network, fallback to placeholder
  if (
    request.destination === 'image' ||
    request.url.includes('/media/') ||
    request.url.includes('/static/images/')
  ) {
    event.respondWith(
      caches.match(request).then((response) => {
        if (response) return response;
        return fetch(request)
          .then((fetched) => {
            if (!fetched || fetched.status !== 200 || fetched.type !== "basic") {
              return fetched;
            }
            const responseClone = fetched.clone();
            caches.open(IMAGE_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
            return fetched;
          })
          .catch(() => caches.match('/static/images/offline-placeholder.png'));
      })
    );
    return;
  }

  // HTML pages: network first, fallback to cache/offline
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache the page
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || caches.match(OFFLINE_URL)))
    );
    return;
  }

  // Static assets (CSS, JS, fonts): cache first, then network
  if (
    request.destination === 'style' ||
    request.destination === 'script' ||
    request.destination === 'font'
  ) {
    event.respondWith(
      caches.match(request).then((response) => {
        if (response) return response;
        return fetch(request).then((fetched) => {
          const responseClone = fetched.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return fetched;
        });
      })
    );
    return;
  }

  // Fallback: try network, then cache
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});

// Notification support
self.addEventListener('push', function(event) {
  let data = {};
  if (event.data) {
    data = event.data.json();
  }
  const title = data.title || 'Notification';
  const options = {
    body: data.body || '',
    icon: data.icon || '/static/images/icon-192.png',
    badge: data.badge || '/static/images/icon-192.png',
    data: data.url || '/',
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  const url = event.notification.data || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(windowClients => {
      for (let client of windowClients) {
        if (client.url === url && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

// Background sync for unlock requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-unlock-requests') {
    event.waitUntil(
      fetch('/sync-unlock-requests/', {
        method: 'POST',
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Unlock requests synced:', data);
        })
        .catch((error) => {
          console.error('Error syncing unlock requests:', error);
        })
    );
  }
});
