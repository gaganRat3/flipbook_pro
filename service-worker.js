// service-worker.js at root
self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

// Only cache static assets, do not intercept all fetch requests
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/static/')) {
    event.respondWith(
      caches.open('static-v1').then(cache => {
        return cache.match(event.request).then(response => {
          return response || fetch(event.request).then(networkResponse => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        });
      })
    );
  }
  // For other requests, let the network handle them
});
