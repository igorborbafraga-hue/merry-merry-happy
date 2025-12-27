const CACHE_NAME = 'merry-ok-v1';
const TO_CACHE = [
  '/',
  '/static/style.css',
  '/static/app.js'
];

self.addEventListener('install', (e)=>{
  e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(TO_CACHE)));
});

self.addEventListener('fetch', (e)=>{
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
