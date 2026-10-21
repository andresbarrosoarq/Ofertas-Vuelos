// Funciona sin conexión: la app se sirve de caché y los precios, de la red si hay.
const CACHE = "vuelos-v1";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  // Red primero; si no hay conexión, lo último guardado.
  e.respondWith(
    fetch(e.request).then((r) => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(url.pathname.endsWith("vuelos.json") ? "vuelos.json" : e.request, copy)); }
      return r;
    }).catch(() => caches.match(url.pathname.endsWith("vuelos.json") ? "vuelos.json" : e.request))
  );
});
