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

// Fetch event - serve cached files
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).then((fetchResponse) => {
        return caches.open(DYNAMIC_CACHE).then((cache) => {
          cache.put(event.request, fetchResponse.clone());
          return fetchResponse;
        });
      });
    })
  );
});
