// service-worker.js for Django static
self.addEventListener('install', event => {
  self.skipWaiting();
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
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim(); // Take control of all pages
});

// Fetch event - intercept network requests
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip API calls and external URLs
  if (request.url.includes('/api/') || request.url.includes('/admin/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.status === 200) {
            const cache =
              request.headers.get('accept').includes('application/json')
                ? DYNAMIC_CACHE
                : STATIC_CACHE;
            const responseClone = response.clone();
            caches.open(cache).then((c) => c.put(request, responseClone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }

  // Cache images separately
  if (
    request.destination === 'image' ||
    request.url.includes('/media/') ||
    request.url.includes('/static/images/')
  ) {
    event.respondWith(
      caches.match(request).then((response) => {
        if (response) {
          return response;
        }
        return fetch(request)
          .then((fetched) => {
            const responseClone = fetched.clone();
            caches.open(IMAGE_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
            return fetched;
          })
          .catch(() => {
            // Return a placeholder offline image if available
            return caches.match('/static/images/offline-placeholder.png');
          });
      })
    );
    return;
  }

  // Network first strategy for HTML pages
  if (request.destination === 'document' || request.destination === '') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then((cached) => {
            if (cached) {
              return cached;
            }
            // Return offline page if available
            return caches.match('/offline.html');
          });
        })
    );
    return;
  }

  // Cache first strategy for static assets (CSS, JS, fonts)
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(request)
        .then((fetched) => {
          const responseClone = fetched.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return fetched;
        })
        .catch(() => {
          console.log('Service Worker: Offline - unable to fetch:', request.url);
        });
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
