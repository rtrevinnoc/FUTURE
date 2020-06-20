const OFFLINE_VERSION = 1;
const CACHE_NAME = 'FUTURE';
var CACHED_FILES = [
	'/offline.html',
	'/apple-touch-icon.png',
	'/favicon-32x32.png',
	'/favicon-16x16.png',
	'/site.webmanifest',
	'/safari-pinned-tab.svg',
	'/css/default/FONTS.css',
	'/css/default/OFFLINE.css',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.otf',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.otf.woff',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.ttf',
	'/fonts/sourceSansPro/Light/SourceSansPro-Light.ttf.woff2',
]

self.addEventListener('install', (event) => {
	event.waitUntil((async () => {
		const cache = await caches.open(CACHE_NAME);
		// Setting {cache: 'reload'} in the new request will ensure that the response
		// isn't fulfilled from the HTTP cache; i.e., it will be from the network.
		await cache.addAll(CACHED_FILES);
	})());
});

self.addEventListener('activate', (event) => {
	event.waitUntil((async () => {
		// Enable navigation preload if it's supported.
		// See https://developers.google.com/web/updates/2017/02/navigation-preload
		if ('navigationPreload' in self.registration) {
			await self.registration.navigationPreload.enable();
		}
	})());

	// Tell the active service worker to take control of the page immediately.
	self.clients.claim();
});

self.addEventListener('fetch', (event) => {
	// We only want to call event.respondWith() if this is a navigation request
	// for an HTML page.
	if (event.request.mode === 'navigate') {
		event.respondWith((async () => {
			const cache = await caches.open(CACHE_NAME);
			try {
				try {
					// First, try to use the navigation preload response if it's supported.
					const preloadResponse = await event.preloadResponse;
					if (preloadResponse) {
						return preloadResponse;
					}

					const networkResponse = await fetch(event.request);
					return networkResponse;
				} catch (error) {
					// catch is only triggered if an exception is thrown, which is likely
					// due to a network error.
					// If fetch() returns a valid HTTP response with a response code in
					// the 4xx or 5xx range, the catch() will NOT be called.
					console.log('Fetch failed; returning offline page instead.', error);

					return await cache.match(OFFLINE_URL);
				}
			} catch (error) {
				return await cache.match(event.request);
			}
		})());
	}
});
